# PixInsight ImageIntegration & DrizzleIntegration Analysis

## Goal

Build a script that points at a WBPP "registered" output directory and performs integration using one or more saved process icons (templates) for both ImageIntegration and DrizzleIntegration. The script should handle file discovery, filter separation, and application of user-defined integration settings while leaving full control over rejection algorithms and other parameters to the process icon templates.

---

## 1. WBPP Output Directory Structure

WBPP creates a predictable output directory structure:

```
output_dir/
  Calibrated/
  Registered/
    Light_BIN-1_3840x2160_EXPOSURE-60.00s_FILTER-H_mono_READOUTM-High Conversion Gain/
      2026-02-28_07-41-44_HFR_1.58_RMSAC_0.75_TEMP_-10.00_c_1_r.xisf
      2026-02-28_07-41-44_HFR_1.58_RMSAC_0.75_TEMP_-10.00_c_1_r.xdrz
      2026-02-28_07-41-44_HFR_1.58_RMSAC_0.75_TEMP_-10.00_c_1_r.xnml
      ...
    Light_BIN-1_3840x2160_EXPOSURE-60.00s_FILTER-O_mono_READOUTM-High Conversion Gain/
      ...
  Master/
    masterLight-BINNING_1-FILTER_Ha-EXPTIME_300.xisf
    ...
```

### Filter Identification from Directory Names

WBPP organizes registered images into **subdirectories per filter**. The directory name contains a `FILTER-X` segment that can be parsed to extract the filter name. Examples:

```
Light_BIN-1_3840x2160_EXPOSURE-60.00s_FILTER-H_mono
Light_BIN-1_3840x2160_EXPOSURE-60.00s_FILTER-H_mono_READOUTM-High Conversion Gain
```

The filter value is extracted from the `FILTER-` prefix. In these examples, the filter is `H`. Note: the directory naming does NOT follow the `KEY_VALUE` convention used elsewhere in WBPP (e.g., master files use `FILTER_Ha`). Instead it uses `FILTER-H` with a hyphen separator.

**Parsing strategy**: Extract the value between `FILTER-` and the next `_` (or end of string). Cannot rely on a leading underscore before `FILTER`.

### Associated Files

For each registered `.xisf` image, there are:
- A `.xdrz` file (drizzle data) -- same base filename
- A `.xnml` file (local normalization data) -- same base filename (present when LocalNormalization was run; in the target workflow, always present)

All three file types (`.xisf`, `.xdrz`, `.xnml`) share the same base filename and reside in the same filter subdirectory.

---

## 2. The Relationship Between ImageIntegration and DrizzleIntegration

This is the critical architectural question for the script design.

### Data Flow

```
StarAlignment
  └─> Creates initial .xdrz files (registration/alignment transforms)
  └─> Creates registered .xisf images

LocalNormalization (optional)
  └─> Creates .xnml files

ImageIntegration
  ├─> Reads registered .xisf images
  ├─> Reads .xdrz files (if drizzle enabled)
  ├─> Reads .xnml files (if local normalization enabled)
  ├─> Performs pixel rejection
  ├─> UPDATES .xdrz files with normalization + rejection data
  └─> Outputs integrated master image

DrizzleIntegration
  ├─> Reads .xdrz files (with rejection data from ImageIntegration)
  ├─> Reads ORIGINAL (unregistered) images via paths stored in .xdrz
  ├─> Applies registration transforms from .xdrz
  ├─> Applies normalization data from .xdrz
  ├─> Applies rejection maps from .xdrz
  └─> Outputs drizzle-integrated image
```

### Key Finding: DrizzleIntegration DEPENDS on ImageIntegration

**DrizzleIntegration does not perform its own pixel rejection.** It relies entirely on the rejection maps stored in the `.xdrz` files, which are written by ImageIntegration.

