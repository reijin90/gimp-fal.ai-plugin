"""
Utility functions for fal.ai GIMP plugin.
"""

from gi.repository import Gimp, Gio

def export_drawable(drawable, path):
    """Export the given drawable to a file at the given path using GIMP's file_save."""
    # Try exporting via direct pixel dump (PIL) to avoid C-API mismatches
    try:
        # Ensure drawable is up-to-date
        drawable.flush()
        drawable.merge_shadow()
        w = drawable.get_width()
        h = drawable.get_height()
        pr = drawable.get_pixel_rgn(0, 0, w, h, False, False)
        data = pr[0:w, 0:h]
        bpp = pr.bpp
        from PIL import Image

        mode = 'RGB' if bpp == 3 else 'RGBA'
        img = Image.frombytes(mode, (w, h), data, 'raw', mode)
        img.save(path)
        return
    except ImportError:
        # Pillow not available; fall back to GIMP file_save API
        pass
    except Exception:
        # Fall back if direct dump fails
        pass

    image = drawable.get_image()
    out_file = Gio.File.new_for_path(path)
    first_exc = None
    # Try 5-arg (run_mode, image, drawable, Gio.File, filename)
    try:
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, drawable, out_file, path)
        return
    except Exception as exc1:
        first_exc = exc1
    # Try 4-arg Gimp.file_save signature: (run_mode, image, GFile, options)
    try:
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, out_file, None)
        return
    except Exception as exc2:
        raise RuntimeError(
            f"Failed to export drawable to {path}: {first_exc}; {exc2}"
        )

def import_image(image, image_path):
    """Import an image file into GIMP as a new layer using GIMP's file_load_layer."""
    try:
        # Load layer from file; wrap path in Gio.File
        # Import via the core file_load_layer API (run-mode, image, Gio.File)
        in_file = Gio.File.new_for_path(image_path)
        layer = Gimp.file_load_layer(
            Gimp.RunMode.NONINTERACTIVE,
            image,
            in_file,
        )
        image.insert_layer(layer, None, -1)
        Gimp.displays_flush()
    except Exception as e:
        raise RuntimeError(f"Failed to import image {image_path} into GIMP: {e}")
