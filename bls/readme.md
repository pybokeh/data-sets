# Bureau of Labor Statistics

#### To use the custom blsutils package found in the src direcctory:
Navigate to `src` directory then issue the following command:

`pip install -e .`

This package assumes that you've acquired the developer API key from `bls.gov` and that 
you have the bls series ID that you want to plot.

Example usage:
```python
from blsutils import BLSClient

with BLSClient() as client:  # key comes from BLS_API_KEY / .env
    df = client.fetch_df("CES0000000001", 2018, 2026)
    client.plot_bls_series(df, "Jobs Added - All employees, thousands, total nonfarm, seasonally adjusted")
    print(df.tail())
```

If you want the actual, low-level Python code used to create the plots, look at the [BLS_API.ipynb](BLS_API.ipynb) 
notebook or the `blsutils` package found in the `src` directory.

#### BLS Index Series
- Complete list of CPI series ID: https://download.bls.gov/pub/time.series/cu/cu.series
- Complete list of national unemployment series ID: https://download.bls.gov/pub/time.series/ln/ln.series
- Complete list of Current Employment Statistics series ID and their descriptions: https://download.bls.gov/pub/time.series/ce/ce.series

#### Avg Price Series (NOTE: Unfortunately, can not tell by description if the series have current prices or only historical (only early start and end years)
- https://download.bls.gov/pub/time.series/ap/ap.series
