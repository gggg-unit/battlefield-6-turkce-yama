import argparse
import hashlib
import json
from pathlib import Path
import secrets
import struct
import zipfile


source_hashes = {
    '81945eafb15a6ffe556167031c7ffdbb6108147669145408c98848cbb2749d7d',
    '2c66c142d468d98e44a32f30efc31d6d8753e74176316f17c1c9e4c361ecf065',
}
variants = ('EA-GamePass', 'Steam-Epic-GOG')
getter = bytes.fromhex('488d0501000000c3')
key_offset = 0x5D18


def digest(data):
    return hashlib.sha256(data).hexdigest()


def xor(data, key):
    return bytes(value ^ key[i % len(key)] for i, value in enumerate(data))


def rekey_runtime(image, key):
    result = bytearray(image)
    pe_offset = struct.unpack_from('<I', result, 0x3C)[0]
    if result[pe_offset:pe_offset + 4] != b'PE\0\0':
        raise ValueError('Unexpected PE header')
    if result[key_offset - len(getter):key_offset] != getter or result[key_offset + 32] != 0:
        raise ValueError('Unexpected runtime key layout')
    result[key_offset:key_offset + 32] = key
    checksum_offset = pe_offset + 24 + 64
    struct.pack_into('<I', result, checksum_offset, 0)
    checksum = 0
    for offset in range(0, len(result), 2):
        checksum += int.from_bytes(result[offset:offset + 2], 'little')
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = (checksum & 0xFFFF) + (checksum >> 16)
    struct.pack_into('<I', result, checksum_offset, (checksum & 0xFFFF) + len(result))
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description="Rebuild the Battlefield 6 Turkish patch v3.5.1.")
    parser.add_argument("--input", required=True, type=Path, help="Published v3.5.1 ZIP")
    parser.add_argument("--output", required=True, type=Path, help="Destination ZIP")
    args = parser.parse_args()
    source = args.input
    destination = args.output
    if digest(source.read_bytes()) not in source_hashes:
        raise ValueError('Unexpected source archive')
    with zipfile.ZipFile(source) as archive:
        files = {entry.filename: archive.read(entry) for entry in archive.infolist() if not entry.is_dir()}

    new_key = secrets.token_hex(16).encode('ascii')
    manifest = []
    for variant in variants:
        prefix = f'{variant}/SP/'
        runtime_name = prefix + 'hook.dll'
        old_runtime = files[runtime_name]
        old_key = old_runtime[key_offset:key_offset + 32]
        files[runtime_name] = rekey_runtime(old_runtime, new_key)
        runtime_key = files[runtime_name][key_offset:key_offset + 32]
        for name in ('Runtime_Win64_Func.dat', 'Runtime_Win64_Sys.dat'):
            path = prefix + name
            original = xor(files[path], old_key)
            if name.endswith('_Sys.dat'):
                if len(json.loads(original)) != 61151:
                    raise ValueError('Unexpected translation data')
            elif original[:4] != b'\0\1\0\0':
                raise ValueError('Unexpected font data')
            files[path] = xor(original, new_key)
            if xor(files[path], runtime_key) != original:
                raise ValueError('Data changed during re-encoding')

        for path, data in sorted(files.items()):
            if path.startswith(prefix):
                manifest.append({'variant': variant, 'path': path[len(variant) + 1:],
                                 'bytes': len(data), 'sha256': digest(data)})

    files['dosyalar.json'] = json.dumps(manifest, indent=2).encode('utf-8')
    files['eski-dosyalar.json'] = json.dumps({
        "SP/dxgi.dll": [
            "ecb82249201007bcb2d33035143f2f0bab628bdc223c26fe7f3492c34b8a2ae6"
        ],
        "SP/Runtime_Win64_Sys.dll": [
            "998813180b2d90f5059bc140116419577a26da2ece5db64a12f01931e5898735",
            "08e85eda5f29ba44e5a377287d44327564522c2933b8a74cef29cf82c89fce8d",
            "032e6c5c0c6a1c355d7c9e502f298b4db8ce69b393a826b029b45824685c71bc",
            "24acebd5cc0c17c64ea36d704b477f5dcafa200fe124a439d7072d784adcce61"
        ]
    }, indent=2).encode('utf-8')
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(files.items()):
            archive.writestr(path, data)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity verification failed')
    print(destination.name, digest(destination.read_bytes()))


if __name__ == '__main__':
    main()
