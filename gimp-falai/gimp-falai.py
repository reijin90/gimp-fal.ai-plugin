#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# fal.ai GIMP3 plugin: settings and image-to-image commands
#
import sys
#import logging

# Debug load message; appears in Error Console or --console-messages
print("🔍 fal.ai plugin.py loaded!", file=sys.stderr)
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
from gi.repository import Gimp, GimpUi, GObject, GLib

from settings import load_settings, save_settings
from ui import show_settings_dialog, show_prompt_dialog

# Procedure identifiers
PROC_SETTINGS = 'plug-in-falai-settings'
PROC_RUN = 'plug-in-falai-run'

def settings_run(proc, run_mode, image, drawables, args, data):
    """Run handler for global settings dialog."""
    # Launch interactive UI for settings
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init(proc.get_name())
        settings = load_settings()
        try:
            show_settings_dialog(settings)
            save_settings(settings)
        except Exception as e:
            Gimp.message(f"[DEBUG] settings dialog failed: {e}")
            raise
    return proc.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

def run_run(proc, run_mode, image, drawables, args, data):
    """Run handler for per-image prompt and processing."""
    # Launch interactive UI for prompt and image processing
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init(proc.get_name())
        drawable = drawables[0] if drawables else None
        try:
            show_prompt_dialog(image, drawable)
        except Exception as e:
            Gimp.message(f"[DEBUG] prompt dialog failed: {e}")
            raise
    return proc.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class FalAiPlugin(Gimp.PlugIn):
    """GIMP3 PlugIn for fal.ai settings and image-to-image."""

    def do_query_procedures(self):
        return [PROC_SETTINGS, PROC_RUN]

    def do_set_i18n(self, name):
        # We do not support translations
        return False

    def do_create_procedure(self, name):
        # if name == PROC_SETTINGS:
        #     proc = Gimp.ImageProcedure.new(
        #         self, name,
        #         Gimp.PDBProcType.PLUGIN,
        #         settings_run, None)
        #     proc.set_image_types('*')
        #     proc.set_menu_label('fal.ai Settings...')
        #     proc.add_menu_path('<Image>/Filters/fal.ai')
        #     proc.set_attribution('fal.ai', 'fal.ai plugin', '2023')
        #     proc.set_documentation(
        #         'Invoke fal.ai image-to-image model',
        #         'Opens a prompt dialog and runs fal.ai model on the current image.',
        #         None)
        #     return proc

        if name == PROC_RUN:
            proc = Gimp.ImageProcedure.new(
                self, name,
                Gimp.PDBProcType.PLUGIN,
                run_run, None)
            proc.set_image_types('*')
            proc.set_menu_label('fal.ai Run...')
            proc.add_menu_path('<Image>/Filters/fal.ai')
            proc.set_attribution('fal.ai', 'fal.ai plugin', '2023')
            proc.set_documentation(
                'Invoke fal.ai image-to-image model',
                'Opens a prompt dialog and runs fal.ai model on the current image.',
                None)
            proc.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE |
                Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
            return proc

Gimp.main(FalAiPlugin.__gtype__, sys.argv)
