# Codex Project Specification

## Required Appendix Architecture

Canon R5 Photography Reference System

## Purpose

The Photography Reference System uses a baseline + overrides architecture.

Profiles contain only the settings that differ from the Baseline.

Educational material must not be duplicated inside profiles. Explanatory content belongs in dedicated appendices that are generated automatically during every build.

Cards must function as quick references in the field. Each card must render the required quick-reference settings from the merged baseline + profile data, even when a required setting is inherited from the baseline rather than repeated in the profile.

Required quick-reference card settings:

- exposure.mode
- autofocus.operation
- autofocus.subject_detection
- autofocus.eye_detection
- autofocus.method
- drive.mode
- shutter.target
- lens.aperture.target
- stabilization.image_stabilization.mode
- exposure.iso.mode
- exposure.auto_iso.maximum

Cards render ISO as a single quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays as the fixed ISO value. Profile data must keep ISO mode, ISO value, and Auto ISO maximum as separate fields.

Cards render IBIS and Lens IS as a single `IBIS/Lens IS` quick-reference row when both settings are shown. Profile data must keep IBIS and Lens IS as separate fields.

Cards omit AF Method, Subject Detection, and Eye Detection when AF Operation is `Manual Focus`.

Cards omit Subject Detection and Eye Detection when AF Method is `Not Used`.

Profile `metadata.release: true` controls whether a card is included in the offline iPhone bundle.

Appendix manifest `release: true` controls whether an appendix is included in the offline iPhone bundle.

## Required Appendices

Required appendices are listed in `50 Field Guide/required_appendices.yaml`.

Appendices do not need to be numbered in filenames or titles. Legacy appendix numbers may be retained as manifest metadata for continuity.

If a required appendix is missing, validation fails.

## Standard Appendix Format

Every appendix must use the same section order:

1. Purpose
2. What it Does
3. How it Works
4. Advantages
5. Disadvantages
6. Recommended Uses
7. When Not to Use
8. Decision Guide
9. Recommended Settings by Profile
10. Canon-Specific Notes
11. Tips
12. Common Mistakes
13. Cross References

## Cross References

Every appendix should link to relevant profiles, camera settings, lens notes, and related appendices.

No duplicate educational content should exist in profiles. Profiles should reference appendices instead.

## Validation Rules

The validator verifies:

- All required appendices exist.
- Required section headings exist.
- Manifest cross references point to valid profiles and appendices.
- Required appendix manifests remain parseable.

## Build Requirements

Build outputs should include every required appendix in HTML, PDF, navigation, search, and icon/index systems where applicable.

Required appendices are part of the core Photography Reference System and are not optional.

Before updating project files, create timestamped backups of the files being changed under `80 Build/Backups/`.
