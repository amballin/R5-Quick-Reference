# Canon Icons Extraction Report

- Total settings detected: 50
- Total icon records created: 50
- Original PNG files created: 50
- Normalized PNG files created: 50
- SVG files created: 50
- Skipped rows: 0
- Duplicate names resolved: 0

## Low-Confidence SVG Conversions
- histogram: Fine stair-step histogram detail converted from raster mask.
- peripheral_illumination_correction: Curved dashed detail converted from raster mask.
- chromatic_aberration_correction: Original includes colored bars; normalized asset converts artwork to black.
- electronic_level: Fine circular level marks converted from raster mask.
- touch_shutter: Fine hand/touch detail converted from raster mask.

## Files Created
- `60 Assets/icon-map.yaml`
- `60 Assets/icons/card_icons/manifest.yaml`
- `60 Assets/icons/card_icons/preview.html`
- `60 Assets/icons/card_icons/REPORT.md`
- `60 Assets/icons/card_icons/Originals/<field_id>_original.png` for each detected setting
- `60 Assets/icons/card_icons/PNG/<field_id>.png` for each detected setting
- `60 Assets/icons/card_icons/SVG/<field_id>.svg` for each detected setting

## Validation Results
- Every detected setting has an original PNG: yes
- Every detected setting has a normalized PNG: yes
- Every detected setting has an SVG: yes
- `icon-map.yaml` references only existing files: yes
- `manifest.yaml` references only existing files: yes
- No duplicate field IDs: yes
- No SVG contains embedded raster images: yes
