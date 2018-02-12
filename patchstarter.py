#!/usr/bin/python
import argparse
from datetime import datetime
import json
import os
import plistlib


def arguments():
    parser = argparse.ArgumentParser(
        description='A script to create a basic patch definition from an '
                    'existing macOS application.\nThis script makes the '
                    'following assumptions about the software:\n'
                    '    * The "name" is derived from "CFBundleName"\n'
                    '    * The "id" is the "name" without spaces\n'
                    '    * The "version" is determined by "CFBundelVersion"\n'
                    '    * Minimum OS version is determined by '
                    '"LSMinimumSystemVersion"\n'
                    '    * The "releaseDate" is determined by the last '
                    'modified timestamp\n      of the application bundle\n'
                    '    * Because the "publisher" cannot be reliably derived '
                    'from Info.plist\n      it is left blank unless passed as '
                    'an argument',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('path', help='Path to the application', type=str)
    parser.add_argument(
        '-o', '--output', help='Directory path to write JSON file', type=str)
    parser.add_argument(
        '-p', '--publisher',
        help='Provide publisher name for a full definition',
        type=str, default=''
    )
    parser.add_argument(
        '--patch-only', help='Only create a patch, not a full definition',
        action='store_true'
    )

    return parser.parse_args()


def main():
    args = arguments()
    app_id, output = make_definition(args)

    if args.output:
        if args.patch_only:
            filename = '{}-patch.json'.format(app_id)
        else:
            filename = '{}.json'.format(app_id)
        with open(os.path.join(args.output, filename), 'w') as f:
            json.dump(output, f)
    else:
        print(json.dumps(output, indent=4))


def make_definition(args):
    app_filename = os.path.basename(args.path)
    app_path = os.path.join(args.path, 'Contents')

    info_plist = plistlib.readPlist(os.path.join(app_path, 'Info.plist'))

    app_name = info_plist['CFBundleName']
    app_id = app_name.replace(' ', '')
    app_version = info_plist['CFBundleVersion']
    app_bundle_id = info_plist['CFBundleIdentifier']
    app_min_os = info_plist['LSMinimumSystemVersion']
    app_last_modified = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    app_timestamp = datetime.utcfromtimestamp(
        os.path.getmtime(args.path)).strftime('%Y-%m-%dT%H:%M:%SZ')

    patch = {
        "version": app_version,
        "releaseDate": app_timestamp,
        "standalone": True,
        "minimumOperatingSystem": app_min_os,
        "reboot": False,
        "killApps": [
            {
                "bundleId": app_bundle_id,
                "appName": app_filename
            }
        ],
        "components": [
            {
                "name": app_name,
                "version": app_version,
                "criteria": [
                    {
                        "name": "Application Bundle ID",
                        "operator": "is",
                        "value": app_bundle_id,
                        "type": "recon",
                        "and": True
                    },
                    {
                        "name": "Application Version",
                        "operator": "is",
                        "value": app_version,
                        "type": "recon"
                    }
                ]
            }
        ],
        "capabilities": [
            {
                "name": "Operating System Version",
                "operator": "greater than or equal",
                "value": app_min_os,
                "type": "recon"
            }
        ],
        "dependencies": []
    }

    if args.patch_only:
        return app_id, patch

    patch_def = {
        "id": app_id,
        "name": app_name,
        "publisher": args.publisher,
        "appName": app_filename,
        "bundleId": app_bundle_id,
        "lastModified": app_last_modified,
        "currentVersion": app_version,
        "requirements": [
            {
                "name": "Application Bundle ID",
                "operator": "is",
                "value": app_bundle_id,
                "type": "recon",
                "and": True
            }
        ],
        "patches": [],
        "extensionAttributes": []
    }

    patch_def['patches'].append(patch)
    return app_id, patch_def


if __name__ == '__main__':
    main()
