# Problem Statement: PixInsight Integration Script

## The Problem

Astrophotography pre-processing with WBPP (Weighted Batch Preprocessing) in PixInsight runs on a memory-constrained VM and crashes during the ImageIntegration step. Recovery is possible by extracting the last ImageIntegration from the process container in the logs directory, but this is manual and tedious.

Beyond crash recovery, there is a deeper problem: **WBPP's automated rejection algorithm choice can reject real nebula signal**, producing suboptimal integration results. The user's last dataset had a rejection algorithm that rejected portions of the nebula itself. Tuning rejection requires experimentation -- trying different algorithms, sigma values, and normalization settings -- which WBPP does not make easy to iterate on.

## What WBPP Does Well

WBPP handles the full pipeline from raw frames to integrated masters:
- Bias/dark/flat calibration
- Cosmetic correction
- Debayering (OSC cameras)
- Subframe selection and weighting
- Star alignment and registration
- Local normalization
- **Image integration** (the step we want to decouple)
- Drizzle integration

Everything up to and including registration and local normalization works well. The intermediate outputs (registered `.xisf` files, `.xdrz` drizzle data, `.xnml` local normalization data) are saved to the `registered/` directory, organized into filter subdirectories.

## What We Want

A PixInsight JavaScript script that takes WBPP's registered output and performs **only the integration step** with full user control:

### Core Requirements

1. **Point at the `registered/` directory** and auto-discover all files grouped by filter (using WBPP's subdirectory naming convention with `FILTER-X` pattern).

2. **Apply saved process icon templates** for ImageIntegration. The user configures one or more ImageIntegration instances in the PixInsight GUI (setting rejection algorithm, sigma values, normalization mode, weighting, memory limits, etc.), saves them as process icons, and the script applies each template to every filter's file set. This enables rapid A/B/C comparison of different rejection strategies.

3. **Optionally apply DrizzleIntegration** using saved process icon templates. Since ImageIntegration writes rejection data into `.xdrz` files (overwriting previous data), each II+DI pair runs as an atomic operation: II runs, then DI runs immediately using the freshly-written rejection data, before the next II template overwrites it.

4. **Generate a comparison report** when multiple II templates are used. Capture the read-only output metrics (median noise reduction, SNR increment, total rejection percentages, per-image weights) and present them side-by-side so the user can make an informed choice about which rejection strategy produced the best result.

5. **Save all outputs** -- integrated masters, rejection maps, and drizzle results -- to an `integration/` directory alongside WBPP's existing `master/` directory, with clear naming that identifies the filter and template used.

### What the Script Does NOT Do

- No calibration, registration, or local normalization -- WBPP already did this
- No FastIntegration support
- No post-integration processing (stretching, color calibration, etc.)
- No GUI -- runs from script with parameters

## Why Not Just Use WBPP?

1. **Crashes**: Memory-constrained VM can't complete WBPP's integration step
2. **No iteration**: WBPP runs one integration with its chosen parameters; changing rejection settings means re-running the entire pipeline
3. **No comparison**: No easy way to compare results of different rejection algorithms side-by-side with quantitative metrics
4. **Signal rejection**: WBPP's automatic rejection choices can be too aggressive for nebula data; user wants to experiment with ESD, relaxed sigma values, and no-rejection baselines

## Why Not Just Run ImageIntegration Manually?

You can, but:
1. Manually adding 25+ files per filter, per run, across multiple filters is tedious
2. Keeping track of which `.xdrz` and `.xnml` files go with which `.xisf` files is error-prone
3. Running DrizzleIntegration immediately after each II (before the next II overwrites `.xdrz` files) requires discipline
4. No automated comparison metrics across runs
5. If you want to try 3 rejection algorithms across 4 filters, that's 12 manual integration setups + 12 drizzle setups

The script automates all of this into: configure your templates once, point at the directory, run, compare results.

## Technical Context

### Data Flow

```
WBPP (already complete)
  └─> registered/
        ├─> Light_..._FILTER-H_.../
        │     ├─ image1_r.xisf   (registered image)
        │     ├─ image1_r.xdrz   (drizzle data with alignment transforms)
        │     └─ image1_r.xnml   (local normalization data)
        ├─> Light_..._FILTER-O_.../
        │     └─ ...
        └─> Light_..._FILTER-S_.../
              └─ ...

Our Script
  └─> For each filter, for each II template:
        1. ImageIntegration (updates .xdrz with rejection data)
        2. DrizzleIntegration (uses updated .xdrz, optional)
        3. Capture metrics
  └─> integration/
        ├─ H_NoRejection.xisf
        ├─ H_NoRejection_rejLow.xisf
        ├─ H_NoRejection_rejHigh.xisf
        ├─ H_NoRejection_drizzle.xisf
        ├─ H_WSC.xisf
        ├─ H_WSC_rejLow.xisf
        ├─ H_WSC_rejHigh.xisf
        ├─ H_WSC_drizzle.xisf
        ├─ H_ESD.xisf
        ├─ ...
        └─ comparison_report.txt
```

### Key Constraint: .xdrz Overwriting

ImageIntegration writes rejection maps into the `.xdrz` files in-place. Running a second II with different rejection settings overwrites the first run's rejection data. This is why II+DI must be atomic pairs -- the drizzle step must consume the rejection data before it gets overwritten by the next II run.
