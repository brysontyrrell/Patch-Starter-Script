# Patch Starter Script

This script will generate a full patch definition, or just the patch data, for a
given macOS application. This tool is to provide a starting point for creating
your own patch definitions to host on a patch server for Jamf Pro 10.2+.

## Basic Usage

### Help Text

You can view the help text for the script by passing the `-h` or `--help`
argument:

```text
$ python patchstarter.py -h
usage: patchstarter.py [-h] [-o <output_dir>] [-p <publisher_name>]
                       [-n <name>] [-e <ext_att_path>]
                       [--app-version <version>] [--min-sys-version <version>]
                       [--patch-only]
                       path

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

A word of warning when using the "--app-version" argument: Jamf Pro's 
"Application Version" criteria matches against "CFBundleShortVersionString".
The intent of this argument is to make it easier to create version updates
for releases of an app other than what is present on your system.

positional arguments:
  path                  Path to the application

optional arguments:
  -h, --help            show this help message and exit
  -o <output_dir>, --output <output_dir>
                        Directory path to write JSON file
  -p <publisher_name>, --publisher <publisher_name>
                        Provide publisher name for a full definition
  -n <name>, --name <name>
                        Provide the display name for a full definition
  -e <ext_att_path>, --extension-attribute <ext_att_path>
                        Path to a script to include as an extension attribute
                        * You can include multiple extension attribute arguments
  --app-version <version>
                        Provide the version of the app (override CFBundleShortVersionString)
  --min-sys-version <version>
                        Provide the minimum supported version fo macOS for this app (e.g. 10.9)
  --patch-only          Only create a patch, not a full definition
```

### Create a Patch Definition

To create a patch definition, pass the path to the application to the script and
it will print the resulting JSON:

```bash
$ python patchstarter.py /Applications/GitHub\ Desktop.app -p "Github"
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
$ python patchstarter.py /Applications/GitHub\ Desktop.app -p "Github" -o .
```

You can bundle an extension attribute into your patch definition by passing the
path to the file tp the `-e` of `--extension-attribute` argument:

```bash
$ python patchstarter.py /Applications/GitHub\ Desktop.app -p "Github" -e ext_att.sh
```

You can use the `-e` argument multiple time. Each passed extension attribute
will appended to the `extensionAttributes` key:

```json
{
    "...",
    "extensionAttributes": [
        {
            "key": "github-desktop",
            "value": "IyEvYmluL2Jhc2gKCm91dHB1dFZlcnNpb249Ik5vdCBJbnN0YWxsZWQiCgppZiBbIC1kIC9BcHBsaWNhdGlvbnMvR2l0SHViXCBEZXNrdG9wLmFwcCBdOyB0aGVuCiAgICBvdXRwdXRWZXJzaW9uPSQoZGVmYXVsdHMgcmVhZCAvQXBwbGljYXRpb25zL0dpdEh1YlwgRGVza3RvcC5hcHAvQ29udGVudHMvSW5mby5wbGlzdCBDRkJ1bmRsZVNob3J0VmVyc2lvblN0cmluZykKZmkKCmVjaG8gIjxyZXN1bHQ+JG91dHB1dFZlcnNpb248L3Jlc3VsdD4iCg==",
            "displayName": "GitHub Desktop"
        }
    ]
}
```

This will NOT add the extension attribute to your `requirements` or
`components/criteria`. You will need to manually update the definition to
reference your extension attributes (using the `key` for the criterion's `name`
value.)

### Create the Patch Data Only

If you only want the patch itself and not the full definition (this is the data
inside the `patches` array), pass the `--patch-only` argument:

```bash
$ python patchstarter.py /Applications/GitHub\ Desktop.app --patch-only
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
$ python patchstarter.py /Applications/GitHub\ Desktop.app --patch-only -o .
```

## Working with Patch Server

You can quickly create new software titles in the [Patch Server](https://github.com/brysontyrrell/PatchServer) project by piping
the output from `patchstarter.py` into a `curl` command:

```bash
$ curl -X POST http://localhost:5000/api/v1/title -d "$(python patchstarter.py /Applications/GitHub\ Desktop.app -p "GitHub" )" -H 'Content-Type: application/json'
```

You can do the same for POSTing a new version:

```bash
$ curl -X POST http://localhost:5000/api/v1/title/GitHubDesktop/version -d "{\"items\": [$(python patchstarter.py /Applications/GitHub\ Desktop.app -p "GitHub" --patch-only)]}" -H 'Content-Type: application/json'
```
