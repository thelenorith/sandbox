# Open Questions for Image Integration Script

These questions need answers before or during implementation. They are ordered by priority.

---

## Critical -- Blocks Design

### Q1: Multiple ImageIntegration templates and drizzle file overwriting

When running multiple ImageIntegration templates (e.g., one with Winsorized Sigma Clipping, one with ESD, one with no rejection), each run **overwrites** the `.xdrz` files with its own rejection data. This means:
- Only the last ImageIntegration run's rejection data survives for DrizzleIntegration
- To compare drizzle results across rejection algorithms, we'd need to copy `.xdrz` files between runs

**Question**: Do you want the script to:
- **(A)** Back up `.xdrz` files before each ImageIntegration run and restore them for paired DrizzleIntegration (most flexible, more disk I/O)
- **(B)** Run each ImageIntegration + DrizzleIntegration as an atomic pair (simpler, but forces 1:1 pairing)
- **(C)** Only run one ImageIntegration template per execution, with DrizzleIntegration after (simplest)
- **(D)** Something else?

### Q2: Exact `images` array format for your PixInsight version

The `images` array format for ImageIntegration appears to be `[enabled, filePath, drizzlePath, localNormPath]` but may have additional fields in newer versions of PixInsight.

**Action needed**: In PixInsight, configure an ImageIntegration instance with a few files (including drizzle and local norm paths), then drag the process triangle to the Script Editor. Paste the generated code (specifically the `P.images = [...]` block) so we can see the exact format. Same for DrizzleIntegration's `P.inputData`.

### Q3: Are the .xnml (LocalNormalization) files always present?

Does your WBPP workflow always produce `.xnml` files, or is LocalNormalization optional/configurable? The script needs to know whether to:
- Always expect and require `.xnml` files
- Optionally use them if present
- Handle mixed cases (some filters with, some without)

---

## Important -- Affects Implementation

### Q4: Filter identification method

How should the script identify which filter each registered image belongs to? Options:
- **(A)** Read the `FILTER` FITS keyword from each `.xisf` file header (most robust, but slower -- requires opening each file)
- **(B)** Parse filter name from the filename (faster, but depends on naming convention)
- **(C)** Expect subdirectories per filter within the registered directory (e.g., `registered/Ha/`, `registered/OIII/`)
- **(D)** User provides a mapping or the directory only contains one filter

What does your WBPP registered directory actually look like? Are files in a flat directory with filter info in the filename/header, or organized into subdirectories?

### Q5: Process icon loading mechanism

How do you want to specify process icons to the script?
- **(A)** Pre-load an `.xpsm` file in PixInsight before running the script, then pass icon names as parameters
- **(B)** Have the script load an `.xpsm` file itself (path provided as parameter)
- **(C)** Inline all settings in the script (no process icons, just hardcoded parameter sets)
- **(D)** Some combination

### Q6: Output naming and organization

When the script produces integrated masters, how should they be named/organized?
- Should outputs go into a subdirectory (e.g., `Integration/`)?
- Naming pattern? e.g., `integration_Ha_WSC.xisf` (filter + rejection algo abbreviation)?
- Should the script also save rejection maps and other diagnostic outputs?

### Q7: DrizzleIntegration -- do you always want it?

Should DrizzleIntegration always run after ImageIntegration, or should it be optional? Some users prefer the non-drizzled integration for certain use cases.

---

## Nice to Know -- Can Defer

### Q8: FastIntegration support

PixInsight 1.8.9-2+ includes FastIntegration as a faster alternative to ImageIntegration. Do you want the script to support FastIntegration process icons as well? Note: there have been reports of artifacts with FastIntegration (star doubling, alignment issues).

### Q9: Reference image selection

ImageIntegration selects a reference image automatically (typically the one with highest weight). Do you want the script to allow specifying a reference image, or always let the process icon template handle this?

### Q10: WBPP resume context

You mentioned resuming WBPP from the last ImageIntegration in the process container saved in the logs directory. Is the script we're building meant to:
- **(A)** Completely replace WBPP's integration step (run independently on registered output)
- **(B)** Serve as an alternative/recovery path when WBPP crashes during integration
- **(C)** Both -- flexible enough for either use case

### Q11: Memory constraints

Since the VM is memory-constrained (causing WBPP crashes), should the script include any memory management strategies?
- Process one filter at a time (rather than loading all filters)
- Force garbage collection between integrations
- Any PixInsight-specific memory settings to configure?

### Q12: Existing AutoIntegrate script

The AutoIntegrate.js script (by Jarmo Ruuth, https://github.com/jarmoruuth/AutoIntegrate) already handles much of this workflow. Have you tried it? Would it be better to use/extend AutoIntegrate rather than building from scratch, or does it not meet your needs?
