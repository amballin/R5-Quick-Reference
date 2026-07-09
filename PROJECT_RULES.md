# Photography Reference System Rules

1. Preserve the existing project structure.

2. Profiles inherit from the baseline.

3. Profile YAML files contain ONLY differences from the baseline.

4. Never redesign the YAML structure unless explicitly instructed.

5. Preserve backward compatibility whenever possible.

6. Generated files belong only in the Output folders.

7. Assets belong only in the Assets folders.

8. Never duplicate baseline settings inside profiles.

9. All rendering decisions belong in the build system, not the profile YAML.

10. Cards must render the required quick-reference settings from the merged baseline + profile data, even when those settings are inherited from the baseline.

11. Required quick-reference card settings are:
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

12. Cards render ISO as a single quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays as the fixed ISO value. Profile data must keep ISO mode, ISO value, and Auto ISO maximum as separate fields.

13. Cards render IBIS and Lens IS as a single `IBIS/Lens IS` quick-reference row when both settings are shown. Profile data must keep IBIS and Lens IS as separate fields.

14. Cards omit AF Method, Subject Detection, and Eye Detection when AF Operation is `Manual Focus`.

15. Cards omit Subject Detection and Eye Detection when AF Method is `Not Used`.

16. Profile `metadata.release: true` controls whether a card is included in the offline iPhone bundle.

17. Appendix manifest `release: true` controls whether an appendix is included in the offline iPhone bundle.

18. Before updating project files, create timestamped backups of the files being changed under `80 Build/Backups/`.

19. Ask before making architectural changes.
