# Raw Data Sources

All data are retrieved from official statistical agencies or from
well-documented, actively-maintained open mirrors of official data (see the
note at the end of this file for why mirrors were used over the primary
UNDP/UN/World Bank endpoints in this build). No Kaggle datasets or unsourced
scrapes are used.

Retrieval date for all files below: **2026-08-12**.

## HDI — `HDR23-24_HDI_Trends.xlsx`
- **Primary source**: UNDP Human Development Report Office, *Human Development
  Report 2023/24*, Statistical Annex, **Table 2: Human Development Index Trends,
  1990–2022**.
- **Official page**: https://hdr.undp.org/data-center/documentation-and-downloads
- **Retrieved via**: mirror hosted in the `openwashdata/worldhdi` GitHub repository
  (an open-data R package that redistributes the official HDR annex file
  unmodified): https://github.com/openwashdata/worldhdi
- **Indicator**: Human Development Index (composite of life expectancy, expected
  and mean years of schooling, and GNI per capita, geometric mean of three
  normalized sub-indices). See UNDP Technical Note 1 for construction details.
- **Coverage**: 195 countries/territories, years 1990, 2000, 2010, 2015,
  2019–2022 (the exact years published in the annex; not a continuous annual
  series before 2019).
- **Known limitation**: this is the most recent HDR available (2023/24 report,
  reflecting 2022 data) — later HDI releases may exist beyond this project's
  data-acquisition date and are not reflected here.

## GDP — `gdp_worldbank.csv`
- **Primary source**: World Bank, GDP (current US$), indicator `NY.GDP.MKTP.CD`.
- **Retrieved via**: `datasets/gdp` (Frictionless Data / Open Knowledge core
  datasets, a maintained standard-CSV mirror of the World Bank indicator):
  https://github.com/datasets/gdp
- **Coverage**: 264 countries/aggregates, 1960–2023 (aggregates removed during
  cleaning; see `src/data_processing.py`).

## Population — `population_worldbank.csv`
- **Primary source**: World Bank, total population, indicator `SP.POP.TOTL`.
- **Retrieved via**: https://github.com/datasets/population
- **Coverage**: 1960–2024. Used only to derive GDP per capita.

## Gini index — `gini_worldbank.csv`
- **Primary source**: World Bank, Gini index, indicator `SI.POV.GINI`.
- **Retrieved via**: https://github.com/datasets/gini-index
- **Coverage**: 1963–2024, but sparse per country (household-survey based,
  not annual — see missing-data analysis in Notebook 1).

## Poverty — `poverty_worldbank_pip.csv`
- **Primary source**: World Bank Poverty and Inequality Platform (PIP),
  headcount ratio at the international poverty line (2017 PPP $2.15/day for
  the vintage used here).
- **Official page**: https://pip.worldbank.org/
- **Retrieved via**: `owid/poverty-data`, Our World in Data's maintained mirror
  of PIP: https://github.com/owid/poverty-data
- **Coverage**: household-survey based, irregular timing per country (see
  missing-data analysis).

## Country reference / UN region — `country_codes.csv`
- **Primary source**: ISO 3166-1 country codes cross-referenced with the UN
  Statistics Division M49 standard (region / sub-region classification).
- **Retrieved via**: https://github.com/datasets/country-codes
- **Note**: no authoritative World Bank income-group classification was found
  via an accessible mirror; income group is therefore **not** included as a
  variable in this project (UN region/sub-region is used instead).

## Secondary dimensions (life expectancy, schooling) — `owid_dimensions/`
- **life_expectancy.csv**: World Bank, life expectancy at birth. Source vintage:
  Our World in Data historical dataset archive (`owid/owid-datasets`, folder
  "Life Expectancy (at birth) - World Bank (2015)"). **Coverage: 1960–2013 only**
  — this archive was not updated after ~2015 and is the most recent freely
  mirrored vintage of this indicator found. Used for the RQ6 dimension analysis,
  clearly dated, not extrapolated to 2022.
- **expected_years_schooling.csv**: UNDP, expected years of schooling. Source:
  `owid/owid-datasets`, folder "Expected Years of Schooling - UNDP (2018)".
  **Coverage: 1990–2017.**
- **mean_years_schooling.csv**: Lee-Lee (2016) / Barro-Lee (2018) / UNDP (2018)
  composite series, average years of schooling, adult population. Source:
  `owid/owid-datasets`. **Coverage: 1870–2017** (used 1990 onward here).
- These three series are **older-vintage** than the 2022 HDI cross-section.
  They are used for a separate "most-recent-available-year" snapshot
  (`data/processed/dimensions_latest_available.csv`), not forced onto 2022 —
  see Notebook 1, Section 29 (Development-Dimension Analysis) for how this
  vintage mismatch is handled and disclosed.

## Why versioned GitHub mirrors instead of live API/site calls
This project deliberately pins every raw input to a specific, citable GitHub
commit rather than calling the UNDP HDR data center, UN SDG API, or World
Bank API live at run time. Three reasons:

1. **Reproducibility.** A live API call can return a different value tomorrow
   than it does today (indicators get revised). A pinned mirror file gives
   every re-run of `src/fetch_raw_data.py` byte-identical input, which matters
   for a project whose entire point is a reproducible pipeline.
2. **Provenance auditability.** Each mirror listed above (`datasets/*`,
   `owid/*`, `openwashdata/worldhdi`) redistributes the official file
   unmodified and links back to the primary indicator code, so the chain from
   raw file to official source is verifiable without needing an active session
   or API key.
3. **No API key / rate-limit dependency.** The World Bank and UN SDG APIs are
   free but rate-limited and occasionally unstable for bulk pulls; the
   mirrors used here are static files, which keeps the pipeline simple and
   fast to re-run.

Each source section above links to both the mirror actually used and the
primary official page/indicator code, so provenance is traceable either way.
Anyone with API access is welcome to substitute direct calls to the UN SDG
API or UNDP HDR data center using the same indicator codes noted throughout
this file — the merge/cleaning logic in `src/data_processing.py` is written
against the column names, not the retrieval method, so it would not need to
change.
