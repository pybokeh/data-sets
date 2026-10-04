import json
from datetime import date

import matplotlib
matplotlib.use("Agg")  # non-interactive backend so tests don't open windows
import matplotlib.pyplot as plt
import polars as pl
import pytest
from unittest.mock import MagicMock

from blsutils.bls import BLSClient


# ---------- fixtures ----------

@pytest.fixture
def sample_response() -> str:
    """A minimal BLS-style response (newest first, like the real API)."""
    return json.dumps({
        "status": "REQUEST_SUCCEEDED",
        "Results": {
            "series": [{
                "seriesID": "CUUR0000SA0",
                "data": [
                    {"year": "2020", "period": "M13", "value": "258.8"},  # annual avg
                    {"year": "2020", "period": "M02", "value": "-"},      # missing
                    {"year": "2020", "period": "M01", "value": "257.97"},
                ],
            }]
        },
    })


@pytest.fixture
def client():
    with BLSClient(api_key="fake-key") as c:
        yield c


# ---------- parse_df ----------

def test_parse_df_columns_and_sorting(sample_response):
    df = BLSClient.parse_df(sample_response)
    assert df.columns == ["series_id", "year_month", "year", "period", "value"]
    assert df["year_month"].to_list() == [date(2020, 1, 1), date(2020, 2, 1)]


def test_parse_df_drops_annual_average(sample_response):
    df = BLSClient.parse_df(sample_response)
    assert "M13" not in df["period"].to_list()


def test_parse_df_missing_value_becomes_null(sample_response):
    df = BLSClient.parse_df(sample_response)
    assert df["value"].to_list() == [257.97, None]
    assert df.schema["value"] == pl.Float64


def test_parse_df_raises_on_api_error():
    bad = json.dumps({"status": "REQUEST_NOT_PROCESSED", "message": ["Bad key"]})
    with pytest.raises(ValueError, match="BLS API error"):
        BLSClient.parse_df(bad)


def test_parse_df_empty_data_keeps_schema():
    empty = json.dumps({
        "status": "REQUEST_SUCCEEDED",
        "Results": {"series": [{"seriesID": "X", "data": []}]},
    })
    df = BLSClient.parse_df(empty)
    assert df.height == 0
    assert "value" in df.columns


# ---------- constructor / API key ----------

def test_init_uses_explicit_key():
    assert BLSClient(api_key="abc").api_key == "abc"


def test_init_reads_env_var(monkeypatch):
    monkeypatch.setattr("blsutils.bls.load_dotenv", lambda: None)  # ignore real .env
    monkeypatch.setenv("BLS_API_KEY", "from-env")
    assert BLSClient().api_key == "from-env"


def test_init_raises_without_key(monkeypatch):
    monkeypatch.setattr("blsutils.bls.load_dotenv", lambda: None)
    monkeypatch.delenv("BLS_API_KEY", raising=False)
    with pytest.raises(ValueError, match="No BLS API key"):
        BLSClient()


# ---------- fetch_raw / fetch_df (mocked HTTP) ----------

def test_fetch_raw_sends_expected_payload(client, sample_response):
    mock_resp = MagicMock()
    mock_resp.text = sample_response
    client._session.post = MagicMock(return_value=mock_resp)

    result = client.fetch_raw("CUUR0000SA0", 2020, 2025)

    assert result == sample_response
    _, kwargs = client._session.post.call_args
    assert kwargs["json"] == {
        "seriesid": ["CUUR0000SA0"],
        "startyear": "2020",
        "endyear": "2025",
        "registrationkey": "fake-key",
    }
    mock_resp.raise_for_status.assert_called_once()


def test_fetch_raw_propagates_http_errors(client):
    import requests
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
    client._session.post = MagicMock(return_value=mock_resp)

    with pytest.raises(requests.HTTPError):
        client.fetch_raw("CUUR0000SA0", 2020, 2025)


def test_fetch_df_end_to_end(client, sample_response):
    mock_resp = MagicMock(text=sample_response)
    client._session.post = MagicMock(return_value=mock_resp)

    df = client.fetch_df("CUUR0000SA0", 2020, 2025)
    assert df.height == 2


# ---------- plotting ----------

def test_plot_runs_without_error(sample_response, monkeypatch):
    shown = MagicMock()
    monkeypatch.setattr(plt, "show", shown)
    df = BLSClient.parse_df(sample_response)

    BLSClient.plot_bls_series(df, "test description")

    shown.assert_called_once()
    assert "CUUR0000SA0" in plt.gcf().axes[0].get_title()
    plt.close("all")


# ---------- context manager ----------

def test_context_manager_closes_session():
    with BLSClient(api_key="k") as c:
        c._session.close = MagicMock()
    c._session.close.assert_called_once()