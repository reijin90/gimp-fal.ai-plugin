}#!/usr/bin/env bash
#
# Update or install the vendored fal-client and dependencies to the latest release.
# Run this from the root of the plugin repository.

set -euo pipefail

echo "Removing old vendored fal_client..."
rm -rf gimp-falai/vendor/fal_client

echo "Vendoring fal_client and dependencies..."
pip3 install --upgrade --target gimp-falai/vendor/fal_client fal_client

echo "fal_client and dependencies updated in gimp-falai/vendor/fal_client"