Specifically:
- The `.xdrz` file stores rejection maps as 8-bit unsigned integer images with bitfield encoding:
  - Bit 0: High statistical rejection (pixel rejected above central value)
  - Bit 1: Low statistical rejection (pixel rejected below central value)
  - Bit 2: High range rejection (pixel exceeds upper limit)
  - Value 0: Not rejected
- If no rejection data exists in the `.xdrz` file, DrizzleIntegration issues a warning: `"** Warning: The drizzle data file contains no pixel rejection data."` and proceeds without rejection
- DrizzleIntegration will still produce an image without rejection data, but artifacts (satellites, cosmic rays) will remain

### Critical Implication for the Script

**ImageIntegration MUST run before DrizzleIntegration**, and the rejection algorithm used in ImageIntegration directly determines what gets rejected in the drizzle output. If you re-run ImageIntegration with different rejection settings and have "Generate drizzle data" enabled, the `.xdrz` files are automatically overwritten with the new rejection data.

This means:
1. Running multiple ImageIntegration templates with different rejection algorithms will produce different `.xdrz` files
2. The **last** ImageIntegration run determines the rejection data in the `.xdrz` files
3. If you want to compare multiple rejection approaches with drizzle, you need to either:
   - Copy the `.xdrz` files after each ImageIntegration run before the next one overwrites them
   - Run ImageIntegration + DrizzleIntegration as paired operations

### Important Caveats

- **Do not use ROI (Region of Interest)** in the final ImageIntegration run -- the rejection data will be incomplete for the drizzle files
- **Do not rename or move files** after drizzle files are created -- file paths are embedded in the `.xdrz` data
- DrizzleIntegration reads the **original unregistered images** (not the registered ones) using transformation data from the `.xdrz` files

---

## 3. Rejection Algorithms and Nebula Signal

### The Problem You Experienced

Seeing nebula structure in rejection maps is a **known and common issue**. It happens because:

1. Nebula signal varies across frames due to slight differences in registration, transparency, and sky conditions
2. Rejection algorithms treat pixels that deviate from the central tendency as outliers
3. The brightest parts of nebulae can trigger high-pixel rejection, especially with aggressive sigma values

### Why Winsorized Sigma Clipping Helps (But Doesn't Fully Solve It)

Unlike pure sigma clipping which discards rejected pixels entirely, Winsorized Sigma Clipping **replaces** outlier pixels with the nearest value within the sigma thresholds. This mitigates signal loss but doesn't eliminate it.

### Local Normalization is Critical

**Local Normalization dramatically improves rejection accuracy** by matching background levels across frames before rejection. When all subframes have well-matched backgrounds, the rejection algorithm can better distinguish true outliers (satellites, cosmic rays) from real signal (nebula structure).

If local normalization was used (and `.xnml` files exist), the script **must** use `LocalNormalization` as the normalization mode for pixel rejection in ImageIntegration.

### Rejection Algorithm Recommendations by Frame Count

| Frame Count | Recommended Algorithm |
|---|---|
| 3-4 | Min/Max |
| 5-9 | Percentile Clipping |
| 9-15 | Averaged Sigma Clipping |
| 15-25 | Winsorized Sigma Clipping |
| 25+ | Linear Fit Clipping or ESD (GESD) |

### ESD (Generalized Extreme Studentized Deviate) -- Worth Investigating

ESD was introduced in PixInsight 1.8.8 and is considered by many to be superior for preserving signal:
- The **relaxation parameter** is key: it makes the algorithm more tolerant of low-value rejections, effectively "lying to the algorithm" about dispersion for pixels below the central value
- Default alpha (significance) = 0.05, meaning high pixels are rejected if ~2 sigma from central value
- ESD works best with 25-50+ subframes
- Multiple experienced astrophotographers report fewer issues with signal rejection using ESD

### Practical Tuning Approach

1. Run an integration with **no rejection** first -- note the median noise reduction (this is your SNR ceiling)
2. Then enable rejection and compare:
   - Total rejection percentages in console output
   - Rejection maps (are they showing only artifacts, or also signal?)
   - Noise reduction metric (should be close to the no-rejection baseline)
