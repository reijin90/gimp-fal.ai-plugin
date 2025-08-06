"""
Persistent settings for the fal.ai GIMP plugin.
"""

import os
import json
# Configuration directory and file (uses XDG_CONFIG_HOME on Unix, APPDATA on Windows)
from pathlib import Path

if os.name == 'nt':
    base_config = os.environ.get('APPDATA', Path.home() / '.config')
else:
    base_config = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')

CONFIG_DIR = Path(base_config) / 'gimp-falai-plugin'
CONFIG_PATH = CONFIG_DIR / 'settings.json'

DEFAULT_SETTINGS = {
    # last_model tracks the most recently selected profile/model
    "last_model": "fal-ai/flux-pro/kontext/max",
    "prompt": "",
    "guidance_scale": 3.5,
    "num_images": 1,
    "seed": None,
    "output_format": "jpeg",
    "safety_tolerance": "2",
    "aspect_ratio": "1:1",
    "sync_mode": True,
    "api_key": "",
}


def load_settings():
    """Load settings from disk, creating defaults if needed."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.isfile(CONFIG_PATH):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_settings(settings):
    """Persist settings to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(settings, f, indent=2)
