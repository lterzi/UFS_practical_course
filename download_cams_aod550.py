r"""Download CAMS aod550 forecasts from the ADS API.

Requires ~/.cdsapirc with your personal access token, see
https://ads.atmosphere.copernicus.eu/how-to-api. You must also accept the
dataset's Terms of Use once via the web form before the API request works.

Usage (activate MTG_env first):
    source ~/MTG_env/bin/activate
    python download_cams_aod550.py --date 20260806

Cron example (runs at 06:00 and 18:00 UTC, downloads today's data,
overwriting the file so it picks up whichever timestep has newly appeared):
    0 6,18 * * * source ~/MTG_env/bin/activate && python /project/meteo/work/L.Terzi/ufs_praktikum/CAMS/download_cams_aod550.py --date $(date -u +\%Y\%m\%d)
"""
import argparse
import datetime
import os
import shutil
import tempfile
import zipfile

import cdsapi

DATASET = "cams-global-atmospheric-composition-forecasts"
OUT_DIR = "/scratch/l/L.Terzi/CAMS/"

LEADTIME_HOUR = [str(x) for x in range(0, 121)]  # 0 to 24 hours in 1-hour steps


def normalize_date(date: str) -> str:
    """Accept YYYY-MM-DD or YYYYMMDD, always return YYYY-MM-DD."""
    fmt = "%Y-%m-%d" if "-" in date else "%Y%m%d"
    return datetime.datetime.strptime(date, fmt).strftime("%Y-%m-%d")


def download(date: str, out_file: str) -> None:
    client = cdsapi.Client()
    request = {
        "variable": ["total_aerosol_optical_depth_550nm"],
        "date": [f"{date}/{date}"],
        "time": ["00:00"],#["00:00", "12:00"],
        "leadtime_hour": LEADTIME_HOUR,
        "type": ["forecast"],
        "data_format": "netcdf_zip",
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "download.zip")
        client.retrieve(DATASET, request, zip_path)

        with zipfile.ZipFile(zip_path) as zf:
            nc_names = [n for n in zf.namelist() if n.endswith(".nc")]
            zf.extractall(tmp_dir)

        shutil.move(os.path.join(tmp_dir, nc_names[0]), out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYYMMDD or YYYY-MM-DD, defaults to today (UTC)")
    parser.add_argument("--out", default=None, help="output .nc path")
    args = parser.parse_args()

    date = normalize_date(args.date) if args.date else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    out_file = args.out or os.path.join(OUT_DIR, f"{date.replace('-', '')}_aod550.nc")
    download(date, out_file)
    print(f"saved {out_file}")
