# UFS Practical Course

Scripts and notebooks for different tasks in the UFS practical course. Each task section below is self-contained — they don't share data or depend on each other, but they do share the same Python environment.

## Tasks

| Task | Files |
|------|-------|
| [CAMS Aerosol Optical Depth Plots](#task-cams-aerosol-optical-depth-plots) | `plot_cams_aod550.py` |
| [MTG FCI Level-1C — Cloud Investigation](#task-mtg-fci-level-1c--cloud-investigation) | `investigate_fci.ipynb` |

`plots/` holds output figures and CSV time series for both tasks.

---

## Setting up the Python environment

Both tasks below use the same virtual environment. Create it once and install the required packages:

```bash
python3 -m venv MTG_env
source MTG_env/bin/activate
pip install satpy cartopy pyproj dask numpy matplotlib pandas netcdf4 xarray cdsapi
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
| `satpy` | Reads FCI NetCDF files, handles calibration (counts → reflectance / brightness temperature) | FCI |
| `pyproj` | Coordinate transforms between lon/lat and geostationary projection | FCI |
| `dask` | Satpy uses dask for lazy loading; forced to synchronous mode to avoid HDF5 crashes | FCI |
| `pandas` | Time series table and CSV export | FCI |
| `netcdf4` | NetCDF backend | both |

All standard-library modules used (`re`, `glob`, `gc`, `collections`, `pathlib`, `warnings`, `argparse`, `datetime`) require no installation.

---

## Task: CAMS Aerosol Optical Depth Plots

`plot_cams_aod550.py` plots CAMS (Copernicus Atmosphere Monitoring Service) total aerosol optical depth at 550 nm forecasts, cropped to a bbox covering 90°W–65°E, 10°–75°N.

### Data

It reads a NetCDF file downloaded from the ADS API (see `download_cams_aod550.py` in `/project/meteo/work/L.Terzi/ufs_praktikum/CAMS/`) at:

```
/scratch/l/L.Terzi/CAMS/{date}_aod550.nc
```

and produces one PNG per forecast hour in `plots/`, named `cams_aod550_{valid_time}.png`. It handles both single-leadtime and multi-leadtime (e.g. 0–120h) files automatically.

### Usage

Activate MTG_env first (see setup above), then:

```bash
source ~/MTG_env/bin/activate
python plot_cams_aod550.py --date 20260807
```

`--date` accepts `YYYYMMDD` or `YYYY-MM-DD` and defaults to today (UTC) if omitted.

---

## Task: MTG FCI Level-1C — Cloud Investigation

Analysis of **Meteosat Third Generation (MTG) Flexible Combined Imager (FCI)** data, focusing on cloud detection and cloud top temperature estimation over the Zugspitze.

### Data

The notebook expects FCI Level-1C **FDHSI** (Full Disk High Spectral resolution Imagery) files in NetCDF format, organised by date under:

```
/scratch/l/L.Terzi/MTG-0degrees-FCI-Level1c/YYYY-MM-DD/
```

Each full-disk scan consists of ~40 body files (`CHK-BODY`) covering horizontal strips south-to-north, plus one trail file (`CHK-TRAIL`) that contains only metadata. The notebook ignores trail files automatically.

### Setup

Activate MTG_env (see setup above), then open the notebook and select **Python (MTG_env)** from the kernel picker.

### Notebook structure

1. **Imports and channel definitions** — lists all 16 FCI spectral channels with their calibration type (reflectance or brightness temperature).

2. **Data loading** — scans the data directory, groups files by scan number from the filename (`_N__O_SSSS_KKKK.nc`), and loads one scan into a satpy `Scene`.

3. **Overview: all 16 channels** — 4×4 panel plot of all channels cropped to Central Europe, saved to `plots/fci_all_channels_europe.png`.

4. **Zugspitze zoom** — side-by-side vis_06 / ir_105 map zoomed to the Alps, saved to `plots/fci_vis06_ir105_zugspitze_zoom.png`.

5. **Exercises** — estimate cloud top temperature, cloud fraction, and cloud top height
