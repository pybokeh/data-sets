# Testing BLSClient with pytest

1. Install and configure

`pip install pytest`

Tell pytest where to find your code by adding this to pyproject.toml:

```aiignore
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

(Alternatively, pip install -e . if you've set up the package in pyproject.toml.) Then import with from blsutils.bls import BLSClient. Run tests from the project root with pytest (or pytest -v).

2. Key principle: never hit the real API 

Your tests should be fast, offline, and not burn your BLS quota. The good news is that your design already helps: parse_df is a pure static method that takes a string, so it's trivial to test. For fetch_raw, you mock the HTTP session.

3. Handy pytest concepts

- Fixtures (@pytest.fixture): reusable setup, injected by naming them as test arguments. The client fixture uses yield so cleanup runs after each test.
- monkeypatch: temporarily changes env vars or attributes, then undoes it automatically. I patch load_dotenv so a real .env on your machine can't make the "no key" test pass or fail unexpectedly.
- pytest.raises(..., match=...): asserts an exception and checks its message via regex.
- MagicMock: a stand-in for requests responses, and it records how it was called (call_args).

4. Useful commands

```
pytest                      # run everything
pytest -v                   # verbose
pytest tests/test_bls.py::test_parse_df_raises_on_api_error   # one test
pytest -k "parse_df"        # tests matching a name
pytest -x                   # stop at first failure
pip install pytest-cov && pytest --cov=blsutils --cov-report=term-missing
```

### Optional Extras

- responses or pytest-httpx/requests-mock: libraries that intercept requests calls at a lower level, so you don't have to patch _session.post by hand.
- Saved real response: run fetch_raw once, save the JSON to tests/data/cpi_sample.json, and load it in a fixture. This is exactly the use case your "workflow 1" (raw first, parse later) design supports.
- Live integration test: mark one with @pytest.mark.integration, skip it by default, and only run it manually when you want to verify the real API still behaves as expected.
