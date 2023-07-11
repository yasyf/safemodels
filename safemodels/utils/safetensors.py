import json, struct, tempfile, shutil
from pathlib import Path
from typing import Union


def extract_headers(filename: Union[str, Path]):
    with open(filename, "rb") as f:
        length = struct.unpack("<Q", f.read(8))[0]
        return length, json.loads(f.read(length))


def extract_metadata(filename: Union[str, Path]) -> dict[str, str]:
    return extract_headers(filename)[1].get("__metadata__", {})


def update_meta(filename: Union[str, Path], meta: dict, clobber: bool = False):
    length, headers = extract_headers(filename)
    if not clobber:
        meta = {**headers.get("__metadata__", {}), **meta}
    headers["__metadata__"] = meta
    headers_json = json.dumps(headers).encode("utf-8")

    with tempfile.NamedTemporaryFile("wb") as g:
        g.write(struct.pack("<Q", len(headers_json)))
        g.write(headers_json)
        with open(filename, "rb") as f:
            f.seek(length + 8)
            g.write(f.read())
        g.flush()

        shutil.copy(g.name, filename)
