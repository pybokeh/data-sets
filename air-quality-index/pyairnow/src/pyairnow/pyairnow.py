import os

from dotenv import load_dotenv
import polars as pl
import requests

URL = "https://www.airnowapi.org/aq/observation/current/ziplatlong/"

class AirNowClient:
    def __init__(self, api_key: str | None = None):
        if api_key is None:
            # Read a .env file (if present) into the environment, then look up the key.
            # Variables already set in the real environment are not overridden.
            load_dotenv()
            api_key = os.getenv("AIRNOW_API_KEY")
        if not api_key:
            raise ValueError(
                "No Air Now API key found. Pass api_key=... or set AIRNOW_API_KEY "
                "in your environment or a .env file."
            )
        self.api_key = api_key
        self._session = requests.Session()

    def fetch_df_by_lat_lon(self, lat: float, lon: float) -> pl.DataFrame:
        params = {
            "format": "application/json",
            "latitude": lat,
            "longitude": lon,
            "API_KEY": self.api_key,
        }
        response = self._session.get(URL, params=params, timeout=(5, 15))
        response.raise_for_status()
        return pl.DataFrame(response.json(), schema_overrides={"reportingAreaName": pl.String})


if __name__ == "__main__":
    client = AirNowClient()
    df: pl.DataFrame = client.fetch_df_by_lat_lon(lat=38.691881, lon=-77.411563)

    print(df)