3. Increase sigma values if you see signal in rejection maps
4. Try different algorithms as process icon templates

---

## 4. Process Icons as Templates in PJSR

### What Process Icons Store

A process icon stores the complete state of a process instance -- all parameters, settings, and configuration. For ImageIntegration this includes:
- Rejection algorithm and all its parameters (sigma high/low, ESD significance, etc.)
- Normalization settings
- Pixel rejection normalization mode
- Combination method (average, median, etc.)
- Weighting mode
- Large-scale rejection settings
- Generate drizzle data flag
- **But NOT the file list** (the `images` array)

### Confirmed API Format: ImageIntegration.images

The `images` array format has been confirmed via drag-to-Script-Editor (4-element sub-arrays):

```javascript
P.images = [ // enabled, path, drizzlePath, localNormalizationDataPath
   [true, "/path/to/image_r.xisf", "/path/to/image_r.xdrz", "/path/to/image_r.xnml"],
   [true, "/path/to/image2_r.xisf", "/path/to/image2_r.xdrz", "/path/to/image2_r.xnml"],
   // ...
];
```

### Confirmed API Format: DrizzleIntegration.inputData

The `inputData` array format has been confirmed (3-element sub-arrays):

```javascript
P.inputData = [ // enabled, path, localNormalizationDataPath
   [true, "/path/to/image_r.xdrz", "/path/to/image_r.xnml"],
   [true, "/path/to/image2_r.xdrz", "/path/to/image2_r.xnml"],
   // ...
];
```

Note: DrizzleIntegration takes `.xdrz` file paths (not `.xisf`), plus optional `.xnml` paths.

### Loading and Using Process Icons in Scripts

```javascript
// Requires process icon to be pre-loaded in PixInsight workspace
let P = ProcessInstance.fromIcon("MyIntegrationTemplate");

// Override the file list with discovered files
P.images = [
   [true, "/path/to/image_r.xisf", "/path/to/image_r.xdrz", "/path/to/image_r.xnml"],
];

// Execute
P.executeGlobal();

// Access results
var integrationWindow = ImageWindow.windowById(P.integrationImageId);
var lowRejMap = ImageWindow.windowById(P.lowRejectionMapImageId);
var highRejMap = ImageWindow.windowById(P.highRejectionMapImageId);

// Read-only output properties available after execution:
// P.integrationImageId, P.lowRejectionMapImageId, P.highRejectionMapImageId
// P.finalNoiseEstimateRK, P.medianNoiseReductionRK, P.referenceSNRIncrementRK
// P.averageSNRIncrementRK, P.totalRejectedLowRK, P.totalRejectedHighRK
// P.imageData (per-image weights and rejection counts -- excluded from CSV; too verbose for aggregate comparison)
```

### Key ImageIntegration Properties (from confirmed template)

Notable properties that the process icon template controls:

```javascript
P.combination = ImageIntegration.prototype.Average;
P.weightMode = ImageIntegration.prototype.PSFSignalWeight;
P.normalization = ImageIntegration.prototype.LocalNormalization;
P.rejection = ImageIntegration.prototype.NoRejection;  // or WinsorizedSigmaClip, ESD, etc.
P.rejectionNormalization = ImageIntegration.prototype.LocalRejectionNormalization;
P.generateDrizzleData = true;   // MUST be true for drizzle workflow
P.generateRejectionMaps = true;
P.autoMemorySize = true;
P.autoMemoryLimit = 0.75;
P.bufferSizeMB = 16;
P.stackSizeMB = 1024;
```

### Key DrizzleIntegration Properties (from confirmed template)

