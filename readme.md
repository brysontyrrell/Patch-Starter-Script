# Patch Starter Script

This script will generate a full patch definition, or just the patch data, for a
given macOS application. This tool is to provide a starting point for creating
your own patch definitions to host on a patch server for Jamf Pro 10.2+.

## Basic Usage

### Help Text

You can view the help text for the script by passing the `-h` or `--help`
argument:

```bash
$ /usr/bin/python patchstarter.py -h
usage: patchstarter.py [-h] [-o OUTPUT] [-p PUBLISHER] [--patch-only] path

A script to create a basic patch definition from an existing macOS application.
This script makes the following assumptions about the software:
    * The "name" is derived from "CFBundleName"
    * The "id" is the "name" without spaces
    * The "version" is determined by "CFBundleShortVersionString"
    * Minimum OS version is determined by "LSMinimumSystemVersion"
    * The "releaseDate" is determined by the last modified timestamp
      of the application bundle
    * Because the "publisher" cannot be reliably derived from Info.plist
      it is left blank unless passed as an argument

positional arguments:
  path                  Path to the application

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Directory path to write JSON file
  -p PUBLISHER, --publisher PUBLISHER
                        Provide publisher name for a full definition
  --patch-only          Only create a patch, not a full definition
```

### Create a Patch Definition

To create a patch definition, pass the path to the application to the script and
it will print the resulting JSON:

```bash
$ /usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app -p "Github"
```

```json
{
    "id": "GitHubDesktop",
    "name": "GitHub Desktop",
    "publisher": "GitHub",
    "appName": "GitHub Desktop.app",
    "bundleId": "com.github.GitHub",
    "lastModified": "2018-02-13T02:55:53Z",
    "currentVersion": "Hasty Things Done Hastily",
    "requirements": [
        {
            "name": "Application Bundle ID",
            "operator": "is",
            "value": "com.github.GitHub",
            "type": "recon",
            "and": true
        }
    ],
    "patches": [
        {
            "version": "Hasty Things Done Hastily",
            "releaseDate": "2017-05-22T20:24:33Z",
            "standalone": true,
            "minimumOperatingSystem": "10.9",
            "reboot": false,
            "killApps": [
                {
                    "bundleId": "com.github.GitHub",
                    "appName": "GitHub Desktop.app"
                }
            ],
            "components": [
                {
                    "name": "GitHub Desktop",
                    "version": "Hasty Things Done Hastily",
                    "criteria": [
                        {
                            "name": "Application Bundle ID",
                            "operator": "is",
                            "value": "com.github.GitHub",
                            "type": "recon",
                            "and": true
                        },
                        {
                            "name": "Application Version",
                            "operator": "is",
                            "value": "Hasty Things Done Hastily",
                            "type": "recon"
                        }
                    ]
                }
            ],
            "capabilities": [
                {
                    "name": "Operating System Version",
                    "operator": "greater than or equal",
                    "value": "10.9",
                    "type": "recon"
                }
            ],
            "dependencies": []
        }
    ],
    "extensionAttributes": []
}
```

Pass a path to a directory using the `-o` or `--output` argument to write a the
patch definition to a JSON file:

```bash
/usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app -p "Github" -o .
```

### Create the Patch Data Only

If you only want the patch itself and not the full definition (this is the data
inside the `patches` array), pass the `--patch-only` argument:

```bash
$ /usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app --patch-only
```

```json
{
    "version": "Hasty Things Done Hastily",
    "releaseDate": "2017-05-22T20:24:33Z",
    "standalone": true,
    "minimumOperatingSystem": "10.9",
    "reboot": false,
    "killApps": [
        {
            "bundleId": "com.github.GitHub",
            "appName": "GitHub Desktop.app"
        }
    ],
    "components": [
        {
            "name": "GitHub Desktop",
            "version": "Hasty Things Done Hastily",
            "criteria": [
                {
                    "name": "Application Bundle ID",
                    "operator": "is",
                    "value": "com.github.GitHub",
                    "type": "recon",
                    "and": true
                },
                {
                    "name": "Application Version",
                    "operator": "is",
                    "value": "Hasty Things Done Hastily",
                    "type": "recon"
                }
            ]
        }
    ],
    "capabilities": [
        {
            "name": "Operating System Version",
            "operator": "greater than or equal",
            "value": "10.9",
            "type": "recon"
        }
    ],
    "dependencies": []
}
```

This option also works with writing out to a file:

```bash
/usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app --patch-only -o .
```

## Working with Patch Server

You can quickly create new software titles in the [Patch Server](https://github.com/brysontyrrell/PatchServer) project by piping
the output from `patchstarter.py` into a `curl` command:

```bash
$ curl -X POST http://localhost:5000/api/v1/title -d "$(/usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app -p "GitHub" --patch-only)" -H 'Content-Type: application/json'
```

You can do the same for POSTing a new version:

```bash
$ curl -X POST http://localhost:5000/api/v1/title/GitHubDesktop/version -d "{\"items\": [$(/usr/bin/python patchstarter.py /Applications/GitHub\ Desktop.app -p "GitHub" --patch-only)]}" -H 'Content-Type: application/json'
```
