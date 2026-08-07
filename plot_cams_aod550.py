"""Plot CAMS aod550, one figure per timestep, cropped to a bbox.

Usage (activate MTG_env first):
    source ~/MTG_env/bin/activate
    python plot_cams_aod550.py --date 20260806
"""
import argparse
import datetime
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr

DATA_DIR = "/scratch/l/L.Terzi/CAMS/"
OUT_DIR = "plots"

VARIABLE = "aod550"
CBAR_LABEL = "Total Aerosol Optical Depth at 550 nm"

# bbox approximated from the Windy.com AOD screenshot
NORTH, SOUTH, WEST, EAST = 75.0, 10.0, -90.0, 65.0


def normalize_date(date: str) -> str:
    """Accept YYYY-MM-DD or YYYYMMDD, always return YYYYMMDD."""
    fmt = "%Y-%m-%d" if "-" in date else "%Y%m%d"
    return datetime.datetime.strptime(date, fmt).strftime("%Y%m%d")


def plot_day(data_file: str) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    ds = xr.open_dataset(data_file)
    if "forecast_period" in ds.dims and ds.sizes["forecast_period"] == 1:
        ds = ds.squeeze("forecast_period", drop=True)
    if "forecast_reference_time" in ds.dims and ds.sizes["forecast_reference_time"] == 1:
        ds = ds.squeeze("forecast_reference_time", drop=True)

    # longitude comes in 0..360, convert to -180..180 and sort so the bbox slice works
    ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180)).sortby("longitude")
    ds = ds.sel(longitude=slice(WEST, EAST), latitude=slice(NORTH, SOUTH))

    da = ds[VARIABLE]

    lon_min, lon_max = float(ds.longitude.min()), float(ds.longitude.max())
    lat_min, lat_max = float(ds.latitude.min()), float(ds.latitude.max())

    # map aspect (height/width) so figure size matches the bbox instead of leaving
    # empty space around a fixed-aspect cartopy axes
    map_aspect = (lat_max - lat_min) / (lon_max - lon_min)
    extra_height = 1.8  # room for title and colorbar

    vmin, vmax = float(da.min()), float(da.max())

    # after squeezing size-1 dims, exactly one time-like dim should remain
    # (forecast_period for a multi-leadtime file, forecast_reference_time
    # for a multi-run file, or valid_time)
    time_dim = next(d for d in ("forecast_reference_time", "forecast_period", "valid_time") if d in da.dims)

    for t in ds[time_dim].values:
        da_t = da.sel({time_dim: t})
        # label by valid_time (actual date/time the map applies to) when available,
        # otherwise fall back to the dim's own value (e.g. a raw leadtime)
        label = da_t["valid_time"].values if "valid_time" in da_t.coords else t
        ts = str(label)[:13].replace("T", "_")

        width = 12
        fig, ax = plt.subplots(
            figsize=(width, width * map_aspect + extra_height),
            subplot_kw={"projection": ccrs.PlateCarree()},
            constrained_layout=True,
        )

        im = da_t.plot(
            ax=ax,
            transform=ccrs.PlateCarree(),
            cmap="YlOrRd",
            vmin=vmin,
            vmax=vmax,
            add_colorbar=False,
        )
        ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
        ax.coastlines(resolution="50m", linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.6)
        ax.set_title(f"CAMS {VARIABLE} — {ts}")

        cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.02, shrink=0.9, aspect=40)
        cbar.set_label(CBAR_LABEL)

        outfile = os.path.join(OUT_DIR, f"cams_aod550_{ts}.png")
        fig.savefig(outfile, dpi=120)
        plt.close(fig)
        print(f"saved {outfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYYMMDD or YYYY-MM-DD, defaults to today (UTC)")
    args = parser.parse_args()

    date = normalize_date(args.date) if args.date else datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    plot_day(os.path.join(DATA_DIR, f"{date}_aod550.nc"))