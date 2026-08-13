"""
Downloads all raw data files used by this project from their canonical URLs.

Run this before src/data_processing.py to regenerate data/raw/ from scratch.
See data/raw/SOURCES.md for full provenance and why these particular URLs
(official-data mirrors) are used instead of the UNDP/UN/World Bank sites
directly.
"""

import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
(RAW / "owid_dimensions").mkdir(parents=True, exist_ok=True)

FILES = {
    "HDR23-24_HDI_Trends.xlsx":
        "https://raw.githubusercontent.com/openwashdata/worldhdi/main/data-raw/"
        "HDR23-24_Statistical_Annex_HDI_Trends_Table.xlsx",
    "gdp_worldbank.csv":
        "https://raw.githubusercontent.com/datasets/gdp/main/data/gdp.csv",
    "gini_worldbank.csv":
        "https://raw.githubusercontent.com/datasets/gini-index/main/data/gini-index.csv",
    "population_worldbank.csv":
        "https://raw.githubusercontent.com/datasets/population/main/data/population.csv",
    "country_codes.csv":
        "https://raw.githubusercontent.com/datasets/country-codes/master/data/country-codes.csv",
    "poverty_worldbank_pip.csv":
        "https://raw.githubusercontent.com/owid/poverty-data/main/datasets/pip_dataset.csv",
    "owid_dimensions/life_expectancy.csv":
        "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
        "Life%20Expectancy%20(at%20birth)%20-%20World%20Bank%20(2015)/"
        "Life%20Expectancy%20(at%20birth)%20-%20World%20Bank%20(2015).csv",
    "owid_dimensions/expected_years_schooling.csv":
        "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
        "Expected%20Years%20of%20Schooling%20-%20UNDP%20(2018)/"
        "Expected%20Years%20of%20Schooling%20-%20UNDP%20(2018).csv",
    "owid_dimensions/mean_years_schooling.csv":
        "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
        "Years%20of%20Schooling%20-%20based%20on%20Lee-Lee%20(2016)%2C%20Barro-Lee%20"
        "(2018)%20and%20UNDP%20(2018)/Years%20of%20Schooling%20-%20based%20on%20"
        "Lee-Lee%20(2016)%2C%20Barro-Lee%20(2018)%20and%20UNDP%20(2018).csv",
}


def main():
    for rel_path, url in FILES.items():
        dest = RAW / rel_path
        print(f"Fetching {rel_path} ...")
        urllib.request.urlretrieve(url, dest)
        print(f"  -> data/raw/{rel_path} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
