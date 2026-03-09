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

### Q12: AutoIntegrate script gap analysis
**Answer:** Build a focused script. AutoIntegrate has high gaps on 5 of 9 requirements (no template consumption, no multi-run comparison, no rejection maps, no atomic II+DI pairing). Its monolithic end-to-end architecture is a poor fit for a modular integration-stage tool. Full analysis in IMAGE_INTEGRATION_ANALYSIS.md section 8.

### Q13: Comparison report format and metrics
**Answer: CSV.** Structured output so additional tools can consume it. Capture all available properties per run. This script is a first-pass data capture tool, not the analysis tool itself. Start with known metrics:
- `medianNoiseReductionRK` -- median noise reduction
- `referenceSNRIncrementRK` / `averageSNRIncrementRK` -- SNR improvement
- `finalNoiseEstimateRK` -- final noise level
- `totalRejectedLowRK` / `totalRejectedHighRK` -- rejection counts
Excluded: `imageData` (per-input-image weights/rejection counts). With hundreds or thousands of input frames, this produces too much data relative to its value here. Frame-level quality assessment belongs upstream (SubframeSelector, pre-WBPP culling), not at integration time.

Additional metrics will be discovered through use. Open to suggestions with rationale.

### Q14: Template naming convention
**Answer: (A)** Use the process icon name directly. No translation or guessing -- 100% user-controlled. Users name their icons descriptively (e.g., "WSC", "ESD_relaxed", "NoRejection").

### Q15: Error handling for missing file associations
**Answer: (B)** Fail the entire filter group. This is an unexpected edge case that shouldn't occur in normal WBPP output. Failing loudly prevents silent data quality issues.

### Q16: Scope of DrizzleIntegration template pairing
**Answer:** Support a single DI template only. DI's primary value is spatial resolution enhancement, not rejection quality differentiation. Running DI for every II comparison run is overkill -- expensive with minimal new information for comparing rejection strategies. In practice, DI would be used only for a final chosen II configuration, not during the comparison phase.

---

## Remaining Open Questions

### Q17: Frame subset selection strategy for preview mode
When `maxFrames` is set, how should frames be selected?
- **(A)** First N files (alphabetical/filesystem order)
- **(B)** Random sample
- **(C)** Quality-sorted (if weight data is available from SubframeSelector, pick the best N)
- **(D)** Evenly spaced across the sorted file list (captures temporal spread)

Note: This affects whether preview results are representative of the full dataset. Random or evenly-spaced may give better statistical representation than first-N.
