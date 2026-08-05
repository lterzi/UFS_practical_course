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
pip install satpy cartopy pyproj dask numpy matplotlib pandas
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

5. **Exercises** — guided tasks on cloud top temperature, cloud fraction, and cloud top height estimation.


## Notes

- The **FDHSI** product (collection `0662`) contains all 16 channels at 1 km (VIS/NIR) and 2 km (IR/WV) resolution. The older **HRFI** product (collection `0665`) contains only 4 channels (vis_06, nir_22, ir_38, ir_105) and is not suitable for the all-channels overview.
- Satpy's `group_files` is not used for scan grouping because its time-based clustering breaks when consecutive scans are back-to-back. Files are instead grouped by the scan number `SSSS` embedded in the filename.
- Dask is forced to synchronous mode (`scheduler='synchronous'`) to prevent HDF5 file-locking crashes when multiple threads try to read the same file.
- The time series loop explicitly deletes each `Scene` object and calls `gc.collect()` after every scan to prevent memory accumulation from crashing the kernel.
