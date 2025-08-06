"""
fal.ai client integration for GIMP plugin.
"""

import sys
import os

# Allow vendored fal_client (and its dependencies) to take priority
_HERE = os.path.dirname(__file__)
sys.path.insert(
    0,
    os.path.join(
        _HERE,
        'vendor',
        'fal_client',
    ),
)

import tempfile
import urllib.request
import ssl
import base64
from gi.repository import Gimp

try:
    import fal_client
except ImportError:
    raise RuntimeError(
        "Vendored 'fal-client' not found or missing its dependencies; "
        "ensure you have run the subtree pull for fal_client and vendored httpx/httpx-sse"
    )

def process_image(settings, prompt, input_path=None):
    """Invoke fal.ai image-to-image or text-to-image API.
    If input_path is provided, perform image-to-image; otherwise fall back to text-to-image.
    """
    # Ensure API key is set
    api_key = settings.get('api_key') or os.environ.get('FAL_KEY')
    if not api_key:
        raise RuntimeError(
            "API key not set in settings or FAL_KEY environment variable"
        )
    # Set for fal-client
    os.environ['FAL_KEY'] = api_key

    # Upload input image file if present (image-to-image); otherwise text-to-image
    image_url = None
    if input_path:
        image_url = fal_client.upload_file(input_path)
        Gimp.message(f"[DEBUG] Uploaded image URL: {image_url}")

    # Prepare arguments for API call
    args = {
        'prompt': prompt,
        'guidance_scale': settings.get('guidance_scale'),
        'num_images': settings.get('num_images'),
        'seed': settings.get('seed'),
        'output_format': settings.get('output_format'),
        'safety_tolerance': settings.get('safety_tolerance'),
        'aspect_ratio': settings.get('aspect_ratio'),
        'sync_mode': settings.get('sync_mode'),
        'enable_safety_checker': settings.get('enable_safety_checker', True),
    }
    if image_url:
        args['image_url'] = image_url

    def _on_update(update):
        # Print progress logs to stderr
        if isinstance(update, fal_client.InProgress):
            for log in getattr(update, 'logs', []):
                msg = log.get('message') if isinstance(log, dict) else str(log)
                print(msg, file=sys.stderr)

    # Debug: show invocation arguments
    Gimp.message(f"[DEBUG] Invoking fal.ai model '{settings.get('model')}' with args: {args}")
    # Invoke the fal.ai model
    result = fal_client.subscribe(
        settings.get('model'),
        arguments=args,
        with_logs=True,
        on_queue_update=_on_update,
    )

    # Debug: report result object and normalize single- vs multi-image response
    images = []
    if isinstance(result, dict):
        # prefer 'images' list, fallback to single 'image' key
        imgs = result.get('images')
        if imgs:
            images = imgs
        elif 'image' in result and result.get('image'):
            images = [result.get('image')]
    else:
        images = getattr(result, 'images', []) or []
        single = getattr(result, 'image', None)
        if not images and single:
            images = [single]
    Gimp.message(f"[DEBUG] fal.ai returned {len(images)} image(s): {images}")

    # Download generated images
    output_paths = []
    # Debug: print full result for inspection
    Gimp.message(f"[DEBUG] fal.ai full result: {result!r}")
    for img in images:
        # support both dict and object types for img
        if isinstance(img, dict):
            url = img.get('url')
            content_type = img.get('content_type')
        else:
            url = getattr(img, 'url', None)
            content_type = getattr(img, 'content_type', None)
        if not url:
            continue
        # Determine file suffix: prefer content_type, else url or output_format
        ext = None
        if content_type and '/' in content_type:
            ext = content_type.split('/', 1)[1]
        if not ext:
            ext = os.path.splitext(url)[1].lstrip('.') or settings.get('output_format', 'jpeg')
        suffix = f".{ext}"
        out_path = tempfile.mktemp(suffix=suffix)
        # Download or decode generated image
        if url.startswith('data:'):
            # data URI: decode base64 or raw data
            header, data_part = url.split(',', 1)
            if ';base64' in header:
                data = base64.b64decode(data_part)
            else:
                data = data_part.encode('utf-8')
            with open(out_path, 'wb') as f:
                f.write(data)
        else:
            try:
                urllib.request.urlretrieve(url, out_path)
            except Exception:
                # Retry download without certificate verification on any SSL/URL error
                ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(url, context=ctx) as resp, open(out_path, 'wb') as f:
                    f.write(resp.read())
        output_paths.append(out_path)

    return output_paths
