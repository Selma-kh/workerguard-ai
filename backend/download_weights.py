"""Downloads the model weights the backend needs into backend/models/.

Run once after installing the requirements:  python download_weights.py

Licenses (see the README): Ultralytics YOLO is AGPL-3.0; the PPE model
harsh-77/ppe-detection is listed as AGPL-3.0 on its Hugging Face page, is described
by its author as for educational and research use, and does not name its training
dataset or that dataset's license.
"""

import urllib.request
from pathlib import Path

MODELS = Path(__file__).resolve().parent / "models"
FILES = {
    "ppe_harsh77.pt": "https://huggingface.co/harsh-77/ppe-detection/resolve/main/best.pt",
}


def main() -> None:
    MODELS.mkdir(exist_ok=True)
    for name, url in FILES.items():
        target = MODELS / name
        if target.exists():
            print(f"{name}: already downloaded")
            continue
        print(f"{name}: downloading from {url}")
        urllib.request.urlretrieve(url, target)
    # The person-detection weights (yolo26n.pt) are downloaded by Ultralytics on first run.
    from ultralytics import YOLO

    YOLO(str(MODELS / "yolo26n.pt"))
    print("Done.")


if __name__ == "__main__":
    main()
