# HDR Mode on ToupTek Camera (16-bit Range!) -- CloudyNights Forum Summary

**Source thread:** [CloudyNights -- HDR mode on Touptek Camera (16-bit range!)](https://www.cloudynights.com/forums/topic/900797-hdr-mode-on-touptek-camera-16-bit-range/)
(6 pages, ~129 replies, last reply April 8, 2025)

**Key contributors:** Scott_AstroSweden (23 posts), ciskje (18 posts), Tom62e (13 posts), IanCass (13 posts)

**Purpose of this summary:** Assess whether HDR mode on the ATR585M is worth using versus sticking with LCG/HCG.

---

## 1. What Is HDR Mode?

The Sony IMX585 sensor (used in the ToupTek ATR585M/C) is natively a **12-bit ADC** sensor that supports three readout modes:

| Mode | Bit Depth | Read Noise | Full Well | Notes |
|------|-----------|------------|-----------|-------|
| **LCG** (Low Conversion Gain) | 12-bit | ~1.91 e- | ~38.9 ke- | Standard mode, higher full well, higher read noise |
| **HCG** (High Conversion Gain) | 12-bit | ~0.5 e- | Lower (~13 ke-) | Low read noise, lower full well capacity |
| **HDR** (High Dynamic Range) | 16-bit output | ~0.64 e- (claimed) | ~46 ke- (QHY figure) | Dual-gain fusion of LCG + HCG |

HDR mode reads each pixel **twice** -- once with LCG circuitry and once with HCG circuitry -- and fuses them into a single 16-bit output. Sony calls this "Clear HDR." The goal is to combine the low read noise of HCG with the high full well capacity of LCG, theoretically yielding **14-15 stops of dynamic range** from a 12-bit sensor.

**Trade-off:** HDR mode halves the frame rate since each frame requires two readouts.

**ToupTek is the only astronomy camera vendor** that has implemented this HDR mode on the IMX585. Other manufacturers (e.g., QHY, ZWO) have not offered it beyond their own variations (QHY calls theirs "Linearity HDR").

---

## 2. Reported Problems (Chronological)

### Early Firmware (pre-v4.36)
- **Vertical line artifacts:** First test images in HDR mode showed prominent vertical lines (not debayer artifacts). Multiple users confirmed this. ToupTek acknowledged: *"We have stably reproduced the problem. Our engineers are solving it."*
- **Dark frame mismatch:** Darks taken in HDR mode did not properly calibrate lights taken with the same settings.

### Firmware v4.35-4.36
- HDR mode became selectable in NINA (LCG, HCG, and HDR options appeared).
- Some users reported **CRC errors** during firmware update process.
- A modified FPGA version (v4.8 beta) was sent to some users -- it fixed HDR mode but produced "weird gain (near LCG)."

### Firmware v4.47-4.49
- ToupTek released FPGA v4.49 specifically to address HDR mode issues on ATR585C/ATR585M.
- **Offset locked at 512:** ToupTek's R&D confirmed this is **by design** -- the offset is preset to an "optimal position" in HDR mode and user adjustments are ignored. This simplifies the LCG/HCG fusion but removes user control over black levels.
- **ADU values jumped dramatically** after update: HDR dark frames went from ~15 ADU (v4.36) to ~500 ADU (v4.49) in Bin1x1; from ~45 ADU to ~2049 ADU in Bin2x2.
- Cameras updated to FPGA 4.49 **must** be used with the matching driver (dated 2025-01-21 or later).

### Firmware v4.50+
- One user's camera shipped with v4.50, but it produced a **stripe artifact on the left edge**. Downgrading to the v4.49 driver (even though it was an older number) fixed this.
- **Linearity HDR still buggy:** Image headers showed incorrect gain and/or offset values. Camera required rebooting when switching between modes.
- Filter wheel firmware also implicated -- an internal IR LED stayed on, making subs look like severe light pollution until a filter wheel firmware update was applied.

### SharpCap Compatibility Issues
- Newer SharpCap versions (post-Nov 2024) produced **garbled images** in HDR mode.
- Sensor analysis gave **invalid results** -- full well capacity measured at 30 ke- vs. ToupTek's claimed 13 ke- at gain 100; bit depth incorrectly detected as 14-bit instead of 12-bit.
- SharpCap developer (Robin Glover) stated: *"I don't understand quite how the HDR mode on these cameras works, which is a shame -- I'd be more inclined to use it for imaging if the operation was well understood."*
- Rolling back to SharpCap 4.1.12711 and/or using the ASCOM driver (instead of native) improved results.

---

## 3. Bias and Flat Calibration Issues

This is one of the most significant practical problems discussed across the thread:

- **Bias frame gradients:** In LCG mode, bias frames look normal. Switching to HCG or HDR produces a "crazy gradient" across bias frames. In at least one case this was traced to a **defective USB cable** -- the very short exposure times saturated the USB bus.
- **Flat calibration failures:** Calibrated images actually looked **worse** than omitting flats entirely. Dust spots remained prominent even after flat calibration. Including or excluding bias frames made no difference.
- **Fixed offset complicates calibration:** The locked offset of 512 in HDR mode means traditional bias/dark subtraction workflows may not behave as expected, since the user cannot match the offset between calibration frames and lights.

---

## 4. Linearity Concerns

A critical discussion point for astrophotography:

- The IMX585 is a native **12-bit sensor**. HDR mode produces 16-bit output by digitally fusing two 12-bit readouts. The fusion algorithm is **not documented** by ToupTek or Sony in any publicly available material.
- Several users expressed concern that the HDR output may be **non-linear** -- i.e., the relationship between photon count and ADU value may not be proportional. Non-linearity would break standard calibration and stacking workflows.
- One forum member (referenced as "twoc") specifically requested linearity analysis, prompting another user (Scott_AstroSweden) to undertake a **5-hour coding project** to test linearity. The results were discussed on later pages, though the full analysis data was not indexed in search results.
- Community concern: *"Typically we want a raw output that has very little to zero digital alterations because that's what is best for astro image manipulating software."*

---

## 5. Community Consensus

### Arguments Against HDR Mode
- **No visible benefit over HCG for most targets:** Multiple users reported seeing no difference when comparing images from HCG vs. HDR mode. Some said HCG actually captured **better and fainter detail**.
- **Stacking solves the dynamic range problem:** *"HDR in this context just means DR above 14-bit. But you can stack 14-bit DR images and reach 16-bit pretty easily."*
- **Marketing gimmick concerns:** Some users called HDR mode a *"marketing gimmick that has no practical benefits"* for deep-sky astrophotography.
- **Pixel wells rarely saturate in deep-sky:** HDR makes sense for DSLRs, security cameras, and dashcams, but *"HDR may provide little to no benefit to extended objects in astrophotography, since pixel wells are usually kept very much below saturation."*
- **Firmware instability:** The mode has gone through multiple firmware revisions and is still not considered stable. Each firmware update requires matching driver versions, and mismatches cause new problems.
- **Undocumented processing:** The fusion algorithm is a black box. Without understanding exactly what processing is applied, it is difficult to trust the output for scientific/quantitative imaging.

### Arguments For HDR Mode
- **High-contrast objects:** HDR could be useful for targets like **M42 (Orion Nebula)** where you want to capture both the bright Trapezium core and faint outer nebulosity in a single exposure, avoiding the need for separate short/long exposure blending.
- **Theoretical dynamic range:** If working correctly, 14-15 stops of DR with sub-1e- read noise is impressive for a $599 camera.
- **Promising sensor analysis:** Some users (using ASCOM driver) reported nearly **16 stops of dynamic range** in SharpCap sensor analysis, calling ToupTek's engineers "impressive."
- **Eliminates need for dual-exposure HDR workflows:** If the camera handles LCG/HCG fusion in hardware, it saves the complexity of manually blending multiple exposure lengths in post-processing.

---

## 6. Assessment for ATR585M: HDR vs. LCG/HCG

### Recommendation from the Forum Community

**For most deep-sky imaging: stick with HCG mode.**

The reasoning:

1. **HCG at gain ~100** gives you ~0.5 e- read noise with well-understood, linear 12-bit output. Calibration (darks, flats, bias) works as expected.
2. **Stacking** dozens or hundreds of HCG frames naturally increases dynamic range and SNR beyond what a single HDR frame provides.
3. HDR mode's **locked offset, calibration difficulties, and unknown linearity** make it unreliable for standard astrophotography workflows.
4. HDR mode's firmware is **still maturing** -- each update introduces new quirks and requires matched driver versions.

### When HDR Might Be Worth Trying

- **Bright targets with extreme contrast** (M42 core, galactic centers) where you want to avoid the complexity of separate short/long exposure blending.
- **If ToupTek stabilizes the firmware** and third-party tools (SharpCap, NINA) fully support the mode with proper calibration.
- **If linearity is confirmed** through independent testing.

### Practical Steps If You Want to Experiment

1. Ensure your FPGA firmware and driver are a **matched pair** from ToupTek's latest release.
2. Update your filter wheel firmware as well.
3. Use the **ASCOM driver** rather than the native driver for better compatibility with analysis tools.
4. Take calibration frames (darks, flats) in HDR mode specifically -- **do not reuse** calibration frames from LCG/HCG modes.
5. Accept that offset is fixed at 512 and cannot be changed.
6. Compare your HDR results side-by-side with HCG results on the same target before committing to HDR for a full session.

---

## 7. Additional Resources

- [CloudyNights main thread (6 pages)](https://www.cloudynights.com/forums/topic/900797-hdr-mode-on-touptek-camera-16-bit-range/)
- [INDI Forum mirror of the discussion](https://indilib.org/forum/general/14083-hdr-mode-on-touptek-camera-16-bit-range.html)
- [SharpCap Forums -- Weird sensor analysis on ATR585C](https://forums.sharpcap.co.uk/viewtopic.php?t=8289)
- [SharpCap Forums -- IMX585 Firmware updates](https://forums.sharpcap.co.uk/viewtopic.php?t=8307)
- [SharpCap Forums -- Weird sensor analysis on ATR585M](https://forums.sharpcap.co.uk/viewtopic.php?t=8704)
- [CloudyNights -- NINA/ToupTek bias frame gradients](https://www.cloudynights.com/topic/922836-nina-touptek-drivers-gradients-in-bias-frames-and-final-image/)
- [Brian G Weber -- Troubleshooting ATR585M](https://blog.briangweber.com/mono-troubleshooting/)
- [AstroBin Forums -- ToupTek 585C offset issues](https://ssr.app.astrobin.com/forum/topic/151078/touptek-atr585c/touptek-585-c-offset-doesnt-work)
- [ToupTek ATR585M Official Page](https://touptek-astro.com/dso-cooled-cameras/ATR585M/)
- [ATR585M User Manual (PDF)](https://touptek-astro.com/dl_manual/ATR585M_en.pdf)
