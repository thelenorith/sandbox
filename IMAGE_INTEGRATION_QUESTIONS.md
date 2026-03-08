# Open Questions for Image Integration Script

Questions resolved from initial round are marked. Remaining open questions are at the bottom.

---

## Resolved Questions

### Q1: Multiple II templates and drizzle file overwriting
**Answer: (B)** Run each ImageIntegration + DrizzleIntegration as an atomic pair. We need the master light, don't care about intermediate data. Simplest approach since .xdrz gets overwritten anyway.

### Q2: Exact `images` array format
**Answer: Confirmed.** ImageIntegration `images` is a 4-element array: `[enabled, path, drizzlePath, localNormalizationDataPath]`. DrizzleIntegration `inputData` is a 3-element array: `[enabled, drizzlePath, localNormalizationDataPath]`. Full property dumps captured in IMAGE_INTEGRATION_ANALYSIS.md section 4.

### Q3: Are .xnml files always present?
**Answer:** In the target workflow, always present. If absent, it's a bespoke case. Either all files have .xnml or none do -- no mixed case within a run.

### Q4: Filter identification method
**Answer: (C)** WBPP produces subdirectories with filter in the name. Parse `FILTER-X` from directory names like `Light_BIN-1_..._FILTER-H_mono_READOUTM-...`. The filter value follows the `FILTER-` prefix (hyphen, not underscore). Cannot rely on leading/trailing underscore.

### Q5: Process icon loading mechanism
**Answer: (A)** Pre-load .xpsm in PixInsight before running script, pass icon names as parameters. UX may evolve later.

### Q6: Output naming and organization
**Answer:** `integration/` directory as peer to `master/`. Filenames like `integration_H_WSC.xisf`. Save rejection maps alongside.

### Q7: DrizzleIntegration always?
**Answer:** Optional. Can run II-only or II+DI.

### Q8: FastIntegration support
**Answer:** No.

### Q9: Reference image selection
**Answer:** Automatic is fine. Same algorithm against same dataset produces consistent reference.

### Q10: WBPP resume context
**Answer:** Primarily (A) -- replace WBPP's integration step. But also enables (C) shotgun approach: automate running many II templates to explore which rejection strategy nets the best result, with quantifiable comparison data.

### Q11: Memory constraints
**Answer:** Handled by the process icon template (memory settings are part of the saved configuration).

---

## Remaining Open Questions

### Q12: AutoIntegrate script gap analysis
**Status: In progress.** Researching what AutoIntegrate.js can and cannot do relative to our requirements. Need to determine if it's better to use/extend AutoIntegrate or build a focused script.

### Q13: Comparison report format and metrics
When running multiple II templates, the script captures read-only output properties after each run. Available metrics include:
- `medianNoiseReductionRK` -- median noise reduction
- `referenceSNRIncrementRK` / `averageSNRIncrementRK` -- SNR improvement
- `finalNoiseEstimateRK` -- final noise level
- `totalRejectedLowRK` / `totalRejectedHighRK` -- rejection counts
- `imageData` -- per-image weights and rejection counts

**Question:** What format do you want the comparison report in? Options:
- **(A)** Plain text table written to a `.txt` file
- **(B)** Console output only (visible in PixInsight's Process Console)
- **(C)** Both
- **(D)** Something else (CSV, HTML)?

Are there additional metrics beyond the above that you'd want captured?

### Q14: Template naming convention
The script needs to derive an output filename suffix from each process icon template (e.g., `H_WSC.xisf` where `WSC` = Winsorized Sigma Clipping). Options:
- **(A)** Use the process icon name directly (user names their icons descriptively: "WSC", "ESD_relaxed", "NoRejection")
- **(B)** Auto-detect the rejection algorithm from the template properties and generate an abbreviation
- **(C)** User provides a mapping of icon names to output suffixes

### Q15: Error handling for missing file associations
If a `.xisf` file exists but its corresponding `.xdrz` or `.xnml` is missing:
- **(A)** Skip that file with a warning
- **(B)** Fail the entire filter group
- **(C)** Include the file without drizzle/LN data (pass empty strings)

### Q16: Scope of DrizzleIntegration template pairing
When multiple II templates and multiple DI templates are specified, how should they be paired?
- **(A)** Every II template paired with every DI template (cartesian product: 3 II x 2 DI = 6 runs per filter)
- **(B)** Pair II and DI templates by position (1st II with 1st DI, 2nd II with 2nd DI)
- **(C)** All II templates use the same single DI template
- **(D)** User specifies explicit pairings
