# JDownloader Package Link Exporter

A Python script that extracts links from JDownloader’s internal state archives and exports them into **per-package CSV files**, **only when a package contains more than one link**.

It supports both:
- **LinkGrabber lists** (`linkcollector*.zip`)
- **Download lists** (`downloadList*.zip`)

This is intended for inspection, auditing, migration, or external processing of JDownloader link data.

---

## Features

- ✅ Automatically locates the JDownloader `cfg` directory (Windows, macOS, Linux)
- ✅ Supports **both** `linkcollector` and `downloadList` archives
- ✅ Correctly handles **different internal JSON schemas**
- ✅ Groups links by their **actual JDownloader package**
- ✅ Exports **one CSV per package**
- ✅ **Skips single-link packages** (noise-free output)
- ✅ Windows-safe CSV filenames
- ✅ Cleans up all temporary files

---

## Output

Only packages containing **more than one link** are exported.
