# GIMP fal.ai Plugin

This _basic_ plugin integrates [fal.ai](https://fal.ai) generative models directly into GIMP, allowing you to generate images or modify layers using state-of-the-art AI models.

## Features
- Select and configure fal.ai models (e.g., `fal-ai/flux-pro/kontext/max`)
- Prompt dialog for text-to-image or image-to-image generation
- Advanced parameter overrides (guidance scale, seed, etc.)
- API key management
- Progress feedback and error reporting in GIMP

---

## Installation

### Prerequisites
- **GIMP 3.0+** with Python support enabled
- **Python 3.8+** (matching your GIMP Python environment)
- Internet connection (for fal.ai API)

### 1. Clone or Download the Plugin
Clone this repo or download and extract the ZIP.

### 2. Install fal-client and Dependencies
The plugin vendors its own `fal_client` and dependencies. The only thing you need to do is update or install them from the repository root:
```sh
cd gimp-fal.ai-plugin
./scripts/update-fal-client.sh
```
This will (re)install the latest `fal_client` and dependencies into `gimp-falai/vendor/fal_client`.

### 3. Install the Plugin in GIMP
- Copy the `gimp-falai/` directory to your GIMP plug-ins folder:
  - **Linux/macOS:** `~/.config/GIMP/3.0/plug-ins/`
  - **Windows:** `%APPDATA%\GIMP\3.0\plug-ins\`
- Ensure all `.py` files are executable:
  ```sh
  chmod +x ~/.config/GIMP/3.0/plug-ins/gimp-falai/*.py
  ```

### 5. Restart GIMP
The plugin should now appear in the GIMP menu (e.g., under `Filters > Images > fal.ai`).

---

## Usage
1. Open an image or create a new one in GIMP.
2. Select the fal.ai plugin from the menu.
3. Enter your prompt and adjust parameters as needed.
4. Click "Run" to generate or modify the image/layer.
5. Results will be imported as a new layer or image.

---

## Updating the Plugin
To update the fal.ai client and dependencies:
```sh
./scripts/update-fal-client.sh
```
To update the plugin code, pull the latest changes from your repository and repeat the installation steps if needed.

---

## Troubleshooting
- **Plugin not visible in GIMP:** Ensure the plugin is in the correct plug-ins folder and is executable.
- **Dependency errors:** Run the update script again. Make sure your Python version matches GIMP's.
- **API errors:** Check your API key and internet connection.
- **Settings not saving:** Ensure you have write permissions to the settings file.

---

## License
This project is licensed under the MIT