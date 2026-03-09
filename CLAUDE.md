# Project: PixInsight Image Integration Script

## What This Is

A PixInsight JavaScript (PJSR) script that resumes from WBPP's registered output and runs ImageIntegration (and optionally DrizzleIntegration) using user-supplied process icon templates. Enables rapid comparison of different rejection algorithms on the same dataset.

## Project Status

**Phase: Design complete, ready for implementation.** All architectural questions resolved.

## Key Documents

- `IMAGE_INTEGRATION_PROBLEM.md` -- Problem statement and motivation (why this script exists)
- `IMAGE_INTEGRATION_ANALYSIS.md` -- Technical analysis: WBPP directory structure, II/DI data flow, PJSR API formats, architecture, AutoIntegrate gap analysis
- `IMAGE_INTEGRATION_QUESTIONS.md` -- All 16 design questions with resolved answers

## Critical Design Decisions

1. **Language**: PJSR (PixInsight JavaScript Runtime). Script runs inside PixInsight.
2. **Process icon templates**: User pre-loads .xpsm in PixInsight, passes icon names to script. Script uses `ProcessInstance.fromIcon()` to load, overrides only the file list (`P.images`), preserves all other settings.
3. **Single DI template**: Only one DrizzleIntegration template supported. DI is for final output, not for comparing rejection strategies (too expensive, no diagnostic value for comparison).
4. **Atomic II+DI pairs**: II overwrites .xdrz rejection data in-place. DI must run immediately after its paired II, before the next II template overwrites the data.
5. **Output**: `integration/` directory as peer to WBPP's `master/`. Filenames use process icon name as suffix: `integration_H_WSC.xisf`.
6. **CSV report**: Aggregate metrics only (SNR, noise, rejection counts). No per-input-image data. This script captures data; analysis is done by other tools.
7. **Fail-fast**: Missing .xdrz/.xnml associations fail the entire filter group.
8. **Filter discovery**: Parse `FILTER-X` from WBPP subdirectory names (regex: `/FILTER-([^_]+)/`). No FITS header reading needed.

## User's Imaging Context

- Narrowband imaging (H, O, S filters) with a mono camera
- Runs WBPP on a memory-constrained VM that crashes during integration
- Datasets can have hundreds to thousands of input frames per filter
- Uses LocalNormalization (`.xnml` files always present in target workflow)
- Experienced enough to configure II process icons manually but wants automated batch application and comparison

## PJSR API Quick Reference

```javascript
// Load template, override file list, execute
let P = ProcessInstance.fromIcon("WSC");
P.images = [[true, "path.xisf", "path.xdrz", "path.xnml"], ...];
P.executeGlobal();

// Read-only outputs after execution
P.integrationImageId        // window ID of result
P.lowRejectionMapImageId    // window ID of low rejection map
P.highRejectionMapImageId   // window ID of high rejection map
P.finalNoiseEstimateRK      // noise estimate
P.medianNoiseReductionRK    // noise reduction factor
P.referenceSNRIncrementRK   // SNR improvement (reference)
P.averageSNRIncrementRK     // SNR improvement (average)
P.totalRejectedLowRK        // total low rejections
P.totalRejectedHighRK       // total high rejections

// DrizzleIntegration
let D = ProcessInstance.fromIcon("Drizzle2x");
D.inputData = [[true, "path.xdrz", "path.xnml"], ...];
D.executeGlobal();

// Save image windows
var win = ImageWindow.windowById(P.integrationImageId);
win.saveAs("/path/to/output.xisf", false, false, false, false);
```

## What NOT to Build

- No GUI (script with parameters only, for now)
- No FastIntegration
- No calibration/registration/normalization (WBPP does this)
- No post-integration processing (stretching, color calibration)
- No per-image quality assessment (that's SubframeSelector's job, upstream)
- No extending AutoIntegrate (architectural mismatch; see analysis doc section 8)
