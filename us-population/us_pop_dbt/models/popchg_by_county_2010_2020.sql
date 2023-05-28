with state_county_fips as (
select
t.state
, t.county
, CONCAT(REPEAT('0', 2 - LENGTH(t.state)), t.state) AS state_fips
, CONCAT(REPEAT('0', 3 - LENGTH(t.county)), t.county) AS county_fips
, t.popestimate2020 - t.popestimate2010 AS npopchg_2010_2020
from
    public.us_counties_pop_est_2010_2020_raw as t
)
select
    CONCAT(state_county_fips.state_fips, state_county_fips.county_fips) as id
    , state_county_fips.state_fips
    , state_county_fips.county_fips
    , raw.stname
    , raw.ctyname
    , raw.popestimate2010
    , raw.popestimate2020
    , state_county_fips.npopchg_2010_2020
    , ROUND(CAST((state_county_fips.npopchg_2010_2020 / CAST(CAST(raw.popestimate2010 AS DOUBLE PRECISION) AS DOUBLE PRECISION)) * 100 AS numeric), 2) as npopchg_2010_2020_perc_diff
from
    public.us_counties_pop_est_2010_2020_raw as raw
    left join
        state_county_fips as state_county_fips
    on
        raw.state = state_county_fips.state
        and raw.county = state_county_fips.county
