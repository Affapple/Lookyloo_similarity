import os
import sys
import requests
from pathlib import Path

ENDPOINT = "http://localhost:8000/get_hash"
IMAGE_EXTENSIONS = {".jpg", ".jpeg"}

def process_image(image_path: Path) -> dict | None:
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f)}
        response = requests.post(ENDPOINT, files=files)
        response.raise_for_status()
        return response.json()

def process_folder(folder_path: str):
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)

    images = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]

    if not images:
        print("No images found in the specified folder.")
        return

    print(f"Found {len(images)} image(s). Starting upload...\n")

    success, failed = 0, 0

    for image_path in images:
        try:
            print(f"  Uploading: {image_path.name} ... ", end="", flush=True)
            result = process_image(image_path)
            print(f"OK → {result}")
            success += 1
        except requests.HTTPError as e:
            print(f"FAILED (HTTP {e.response.status_code})")
            failed += 1
        except Exception as e:
            print(f"FAILED ({e})")
            failed += 1

    print(f"\nDone. {success} succeeded, {failed} failed.")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    process_folder(folder)