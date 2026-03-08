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
    <registered images>.xisf
    <drizzle data>.xdrz
    <local normalization data>.xnml
  Master/
    masterLight-BINNING_1-FILTER_Ha-EXPTIME_300.xisf
    masterLight-BINNING_1-FILTER_OIII-EXPTIME_300.xisf
    ...
```

### File Naming Conventions

WBPP uses FITS header keywords (particularly `FILTER`) to organize files. Master file naming follows the pattern:

```
masterLight-BINNING_1-FILTER_Ha-EXPTIME_300.xisf
```

Registered image files retain their original names with registration suffixes. The filter identity is stored in the FITS header `FILTER` keyword.

### Associated Files

For each registered `.xisf` image, there may be:
- A `.xdrz` file (drizzle data) -- created during StarAlignment if "generate drizzle data" was enabled
- A `.xnml` file (local normalization data) -- created if LocalNormalization was run

The `.xdrz` and `.xnml` files share the same base filename as the registered image.

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

### Loading and Using Process Icons in Scripts

```javascript
// Load a process icon set (.xpsm file) -- requires it to already be loaded
// or loaded via startup script
let P = ProcessInstance.fromIcon("MyIntegrationTemplate");

// Modify the file list
P.images = [
   [true, "/path/to/registered_image1.xisf", "/path/to/drizzle1.xdrz", "/path/to/norm1.xnml"],
   [true, "/path/to/registered_image2.xisf", "/path/to/drizzle2.xdrz", "/path/to/norm2.xnml"],
];

// Execute
P.executeGlobal();

// Access result
var window = ImageWindow.windowById(P.integrationImageId);
```

### Loading .xpsm Files

Process icon sets are saved as `.xpsm` files. They can be loaded:
1. By double-clicking the file (opens PixInsight with icons loaded)
2. Via startup script in `PixInsight/etc/startup/`: `.open /path/to/icons.xpsm`
3. The icons are then available via `ProcessInstance.fromIcon("iconName")`

### The Recommended Approach: Drag-to-Script-Editor

The most reliable way to discover the exact property format for any process is:
1. Configure the process in the GUI with desired settings
2. Drag the process triangle (new instance icon) to the Script Editor
3. PixInsight auto-generates the exact JavaScript code with all properties

This is the authoritative way to determine the exact `images` array format for your version of PixInsight, since the array structure may have additional fields beyond `[enabled, path, drizzlePath, localNormPath]`.

---

## 5. Proposed Script Architecture

### Input
- Path to the "registered" directory
- One or more ImageIntegration process icon names (from a loaded .xpsm)
- One or more DrizzleIntegration process icon names (from a loaded .xpsm)

### Processing Steps

```
1. Scan registered directory for .xisf files
2. Read FILTER keyword from FITS headers to group by filter
3. For each filter group:
   a. Find associated .xdrz files (same base name)
   b. Find associated .xnml files (same base name)
   c. For each ImageIntegration template icon:
      i.   Load process instance from icon
      ii.  Set the images array with discovered files
      iii. Ensure "generate drizzle data" is enabled
      iv.  Execute ImageIntegration
      v.   Save/rename the output master
   d. For each DrizzleIntegration template icon:
      i.   Load process instance from icon
      ii.  Set the inputData array with .xdrz files
      iii. Execute DrizzleIntegration
      iv.  Save/rename the output
```

### Critical Design Decisions

1. **Multiple templates overwrite .xdrz files**: If running multiple ImageIntegration templates for the same filter, the second run will overwrite the rejection data from the first. Options:
   - **Option A**: Copy .xdrz files before each integration run (safest, allows parallel comparison)
   - **Option B**: Run ImageIntegration + DrizzleIntegration as paired atomic operations
   - **Option C**: Only support one ImageIntegration template per run (simplest)

2. **File list format**: The `images` array format should be verified by dragging a configured ImageIntegration to the Script Editor. Based on research, the format is:
   ```javascript
   [enabled, filePath, drizzlePath, localNormalizationPath]
   ```
   But there may be additional fields in newer versions.

3. **DrizzleIntegration file list**: Uses `inputData` property with drizzle file paths:
   ```javascript
   P.inputData = [
      [true, "/path/to/file1.xdrz"],
      [true, "/path/to/file2.xdrz"],
   ];
   ```

4. **FastIntegration**: PixInsight 1.8.9-2+ offers FastIntegration as a speed-optimized alternative. Consider supporting it as an option, but note:
   - It skips cosmetic correction by default
   - Uses a subset of frames for reference image selection
   - There have been reports of alignment artifacts (December 2025, Cloudy Nights)
   - For critical work, standard ImageIntegration remains more reliable

---

## 6. Local Normalization Considerations

When `.xnml` files are present:
- ImageIntegration's "Normalization for pixel rejection" should be set to **LocalNormalization**
- The `.xnml` file paths must be included in the `images` array
- This is typically the single most impactful setting for rejection quality
- The process icon template should already have this setting configured, but the script should validate/warn if `.xnml` files exist but the template doesn't use LocalNormalization mode

---

## 7. Reading FITS Headers in PJSR

To group files by filter, the script needs to read the `FILTER` keyword from FITS headers:

```javascript
var window = ImageWindow.open(filePath);
var keywords = window[0].keywords;
for (var i = 0; i < keywords.length; i++) {
   if (keywords[i].name == "FILTER") {
      var filterName = keywords[i].strippedValue;
      break;
   }
}
window[0].forceClose();
```

Note: Opening and closing windows just to read headers is expensive. Alternative approaches:
- Use `File` and parse XISF XML headers directly
- Use filename patterns if filter info is in filenames
- Read FITS headers without fully opening the image (if PJSR supports it)

---

## 8. Sources

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
- [PixInsight PJSR Reference](https://pixinsight.com/developer/pjsr/index.html)
- [WBPP Guide - Utah Desert Remote](https://utahdesertremote.com/improve-your-astrophotography-with-weighted-batch-preprocessing/)
- [Cloudy Nights - Rejection Algorithms Discussion](https://www.cloudynights.com/forums/topic/697077-question-about-rejection-algorithms-in-pixinsight/)
- [FastIntegration Caution - Cloudy Nights](https://www.cloudynights.com/forums/topic/987211-pixinsight-fast-integration-perhaps-a-caution/)
