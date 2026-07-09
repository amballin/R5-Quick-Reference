# Canon R5 Reference iOS Wrapper

This Xcode project packages the generated Photography Reference System website into a native iPhone/iPad app. The iOS app is only a deployment wrapper. The documentation source remains the YAML plus `build.py` output.

## Project Layout

- `Canon R5 Reference.xcodeproj`: Xcode project and shared scheme.
- `Canon R5 Reference/`: SwiftUI app and `WKWebView` wrapper.
- `Resources/Website/`: generated website resources copied by automation.
- `Tests/`: XCTest validation for bundled resources.
- `UITests/`: launch and basic navigation UI tests.

## Resource Generation

Do not edit `ios/Resources/Website` by hand. It is deleted and regenerated every time the iOS build path runs.

The pipeline is:

1. Generate the merged website/PWA bundle at `output/merged-build/`.
2. Copy that bundle to `output/website/` for host/iOS staging.
3. Copy `output/website/` into `ios/Resources/Website/`.
4. Validate copied files and local relative links.
5. Build the Xcode project.

The Xcode project uses a folder resource reference for `Resources/Website`, so new generated files are included without manual project-file edits.

## Build

From the repository root:

```sh
python build.py build website
python build.py build ios
```

On systems where `python` is not configured, use `python3`.

## Run

Open `ios/Canon R5 Reference.xcodeproj` in Xcode, select the `Canon R5 Reference` scheme, choose an iPhone or iPad simulator, and press Run.

The app opens `Website/index.html` with `WKWebView.loadFileURL(_:allowingReadAccessTo:)`, granting read access to the full bundled `Website` folder.

## Install On iPhone

1. Open the project in Xcode.
2. Select your connected iPhone as the run destination.
3. Set your development team in Signing & Capabilities if Xcode asks.
4. Press Run.
5. Trust the developer profile on the phone if prompted.

## Regenerate After Build Changes

After changing `build.py` or any renderer, run:

```sh
python build.py build ios
python test_ios_wrapper.py
```

This refreshes generated resources, validates the bundle, builds the app, and runs the XCTest suite.

## Troubleshooting Missing Resources

- Run `python build.py build website` first and confirm `output/website/index.html` exists.
- Run `python build.py build ios` and inspect `IOS_VALIDATION_REPORT.md`.
- If Xcode reports missing files, confirm `ios/Resources/Website/index.html` exists.
- If `xcodebuild` says Command Line Tools are active, install/open full Xcode and select it with Xcode Settings or `xcode-select`.