```javascript
P.scale = 2.00;
P.dropShrink = 0.90;
P.kernelFunction = DrizzleIntegration.prototype.Kernel_Square;
P.enableRejection = true;        // uses rejection maps from .xdrz
P.enableImageWeighting = true;
P.enableSurfaceSplines = true;
P.enableLocalDistortion = true;
P.enableLocalNormalization = true;
P.enableAdaptiveNormalization = false;
```

### Loading .xpsm Files

Process icon sets are saved as `.xpsm` files. They can be loaded:
1. By double-clicking the file (opens PixInsight with icons loaded)
2. Via startup script in `PixInsight/etc/startup/`: `.open /path/to/icons.xpsm`
3. The icons are then available via `ProcessInstance.fromIcon("iconName")`

---

## 5. Proposed Script Architecture

### Design Decisions (Confirmed)

- **II + DI as atomic pairs**: Since ImageIntegration overwrites `.xdrz` rejection data, each II template is immediately followed by the DI template before the next II run. No `.xdrz` backup needed.
- **DrizzleIntegration is optional**: Can run II-only or II+DI. Only a single DI template is supported -- DI adds spatial resolution but doesn't differentiate rejection strategies, so running DI for every II comparison run is expensive with minimal diagnostic value. In practice, DI is used for the final chosen II configuration, not during comparison.
- **Filter discovery from directory names**: Parse `FILTER-X` from WBPP subdirectory names (no FITS header reading needed).
- **Local normalization always present** in the target workflow (but script handles absent `.xnml` gracefully).
- **Process icons pre-loaded**: User loads `.xpsm` into PixInsight workspace before running script, passes icon names as parameters.
- **Output directory**: `integration/` as a peer to `master/`, with filenames like `integration_H_WSC.xisf`.
- **Rejection maps saved**: Yes, alongside integration outputs.
- **Reference image**: Automatic selection (same algorithm, same dataset = consistent reference across runs).
- **No FastIntegration support**.
- **Comparison output**: CSV format with all captured properties per run, for consumption by other tools. This script is a data-capture first pass, not the analysis tool.
- **Template naming**: Use process icon names directly as output suffixes (user-controlled, no translation).
- **Missing file handling**: Fail the entire filter group if expected `.xdrz`/`.xnml` associations are missing.

### Input
- Path to the "registered" directory
- One or more ImageIntegration process icon names (from a loaded .xpsm)
- Zero or one DrizzleIntegration process icon name (optional, from a loaded .xpsm)

### Processing Steps

```
1. Scan registered directory for filter subdirectories
2. Parse FILTER-X from each subdirectory name
3. For each filter subdirectory:
   a. Discover .xisf files and their associated .xdrz/.xnml files (same base name)
   b. Validate: if DI requested or .xnml expected, fail filter group if associations missing
   c. For each ImageIntegration template icon:
      i.    Load process instance from icon via ProcessInstance.fromIcon()
      ii.   Set P.images array with discovered files
      iii.  Verify P.generateDrizzleData == true (if DI will follow)
      iv.   Execute P.executeGlobal()
      v.    Capture read-only output: aggregate metrics (SNR, noise estimates, rejection counts)
      vi.   Save integration result to integration/<filter>_<iconName>.xisf
      vii.  Save rejection maps to integration/<filter>_<iconName>_rejLow.xisf etc.
      viii. If DrizzleIntegration template specified:
              * Load DI process instance from icon
              * Set P.inputData with .xdrz + .xnml paths
              * Execute P.executeGlobal()
              * Save drizzle result to integration/<filter>_<iconName>_drizzle.xisf
4. Write CSV report with all captured metrics per run (filter, template, SNR, noise, rejection counts, etc.)
```

---

## 6. Local Normalization Considerations

When `.xnml` files are present:
- ImageIntegration's "Normalization for pixel rejection" should be set to **LocalNormalization**
- The `.xnml` file paths must be included in the `images` array
- This is typically the single most impactful setting for rejection quality
- The process icon template should already have this setting configured, but the script should validate/warn if `.xnml` files exist but the template doesn't use LocalNormalization mode

