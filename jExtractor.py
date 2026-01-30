#!/usr/bin/env python3
import platform
import os
import glob
import shutil
import json
import csv
import re
from zipfile import ZipFile
from collections import defaultdict

# ----------------------------
# Helpers
# ----------------------------
def safe_name(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name or "unnamed")

# ----------------------------
# Locate JDownloader cfg dir
# ----------------------------
iam = os.getlogin()

paths = {
    "Windows": [
        f"C:/Users/{iam}/AppData/Local/JDownloader 2.0/cfg",
        "C:/Program Files/JDownloader/cfg"
    ],
    "Darwin": [f"/Users/{iam}/bin/JDownloader 2.0/cfg"],
    "Linux": [f"/home/{iam}/jd2/cfg"]
}

cfg_dir = None
for p in paths.get(platform.system(), []):
    if os.path.exists(p):
        cfg_dir = p
        break

if not cfg_dir:
    raise RuntimeError("JDownloader cfg directory not found")

print(f"Using cfg directory: {cfg_dir}")

# ----------------------------
# Select archive
# ----------------------------
choice = input("Extract from (1) linkcollector or (2) downloadList? [1/2]: ").strip()

pattern = "linkcollector*.zip" if choice == "1" else "downloadList*.zip"
archives = sorted(glob.glob(os.path.join(cfg_dir, pattern)), reverse=True)

if not archives:
    raise RuntimeError("No matching ZIP files found")

archive = archives[0]
print(f"Using archive: {archive}")

# ----------------------------
# Extract ZIP
# ----------------------------
temp_dir = os.path.join(cfg_dir, "temp")

with ZipFile(archive) as z:
    z.extractall(temp_dir)

# ----------------------------
# Load package metadata
# ----------------------------
packages = {}

for name in os.listdir(temp_dir):
    if len(name) == 2:
        path = os.path.join(temp_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                js = json.load(f)
                packages[name] = js.get("name")
        except Exception:
            pass

# ----------------------------
# Load links + group by package
# ----------------------------
grouped = defaultdict(list)

for name in os.listdir(temp_dir):
    if "_" not in name:
        continue

    pkg_id = name.split("_")[0]
    pkg_name = packages.get(pkg_id)

    path = os.path.join(temp_dir, name)
    try:
        with open(path, encoding="utf-8") as f:
            js = json.load(f)
    except Exception:
        continue

    # Schema differences
    if "sourceUrls" in js:
        url = js["sourceUrls"][0]
        filename = js.get("downloadLink", {}).get("name")
    else:
        url = js.get("url")
        filename = js.get("name")

    if url:
        grouped[pkg_name].append((filename, url))

# ----------------------------
# Export per-package CSVs (>1 link only)
# ----------------------------
out_dir = os.path.join(os.getcwd(), "jDownloader_Packages")
os.makedirs(out_dir, exist_ok=True)

exported = 0

for pkg, items in grouped.items():
    if len(items) <= 1:  # Increase this to export single-link packages
        continue  # Skip single-link packages

    fname = safe_name(pkg) + ".csv"
    out_path = os.path.join(out_dir, fname)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "url"])
        for filename, url in items:
            writer.writerow([filename, url])

    exported += 1

# ----------------------------
# Cleanup
# ----------------------------
shutil.rmtree(temp_dir)

print(f"Done. Exported {exported} package CSVs to '{out_dir}'")
