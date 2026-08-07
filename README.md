# UFS Practical Course

Scripts and notebooks for different tasks in the UFS practical course. Each task section below is self-contained — they don't share data or depend on each other, but they do share the same Python environment.

## Tasks

| Task | Files |
|------|-------|
| [CAMS Aerosol Optical Depth Plots](#task-cams-aerosol-optical-depth-plots) | `download_cams_aod550.py`, `plot_cams_aod550.py`, `make_day_viewer.py` |
| [MTG FCI Level-1C — Cloud Investigation](#task-mtg-fci-level-1c--cloud-investigation) | `download_fci.sh`, `investigate_fci.ipynb` |

`plots/` holds output figures and CSV time series for both tasks.

---

## Setting up the Python environment

Both tasks below use the same virtual environment. Create it once and install the required packages:

```bash
python3 -m venv MTG_env
source MTG_env/bin/activate
pip install satpy cartopy pyproj dask numpy matplotlib pandas netcdf4 xarray cdsapi pillow
```

To make the environment available as a kernel in Jupyter (needed for the FCI notebook):

```bash
pip install ipykernel
python -m ipykernel install --user --name MTG_env --display-name "Python (MTG_env)"
```

### Required packages

| Package | Purpose | Used by |
|---------|---------|---------|
| `cartopy` | Geographic map projections and coastline/border overlays | both |
| `matplotlib` | Plotting | both |
| `numpy` | Array operations | both |
| `xarray` | Reads/subsets NetCDF forecast data | CAMS |
| `cdsapi` | Downloads data from the ADS API | CAMS |
| `pillow` | Downsamples/re-encodes PNGs into the day-viewer HTML | CAMS |
| `satpy` | Reads FCI NetCDF files, handles calibration (counts → reflectance / brightness temperature) | FCI |
| `pyproj` | Coordinate transforms between lon/lat and geostationary projection | FCI |
| `dask` | Satpy uses dask for lazy loading; forced to synchronous mode to avoid HDF5 crashes | FCI |
| `pandas` | Time series table and CSV export | FCI |
| `netcdf4` | NetCDF backend | both |

All standard-library modules used (`re`, `glob`, `gc`, `collections`, `pathlib`, `warnings`, `argparse`, `datetime`, `json`, `base64`, `io`, `shutil`, `tempfile`, `zipfile`) require no installation.

---

## Task: CAMS Aerosol Optical Depth Plots

Downloads and plots CAMS (Copernicus Atmosphere Monitoring Service) total aerosol optical depth at 550 nm forecasts, cropped to a bbox covering 90°W–65°E, 10°–75°N. Three scripts form a pipeline: download → plot → interactive viewer.

### 1. `download_cams_aod550.py` — download

Downloads a forecast run from the ADS API (00 UTC, leadtimes 0–120h) and saves it to:

```
/scratch/l/L.Terzi/CAMS/{date}_aod550.nc
```

Requires `~/.cdsapirc` with a personal access token — see https://ads.atmosphere.copernicus.eu/how-to-api. You must also accept the dataset's Terms of Use once via the ADS web form before the API request works.

```bash
source ~/MTG_env/bin/activate
python download_cams_aod550.py --date 20260807
```

`--date` accepts `YYYYMMDD` or `YYYY-MM-DD` and defaults to today (UTC) if omitted.

### 2. `plot_cams_aod550.py` — plot

Reads the downloaded NetCDF file and produces one PNG per forecast hour in `plots/`, named `cams_aod550_{valid_time}.png`. Handles both single-leadtime and multi-leadtime (e.g. 0–120h) files automatically.

```bash
source ~/MTG_env/bin/activate
python plot_cams_aod550.py --date 20260807
```

`--date` works the same way as above and must match a file already downloaded.

### 3. `make_day_viewer.py` — interactive viewer

Builds a single self-contained HTML page with a slider/play-button to scrub through the PNGs produced above, over any date range. All frames are embedded as base64 JPEGs, so the resulting file has no external dependencies and works fully offline.

```bash
source ~/MTG_env/bin/activate
python make_day_viewer.py --start 20260807 --end 20260812
```

`--start`/`--end` accept `YYYYMMDD` or `YYYY-MM-DD`. The output is saved as `plots/viewer_{start}_{end}.html` — open it directly in any browser.

---

## Task: MTG FCI Level-1C — Cloud Investigation

Analysis of **Meteosat Third Generation (MTG) Flexible Combined Imager (FCI)** data, focusing on cloud detection and cloud top temperature estimation over the Zugspitze.

### Data

The notebook expects FCI Level-1C **FDHSI** (Full Disk High Spectral resolution Imagery) files in NetCDF format, organised by date under:

```
/scratch/l/L.Terzi/MTG-0degrees-FCI-Level1c/YYYY-MM-DD/
```

Each full-disk scan consists of ~40 body files (`CHK-BODY`) covering horizontal strips south-to-north, plus one trail file (`CHK-TRAIL`) that contains only metadata. The notebook ignores trail files automatically.

To download data for a specific date, run:

```bash
bash download_fci.sh 20260805   # YYYYMMDD
bash download_fci.sh            # defaults to today (UTC)
```

The script fetches EUMETSAT collection `EO:EUM:DAT:0662` (FDHSI, all 16 channels). It requires the `eumdac` CLI tool to be installed and configured with valid EUMETSAT API credentials.

### Setup

Activate MTG_env (see setup above), then open the notebook and select **Python (MTG_env)** from the kernel picker.

### Notebook structure

1. **Imports and channel definitions** — lists all 16 FCI spectral channels with their calibration type (reflectance or brightness temperature).

2. **Data loading** — scans the data directory, groups files by scan number from the filename (`_N__O_SSSS_KKKK.nc`), and loads one scan into a satpy `Scene`.

3. **Overview: all 16 channels** — 4×4 panel plot of all channels cropped to Central Europe, saved to `plots/fci_all_channels_europe.png`.

4. **Zugspitze zoom** — side-by-side vis_06 / ir_105 map zoomed to the Alps, saved to `plots/fci_vis06_ir105_zugspitze_zoom.png`.

5. **Exercises** — determine cloud top temperature, cloud fraction, and cloud top height estimation.