---

## 7. Filter Discovery from Directory Names

The script extracts filter names from WBPP subdirectory names rather than reading FITS headers (much faster, no image I/O):

```javascript
// Parse filter from directory name like:
//   "Light_BIN-1_3840x2160_EXPOSURE-60.00s_FILTER-H_mono_READOUTM-High Conversion Gain"
function extractFilter(dirName) {
   var match = dirName.match(/FILTER-([^_]+)/);
   return match ? match[1] : null;
}
```

This avoids the expense of opening every `.xisf` file just to read headers.

---

## 8. AutoIntegrate.js Gap Analysis

[AutoIntegrate](https://github.com/jarmoruuth/AutoIntegrate) (v1.84.1, Feb 2026) by Jarmo Ruuth is a comprehensive PixInsight script that automates image processing from calibrated files to final image. It has 90+ releases and 832 commits. Here's how it compares to our requirements:

### What AutoIntegrate CAN Do (Overlap)

- **ImageIntegration**: Runs ImageIntegration on grouped light files (LRGB, narrowband, OSC)
- **DrizzleIntegration**: Supports drizzle as an option (added v1.75)
- **Local Normalization**: Can run its own LocalNormalization (disabled by default)
- **Filter grouping**: Auto-detects filters from FITS headers or filename suffixes (`_L`, `_Ha`, etc.)
- **Rejection algorithm selection**: Dynamically chooses rejection method based on frame count
- **Accepts pre-calibrated files**: Can start from already-calibrated images (skipping calibration steps)
- **Process icon export**: v1.80 added saving executed processes as process icons for later manual review (but this is export, not import)
- **Metrics Visualizer**: v1.76 added SubframeSelector metrics visualization (FWHM, Eccentricity, SNR, PSF Signal)
- **Full pipeline**: CosmeticCorrection → SubframeSelector → StarAlignment → ImageIntegration → post-processing

### Gap Analysis Table

| Requirement | AutoIntegrate Support | Gap |
|---|---|---|
| Start from WBPP registered dir | Accepts pre-calibrated files via GUI, but no directory-pointing mode | Medium |
| Apply II process icon templates | Cannot consume templates; only exports them | **High** |
| Apply DI process icon templates | Cannot consume templates | **High** |
| Atomic II+DI pairs | No explicit support (runs single integration per filter) | **High** |
| Support pre-existing .xnml files | Runs its own LN; no documented import of external .xnml | Medium |
| Auto-discover from WBPP dirs | Reads FITS headers/filenames, not WBPP directory naming | Medium |
| Comparison reports across runs | No multi-run comparison (metrics visualizer is for input subframes only) | **High** |
| Save rejection maps | No documented support | **High** |
| Output as peer to WBPP master/ | Own directory structure (AutoOutput/, AutoMaster/, AutoProcessed/) | Low |

### Detailed Gaps

1. **No "registered directory" input**: Files must be added individually through the GUI or via file lists. No mode to point at a WBPP `registered/` directory tree.

2. **No user-supplied process icon templates**: AutoIntegrate's v1.80 "process icons" feature works in the **opposite direction** -- it saves processes AutoIntegrate executed as icons for review. It does not consume user-supplied templates. II/DI settings are managed internally through AutoIntegrate's own simplified GUI.

3. **No multiple rejection algorithm comparison**: One integration per filter with auto-selected algorithm. No facility to run the same data through 3+ different rejection configurations.

4. **No comparison reporting**: The Metrics Visualizer evaluates input subframes, not output integration results across runs.

5. **No atomic II+DI pairing**: Single integration means the .xdrz overwriting problem doesn't arise, but also means no multi-template workflow.

6. **Full pipeline overhead**: Would duplicate StarAlignment, cosmetic correction, etc. that WBPP already completed.

7. **External .xnml ingestion unclear**: Can run its own LocalNormalization but no documented support for consuming WBPP-generated `.xnml` files as ImageIntegration input.

### Verdict

**Recommendation: Build a focused script rather than extending AutoIntegrate.**

Reasons:
- **Architectural mismatch**: AutoIntegrate is a monolithic end-to-end pipeline; our tool is a modular integration-stage component downstream of WBPP
- **Process icon template consumption is antithetical to AutoIntegrate's design**: Its value proposition is managing II/DI settings internally; accepting arbitrary templates would undermine its abstraction
- **Multi-run comparison is entirely novel**: Nothing in AutoIntegrate's architecture supports this
- **Maintenance burden**: Forking a 832-commit single-file JavaScript project with active upstream development means merge conflict risk
- **Our requirements are well-scoped**: A purpose-built script is tractable and simpler

AutoIntegrate's source code (specifically `AutoIntegrateEngine.js`) remains a useful reference for PixInsight scripting patterns.

---

## 9. Sources

- [PixInsight Image Integration - Chaotic Nebula](https://chaoticnebula.com/pixinsight-image-integration/)
- [Pixel Rejection Methods - DSLR Astrophotography](https://dslr-astrophotography.com/detailed-pixel-rejection-methods/)
- [Winsorized Sigma Clipping Rejection Values - PixInsight Forum](https://pixinsight.com/forum/index.php?threads/winsorised-sigma-clipping-rejection-values.8069/)
- [Drizzle Integration - MyPetStars](https://mypetstars.com/tutorials/pixinsight/processes/drizzleintegration)
- [PixInsight Drizzle Integration - Chaotic Nebula](https://chaoticnebula.com/pixinsight-drizzle-integration/)
- [LocalNormalization and Reference Image - Stirling Astrophoto](https://stirlingastrophoto.com/posts/localnormalization-and-reference-image/)
- [WBPP .xdrz files - PixInsight Forum](https://pixinsight.com/forum/index.php?threads/wbpp-2-5-what-are-xdrz-files.19109/)
- [Run Process Icons Programmatically - PixInsight Forum](https://pixinsight.com/forum/index.php?threads/run-process-icons-programmatically.13518/)
- [ESD Rejection - Adam Block Studios](https://www.adamblockstudios.com/articles/extreme-studentized-deviate-pixel-rejection-esd)
- [ESD Notes - toomanyhobbies](https://too.manyhobbies.com/2021/08/25/pixinsight-generalized-extreme-studentized-test-rejection-algorithm/)
- [Pre-processing Tutorial - Light Vortex Astronomy](https://www.lightvortexastronomy.com/tutorial-pre-processing-calibrating-and-stacking-images-in-pixinsight.html)
- [Drizzle Integration in PI 1.8.8 - Star Watcher](https://www.star-watcher.ch/image-processing/drizzle-integration-pix-insight-1-8-8/)
- [PCL DrizzleData Class Reference](https://pixinsight.com/developer/pcl/doc/html/classpcl_1_1DrizzleData.html)
- [AutoIntegrate Script - GitHub](https://github.com/jarmoruuth/AutoIntegrate)
- [AutoIntegrate Documentation](https://ruuth.xyz/AutoIntegrateInfo.html)
- [AutoIntegrate Forum - Local Normalization](https://forums.ruuth.xyz/t/outliers-rejection-local-normalization-not-run-as-default/95)
- [PixInsight PJSR Reference](https://pixinsight.com/developer/pjsr/index.html)
- [WBPP Guide - Utah Desert Remote](https://utahdesertremote.com/improve-your-astrophotography-with-weighted-batch-preprocessing/)
- [Cloudy Nights - Rejection Algorithms Discussion](https://www.cloudynights.com/forums/topic/697077-question-about-rejection-algorithms-in-pixinsight/)
- [FastIntegration Caution - Cloudy Nights](https://www.cloudynights.com/forums/topic/987211-pixinsight-fast-integration-perhaps-a-caution/)
