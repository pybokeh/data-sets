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

The source code is located [here](src/blsutils/bls.py)

**References:**
- URL: https://www.bls.gov/
- Developer API: https://www.bls.gov/developers/home.htm
- Registering for the API V2: https://www.bls.gov/developers/api_faqs.htm#register3
- How to add optional parameters like the secret key to the request: https://www.bls.gov/developers/api_signature_v2.htm#parameters
- Complete list of CPI series ID: https://download.bls.gov/pub/time.series/cu/cu.series
- Complete list of national unemployment series ID: https://download.bls.gov/pub/time.series/ln/ln.series


**Popular series ID:**
- LNS14000000: National unemployment rate - seasonally adjusted
- CUSR0000SA0: All items in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SETA: New and used motor vehicles in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SETA01: New vehicles in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SETA02: Used cars and trucks in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SAF: Food and beverages in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SACL1E4: Commodities less food, energy, and used cars and trucks in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SACE: Energy commodities in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SS47014: Gasoline, unleaded regular in U.S. city average, all urban consumers, seasonally adjusted
- CUSR0000SAH: Housing in U.S. city average, all urban consumers, seasonally adjusted

#### BLS Index Series
- Complete list of CPI series ID: https://download.bls.gov/pub/time.series/cu/cu.series
- Complete list of national unemployment series ID: https://download.bls.gov/pub/time.series/ln/ln.series
- Complete list of Current Employment Statistics series ID and their descriptions: https://download.bls.gov/pub/time.series/ce/ce.series

#### Avg Price Series (NOTE: Unfortunately, can not tell by description if the series have current prices or only historical (only certain start and end years)
- https://download.bls.gov/pub/time.series/ap/ap.series
