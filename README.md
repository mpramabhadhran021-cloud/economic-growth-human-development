# Does Economic Growth Translate into Human Development?

### An Empirical Statistical Analysis of Economic Prosperity, Inequality, Poverty, and Human Development Across Countries

## Research Question

To what extent is economic prosperity associated with human development, and
how does inequality relate to this relationship? This project investigates
the chain **economic prosperity → inequality/poverty → human development**
using official cross-country statistics, distinguishing carefully between
*association*, *prediction*, and *causal* claims throughout.

## Motivation

GDP and GNI per capita remain the default proxies for national progress, but
they measure market production, not distribution or wellbeing. The UNDP's
Human Development Index (HDI) was created precisely to address this gap by
combining health, education, and income into a single composite measure.
This project asks how far income alone gets you in explaining HDI, and
whether inequality and poverty carry additional, independent information.
The chain tested here maps directly onto three SDGs UN agencies track
jointly: **SDG 1** (poverty), **SDG 8** (income/economic growth), and
**SDG 10** (inequality) — asking whether progress on SDG 8 mechanically
carries over into broader human development, or whether SDG 10-type
inequality and SDG 1-type poverty measures add independent information
beyond income alone.

## Research Objectives

- Quantify the association between income per capita and HDI (RQ1).
- Test whether inequality is associated with HDI conditional on income (RQ2).
- Test the same for poverty (RQ3).
- Characterize heterogeneity among similarly-wealthy countries (RQ4).
- Identify countries with HDI substantially above/below their income-based
  prediction (RQ5), as a *model-conditional*, not absolute, ranking.
- Compare income's association across separate development dimensions —
  health and education — rather than mechanically regressing HDI on its own
  components (RQ6).

## Hypotheses

| # | Hypothesis | Result |
|---|---|---|
| H1 | Higher income per capita → higher HDI (β₁ > 0) | **Supported, with a magnitude caveat.** Strong and stable across cross-sectional specifications (β≈0.10); a panel fixed-effects check shows the purely within-country association is smaller (β≈0.035, still highly significant) once persistent between-country differences are removed. |
| H2 | Greater inequality → lower HDI, conditional on income (β₂ < 0) | **Directionally supported, but weak.** Borderline significant (p≈0.05); loses significance once poverty is added. |
| H3 | Similar-income countries can have substantially different HDI | **Supported.** Considerable heterogeneity visible at every income level. |
| H4 | Some countries substantially outperform their income-based HDI prediction | **Supported.** A model-conditional ranking is produced and shown to be stable under an alternative functional form. |

## Data Sources

Official/authoritative sources only (no Kaggle, no unattributed scrapes):

- **UNDP Human Development Report 2023/24**, Statistical Annex Table 2 (HDI, 1990–2022)
- **World Bank**: GDP, population, Gini index
- **World Bank Poverty and Inequality Platform (PIP)**: poverty headcount ratios
- **UN Statistics Division**: ISO/M49 country and region reference

Full provenance, exact indicator codes, retrieval dates, and known
limitations of every source are documented in `data/raw/SOURCES.md`. The
complete variable-level data dictionary is in
`data/processed/data_dictionary.md`.

*Note: raw inputs are pinned to versioned, citation-preserving GitHub mirrors
(`datasets/*`, `owid/*`) rather than called live from the UNDP/UN/World Bank
sites at run time, for reproducibility — a pinned file gives byte-identical
input on every re-run, whereas a live API/site call can return a revised
value tomorrow. Each mirror links back to the same official indicator — see
`SOURCES.md` for the full rationale and exact URLs.*

## Methodology

- **Unit of analysis**: country-year panel (1990–2022, 193 countries), used
  two ways — a 2022 cross-section as the primary analytical sample, and the
  full panel for a fixed-effects check (below).
- **Models**: OLS regression, HDI on log(GDP per capita), then adding Gini
  and poverty; heteroskedasticity-robust (HC3) standard errors used for
  formal inference. A **panel two-way (country + year) fixed-effects model**
  is also estimated on the full 1990–2022 panel to separate the
  within-country association from persistent between-country differences.
