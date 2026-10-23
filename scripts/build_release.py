#!/usr/bin/env python3
"""Build the pinned gggg-unit V3 release without network access.

Copyright (c) 2026 gggg-unit
Source: https://github.com/gggg-unit/battlefield-6-turkce-yama
LicenseRef-GGGG-Unit-Attribution-1.0; see LICENSE.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.0"
NAME = f"gggg-unit-BF6-Turkce-Yama-v{VERSION}"
KEY = b"PlayCeviri_Secure_Key_2026_V19!!"
VARIANTS = ("Steam-Epic-GOG", "EA-GamePass")
NOTICES = ("LICENSE", "NOTICE", "CHANGELOG.md")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def xor_payload(data):
    return bytes(value ^ KEY[index % len(KEY)] for index, value in enumerate(data))


def patch_runtime(data):
    """Replace the verified translation-key getter with a local key return."""
    image = bytearray(data)
    pe_offset = struct.unpack_from("<I", image, 0x3C)[0]
    if image[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise ValueError("Invalid PE image")
    # These offsets apply exclusively to the hash-pinned input images.
    offset = 0x5D10
    signature = bytes.fromhex("40555356574154415541564157488dac2458fcffff4881eca8040000")
    if image[offset:offset + len(signature)] != signature:
        raise ValueError("Unexpected key getter signature")
    replacement = bytes.fromhex("488d0501000000c3") + KEY + b"\0"
    image[offset:offset + len(replacement)] = replacement
    checksum_offset = pe_offset + 24 + 64
    image[checksum_offset:checksum_offset + 4] = b"\0" * 4
    checksum = 0
    for index in range(0, len(image), 2):
        checksum += int.from_bytes(image[index:index + 2], "little")
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = (checksum & 0xFFFF) + len(image)
    struct.pack_into("<I", image, checksum_offset, checksum)
    return bytes(image)


def customize_translation(data):
    decoded = xor_payload(data)
    original = json.loads(decoded)
    text = decoded.decode("utf-8")
    substitutions = {
        "Menüye Dön / PlayCeviri.Net": "Menüye Dön",
        "TÜRKÇE ÇEVİRİ - NARAYANNA": "TÜRKÇE ÇEVİRİ - gggg-unit",
    }
    for old, new in substitutions.items():
        if text.count(old) != 1:
            raise ValueError(f"Expected one occurrence of {old!r}")
        text = text.replace(old, new)
    encoded = text.encode("utf-8")
    customized = json.loads(encoded)
    if original.keys() != customized.keys() or len(customized) != 61151:
        raise ValueError("Unexpected translation inventory")
    if sum(original[key] != customized[key] for key in original) != 2:
        raise ValueError("Unexpected translation changes")
    return xor_payload(encoded), encoded


def archive(folder, output):
    """Use fixed ZIP metadata so the same inputs produce identical archives."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(folder).as_posix(),
                                       date_time=(2026, 10, 23, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(output) as bundle:
        if bundle.testzip() is not None:
            raise ValueError(f"Archive verification failed: {output.name}")


def copy_notices(destination):
    for filename in NOTICES:
        shutil.copyfile(ROOT / filename, destination / filename)
    shutil.copytree(ROOT / "LICENSES", destination / "LICENSES")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                        help="Original extracted platform folders; never modified")
    parser.add_argument("--output", default=ROOT / "dist", type=Path,
                        help="New output directory; existing directories are refused")
    args = parser.parse_args()
    source = args.input.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    # Validate the entire input set before producing any files.
    expected = json.loads((ROOT / "metadata/expected-inputs.json").read_text("utf-8"))
    contents = {}
    for entry in expected:
        relative = f"{entry['variant']}/{entry['path']}"
        path = (source / relative).resolve(strict=True)
        if not path.is_relative_to(source):
            raise ValueError("Input path escapes its root")
        data = path.read_bytes()
        if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
            raise ValueError(f"Input hash mismatch: {relative}")
        contents[relative] = data
    output.mkdir(parents=True)
    full = output / NAME
    full.mkdir()
    for relative, data in contents.items():
        path = full / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.name == "Runtime_Win64_Sys.dll":
            data = patch_runtime(data)
        elif path.name == "Runtime_Win64_Sys.dat":
            data, translation = customize_translation(data)
            resources = full / "Acik-Ceviri-Kaynaklari"
            resources.mkdir(exist_ok=True)
            (resources / "ceviri.json").write_bytes(translation)
        elif path.name == "Runtime_Win64_Func.dat":
            font = xor_payload(data)
            if font[:4] != b"\x00\x01\x00\x00":
                raise ValueError("Invalid decoded font")
            resources = full / "Acik-Ceviri-Kaynaklari"
            resources.mkdir(exist_ok=True)
            (resources / "yazi-tipi.ttf").write_bytes(font)
        path.write_bytes(data)
    release_manifest = json.loads((ROOT / "metadata/release-manifest.json").read_text("utf-8"))
    for entry in release_manifest:
        path = full / entry["variant"] / entry["path"]
        if digest(path.read_bytes()) != entry["sha256"]:
            raise ValueError(f"Output hash mismatch: {path.relative_to(full)}")
    (full / "dosyalar.json").write_text(json.dumps(release_manifest, indent=2), encoding="utf-8")
    for filename in ("Kur.ps1", "Kurulumu-Baslat.cmd"):
        shutil.copyfile(ROOT / "installer" / filename, full / filename)
    copy_notices(full)
    archive(full, output / f"{NAME}-Tum-Platformlar.zip")
    for variant in VARIANTS:
        manual = output / f"{NAME}-{variant}"
        manual.mkdir()
        shutil.copytree(full / variant / "SP", manual / "SP")
        copy_notices(manual)
        (manual / "PLATFORM.txt").write_text(
            f"{variant}\nManual install: back up existing files, then copy SP into the main game directory.\n"
            "Elle kurulum: mevcut dosyalari yedekleyin, sonra SP klasorunu ana oyun klasorune kopyalayin.\n",
            encoding="utf-8")
        archive(manual, output / f"{NAME}-{variant}.zip")
    print("\n".join(path.name for path in sorted(output.glob("*.zip"))))


if __name__ == "__main__":
    main()
