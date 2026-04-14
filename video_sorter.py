"""
VIDEO SORTER
------------
Scans all partitions (D:, E:, F:, etc.) for video files.
Moves horizontal videos → "Long Format" folder (same partition)
Moves vertical videos  → "Short Format" folder (same partition)

Requires: pip install opencv-python
"""

import os
import shutil
import string
import cv2


# ── Settings ────────────────────────────────────────────────────────────────
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi')
LONG_FORMAT_FOLDER = "Long Format"
SHORT_FORMAT_FOLDER = "Short Format"
SKIP_C_DRIVE = True   # Set to False if you also want to scan C:
# ────────────────────────────────────────────────────────────────────────────


def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            if SKIP_C_DRIVE and letter == "C":
                continue
            drives.append(drive)
    return drives


def get_orientation(filepath):
    """Returns 'horizontal', 'vertical', or None if the file can't be read."""
    try:
        cap = cv2.VideoCapture(filepath)
        width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cap.release()

        if width == 0 or height == 0:
            return None

        return "horizontal" if width >= height else "vertical"
    except Exception:
        return None


def safe_destination(folder, filename):
    """If a file with the same name already exists, adds _1, _2, etc."""
    dest = os.path.join(folder, filename)
    if not os.path.exists(dest):
        return dest

    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest):
        dest = os.path.join(folder, f"{base}_{counter}{ext}")
        counter += 1
    return dest


def scan_and_sort():
    drives = get_available_drives()

    if not drives:
        print("No drives found (other than C:). Nothing to do.")
        return

    total_moved   = 0
    total_skipped = 0

    for drive in drives:
        print(f"\n{'='*50}")
        print(f"  Scanning {drive}")
        print(f"{'='*50}")

        for root, dirs, files in os.walk(drive):
            # Don't scan inside the destination folders themselves
            dirs[:] = [d for d in dirs if d not in (LONG_FORMAT_FOLDER, SHORT_FORMAT_FOLDER)]

            for filename in files:
                if not filename.lower().endswith(VIDEO_EXTENSIONS):
                    continue

                filepath = os.path.join(root, filename)
                orientation = get_orientation(filepath)

                if orientation is None:
                    print(f"  [SKIP]  Could not read → {filename}")
                    total_skipped += 1
                    continue

                folder_name = LONG_FORMAT_FOLDER if orientation == "horizontal" else SHORT_FORMAT_FOLDER
                dest_folder = os.path.join(drive, folder_name)
                os.makedirs(dest_folder, exist_ok=True)

                dest_path = safe_destination(dest_folder, filename)
                shutil.move(filepath, dest_path)

                label = "HORIZONTAL" if orientation == "horizontal" else "VERTICAL  "
                print(f"  [{label}] {filename}")
                print(f"            → {dest_path}")
                total_moved += 1

    print(f"\n{'='*50}")
    print(f"  DONE!  Moved: {total_moved}  |  Skipped: {total_skipped}")
    print(f"{'='*50}\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════╗")
    print("║         VIDEO SORTER  v1.0           ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("This script will scan all drives (except C:) and move")
    print("video files into 'Long Format' or 'Short Format' folders")
    print("at the ROOT of each partition.")
    print()

    drives = get_available_drives()
    if drives:
        print(f"Drives found: {', '.join(drives)}")
    else:
        print("No drives found (other than C:).")

    print()
    answer = input("Ready to start? Type YES and press Enter: ").strip().upper()

    if answer == "YES":
        scan_and_sort()
    else:
        print("\nCancelled. No files were moved.")

    input("\nPress Enter to close...")
