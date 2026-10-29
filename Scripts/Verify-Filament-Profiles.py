"""Validate archived A1 filament presets, build their bundle, and audit installation."""
import argparse
import hashlib
import json
import os
import re
import zipfile
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / 'Profiles' / 'Filament' / 'Universal-A1'
METADATA = {'name', 'from', 'version', 'type', 'filament_settings_id', 'filament_id',
            'setting_id', 'instantiation', 'description', 'inherits'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equivalent(left, right):
    if left == right:
        return True
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(equivalent(a, b) for a, b in zip(left, right))
    if isinstance(left, str) and isinstance(right, str):
        numeric = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
        if re.fullmatch(numeric, left) and re.fullmatch(numeric, right):
            return Decimal(left) == Decimal(right)
    return False


def validate_archive(manifest):
    entries = manifest['profiles']
    names = set()
    for entry in entries:
        path = ARCHIVE / entry['path']
        if not path.resolve().is_relative_to(ARCHIVE.resolve()):
            raise ValueError('Profile path escapes archive')
        if sha256(path) != entry['sha256']:
            raise ValueError('Hash mismatch: ' + entry['path'])
        data = read_json(path)
        if data['name'] in names:
            raise ValueError('Duplicate profile name: ' + data['name'])
        names.add(data['name'])
        if data['type'] != 'filament' or data['from'] != 'User':
            raise ValueError('Unexpected preset type: ' + entry['path'])
        if data['version'] != manifest['version'] or not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', data['version']):
            raise ValueError('Invalid version: ' + entry['path'])
        if data['filament_settings_id'] != [data['name']]:
            raise ValueError('Invalid settings ID: ' + entry['path'])
        if data['name'] != entry['name'] or data['inherits'] != entry['inherits']:
            raise ValueError('Manifest identity mismatch: ' + entry['path'])
        if entry['status'] == 'importable':
            if path.suffix != '.json' or data['compatible_printers'] != [entry['machine']]:
                raise ValueError('Unexpected nozzle compatibility: ' + entry['path'])
        elif not path.name.endswith('.json.disabled'):
            raise ValueError('Reference profile must use .json.disabled: ' + entry['path'])
    active = [e for e in entries if e['status'] == 'importable']
    if len(entries) != manifest['total_profiles'] or len(active) != manifest['importable_profiles']:
        raise ValueError('Manifest count mismatch')
    return active


def build_bundle(manifest, active):
    path = ARCHIVE / 'Bambu-A1-Universal-Filaments-18.zip'
    date = tuple(map(int, manifest['generated'].split('-'))) + (0, 0, 0)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for entry in sorted(active, key=lambda x: x['path']):
            info = zipfile.ZipInfo(entry['path'], date_time=date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, (ARCHIVE / entry['path']).read_bytes())
    with zipfile.ZipFile(path) as bundle:
        if len(bundle.namelist()) != len(active) or any('Reference-' in name for name in bundle.namelist()):
            raise ValueError('Bundle contains unexpected profiles')
    return {'path': path.relative_to(REPO).as_posix(), 'profiles': len(active), 'sha256': sha256(path)}


def audit_installed(active, user_data, install_dir):
    conf = json.JSONDecoder().raw_decode((user_data / 'BambuStudio.conf').read_text(encoding='utf-8-sig'))[0]
    user_store = user_data / 'user' / conf['app']['preset_folder'] / 'filament'
    system_store = install_dir / 'resources' / 'profiles' / 'BBL' / 'filament'
    system = {}
    for path in system_store.rglob('*.json'):
        data = read_json(path)
        system[data.get('name', path.stem)] = data
    user = {path.stem: read_json(path) for path in user_store.glob('*.json')}

    def resolve(name, visited=()):
        if name in visited:
            raise ValueError('Circular inheritance: ' + name)
        data = user.get(name, system.get(name))
        if data is None:
            raise ValueError('Missing parent: ' + name)
        parent = data.get('inherits')
        settings = resolve(parent, visited + (name,)) if parent else {}
        settings.update({k: v for k, v in data.items() if k not in METADATA})
        return settings

    results = []
    for entry in active:
        source = read_json(ARCHIVE / entry['path'])
        installed = user.get(source['name'])
        if installed is None:
            results.append({'name': source['name'], 'ok': False, 'reason': 'not installed'})
            continue
        expected = resolve(source['inherits'])
        expected.update({k: v for k, v in source.items() if k not in METADATA})
        actual = resolve(source['name'])
        differences = [{'key': k, 'source': expected.get(k), 'installed': actual.get(k)}
                       for k in sorted(expected.keys() | actual.keys())
                       if k not in expected or k not in actual or not equivalent(expected[k], actual[k])]
        version = installed.get('version', '')
        version_ok = bool(re.fullmatch(r'\d+\.\d+\.\d+\.\d+', version)) and tuple(map(int, version.split('.'))) == tuple(map(int, source['version'].split('.')))
        identity_ok = installed.get('name') == source['name'] and installed.get('inherits') == source['inherits']
        results.append({'name': source['name'], 'nozzle_mm': entry['nozzle_mm'],
                        'ok': version_ok and identity_ok and not differences,
                        'version_ok': version_ok, 'identity_ok': identity_ok,
                        'effective_settings_checked': len(expected), 'differences': differences})
    blocked = [e['name'] for e in read_json(ARCHIVE / 'Manifest.json')['profiles'] if e['status'] != 'importable']
    blocked_present = [name for name in blocked if name in user]
    return {'bambu_studio_version': conf['app'].get('version'), 'profiles': results,
            'installed_matching': sum(r['ok'] for r in results),
            'reference_profiles_installed': blocked_present,
            'ok': all(r['ok'] for r in results) and not blocked_present,
            'physical_print_tested_by_this_audit': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', action='store_true', help='Build the ZIP containing only importable presets')
    parser.add_argument('--installed', action='store_true', help='Compare archived and installed effective settings')
    parser.add_argument('--user-data-dir', type=Path, default=Path(os.environ.get('APPDATA', '.')) / 'BambuStudio')
    parser.add_argument('--install-dir', type=Path, default=Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Bambu Studio')
    parser.add_argument('--report', type=Path, help='Write a JSON report without account IDs or absolute user paths')
    args = parser.parse_args()
    manifest = read_json(ARCHIVE / 'Manifest.json')
    active = validate_archive(manifest)
    report = {'profile_version': manifest['version'], 'archive_profiles': manifest['total_profiles'],
              'importable_profiles': len(active), 'reference_only_profiles': manifest['reference_only_profiles'],
              'archive_hashes_match': True}
    if args.bundle:
        report['bundle'] = build_bundle(manifest, active)
    if args.installed:
        report['installation'] = audit_installed(active, args.user_data_dir, args.install_dir)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'archive_profiles': report['archive_profiles'], 'importable_profiles': len(active),
                      'installed_matching': report.get('installation', {}).get('installed_matching'),
                      'installation_ok': report.get('installation', {}).get('ok')}, ensure_ascii=False))
    if args.installed and not report['installation']['ok']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
