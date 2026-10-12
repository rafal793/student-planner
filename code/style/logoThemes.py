"""Generowanie wariantów logo dopasowanych do palet motywu."""

from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image

SOURCE_LOGO = Path(__file__).resolve().parent.parent / 'images' / 'logo_default.png'
OUTPUT_DIR = SOURCE_LOGO.parent

THEME_LOGO_SPECS = {
    'default': None,
    'midnight': {'hue_delta': -0.045, 'sat_mul': 1.18, 'val_mul': 1.1},
    'rose': {'hue_delta': 0.42, 'sat_mul': 1.2, 'val_mul': 1.28, 'lighten_grays': True},
}


def _recolor_pixel(r: int, g: int, b: int, a: int, spec: dict) -> tuple[int, int, int, int]:
    if a < 20:
        return r, g, b, a

    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    if s < 0.12:
        if spec.get('lighten_grays'):
            h = 0.92
            s = 0.22
            v = max(v * spec['val_mul'], 0.82)
        elif spec['val_mul'] != 1.0:
            v = min(1.0, v * spec['val_mul'])
        else:
            return r, g, b, a
    else:
        h = (h + spec['hue_delta']) % 1.0
        s = min(1.0, s * spec['sat_mul'])
        v = min(1.0, v * spec['val_mul'])

    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
    return int(nr * 255), int(ng * 255), int(nb * 255), a


def build_themed_logo(palette_name: str) -> Path:
    spec = THEME_LOGO_SPECS.get(palette_name)
    if spec is None:
        return SOURCE_LOGO

    output = OUTPUT_DIR / f'logo_theme_{palette_name}.png'
    img = Image.open(SOURCE_LOGO).convert('RGBA')
    img.putdata([_recolor_pixel(*px, spec) for px in img.getdata()])
    img.save(output, optimize=True)
    return output


LOGO_BY_PALETTE = {
    'default': 'images/logo_default.png',
    'midnight': 'images/logo_theme_midnight.png',
    'rose': 'images/logo_theme_rose.png',
}


if __name__ == '__main__':
    for name in THEME_LOGO_SPECS:
        if name == 'default':
            continue
        path = build_themed_logo(name)
        print(f'Generated {path}')
