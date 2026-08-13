"""
Data processing pipeline for "Does Economic Growth Translate into Human Development?"

Reads raw official data from data/raw/ and produces a cleaned, merged
country-year analytical panel in data/processed/.

Raw sources (see data/raw/SOURCES.md for full provenance):
  - HDR23-24_HDI_Trends.xlsx      : UNDP HDR 2023/24 Statistical Annex, Table 2
                                     (HDI by country, 1990-2022)
  - gdp_worldbank.csv             : World Bank GDP, current US$, by country-year
  - population_worldbank.csv      : World Bank total population, by country-year
  - gini_worldbank.csv            : World Bank Gini index, by country-year
  - poverty_worldbank_pip.csv     : World Bank Poverty and Inequality Platform
                                     (headcount ratios), by country-year
  - country_codes.csv             : ISO3166 / UN M49 country reference (names,
                                     ISO3 codes, UN region & sub-region)

No values are imputed or fabricated. Countries that cannot be matched across
sources are logged, not silently dropped.
"""

import csv
import json
import unicodedata
from pathlib import Path

import openpyxl
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

HDI_YEAR_COLS = {
    1990: 2, 2000: 4, 2010: 6, 2015: 8, 2019: 10, 2020: 12, 2021: 14, 2022: 16,
}
HDI_RANK_COL = 0
HDI_NAME_COL = 1

# Names in the HDR table that do not correspond to individual countries
# (region / income-group / development-group aggregate rows, footnotes).
NON_COUNTRY_ROWS = {
    "Human development groups", "Very high human development", "High human development",
    "Medium human development", "Low human development", "Developing countries", "Regions",
    "Arab States", "East Asia and the Pacific", "Europe and Central Asia",
    "Latin America and the Caribbean", "South Asia", "Sub-Saharan Africa",
    "Least developed countries", "Small island developing states",
    "Organisation for Economic Co-operation and Development", "World",
}

# Manual overrides: HDR country name -> ISO3 code, for names that don't match
# country_codes.csv automatically (different naming conventions between the
# UN Statistics Division reference list and the UNDP HDR statistical annex).
HDR_NAME_TO_ISO3 = {
    "Hong Kong, China (SAR)": "HKG",
    "Korea (Republic of)": "KOR",
    "Korea (Democratic People's Rep. of)": "PRK",
    "Türkiye": "TUR",
    "Russian Federation": "RUS",
    "Brunei Darussalam": "BRN",
    "Bahamas": "BHS",
    "Iran (Islamic Republic of)": "IRN",
    "Moldova (Republic of)": "MDA",
    "Palestine, State of": "PSE",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Bolivia (Plurinational State of)": "BOL",
    "Micronesia (Federated States of)": "FSM",
    "Lao People's Democratic Republic": "LAO",
    "Eswatini (Kingdom of)": "SWZ",
    "Syrian Arab Republic": "SYR",
    "Tanzania (United Republic of)": "TZA",
    "Congo (Democratic Republic of the)": "COD",
    "Congo": "COG",
    "Côte d'Ivoire": "CIV",
    "Viet Nam": "VNM",
    "Cabo Verde": "CPV",
    "Sao Tome and Principe": "STP",
    "Czechia": "CZE",
    "North Macedonia": "MKD",
    "Timor-Leste": "TLS",
    "Guinea-Bissau": "GNB",
    "South Sudan": "SSD",
    "Saint Kitts and Nevis": "KNA",
    "Saint Vincent and the Grenadines": "VCT",
    "Saint Lucia": "LCA",
    "Antigua and Barbuda": "ATG",
    "Trinidad and Tobago": "TTO",
    "Bosnia and Herzegovina": "BIH",
    "Marshall Islands": "MHL",
    "Solomon Islands": "SLB",
    "Papua New Guinea": "PNG",
    "United States": "USA",
    "United Kingdom": "GBR",
    "United Arab Emirates": "ARE",
    "Andorra": "AND",
    "Monaco": "MCO",
    "San Marino": "SMR",
    "Liechtenstein": "LIE",
    # PIP (poverty) dataset spells some names differently from the HDR table
    "Turkey": "TUR",
    "Democratic Republic of Congo": "COD",
    "Micronesia (country)": "FSM",
    "Timor": "TLS",
    "Kosovo": "XKX",
}

