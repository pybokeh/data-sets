import json
import matplotlib.pyplot as plt
import os
import polars as pl
import requests
from dotenv import load_dotenv

_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

class BLSClient:
    def __init__(self, api_key: str | None = None):
        if api_key is None:
            # Read a .env file (if present) into the environment, then look up the key.
            # Variables already set in the real environment are not overridden.
            load_dotenv()
            api_key = os.getenv("BLS_API_KEY")
        if not api_key:
            raise ValueError(
                "No BLS API key found. Pass api_key=... or set BLS_API_KEY "
                "in your environment or a .env file."
            )
        self.api_key = api_key
        self._session = requests.Session()

    def fetch_raw(self, series_id: str, start_year: int, end_year: int) -> str:
        """Return the raw BLS JSON response text."""
        response = self._session.post(
            _URL,
            json={
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(end_year),
                "registrationkey": self.api_key,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def fetch_df(self, series_id: str, start_year: int, end_year: int) -> pl.DataFrame:
        """Fetch and parse into a polars DataFrame in one call."""
        return self.parse_df(self.fetch_raw(series_id, start_year, end_year))

    @staticmethod
    def parse_df(data_str: str) -> pl.DataFrame:
        """Parse previously saved raw JSON text into a DataFrame."""
        parsed: dict = json.loads(data_str)

        # BLS can return HTTP 200 with an error described in the body
        if parsed.get("status") != "REQUEST_SUCCEEDED":
            raise ValueError(f"BLS API error: {parsed.get('message')}")

        series: dict = parsed["Results"]["series"][0]
        series_id: str = series["seriesID"]

        records = [
            {"year": d["year"], "period": d["period"], "value": d["value"]}
            for d in series["data"]
        ]

        # Explicit schema so an empty result still has the expected columns
        schema: dict = {"year": pl.Utf8, "period": pl.Utf8, "value": pl.Utf8}

        return (
            pl.DataFrame(records, schema=schema)
            # Monthly values only; M13 is the annual average
            .filter(
                (pl.col("period") >= "M01") & (pl.col("period") <= "M12")
            )
            .with_columns(
                pl.lit(series_id).alias("series_id"),
                pl.concat_str(
                    pl.col("year") + "-" + pl.col("period").str.slice(-2) + "-01"
                )
                .str.to_date("%Y-%m-%d")
                .alias("year_month"),
                # Missing values are "-", which becomes null with strict=False
                pl.col("value").cast(pl.Float64, strict=False),
            )
            .select("series_id", "year_month", "year", "period", "value")
            .sort("year_month")  # BLS returns newest first
        )

    @staticmethod
    def plot_bls_series(data: pl.DataFrame, series_desc: str):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(
            data["year_month"].to_numpy(),
            data["value"].to_numpy(),  # nulls become NaN, which matplotlib draws as a gap
        )

        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.set_title(f'Series ID: {data.unique("series_id").select("series_id").item()}' + '\n' + series_desc)
        ax.spines[["right", "top"]].set_visible(False)

        plt.tight_layout()
        plt.show()


# Following methods allow for use with Context Manager
    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "BLSClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()


if __name__ == "__main__":
    with BLSClient() as client:  # key comes from BLS_API_KEY / .env
        raw = client.fetch_raw("CUUR0000SA0", 2020, 2025)  # workflow 1
        df = client.fetch_df("CUUR0000SA0", 2020, 2025)    # workflow 2
        client.plot_bls_series(df, "chart title")
        print(df.head())

    with pl.Config(tbl_rows=1000):  # -1 means show all rows
        print(df.sort(["year", "period"]))

# Discovered that in the BLS API, the "value" attribute can contain dash/"-" to indicate missing data
# Background info: https://www.bls.gov/bls/bls-handling-of-missing-data.htm
