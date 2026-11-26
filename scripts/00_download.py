"""Download and unpack the three official BBBC010 archives."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, BadZipFile

import requests
from requests.adapters import HTTPAdapter

BASE = "https://data.broadinstitute.org/bbbc/BBBC010/"
ARCHIVES = (
    "BBBC010_v2_images.zip",
    "BBBC010_v1_foreground.zip",
    "BBBC010_v1_foreground_eachworm.zip",
)


def main():
    data = Path("data")
    data.mkdir(exist_ok=True)
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=3))
        for name in ARCHIVES:
            archive = data / name
            with TemporaryDirectory(dir=data) as temp:
                temp = Path(temp)
                if archive.exists() and not valid_zip(archive):
                    archive.unlink()
                if not archive.exists():
                    print("Downloading", name, flush=True)
                    partial = temp / name
                    with session.get(BASE + name, stream=True, timeout=60) as response:
                        response.raise_for_status()
                        with partial.open("wb") as handle:
                            for chunk in response.iter_content(1 << 20):
                                handle.write(chunk)
                    if not valid_zip(partial):
                        raise ValueError(f"Incomplete archive: {name}")
                    partial.replace(archive)
                folder = data / archive.stem
                if not folder.is_dir():
                    extracted = temp / "extracted"
                    with ZipFile(archive) as bundle:
                        bundle.extractall(extracted)
                    extracted.replace(folder)
                print("Ready:", folder)


def valid_zip(path):
    try:
        with ZipFile(path) as archive:
            return archive.testzip() is None
    except BadZipFile:
        return False


if __name__ == "__main__":
    main()
