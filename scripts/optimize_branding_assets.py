from pathlib import Path
from PIL import Image

ROOT = Path('/home/ubuntu/phantm')
ASSET_PATHS = [
    ROOT / 'assets/images/icon.png',
    ROOT / 'assets/images/splash-icon.png',
    ROOT / 'assets/images/favicon.png',
    ROOT / 'assets/images/android-icon-foreground.png',
]

for path in ASSET_PATHS:
    with Image.open(path) as img:
        img = img.convert('RGBA')
        target_size = (1024, 1024)
        if path.name == 'favicon.png':
            target_size = (256, 256)
        elif path.name == 'splash-icon.png':
            target_size = (512, 512)
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        palette = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=192)
        palette.save(path, format='PNG', optimize=True)
        print(f'{path.name}: {path.stat().st_size / 1024:.1f} KB')
