# Data Dictionary

Analytical files: `analytical_panel.csv` (country-year, 1990–2022),
`cross_section_2022.csv` (subset, year == 2022),
`dimensions_latest_available.csv` (most recent available year per country for
the three older-vintage dimension variables — see `data/raw/SOURCES.md`).

| Variable | Definition | Unit | Source | Years available | 2022 coverage | Role |
|---|---|---|---|---|---|---|
| `country` | Country/territory name (as published by UNDP HDR) | text | UNDP HDR | — | 195/195 | identifier |
| `country_code` | ISO 3166-1 alpha-3 code | text | derived crosswalk | — | 195/195 | identifier |
| `year` | Calendar year | year | — | 1990–2022 | — | identifier |
| `hdi` | Human Development Index (composite of health, education, income sub-indices) | index, 0–1 | UNDP HDR 2023/24, Table 2 | 1990, 2000, 2010, 2015, 2019–2022 | 195/195 | **outcome** |
| `hdi_rank_2022` | Country's HDI rank in the 2022 report edition | rank | UNDP HDR 2023/24, Table 2 | fixed (2022 ranking) | 193/195 | descriptive |
| `gdp_current_usd` | Gross Domestic Product, current US$ | US$ | World Bank (`NY.GDP.MKTP.CD`) via `datasets/gdp` | 1960–2023 | 187/195 | intermediate (used to build per-capita) |
| `population` | Total population | persons | World Bank (`SP.POP.TOTL`) via `datasets/population` | 1960–2024 | 195/195 | intermediate |
| `gdp_per_capita_usd` | GDP ÷ population | US$/person | derived | 1960–2023 | 187/195 | **predictor** (economic prosperity) |
| `gini_index` | Gini coefficient of income/consumption inequality | index, 0–100 | World Bank (`SI.POV.GINI`) via `datasets/gini-index` | irregular, 1963–2024 | 134/195 (nearest survey within ±5y) | **predictor** (inequality) |
| `gini_index_source_year` | Actual survey year the matched Gini value comes from | year | derived | — | 134/195 | data-quality flag |
| `poverty_headcount_ratio` | % of population below the international poverty line | % | World Bank PIP via `owid/poverty-data` | irregular, 1967–2021 | 104/195 (nearest survey within ±5y) | **predictor** (poverty) |
| `poverty_headcount_ratio_source_year` | Actual survey year the matched poverty value comes from | year | derived | — | 104/195 | data-quality flag |
| `life_expectancy` | Life expectancy at birth | years | World Bank, via OWID archive | 1960–2013 only | 0/195 (see `dimensions_latest_available.csv`) | secondary outcome (RQ6) |
| `expected_years_schooling` | Expected years of schooling for a child entering school | years | UNDP, via OWID archive | 1990–2017 only | 0/195 (see `dimensions_latest_available.csv`) | secondary outcome (RQ6) |
| `mean_years_schooling` | Average years of schooling, adult population | years | Lee-Lee/Barro-Lee/UNDP, via OWID archive | 1990–2017 only (used from 1870) | 0/195 (see `dimensions_latest_available.csv`) | secondary outcome (RQ6) |
| `un_region` | UN M49 macro-region | text | UN Statistics Division, via `datasets/country-codes` | static | 195/195 | grouping variable |
| `un_subregion` | UN M49 sub-region | text | UN Statistics Division, via `datasets/country-codes` | static | 195/195 | grouping variable |

## Notes on construction (Section 5 constraint)

`hdi` is a **composite index built from** life expectancy, schooling, and GNI
per capita. `life_expectancy`, `expected_years_schooling`, and
`mean_years_schooling` are therefore **not** used as independent predictors of
`hdi` anywhere in this project — they are analysed only as separate outcomes
in their own right (RQ6 / Section 29), regressed on the same economic and
distributional predictors used for HDI, never regressed *against* HDI.

`gdp_per_capita_usd` (World Bank GDP ÷ population) is used as the income
predictor rather than GNI per capita (the income measure embedded in HDI
itself), because a GNI-per-capita series could not be retrieved through an
accessible mirror. This is a deliberate choice to avoid a mechanical,
near-tautological relationship between the income predictor and HDI's own
income sub-index; it is discussed as a limitation (GDP and GNI per capita are
highly correlated but not identical, particularly for countries with large
net income flows abroad).

## Note on analytical use of the panel

`cross_section_2022.csv` (the `year == 2022` slice) is the primary sample
for all cross-sectional models (M1–M3, diagnostics, the flagship residual
analysis). `analytical_panel.csv` — the full country-year file, not just its
2022 slice — is used separately for a panel fixed-effects check
(Notebook 2, Robustness 7) that regresses `hdi` on `log(gdp_per_capita_usd)`
with country and year fixed effects, to test how much of the cross-sectional
association reflects persistent between-country differences versus a
within-country relationship. `hdi` is only observed in 8 of the 33 years in
the panel (1990, 2000, 2010, 2015, 2019–2022, per the HDR annex — see
`data/raw/SOURCES.md`), so the panel model uses an unbalanced, non-continuous
time dimension, not annual data.
