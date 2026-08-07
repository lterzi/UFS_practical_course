# MTG FCI Level-1C — Cloud Investigation

Analysis of **Meteosat Third Generation (MTG) Flexible Combined Imager (FCI)** data, focusing on cloud detection and cloud top temperature estimation over the Zugspitze.

## Files

| File | Purpose |
|------|---------|
| `investigate_fci.ipynb` | Main analysis notebook |
| `plots/` | Output figures and CSV time series |

## Data

The notebook expects FCI Level-1C **FDHSI** (Full Disk High Spectral resolution Imagery) files in NetCDF format, organised by date under:

```
/scratch/l/L.Terzi/MTG-0degrees-FCI-Level1c/YYYY-MM-DD/
```

Each full-disk scan consists of ~40 body files (`CHK-BODY`) covering horizontal strips south-to-north, plus one trail file (`CHK-TRAIL`) that contains only metadata. The notebook ignores trail files automatically.

## Setting up the Python environment

Create a virtual environment and install the required packages:

```bash
python3 -m venv MTG_env
source MTG_env/bin/activate
pip install satpy cartopy pyproj dask numpy matplotlib pandas netcdf4
```

To make the environment available as a kernel in Jupyter:

```bash
pip install ipykernel
python -m ipykernel install --user --name MTG_env --display-name "Python (MTG_env)"
```

After that, open the notebook and select **Python (MTG_env)** from the kernel picker.

## Required packages

| Package | Purpose |
|---------|---------|
| `satpy` | Reads FCI NetCDF files, handles calibration (counts → reflectance / brightness temperature) |
| `cartopy` | Geographic map projections and coastline/border overlays |
| `pyproj` | Coordinate transforms between lon/lat and geostationary projection |
| `dask` | Satpy uses dask for lazy loading; forced to synchronous mode to avoid HDF5 crashes |
| `numpy` | Array operations |
| `matplotlib` | Plotting |
| `pandas` | Time series table and CSV export |

All standard-library modules used (`re`, `glob`, `gc`, `collections`, `pathlib`, `warnings`) require no installation.

## Notebook structure

1. **Imports and channel definitions** — lists all 16 FCI spectral channels with their calibration type (reflectance or brightness temperature).

2. **Data loading** — scans the data directory, groups files by scan number from the filename (`_N__O_SSSS_KKKK.nc`), and loads one scan into a satpy `Scene`.

3. **Overview: all 16 channels** — 4×4 panel plot of all channels cropped to Central Europe, saved to `plots/fci_all_channels_europe.png`.

4. **Zugspitze zoom** — side-by-side vis_06 / ir_105 map zoomed to the Alps, saved to `plots/fci_vis06_ir105_zugspitze_zoom.png`.

5. **Exercises** — estimate cloud top temperature, cloud fraction, and cloud top height
