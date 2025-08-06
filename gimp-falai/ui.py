"""
UI dialogs for fal.ai GIMP plugin (settings and prompt interfaces).
"""

from gi.repository import GimpUi, Gtk, Gimp, GLib

import tempfile
import os
import utils

import falai_wrapper
import settings

def show_settings_dialog(settings):
    pass

def show_prompt_dialog(image, drawable):
    """
    Display the main run dialog which includes all settings.
    Settings are loaded from disk on open and saved on OK.
    """
    # Add immediate feedback
    Gimp.message("[fal.ai] Opening dialog...")
    
    # --- 1. Load settings from disk at the start ---
    try:
        conf = settings.load_settings()
        Gimp.message("[fal.ai] Settings loaded successfully")
    except Exception as e:
        Gimp.message(f"[fal.ai] Could not load settings, using defaults. Error: {e}")
        conf = {}

    # Initialize GimpUi if needed
    GimpUi.init("python-fu-falai-run")

    dialog = GimpUi.Dialog(title="fal.ai Run", role="python-fu-falai-run")
    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    ok_button = dialog.add_button("_OK", Gtk.ResponseType.OK)
    dialog.set_default_size(500, -1)

    box = dialog.get_content_area()
    box.set_spacing(12)
    box.set_border_width(12)
    
    grid = Gtk.Grid(row_spacing=6, column_spacing=6)
    box.pack_start(grid, True, True, 0)

    # --- Main Prompt ---
    grid.attach(Gtk.Label(label="Prompt:", halign=Gtk.Align.START), 0, 0, 1, 1)
    entry_prompt = Gtk.Entry()
    entry_prompt.set_text(conf.get('prompt', ''))
    entry_prompt.set_hexpand(True)
    entry_prompt.set_activates_default(True)
    grid.attach(entry_prompt, 1, 0, 1, 1)

    # --- All other settings go into an expander ---
    expander = Gtk.Expander(label="Settings")
    expander.set_expanded(False)
    grid.attach(expander, 0, 1, 2, 1)

    settings_grid = Gtk.Grid(row_spacing=6, column_spacing=6)
    settings_grid.set_margin_top(12)
    expander.add(settings_grid)

    # Helper to find and set the active text in a ComboBoxText
    def _set_combo_text(combo, text):
        text = str(text)
        model = combo.get_model()
        for i in range(model.iter_n_children(None)):
            if combo.get_model()[i][0] == text:
                combo.set_active(i)
                return
        # If not found, set to first item if available
        if model.iter_n_children(None) > 0:
            combo.set_active(0)

    # --- Create and populate all setting widgets ---

    row = 0
    
    # API Key
    settings_grid.attach(Gtk.Label(label="API Key:", halign=Gtk.Align.START), 0, row, 1, 1)
    key_entry = Gtk.Entry()
    key_entry.set_text(conf.get('api_key', ''))
    key_entry.set_visibility(False)
    key_entry.set_hexpand(True)
    settings_grid.attach(key_entry, 1, row, 1, 1)
    row += 1

    # Model endpoint
    settings_grid.attach(Gtk.Label(label="Model:", halign=Gtk.Align.START), 0, row, 1, 1)
    model_endpoint = Gtk.Entry()
    model_endpoint.set_text(str(conf.get('model') or ''))
    settings_grid.attach(model_endpoint, 1, row, 1, 1)
    row += 1

    # Sync mode
    settings_grid.attach(Gtk.Label(label="Sync Mode:", halign=Gtk.Align.START), 0, row, 1, 1)
    sync_btn = Gtk.CheckButton(label="Wait for result")
    sync_btn.set_active(conf.get('sync_mode', True))
    settings_grid.attach(sync_btn, 1, row, 1, 1)
    row += 1

    # Safety checker
    settings_grid.attach(Gtk.Label(label="Safety Checker:", halign=Gtk.Align.START), 0, row, 1, 1)
    safe_btn = Gtk.CheckButton(label="Enable safety filter")
    safe_btn.set_active(conf.get('enable_safety_checker', True))
    settings_grid.attach(safe_btn, 1, row, 1, 1)
    row += 1

    # Guidance scale
    settings_grid.attach(Gtk.Label(label="Guidance Scale:", halign=Gtk.Align.START), 0, row, 1, 1)
    guid_adj = Gtk.Adjustment(value=conf.get('guidance_scale', 3.5), lower=0, upper=50, step_increment=0.1, page_increment=1, page_size=0)
    guid_spin = Gtk.SpinButton()
    guid_spin.set_adjustment(guid_adj)
    guid_spin.set_numeric(True)
    guid_spin.set_digits(2)
    settings_grid.attach(guid_spin, 1, row, 1, 1)
    row += 1

    # Num images
    settings_grid.attach(Gtk.Label(label="# Images:", halign=Gtk.Align.START), 0, row, 1, 1)
    num_adj = Gtk.Adjustment(value=conf.get('num_images', 1), lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
    num_spin = Gtk.SpinButton()
    num_spin.set_adjustment(num_adj)
    num_spin.set_numeric(True)
    settings_grid.attach(num_spin, 1, row, 1, 1)
    row += 1

    # Seed
    settings_grid.attach(Gtk.Label(label="Seed (optional):", halign=Gtk.Align.START), 0, row, 1, 1)
    seed_entry = Gtk.Entry()
    seed_entry.set_text(str(conf.get('seed') or ''))
    settings_grid.attach(seed_entry, 1, row, 1, 1)
    row += 1

    # Output format
    settings_grid.attach(Gtk.Label(label="Output Format:", halign=Gtk.Align.START), 0, row, 1, 1)
    fmt_combo = Gtk.ComboBoxText()
    for f in ['jpeg', 'png']: 
        fmt_combo.append_text(f)
    _set_combo_text(fmt_combo, conf.get('output_format', 'jpeg'))
    settings_grid.attach(fmt_combo, 1, row, 1, 1)
    row += 1

    # Safety tolerance
    settings_grid.attach(Gtk.Label(label="Safety Tolerance:", halign=Gtk.Align.START), 0, row, 1, 1)
    tol_combo = Gtk.ComboBoxText()
    for t in ['1', '2', '3', '4', '5', '6']: 
        tol_combo.append_text(t)
    _set_combo_text(tol_combo, conf.get('safety_tolerance', '2'))
    settings_grid.attach(tol_combo, 1, row, 1, 1)
    row += 1

    # Aspect ratio
    settings_grid.attach(Gtk.Label(label="Aspect Ratio:", halign=Gtk.Align.START), 0, row, 1, 1)
    ar_combo = Gtk.ComboBoxText()
    for ar in ['21:9', '16:9', '4:3', '3:2', '1:1', '2:3', '3:4', '9:16', '9:21']: 
        ar_combo.append_text(ar)
    _set_combo_text(ar_combo, conf.get('aspect_ratio', '1:1'))
    settings_grid.attach(ar_combo, 1, row, 1, 1)

    # --- Run the dialog ---
    dialog.set_default(ok_button)
    dialog.show_all()
    
    Gimp.message("[fal.ai] Dialog shown, waiting for response...")
    response = dialog.run()
    Gimp.message(f"[fal.ai] Dialog response: {response}")

    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        Gimp.message("[fal.ai] Dialog cancelled")
        return

    # --- 2. Gather all settings from UI ---
    prompt_text = entry_prompt.get_text().strip()
    if not prompt_text:
        Gimp.message("Prompt cannot be empty.")
        dialog.destroy()
        return

    # Update the settings dictionary with all current values from the UI
    conf['model'] = model_endpoint.get_text().strip()
    conf['prompt'] = prompt_text
    conf['api_key'] = key_entry.get_text().strip()
    conf['sync_mode'] = sync_btn.get_active()
    conf['enable_safety_checker'] = safe_btn.get_active()
    conf['guidance_scale'] = guid_spin.get_value()
    conf['num_images'] = num_spin.get_value_as_int()
    seed_text = seed_entry.get_text().strip()
    conf['seed'] = int(seed_text) if seed_text.isdigit() else None
    conf['output_format'] = fmt_combo.get_active_text()
    conf['safety_tolerance'] = tol_combo.get_active_text()
    conf['aspect_ratio'] = ar_combo.get_active_text()

    # --- 3. Save settings to disk for next time ---
    try:
        settings.save_settings(conf)
        Gimp.message("[fal.ai] Settings saved")
    except Exception as e:
        Gimp.message(f"[fal.ai] Warning: Could not save settings. Error: {e}")

    # Check if layer has content to determine if we do img2img or txt2img
    def layer_has_content(layer):
        if layer is None:
            return False
            
        w, h = layer.get_width(), layer.get_height()
        if w == 0 or h == 0:
            return False
            
        if not layer.has_alpha():
            return True # Opaque layer definitely has content
        
        try:
            # Get pixel region
            pr = layer.get_pixel_rgn(0, 0, w, h, False, False)
            data = bytearray(pr[0:w, 0:h])
            bpp = pr.bpp

            # Check alpha channel for any non-transparent pixels
            for i in range(bpp - 1, len(data), bpp):
                if data[i] > 0:
                    return True
            return False
        except Exception as e:
            Gimp.message(f"[fal.ai] Error checking layer content: {e}")
            return True  # Assume it has content if we can't check

    tmp_input = None
    drawable = drawable or image.get_active_layer()
    
    if drawable is None:
        Gimp.message("[fal.ai] No active layer found")
        dialog.destroy()
        return
        
    try:
        if layer_has_content(drawable):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_input = tmp.name
            Gimp.message(f"[fal.ai] Exporting layer to: {tmp_input}")
            utils.export_drawable(drawable, tmp_input)
        else:
            Gimp.message("[fal.ai] Active layer is empty; running in text-to-image mode.")
    except Exception as e:
        Gimp.message(f"[fal.ai] Could not check or export layer content, running text-to-image. Error: {e}")
        tmp_input = None

    dialog.destroy() # Close the UI before starting the long-running task

    try:
        # The `settings` dictionary now contains all params needed.
        Gimp.progress_init("Running fal.ai generation...")
        Gimp.message(f"[fal.ai] Starting generation with prompt: {prompt_text}")
        
        paths = falai_wrapper.process_image(conf, prompt_text, tmp_input)
        Gimp.progress_end()
        
        if not paths:
            Gimp.message("[fal.ai] No images returned from fal.ai; check the console for debug info.")
            return

        Gimp.message(f"[fal.ai] Received {len(paths)} images")
        
        for i, path in enumerate(paths):
            try:
                Gimp.progress_update(i / len(paths))
                utils.import_image(image, path)
                Gimp.message(f"[fal.ai] Imported image {i+1}/{len(paths)}")
            except Exception as e:
                Gimp.message(f"[fal.ai] Could not import layer, opening as new image. Error: {e}")
                try:
                    new_img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, path)
                    Gimp.Display.new(new_img)
                except Exception as e2:
                    Gimp.message(f"[fal.ai] Failed to open as new image: {e2}")
                    
    except NotImplementedError as e:
        Gimp.message(f"[fal.ai] Not implemented: {str(e)}")
    except Exception as e:
        Gimp.message(f"[fal.ai] Error during fal.ai processing: {e}")
        import traceback
        Gimp.message(f"[fal.ai] Traceback: {traceback.format_exc()}")
    finally:
        if tmp_input and os.path.exists(tmp_input):
            try:
                os.remove(tmp_input)
            except:
                pass