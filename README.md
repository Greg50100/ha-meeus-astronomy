# ha-meeus-astronomy

Home Assistant custom component for astronomical calculations based on Jean Meeus' "Astronomical Algorithms".

## Installation

### HACS (Home Assistant Community Store)

1.  Add this repository as a custom repository in HACS.
2.  Search for "Jean Meeus Astronomy" and install it.
3.  Restart Home Assistant.
4.  Add the "Jean Meeus Astronomy" integration through the Home Assistant UI.

## Releases and Updates

This component is updated through HACS, which relies on GitHub releases.

To publish a new version:

1.  **Update the version number:** The version number is defined in `custom_components/meeus_astronomy/manifest.json`. Before creating a release, update this version number following the [Semantic Versioning](https://semver.org/) guidelines (e.g., `0.1.1`, `0.2.0`).

2.  **Create a new release on GitHub:**
    *   Go to the "Releases" page of the repository.
    *   Click on "Draft a new release".
    *   The "Tag version" must match the version in `manifest.json` (e.g., `0.1.0`).
    *   Write a description of the changes in the release.
    *   Publish the release.

HACS will then automatically detect the new version and notify users that an update is available.