- **Diagnostics**: multicollinearity (VIF), heteroskedasticity
  (Breusch-Pagan), functional form (raw vs. log vs. quadratic income),
  influential-observation analysis (Cook's distance, leverage).
- **Flagship analysis**: residuals from the income-only model, interpreted
  as *"higher/lower than income-based prediction"* — explicitly not labeled
  causal efficiency or policy performance.
- **Robustness (8 checks)**: HC3 robust SE, quadratic functional form,
  excluding influential observations, alternative year (2015), excluding
  micro-states, complete-case sample comparison, panel fixed-effects
  (within- vs. between-country), and region-clustered standard errors.
- Full code in `notebooks/01_data_exploration.ipynb` and
  `notebooks/02_statistical_analysis.ipynb`; reusable logic in `src/`.

## Key Findings

- The association between log income per capita and HDI is strong,
  precisely estimated, and extremely stable *across cross-sectional
  specifications*: R² ≈ 0.90, coefficient ≈ 0.10, essentially unchanged
  across the primary specification, a different year (2015), a sample
  excluding micro-states, and a sample excluding the most influential
  observations. A panel fixed-effects check (country + year effects, full
  1990–2022 panel) shows this shrinks to β ≈ 0.035 once persistent
  between-country differences are removed — still positive and highly
  significant, but roughly a third the cross-sectional size. Both numbers
  are reported: cross-country income differences track HDI closely, while
  the purely within-country link (a country's own income change predicting
  its own HDI change) is real but more modest.
- Conditional on income, higher inequality (Gini) is associated with lower
  HDI, but this result is only borderline statistically significant and does
  not survive the addition of a poverty measure to the model — it is
  reported as tentative, not confirmed.
- Gini and poverty missingness are not equally random: Gini coverage shows
  no significant relationship to income or HDI, while poverty coverage does
  — but bimodally, with both the poorest, most fragile states and a handful
  of very high-income states disproportionately missing, for different
  reasons (survey infrastructure gaps vs. the poverty line not being
  tracked the same way near zero).
- Substantial heterogeneity in HDI exists among countries at similar income
  levels. A residual-based ranking identifies countries such as Tajikistan,
  Sri Lanka, and Kyrgyzstan as having notably higher HDI than their income
  alone predicts, and others (including some high-income micro-states) as
  notably lower — a ranking shown to be robust to an alternative functional
  form, but explicitly *model-conditional*, not an absolute judgment.
- Income shows a broadly similar-strength association with life expectancy
  and expected years of schooling individually (R² ≈ 0.64–0.66 for each),
  though this specific comparison is limited by a data-vintage mismatch
  (older life-expectancy/schooling data matched against 2022 income).

## Robustness

Eight robustness/sensitivity checks are reported in Notebook 2. Six
cross-sectional variants (HC3 SE, quadratic form, excluding influential
observations, alternative year, excluding micro-states, complete-case
sample) all point to the same conclusion: the income–HDI association is
strong and stable, and the inequality association is real in direction but
small and fragile. The remaining two are the deliberate exception, not a
robustness pass: the **panel fixed-effects check** shows the within-country
association is materially smaller than the cross-sectional one (see Key
Findings), and **region-clustered SE** (5 clusters — a directional check
only) leave the income result significant despite a 3x wider standard
error. See the full specification-comparison table in
`02_statistical_analysis.ipynb`.

## Limitations

This project is primarily **observational and cross-sectional**; every
reported relationship is a statistical association, not a causal effect.
The panel fixed-effects check narrows one channel of omitted-variable bias
(time-invariant confounders) but not others (time-varying confounders), so
this remains true even for the within-country estimate. Key limitations
include incomplete Gini/poverty coverage (quantified, not just flagged —
Gini missingness is unrelated to income/HDI, poverty missingness is
significant and bimodal across both ends of the income distribution), a
data-vintage mismatch for the secondary health/education dimension analysis,
use of GDP rather than GNI per capita as the income measure, and the
inherent limitations of composite indices like HDI and single summary
statistics like the Gini coefficient. HDI reflects the 2023/24 Human
Development Report (2022 data), the latest available at this project's
data-acquisition date (2026-08-12) — check
[hdr.undp.org/data-center](https://hdr.undp.org/data-center) for a newer
release before treating this as current. The full limitations discussion —
data, statistical, measurement, and interpretation — is in Notebook 2.

## Reproducibility

```bash
pip install -r requirements.txt
python src/fetch_raw_data.py      # downloads all raw data from source URLs
python src/data_processing.py     # cleans and merges into data/processed/
jupyter nbconvert --to notebook --execute notebooks/01_data_exploration.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_statistical_analysis.ipynb
```

No absolute/machine-specific paths, no random-seed-dependent steps beyond a
fixed seed (42) set for reproducibility, and raw data are never overwritten
by processed output.

## Repository Structure

```text
economic-growth-human-development/
├── README.md
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_statistical_analysis.ipynb
├── data/
│   ├── raw/            # untouched downloaded source files + SOURCES.md
│   └── processed/      # analytical_panel.csv, cross_section_2022.csv,
│                        # dimensions_latest_available.csv, data_dictionary.md
├── figures/             # all publication-quality figures (PNG)
├── report/
│   └── research_report.pdf
├── src/
│   ├── fetch_raw_data.py
│   └── data_processing.py
├── requirements.txt
├── LICENSE
└── .gitignore
```

## References

- UNDP Human Development Report Office (2024). *Human Development Report
  2023/24*, Statistical Annex. https://hdr.undp.org/data-center
- World Bank. World Development Indicators.
  https://data.worldbank.org
- World Bank. Poverty and Inequality Platform. https://pip.worldbank.org
- UN Statistics Division. Standard Country or Area Codes for Statistical
  Use (M49). https://unstats.un.org/unsd/methodology/m49/
