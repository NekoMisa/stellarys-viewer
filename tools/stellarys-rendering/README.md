# Mirror texture sampling guard

The inherited mirror renderer generates `floor(heroMipCount / 4)` radiance
levels, but allocates a full cubemap mip chain. Sampling past the generated
levels can blend in unwritten data. Sampling with zero blend weight can also
propagate non-finite values from those unused levels.

The shader skips zero-weight samples and clamps explicit LOD to the highest
generated level, including the upper neighbour used by trilinear filtering.
It retains the existing blend weight, mirror rendering and AMD skinning changes.

## Windows GPU regression test

With an installed v143 compiler and Windows SDK:

```powershell
python tools/stellarys-rendering/test_mirror_mips.py --work-dir D:/StellarysTests/mirror-mips
```

This creates a disposable hidden OpenGL context and extracts the actual production
`tapHeroProbe` function into a test shader. The cube texture's generated levels
have known colours; unused levels are deliberately filled with extreme colours
or NaNs. Seven mip counts and 101 gloss values exercise boundaries and zero-weight
reads. All 1,414 guarded draw results must match the expected colour.

Optionally pass `--reference path/to/original/reflectionProbeF.glsl` to compare
the pre-fix function against the same texture data. The original must demonstrate
a mismatch, while the production shader must pass. The helper does not change
viewer settings, profiles, installed applications or protocol associations.

This is a synthetic GPU test. In-world scene testing and driver coverage must be
reported separately; passing does not establish a universal reflection fix.