# The HDI table lists real countries first, then switches to aggregate rows
# (development groups, regions, income groups, world). Stop parsing as soon
# as we reach the first aggregate-section marker.
HDI_TABLE_STOP_MARKER = "Human development groups"


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.strip().lower()


def build_name_to_iso3():
    """Build a lookup from (normalized) country name -> ISO3 using the UN
    country-codes reference file, then layer the manual HDR overrides on top."""
    lookup = {}
    with open(RAW / "country_codes.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = row.get("ISO3166-1-Alpha-3", "").strip()
            if not iso3:
                continue
            for key in ("official_name_en", "UNTERM English Short", "UNTERM English Formal", "CLDR display name"):
                val = (row.get(key) or "").strip()
                if val:
                    lookup[_norm(val)] = iso3
    for name, iso3 in HDR_NAME_TO_ISO3.items():
        lookup[_norm(name)] = iso3
    return lookup


def parse_hdi():
    wb = openpyxl.load_workbook(RAW / "HDR23-24_HDI_Trends.xlsx", data_only=True)
    ws = wb["HDI trends"]
    rows = list(ws.iter_rows(min_row=6, values_only=True))

    name_to_iso3 = build_name_to_iso3()
    records = []
    unmatched = []
    for row in rows:
        name = row[HDI_NAME_COL]
        if name is None:
            continue
        name = str(name).strip()
        if name == HDI_TABLE_STOP_MARKER:
            break
        if name in NON_COUNTRY_ROWS:
            continue
        if name.isupper():  # section header rows e.g. 'VERY HIGH HUMAN DEVELOPMENT'
            continue
        iso3 = name_to_iso3.get(_norm(name))
        if iso3 is None:
            unmatched.append(name)
            continue
        rank_2022 = row[HDI_RANK_COL]
        for year, col in HDI_YEAR_COLS.items():
            val = row[col]
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                # HDR annex uses ".." for genuinely unavailable country-year
                # observations (e.g. state did not exist / no data collected).
                # Treated as missing, not zero or interpolated.
                continue
            records.append({"country": name, "country_code": iso3, "year": year,
                             "hdi": val, "hdi_rank_2022": rank_2022})
    df = pd.DataFrame.from_records(records)
    if unmatched:
        print(f"[HDI] {len(unmatched)} HDR entities could not be matched to an ISO3 code "
              f"(likely aggregates, already excluded, or naming mismatches): {sorted(set(unmatched))}")
    return df


def load_wb_series(filename, value_name):
    df = pd.read_csv(RAW / filename, encoding="utf-8-sig")
    df = df.rename(columns={"Country Name": "country_wb", "Country Code": "country_code",
                             "Year": "year", "Value": value_name})
    df = df[["country_code", "year", value_name]].dropna(subset=[value_name])
    return df


def load_poverty():
    df = pd.read_csv(RAW / "poverty_worldbank_pip.csv", encoding="utf-8-sig")
    # Keep national-level headcount ratio at the international poverty line, one row
    # per country-year (this file has multiple reporting_level/welfare_type rows).
    df = df[(df["reporting_level"].isin(["national"])) ]
    df = df[["country", "year", "headcount_ratio_international_povline"]].rename(
        columns={"headcount_ratio_international_povline": "poverty_headcount_ratio"})
    df["year"] = df["year"].astype(int)
    df = df.dropna(subset=["poverty_headcount_ratio"])
    # attach iso3 via name lookup (PIP uses World Bank country names, close to country_codes)
    name_to_iso3 = build_name_to_iso3()
    df["country_code"] = df["country"].map(lambda n: name_to_iso3.get(_norm(n)))
    unmatched = sorted(df.loc[df["country_code"].isna(), "country"].unique())
    if unmatched:
        print(f"[Poverty] {len(unmatched)} PIP entities could not be matched to ISO3: {unmatched}")
    df = df.dropna(subset=["country_code"])
    return df[["country_code", "year", "poverty_headcount_ratio"]]


def load_region_metadata():
    rows = []
    with open(RAW / "country_codes.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = row.get("ISO3166-1-Alpha-3", "").strip()
            if not iso3:
                continue
            rows.append({
                "country_code": iso3,
                "un_region": row.get("Region Name", "").strip(),
                "un_subregion": row.get("Sub-region Name", "").strip(),
            })
    df = pd.DataFrame(rows).drop_duplicates(subset="country_code")
    return df


# Additional name variants seen in the OWID-curated dimension series (life
# expectancy, schooling) that are not already covered by HDR_NAME_TO_ISO3.
OWID_EXTRA_NAME_TO_ISO3 = {
    "Cote d'Ivoire": "CIV",
    "Democratic Republic of Congo": "COD",
    "Congo": "COG",
    "South Korea": "KOR",
    "North Korea": "PRK",
    "Micronesia (country)": "FSM",
    "Laos": "LAO",
    "Swaziland": "SWZ",
    "Cape Verde": "CPV",
    "Czech Republic": "CZE",
    "Macedonia": "MKD",
    "Timor": "TLS",
    "East Timor": "TLS",
    "Saint Kitts and Nevis": "KNA",
    "United States Virgin Islands": "VIR",
    "Vatican": "VAT",
    "Brunei": "BRN",
    "Bahamas": "BHS",
    "Gambia": "GMB",
    "Palestine": "PSE",
    "Russia": "RUS",
    "Iran": "IRN",
    "Vietnam": "VNM",
    "Syria": "SYR",
    "Tanzania": "TZA",
    "Moldova": "MDA",
    "Bolivia": "BOL",
    "Venezuela": "VEN",
    "Turkey": "TUR",
}


def load_owid_dimension_series(filename, value_col_substr, output_name):
    """Load one of the OWID-curated 'Entity, Year, <value>' dimension CSVs and
    attach ISO3 codes. Returns a DataFrame with country_code, year, output_name."""
    df = pd.read_csv(RAW / "owid_dimensions" / filename, encoding="utf-8-sig")
    value_col = [c for c in df.columns if value_col_substr.lower() in c.lower()][0]
    df = df.rename(columns={"Entity": "entity", "Year": "year", value_col: output_name})
    df = df[["entity", "year", output_name]].dropna(subset=[output_name])

    name_to_iso3 = build_name_to_iso3()
    name_to_iso3.update({_norm(k): v for k, v in OWID_EXTRA_NAME_TO_ISO3.items()})
    df["country_code"] = df["entity"].map(lambda n: name_to_iso3.get(_norm(n)))
    unmatched = sorted(df.loc[df["country_code"].isna(), "entity"].unique())
    if unmatched:
        print(f"[{output_name}] {len(unmatched)} entities could not be matched to ISO3 "
              f"(likely aggregates/regions, excluded): {unmatched}")
    df = df.dropna(subset=["country_code"])
    df["year"] = df["year"].astype(int)
    return df[["country_code", "year", output_name]]


def main():
    hdi = parse_hdi()
    gdp = load_wb_series("gdp_worldbank.csv", "gdp_current_usd")
    pop = load_wb_series("population_worldbank.csv", "population")
    gini = load_wb_series("gini_worldbank.csv", "gini_index")
    poverty = load_poverty()
    region = load_region_metadata()
    life_exp = load_owid_dimension_series("life_expectancy.csv", "Life Expectancy", "life_expectancy")
    exp_school = load_owid_dimension_series("expected_years_schooling.csv", "Expected Years", "expected_years_schooling")
    mean_school = load_owid_dimension_series("mean_years_schooling.csv", "Average Total Years", "mean_years_schooling")

    panel = hdi.merge(gdp, on=["country_code", "year"], how="left")
    panel = panel.merge(pop, on=["country_code", "year"], how="left")
    panel["gdp_per_capita_usd"] = panel["gdp_current_usd"] / panel["population"]

    # Gini and poverty are irregular (survey years), so merge as "nearest available
    # observation within +/- 2 years" per country rather than exact-year match, and
    # flag the linkage. This is documented explicitly, not silently interpolated.
    panel = panel.sort_values(["country_code", "year"])

    def nearest_merge(base, other, value_col, tol=2):
        out = []
        other_by_country = {k: v.sort_values("year") for k, v in other.groupby("country_code")}
        for _, row in base.iterrows():
            cc, yr = row["country_code"], row["year"]
            val, val_year = None, None
            if cc in other_by_country:
                cand = other_by_country[cc]
                cand = cand.assign(diff=(cand["year"] - yr).abs())
                cand = cand[cand["diff"] <= tol].sort_values("diff")
                if len(cand):
                    val = cand.iloc[0][value_col]
                    val_year = int(cand.iloc[0]["year"])
            out.append((val, val_year))
        base = base.copy()
        base[value_col] = [o[0] for o in out]
        base[value_col + "_source_year"] = [o[1] for o in out]
        return base

    # Gini and poverty surveys are infrequent (some countries go 5-10 years between
    # surveys), so a wider window is used than for GDP/population. The exact
    # source year of the matched observation is retained for transparency.
    panel = nearest_merge(panel, gini, "gini_index", tol=5)
    panel = nearest_merge(panel, poverty, "poverty_headcount_ratio", tol=5)

    # Life expectancy / schooling series are exact-year annual series, but the
    # underlying source archives stop in 2013 (life expectancy) and 2017
    # (schooling) -- these will be NaN for 2018-2022 by construction, not by
    # any processing error. Documented in the missing-data section, not imputed.
    panel = panel.merge(life_exp, on=["country_code", "year"], how="left")
    panel = panel.merge(exp_school, on=["country_code", "year"], how="left")
    panel = panel.merge(mean_school, on=["country_code", "year"], how="left")

    panel = panel.merge(region, on="country_code", how="left")

    col_order = ["country", "country_code", "year", "hdi", "hdi_rank_2022",
                 "gdp_current_usd", "population", "gdp_per_capita_usd",
                 "gini_index", "gini_index_source_year",
                 "poverty_headcount_ratio", "poverty_headcount_ratio_source_year",
                 "life_expectancy", "expected_years_schooling", "mean_years_schooling",
                 "un_region", "un_subregion"]
    panel = panel[col_order]
    panel.to_csv(PROCESSED / "analytical_panel.csv", index=False)

    # Convenience cross-section: latest HDI year (2022) only.
    cross = panel[panel["year"] == 2022].copy()
    cross.to_csv(PROCESSED / "cross_section_2022.csv", index=False)

    # Secondary-dimension snapshot: most recent available life-expectancy/schooling
    # observation per country (any year), with the source year retained, for the
    # RQ6 dimension analysis. This is deliberately NOT forced onto 2022.
    def latest_available(df, value_col):
        idx = df.dropna(subset=[value_col]).groupby("country_code")["year"].idxmax()
        out = df.loc[idx, ["country_code", "year", value_col]].rename(
            columns={"year": value_col + "_year"})
        return out

    dims = latest_available(panel[["country_code", "year", "life_expectancy"]], "life_expectancy")
    dims = dims.merge(latest_available(panel[["country_code", "year", "expected_years_schooling"]],
                                        "expected_years_schooling"), on="country_code", how="outer")
    dims = dims.merge(latest_available(panel[["country_code", "year", "mean_years_schooling"]],
                                        "mean_years_schooling"), on="country_code", how="outer")
    country_names = hdi[["country_code", "country"]].drop_duplicates()
    dims = country_names.merge(dims, on="country_code", how="right")
    dims.to_csv(PROCESSED / "dimensions_latest_available.csv", index=False)

    print(f"Panel: {panel.shape[0]} country-year rows, {panel['country_code'].nunique()} countries, "
          f"years {panel['year'].min()}-{panel['year'].max()}")
    print(f"2022 cross-section: {cross.shape[0]} countries")
    print(f"  with GDP per capita: {cross['gdp_per_capita_usd'].notna().sum()}")
    print(f"  with Gini (+/-5y):   {cross['gini_index'].notna().sum()}")
    print(f"  with poverty (+/-5y):{cross['poverty_headcount_ratio'].notna().sum()}")
    print(f"Dimensions snapshot (latest available, any year): {dims.shape[0]} countries")
    print(f"  with life expectancy:   {dims['life_expectancy'].notna().sum()}")
    print(f"  with expected schooling:{dims['expected_years_schooling'].notna().sum()}")
    print(f"  with mean schooling:    {dims['mean_years_schooling'].notna().sum()}")


if __name__ == "__main__":
    main()
