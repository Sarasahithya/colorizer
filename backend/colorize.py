from deoldify.visualize import get_image_colorizer
from pathlib import Path
import torch
from PIL import Image, UnidentifiedImageError

# Ensure dummy folder exists for DeOldify
Path('dummy').mkdir(exist_ok=True)

# Initialize DeOldify colorizer
colorizer = get_image_colorizer(artistic=True)

# Lazy-load GFPGAN only when needed
def init_gfpgan():
    from gfpgan import GFPGANer
    model_path = 'gfpgan/weights/GFPGANv1.4.pth'
    return GFPGANer(
        model_path=model_path,
        upscale=1,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=None
    )

def colorize_image(input_path, output_path, restore_faces=False):
    input_path, output_path = Path(input_path), Path(output_path)

    # 1. Colorize image
    try:
        colorizer.plot_transformed_image(
            path=input_path,
            results_dir=output_path.parent,
            render_factor=35,
            display_render_factor=False,
            figsize=(8, 8),
        )
    except Exception as e:
        raise RuntimeError(f"Colorization failed: {e}")

    # Locate generated file
    rendered_path = None
    for ext in ['.jpg', '.jpeg', '.png']:
        candidate = output_path.parent / f"{input_path.stem}{ext}"
        if candidate.exists():
            rendered_path = candidate
            break
    if not rendered_path:
        raise FileNotFoundError(f"No rendered output found for {input_path.stem}")

    # 2. Save final colorized image (unmodified)
    ext = output_path.suffix.lstrip('.').lower()
    format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG'}
    fmt = format_map.get(ext, 'PNG')
    try:
        with Image.open(rendered_path) as img:
            img = img.convert("RGB")
            img.save(output_path, format=fmt)
    except Exception as e:
        raise RuntimeError(f"Error processing final image: {e}")

    # Clean up temp file
    try:
        rendered_path.unlink()
    except:
        pass

    # 3. Apply face restoration if requested
    if restore_faces:
        restorer = init_gfpgan()
        import numpy as np
        img = Image.open(output_path).convert('RGB')
        arr = np.array(img)
        _, _, restored = restorer.enhance(
            arr,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        Image.fromarray(restored).save(output_path)
