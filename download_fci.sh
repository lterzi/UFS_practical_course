#!/bin/bash
# Download MTG FCI Level-1C FDHSI data from EUMETSAT Data Store,
# then extract the ZIP files and remove them.
#
# Usage:
#   bash download_fci.sh           # today (UTC)
#   bash download_fci.sh 20260803  # specific date (YYYYMMDD)
#
# Cron example (every 15 minutes, today's data):
#   */15 * * * * /project/meteo/work/L.Terzi/ufs_praktikum/MTG-0degrees-FCI-Level1c/download_fci.sh

source ~/MTG_env/bin/activate

COLLECTION="EO:EUM:DAT:0662"

if [ -n "$1" ]; then
    DATE=$(date -u -d "$1" +%Y-%m-%d)
else
    DATE=$(date -u +%Y-%m-%d)
fi
OUT_DIR="/scratch/l/L.Terzi/MTG-0degrees-FCI-Level1c/${DATE}"
mkdir -p "$OUT_DIR"

START="${DATE}T00:00:00"
END="${DATE}T23:59:59"

echo "Downloading FCI data for $DATE ..."
eumdac download -c "$COLLECTION" --start "$START" --end "$END" -o "$OUT_DIR" -y

echo "Extracting ZIP files ..."
for zip in "$OUT_DIR"/*.zip; do
    [ -f "$zip" ] || continue
    marker="${zip}.extracted"
    [ -f "$marker" ] && continue
    echo "$zip"
    unzip -n -q "$zip" -d "$OUT_DIR" && touch "$marker" #&& rm "$zip"
done

echo "Done."
