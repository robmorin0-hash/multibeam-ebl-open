# Stage A Prototype Build Manual

**Companion document to Morin (2026) v5 — Multi-Beam Direct-Write Electron Lithography**
*Edmonton, AB · May 2026 · v1*

---

This manual is the hands-on, bench-level companion to the v4 Stage A specification
(`v4_stage_A_prototype.md`) and the v5 preprint. It tells someone in a lab how to
physically take the BOM and turn it into a 1–4 beam validator of the v4/v5
architecture, in 18 weeks of build time plus an integrated test campaign of 6
experiments.

This is not a generic EBL build guide. Every choice in this manual is traceable
to one of the v4 subsystem specifications: the cryogenic column
(`v4_cryocolumn.md`), the photonic data path (`v4_datapath.md`), the blanker
(`v4_blanker.md`), the source-and-registration loop
(`v4_source_and_registration.md`), the wafer-thermal subsystem
(`v4_wafer_thermal.md`), and the resist outgassing subsystem
(`v4_resist_outgassing.md`).

---

## 1. What you're building

**Stage A is the 1–4 beam validator of the v5 architecture.**
Capital cost: $600 k (hardware + 18 months engineer labour, per v4 §BOM).
Build time: 18 weeks from parts delivery to first electron beam on a fluorescent
screen, then a 30-week integrated test campaign that exercises six independent
validation experiments.

What Stage A is *for*:

- Prove that the cryogenic 77 K column actually works at single-beam scale —
  that YBCO planar Helmholtz coils deflect a 50 kV electron beam linearly,
  with sub-10 μs settling, and that AC losses fit the predicted ~0.5 W budget.
- Prove the Meissner shield attenuates a switched coil field by ≥ 80 dB at
  20 μm distance, using a second (neighbour) beam as the probe.
- Prove the cryo-CMOS 16-bit DAC at 77 K closes the loop end-to-end from an
  off-the-shelf SFP+ optical TX to a YBCO coil current, with INL ≤ 1 LSB,
  DNL ≤ 0.5 LSB, and < 10 μs settling.
- Prove BSE registration loop closure: scan the beam over a fiducial wafer,
  read backscattered electrons through an El-Mul detector, run a feedback loop
  that holds the beam to < 2 nm RMS over 1 mm of field.
- Prove cryosorption pump-down: expose an HSQ-coated wafer, watch the residual
  gas analyser spectrum, verify the cold column captures ≥ 50 % of the
  outgassing burst on first impact.
- Prove the wafer chuck can hold ±50 mK under a 250 mW scaled-down beam
  deposition load.

What Stage A is *not* for: it does not validate the 10⁶-beam aggregate
performance (that's Stage B, $5 M), it does not validate the 50 Tbps full
photonic transport (Stage B), it does not produce production-grade wafers
(Stage C/D), and it does not measure throughput (no throughput is meaningful
with 1–4 beams).

If Stage A passes all six tests, the v4/v5 architecture is empirically
de-risked, the v5 software stack has working hardware to bring up against, and
the program is ready for the Stage B (16–64 beam) parallel-column build at
$3–5 M.

---

## 2. Physical layout — the bench

The whole tool fits on a single optical bench. The dimensions, isolation, and
layout below are minimum-acceptable; if you have a bigger optical lab, use it.

**Bench:**

- Newport (or equivalent) sealed honeycomb optical-flat granite bench,
  1.5 m × 1.5 m × 0.30 m. Granite (not steel) because vibration response is
  flatter to high frequency, which matters for the BSE registration loop.
- Mass: ~600 kg. Floor must support 800 kg/m² point load. Verify with your
  building engineer before delivery; granite slabs have broken garage-style
  raised floors before.
- Four pneumatic isolators (Newport S-2000 or Thorlabs PWA075) under each
  corner. Self-levelling air bladders, ~0.5 Hz isolation corner, > 30 dB
  isolation above 5 Hz.
- **Vibration target: < 5 nm RMS at the wafer plane** in the 1 Hz – 10 kHz
  band. Verify with a Polytec or Bruker laser-Doppler vibrometer before any
  electron-column work. The cryocooler compressor must be off-bench, on a
  separate vibration-isolated pad on the floor, with the He hose looped to
  decouple the residual 50 / 60 Hz compressor harmonics.

**Layout (top-down, Figure 1):**

The UHV chamber sits at the bench centre, with the cryostat stacked above it.
The CFE electron gun mounts as a side flange on the upper-left port; the BSE
detector mirrors it on the upper-right port. The wafer load-lock is back-top,
the fiber feedthrough is back-top-right, and the turbo + ion pump stack hangs
underneath the chamber, off the bottom port. The ZMI interferometer head sits
external, on the lower-right of the bench, looking into a viewport on the lower
chamber wall. The 19" control rack lives off-bench (right side, on its own
caster frame); a single armoured fiber bundle runs from the rack into the
chamber's optical feedthrough.

![Figure 1. Bench top-down layout](build_fig1_bench.png)

---

## 3. The vacuum chamber stack

**Chamber.** Off-the-shelf 8" CF UHV chamber, Pfeiffer or Kurt J. Lesker
(316L stainless, electropolished interior, helium-leak-tested to 1 × 10⁻⁹
Torr·L/s at the vendor). Internal volume ~12 L. Six CF ports plus the top and
bottom mating flanges:

| Port | Size | Function |
|---|---|---|
| Top (axis) | 8" CF | Cryostat cold-finger entry (custom bellows + 8" CF flange) |
| Bottom (axis) | 6" CF | Pumping stack (turbo + ion pump) |
| Side, upper-left | 4.5" CF | CFE source gun |
| Side, upper-right | 4.5" CF | BSE detector |
| Side, lower-right | 2.75" CF | Viewport (ZMI interferometer read-through) |
| Side, back | 4.5" CF | Wafer load-lock gate valve |
| Side, back-upper | 2.75" CF | Optical fiber feedthrough (Accu-Glass 32-fiber) |
| Side, lower-left | 2.75" CF | Electrical feedthrough (HV + thermocouples) |

**Bake-out heaters.** Tape heaters (200 °C max) on every external CF flange
plus the chamber body. Thermocouples (K-type) at the flange centres and on the
chamber body at top, middle, and bottom. A small control unit (e.g. Watlow
EZ-Zone PM, ~$500) handles the ramp profile.

**Pumping sequence (from atmosphere to UHV base):**

1. Scroll/diaphragm roughing pump (Edwards nXDS-10i or Pfeiffer HiScroll 6).
   Pumps chamber from atmosphere to ~5 × 10⁻³ Torr in ~10 minutes. Oil-free —
   critical, no hydrocarbons in a UHV system.
2. Turbomolecular pump (Pfeiffer HiPace 80 or HiPace 300, magnetically
   levitated rotor preferred for vibration). Pumps to ~5 × 10⁻⁸ Torr in
   ~2 hours. Backing line connects to the roughing pump.
3. Ion pump (Gamma Vacuum 75 L/s or Agilent VacIon Plus 75). Takes over after
   bake-out; pumps to base pressure of ~5 × 10⁻¹⁰ Torr indefinitely. No moving
   parts in the high-vacuum regime, no vibration contribution.

The turbo runs continuously during operation; the ion pump is for true UHV
hold. A residual gas analyser (RGA — Stanford Research Systems RGA-100, $6 k)
sits on a 2.75" CF tee in the pumping line for diagnostics and for the
cryosorption test in §11.

**Assembly sequence — chamber:**

1. **Clean** every CF flange face. Acetone + IPA + lint-free wipe, followed by
   a final wipe with vacuum-grade methanol. Wear powder-free nitrile gloves
   from this point onward. Once the chamber interior is exposed to filtered
   lab air, *do not touch anything* with bare skin.
2. **Assemble** the chamber on a clean, level work surface. Use new copper
   gaskets at every CF joint (never reuse). Torque CF bolts in a star pattern,
   three passes: 25 %, 75 %, 100 % of the spec value (typically 12 ft-lb for
   8" CF, 7 ft-lb for 4.5" CF, 4 ft-lb for 2.75" CF).
3. **Helium-leak test.** Connect a helium leak detector (Pfeiffer ASM 340 or
   equivalent) to the foreline of the turbo, pull rough vacuum, and bag-spray
   each flange with helium for 60 seconds. Reject any flange showing > 1 × 10⁻⁹
   Torr·L/s. Plan on re-doing at least one flange — fresh-bolted CFs sometimes
   need a quarter-turn after the first pump-down.
4. **Bake.** 120 °C for 48 hours minimum, all heaters on, ion pump valved off
   (it does not like the bake heat). Continuous turbomolecular pumping
   throughout. Bake limits are set by the *coolest* component in the chamber:
   the YBCO coil assembly cannot exceed 80 °C, so bake the empty chamber to
   120 °C first, then re-introduce the cold-finger assembly under positive
   N₂ purge before the next pump-down (see §5).

After bake and cooldown, the base pressure should be ≤ 1 × 10⁻⁹ Torr without
the ion pump, and ≤ 5 × 10⁻¹⁰ Torr with the ion pump on. If you are above
those numbers, leak-test again before proceeding to the cryostat install.

---

## 4. The cryogenic stack (above the chamber)

**Pulse-tube cold head.** Cryomech PT-90 (single-stage, 25–30 W at 77 K,
~$30 k as of 2026). Pulse-tube is non-negotiable for an EBL build —
Gifford-McMahon coolers produce 5–50 μm displacement at the cold head from the
moving displacer at 1–2 Hz, which couples *directly* into beam-placement error
at the wafer. Pulse-tube coolers have no moving displacer at the cold head and
deliver < 100 nm residual displacement (measured). This is the single most
important component-selection decision in the build.

**He compressor.** Cryomech CP-289, water-cooled. Sits on the floor, **off the
bench**, on its own vibration-isolated pad. Connect to the cold head via the
supplied flexible braided high-pressure He hoses (typical 3 m length). The
hose's flex is what isolates compressor harmonics from the cold head. Tie the
hose to a wall standoff midway to break the direct mechanical path further.

**Cold-finger drop into the chamber.** The PT-90 cold head body mounts to an
8" CF flange on the chamber top via a custom thin-wall stainless bellows
(~50 mm length). The bellows decouples cold-head residual vibration from the
chamber body and accommodates thermal contraction of the cold finger
(~0.3 mm over 77 K – 295 K). The cold finger itself is a 100 mm OFHC copper
rod, ~25 mm diameter, machined to a flat instrument-grade mounting platform
at its bottom (the "cold platform"), with M3 tapped holes on a 5 mm grid for
mounting the YBCO coil, Meissner shield, DAC, and photodiode.

**Thermal mass.** A 2 kg OFHC copper block bolts to the cold-finger platform,
with thermometry holes (Cernox or Lake Shore PT-100) drilled 10 mm into the
side. This block damps the temperature transients of pulsed AC loss in the
coils — without it, an AC-loss burst would swing the coil temperature by
~1 K, which is enough to walk the YBCO Tc margin during long writes.

**Heat-strap to first stage.** A 6 mm × 30 mm braided OFHC copper strap
(McMaster-Carr 1278K34 or equivalent annealed) bonds the second-stage cold
platform to the first-stage 150 K shield, which intercepts radiation from the
warm chamber walls. The first-stage shield itself is a thin (0.5 mm) Al cup
~50 mm OD that surrounds the cold platform, with a 10 mm clearance hole for
the beam to pass through.

**MLI wrap.** 30-layer aluminised Mylar / Dacron-net blanket (Ruag or
Aerospace Fabrication & Materials, ~$2 k for a custom-cut blanket). Wraps the
*warm side only* of the cold finger — that is, from the chamber top flange
down to the first-stage shield, never below. Effective emissivity ~5 × 10⁻⁴.
The radiative load to 77 K through the MLI is ~2 mW (v4 §X.3); without MLI it
would be ~1 W.

**YBCO coil + Meissner shield assembly.** Patterned on a 4" sapphire wafer at
SuperPower or the University of Alberta nanoFab facility (or equivalent
academic clean room: NRC-NINT, UWaterloo QNC, Cornell CNF). The wafer carries
the YBCO planar Helmholtz coil pair (one on each face, 30-turn spiral, 8 μm
mean radius, 2 μm trace width) and an adjacent Meissner shield strip
(10 μm thick YBCO film, 200 × 200 μm patch) sitting 20 μm from the coil. Both
are deposited by PLD or MOCVD followed by ion-mill patterning. Sapphire is
chosen for its closely-matched thermal expansion to YBCO and for its
electrical insulation.

The assembly mounts to the cold platform via a non-magnetic stainless steel
(316LN) flexure clamp, with kapton thermal-interface tape between the sapphire
and the platform. Current leads are 100 μm Au wires bonded to the YBCO pads
and routed up to the cryo-CMOS DAC chip on the same platform.

**Cryo-CMOS DAC.** Imec or Fraunhofer IPMS engineering-sample 16-bit cryo
current DAC, ~$10 k for a single packaged die. It sits on a 5 × 5 mm Al₂O₃
interposer with gold wire-bonds to the YBCO coil leads (output side) and to
the photodiode (input side). The DAC's supply rails (1.2 V and 3.3 V) come
in on phosphor-bronze hookup wire from a small low-dropout regulator board on
the warm side, fed through the electrical CF feedthrough.

The interposer mounts to the cold platform with a thin (0.2 mm) layer of
Apiezon N grease, which preserves thermal contact through cool-down cycles.

**Cryo-qualified InP photodiode.** Hamamatsu G12180-series (cryo-rated) or
equivalent. Sits adjacent to the DAC, connected by a short
(few-cm) cryo-rated SMA cable. The photodiode itself receives 1310 nm or
1550 nm light from the photonic data path (§7) via a polished-end single-mode
fiber pigtail.

![Figure 2. Vacuum chamber cross-section + cold-finger stack](build_fig2_chamber.png)

---

## 5. The electron column

The electron column is deliberately minimal in Stage A: one source, one
condenser lens, one HTS deflection coil. No multi-stage demagnification, no
crossover optics. Stage A is not trying to be a production EBL tool — it is
trying to test the HTS deflection scheme with the smallest set of confounding
variables.

**Source gun.** FEI / Thermo Fisher single-tip cold-field-emitter electron
gun, off-the-shelf module (~$50 k as of 2026). 50 kV acceleration, 5 nA
emission current at the tip aperture, ~0.3 eV energy spread, ~10⁹ A/m²/sr/V
reduced brightness. The gun is a self-contained CF-mountable module — it
includes its own Wehnelt, extractor, anode, and gun-vacuum getter pump (the
gun's internal pressure is held at ~10⁻¹¹ Torr by a small ion pump cell built
into the gun body, independent of the chamber).

For Stage A you can also dual-source as a "dual-tip Wehnelt" assembly: a
single CFE module modified to host two tips (5–10 mm apart) so that one tip
serves as the primary beam and the second as the neighbour-beam crosstalk
probe in test 2 (Meissner shield attenuation). This is a wiring-only
modification at the vendor, ~$5 k extra. Strongly recommended.

**Source mount.** The gun bolts to the upper-left 4.5" CF port via a
kinematic three-point picomotor (New Focus 8302) mount. Picomotors give 30 nm
incremental travel and ~10 mm coarse range — enough to walk the beam axis
across the column's full aperture during alignment. *Do not skip the
kinematic mount.* A fixed flange-mount gun will be 100 μm to 1 mm off-axis
out of the box, which is hopeless for any kind of beam-on-coil alignment.

**Condenser optics.** A single magnetic lens (off-the-shelf scanning-electron-
microscope condenser, e.g. Spectroscopy Instruments KE-1100, ~$15 k), mounted
inline between the gun and the cold finger. It is just a solenoid in a soft-
iron pole-piece housing, driven by a 0–5 A current source from the warm side
through the electrical CF feedthrough. Its job is to bring the beam to a
~1 μm waist at the YBCO coil plane.

**HTS deflection coil.** As described in §4 — hangs from the cold finger, in
the beam path ~50 mm below the gun, ~50 mm above the wafer.

**Beam path:**

```
   CFE gun (50 kV, side-mounted, kinematic picomotor)
         │
         ▼ (45° miter into chamber axis)
   condenser magnetic lens (single solenoid, warm)
         │
         ▼
   YBCO Helmholtz planar coil pair (77 K, on cold finger)
         │
         ▼ (deflected beam, ±2 mrad swing)
   ~50 mm drift, UHV
         │
         ▼
   fiducial wafer or HSQ resist (295 K, on piezo stage)
```

The Stage A column has no aperture stops, no blanker, and no demagnification.
Beam current arriving at the wafer is full source current (~5 nA),
spot size at the wafer is ~1–5 μm (limited by the simple optics, not by the
underlying source brightness). That is fine — Stage A is not measuring
ultimate resolution. It is measuring the deflection physics.

![Figure 3. Stage A beam-path block diagram](build_fig3_beampath.png)

---

## 6. The wafer stage

**Stage.** 6-DOF piezo stage from Physik Instrumente (PI N-664 or N-731,
~$50 k class). Travel range 100 μm × 100 μm in X-Y, 10 μm in Z, sub-nm
position resolution, 100 Hz closed-loop bandwidth. The 6 DOF (X, Y, Z, θx,
θy, θz) lets you correct chuck tip/tilt and rotation as part of the
registration loop, not just lateral translation.

For Stage A's 1 mm field, you only ever scan with the deflection coil — the
piezo stage is for *positioning the wafer under the column*, not for raster
scanning. It moves between dies, not within a die.

**Chuck.** Bare aluminium disc, 100 mm OD × 15 mm thick, with a 50 mm centre
recess to hold a 4" silicon wafer. A backside He gas line (~5 Torr) supplied
through a flexible Teflon tube provides thermal contact between the wafer
backside and the chuck. The chuck is bolted to the top of the PI stage with
non-magnetic Ti screws (steel screws are out of the question — too close to
the BSE detector).

Stage A doesn't need the full v4 AlN chuck + Galden microchannel + 36-zone TEC
trim. That comes later, in Stage B/C, when the beam thermal load demands it.
At 1–4 beams the chuck dissipation is ~5 mW — passive conduction to the
aluminium chuck is fine.

**ZMI interferometer.** Zygo ZMI-2000 or ZMI-4000 series ($25 k for a
two-axis head, plus optics). The laser head sits external on the bench (cold
zone), the beam goes through the lower-right viewport into the chamber, and
two retroreflector cube corners are bonded to the stage with cryo-rated epoxy
(Stycast 2850 FT). Two-axis (X, Y) position resolution: 0.1 nm. Sample rate:
100 kHz. This is the "ground truth" for the registration loop in test 4 — the
BSE registration result is benchmarked against the ZMI.

**BSE detector.** El-Mul Technologies SE/BSE annular detector ($30 k),
mounted on the upper-right CF port, with its annular collection element ~5 mm
above the wafer surface, on-axis with the beam. The annular geometry lets the
incoming primary beam pass through the centre while collecting backscattered
electrons on the surrounding silicon detector tile. Output: a ±5 V analog
signal, fed via a coax CF feedthrough to a fast ADC (AlazarTech ATS9462, ~16
bits, 180 MS/s) in the control rack.

The BSE detector is critical for *both* test 4 (registration loop) and for
column alignment in §11 — without BSE imaging you have no way to find the
fiducial mark or to confirm the beam landed where you sent it.

---

## 7. The photonic data path

**Pattern source (warm side).** A workstation in the control rack runs the
v5 GDS-II → blanker-schedule pattern compiler. Output is a single 10 Gbps
serial stream (sufficient for a 1–4 beam test) over an SFP+ optical
transceiver (Cisco SFP-10G-LR, $200) feeding a single-mode 1310 nm fiber.

**Vacuum feedthrough.** Accu-Glass Products single-fiber CF feedthrough on a
2.75" CF flange (~$2 k). Bake-rated to 200 °C, hermeticity ≤ 1 × 10⁻¹⁰
Torr·L/s. The fiber is polished SMF-28 (Corning, $200/m), Kapton-jacketed on
the vacuum side. A short (~30 cm) pigtail on the vacuum side terminates at an
FC/APC bulkhead on the warm shield, from which another short polished-end
fiber pigtail drops down to the cryo photodiode on the cold platform.

**Cryo photodiode.** Hamamatsu G12180 series InP photodiode ($5 k),
cryo-qualified at 77 K. Responsivity at 1310 nm: ~1 A/W (slightly improved at
77 K vs 295 K due to reduced dark current). The photodiode mounts on the
cold platform with a 0.2 mm layer of Apiezon N grease for thermal contact,
and a small focusing lens (Thorlabs C220TME-C, $200) couples the fiber output
onto the active area.

**Pattern flow:**

```
Warm side                           Cold side
─────────                           ─────────
GDS-II  ──▶  v5 compiler  ──▶  SFP+ TX  ──▶  ──fiber──▶  PD (77 K)
                                                           │
                                                           ▼
                                                   TIA / level shift
                                                           │
                                                           ▼
                                                   cryo-CMOS DAC (16 b)
                                                           │
                                                           ▼
                                                   YBCO Helmholtz coil
```

This is the photonic data path *in miniature*. Stage A runs one fiber and one
photodiode. Stage B scales it to 32 fibers × 96 wavelengths × 200 Gbps
(v4_datapath.md §7.3). The architectural pattern is the same; only the count
scales.

---

## 8. Control electronics rack

The 19" rack lives off-bench (on casters, on its own footprint to the right
of the bench), 1.5 m tall, with cable management for the bench-side
penetrations.

| Slot | Component | Notes |
|---|---|---|
| Top | Pattern streamer workstation | Linux box, 64 GB RAM, NVMe scratch; runs v5 compiler + GUI |
| | FPGA evaluation board | Xilinx Versal Premium or Alveo U200; runs the L1–L4 control firmware. Connects to PD/DAC supervisor lines via a custom mezzanine. |
| | 50 kV HVPS | Spellman SR50PN (negative polarity, 50 kV / 5 mA) — drives the gun cathode bias. ~$10 k. |
| | Cryocooler control + thermometry | Cryomech CPA-1110 controller (compressor command); Lake Shore Model 336 temperature controller (Cernox + heater channels). |
| | Vacuum control | Pfeiffer DCU + TPG-366 gauge controller — turbo, valves, RGA, ion pump. |
| | DAQ | AlazarTech ATS9462 for BSE; PI E-518 for stage; ZMI controller. |
| Bottom | UPS | 3 kVA online double-conversion. Mandatory — an unplanned shutdown of the cryocooler mid-cool-down loses 24 hours. |

Two long bundles run from rack to bench:

1. **Signal bundle:** fiber (pattern data, single SMF), coax × ~4 (BSE, ZMI,
   stage encoder), and DC power for the warm electronics (condenser lens
   driver, thermometry).
2. **HV bundle:** 50 kV shielded coax (Spellman to gun cathode), kept
   separate from the signal bundle by ≥ 30 cm.

---

## 9. Assembly sequence (chronological)

The build proceeds in roughly weekly milestones. Some weeks parallelise
(two engineers, one on optics and one on cryo); the timeline below assumes a
sequential one-engineer build for clarity. With two engineers, compress to
12–14 weeks.

![Figure 4. Stage A build Gantt chart](build_fig4_gantt.png)

**Day 0 (parts arrive).** Inventory every line item against the BOM (§12).
Quarantine any component with shipping damage. Critical — there is a single
PT-90 in this build with no spare, so a damaged cold head means a 6-month
backorder from Cryomech. Photograph everything as-received.

**Week 1: Bench setup.** Receive and install the granite bench and the four
pneumatic isolators. Level the bench (laser level, 4-corner method). Run a
vibration sweep with the LDV — confirm < 5 nm RMS floor before any chamber
work. Set up the cleanroom-style enclosure (HEPA-filtered air curtain, ISO
class 6 equivalent, ~$3 k for a fan-filter unit) over the chamber footprint.

**Week 2: Vacuum assembly + leak test.** Per §3. Empty chamber, all flanges
installed, copper gaskets fresh, helium-leak-tested to ≤ 1 × 10⁻⁹ Torr·L/s
on every joint. Cycle once to verify, no overnight pressure rise above
2 × 10⁻⁸ Torr without the ion pump.

**Weeks 3–4: Bake-out + pump-down.** 120 °C, 48 h continuous, then cool over
24 h, then ion-pump ignition. Verify ≤ 5 × 10⁻¹⁰ Torr base. Run an RGA
spectrum to confirm dominant peaks are H₂ (mass 2) and H₂O (mass 18); any
mass 28 (CO/N₂) signal more than ~10 % of H₂ suggests a virtual leak or a
residual hydrocarbon — re-clean.

**Week 5: Install source gun + cold finger.** Vent the chamber under dry N₂
(grade 5), install the CFE gun on the upper-left port via the picomotor
kinematic mount, install the cold-finger assembly via the top 8" CF and
bellows. The cold finger goes in *empty* — coil/DAC/photodiode are bolted to
the cold platform on the bench, then the whole platform-loaded cold finger
drops in as a unit. Re-pump and re-bake at the lowered 80 °C ceiling.

**Weeks 6–8: HTS coil + cryo-CMOS DAC + wiring.** This is the most
finicky phase of the build. Bring the cold-finger payload up to the bench
ESD-safe assembly area. Bolt the YBCO sapphire wafer to the cold platform via
the flexure clamp. Wire-bond the Au coil leads to the DAC output pads.
Solder the photodiode pigtail to the DAC input. Mount the InP photodiode
beside the DAC with Apiezon N. Verify electrical continuity end-to-end with
a low-current (μA) source meter, *before* the assembly goes back into vacuum.

Wire the warm-side feedthroughs: phosphor-bronze hookup wire for the DAC
supply rails, coax for the cold thermometry, and a small connector board on
the chamber-external side of the electrical CF feedthrough. Heat-shrink and
strain-relieve everything; the cold finger sees ~0.3 mm of contraction, so
wires need to be ~5 mm slack at room temperature.

Re-install the loaded cold finger. Re-bake (80 °C ceiling, 24 h). Cool to
77 K and verify the DAC powers up and the photodiode shows reasonable dark
current (< 1 nA at 77 K).

**Weeks 9–12: Photonic data path.** Install the Accu-Glass fiber feedthrough.
Pull the SMF from the rack to the feedthrough warm side, splice the polished
pigtail to the cold-side bulkhead. Bring up the SFP+ at the rack, send a
known bit pattern, scope it on the photodiode at 77 K. Verify the DAC ingest
pipeline (FPGA at the rack drives the SFP+; DAC at the cold side reads the
photodiode and emits a current). Calibrate one fixed output current and
verify it on the YBCO coil with a Hall probe held at room temperature
adjacent to the coil (room-temperature Hall, ~$200 from Lake Shore, suffices
for a coarse cross-check; the precise calibration comes from the deflection
test in §11).

**Weeks 13–15: Wafer stage + BSE detector.** Vent under N₂, install the PI
piezo stage on the chamber floor with a kinematic bolt-down (the stage needs
to come out for service without re-aligning the column every time). Bolt
down the Al chuck, route the He backside gas line through a 2.75" CF
feedthrough on the lower-left port. Install the BSE detector on the
upper-right port. Bond the ZMI cube corners to the chuck with Stycast 2850
FT. Set up the ZMI optical path through the lower-right viewport — get the
two-axis interferometer reading to within ±1 nm RMS on a static chuck.

Re-pump, re-bake (the BSE detector is the new low-bake-temperature item;
follow El-Mul's spec, typically 100 °C max).

**Weeks 16–17: Cool-down, HV ramp, alignment.** Start the PT-90, cool to
77 K over ~6 h, dwell overnight to thermalise. Ramp the HVPS from 0 to 50 kV
over ~30 min, watching for any HV arc events on the Spellman current meter
(any unscheduled current pulse > 10 μA is an arc; back off, condition the
gun further). Once at 50 kV, scan the gun's picomotor mount to find first
beam on a fluorescent screen (a YAG:Ce single-crystal coupon, $500, mounted
on the chuck for this purpose) — the beam is found as a bright spot under a
viewport-mounted CCD camera.

**Week 18: First beam test.** §11.

---

## 10. ASCII diagrams (cross-reference)

For reference at the bench (printable companion to Figures 1, 2, 3 above):

```
TOP-DOWN BENCH (Figure 1, simplified):

   ┌──────────────────────────────────────┐
   │ ISO                              ISO │
   │                                      │
   │   ┌───────┐ ┌───────────┐ ┌───────┐  │
   │   │ CFE   │ │           │ │ BSE   │  │
   │   │ gun   │─│  CHAMBER  │─│ det.  │  │
   │   │ (50kV)│ │   8" CF   │ │       │  │
   │   └───────┘ └───────────┘ └───────┘  │
   │             │           │            │
   │             ▼           │            │
   │         pump stack     ZMI viewport  │
   │                                      │
   │ ISO                              ISO │
   └──────────────────────────────────────┘
   Rack (off-bench, fiber+coax bundle in)
```

```
COLD-FINGER STACK (Figure 2, simplified):

   ┌────────────────────────┐
   │ PT-90 head    (295 K)  │
   │ + bellows              │
   └──────────┬─────────────┘
              │ 8" CF flange
              │
   ╔══════════▼═════════════╗  ← chamber top
   ║                        ║
   ║   MLI ░░░░░░░░░░░      ║
   ║   ░ cold finger ░      ║  (77 K)
   ║   ░ cu rod      ░      ║
   ║   ░░░░░░░░░░░░░░░      ║
   ║   ┌─────────────┐      ║
   ║   │ YBCO coil + │      ║
   ║   │ Meissner    │      ║
   ║   │ shield      │      ║
   ║   ├─────────────┤      ║
   ║   │ DAC + PD    │      ║
   ║   └─────────────┘      ║
   ║         │              ║
   ║   beam ▼               ║
   ║                        ║
   ║   ─── wafer ───        ║  (295 K)
   ║   piezo stage          ║
   ╚════════════════════════╝
              │ pump
              ▼
```

![Figure 5. Cold-finger payload exploded view](build_fig5_exploded.png)

---

## 11. First-light test sequence

Once the build hits week 18 and all systems are nominally operational, the
following sequence brings the tool from "powered up" to "first electron-beam
exposure on resist". Each step is a checkpoint — *do not skip ahead*.

**Step 1: Vacuum check.** Confirm chamber pressure ≤ 5 × 10⁻¹⁰ Torr.
RGA shows the expected H₂/H₂O-dominated spectrum, no anomalous mass peaks.
Cryo surfaces are now active cryosorbers — the system pressure will *drop* by
~10× when the PT-90 reaches 77 K.

**Step 2: HV ramp-up.** With the gun's internal getter pump confirmed active
(gun-vacuum readout < 10⁻¹⁰ Torr), the HVPS ramps from 0 → 50 kV at
~1 kV/min. Watch the gun current monitor. Conditioning arcs are normal in
the first ~30 minutes of operation on a fresh column; they should subside.
Stop at 50 kV. Confirm gun emission current of ~5 nA at the tip aperture
(read out on the gun's internal monitor electrode).

**Step 3: First electron beam to fluorescent screen.** Open the picomotor
shutter on the gun. Scan the gun X/Y picomotors slowly while watching the
viewport CCD (looking at the YAG:Ce coupon on the chuck). When the beam
lands on the YAG, you see a small bright (green, ~550 nm) spot. Centre the
beam on the coupon using the picomotors. Without the YBCO coil powered, the
spot is at the column axis defined by the gun pointing.

**Step 4: BSE detection on a fiducial.** Replace the YAG coupon with a
fiducial wafer (etched W cross marks, 5 μm arm length, 100 nm width). Scan
the beam over the fiducial by stepping the piezo stage — the BSE detector
shows a signal modulation as the beam crosses the W mark (W has high BSE
yield against Si substrate, ~4× contrast). Confirm BSE imaging works.

**Step 5: Cryostat cool-down (if not already cold).** PT-90 on, ~6 h to
77 K. Cernox readout on the cold platform reads 77 K ± 1 K stable. Note
that pressure drops to ~5 × 10⁻¹¹ Torr — the cryosorption is active.

**Step 6: DAC commissioning.** Walk the cryo-CMOS DAC through its full
16-bit range, one LSB at a time, monitoring the output current with the
in-line shunt resistor on the warm side (the DAC return current passes
through a 100 Ω shunt before the supply return). Measure INL/DNL — target
INL ≤ 1 LSB, DNL ≤ 0.5 LSB. If INL exceeds spec, run the DAC's on-chip
calibration routine (per Imec/IPMS engineering-sample app note).

**Step 7: HTS coil deflection sweep.** With the beam landed on the YAG
coupon and the DAC commissioned, ramp the DAC output current 0 → I_max.
Watch the YAG spot translate. Measure the deflection angle as a function of
DAC code: with a 50 mm drift to the wafer, a 1 mrad deflection = 50 μm at
the chuck, which is easily resolved by the viewport CCD. *Target: 1 mrad
deflection per ~0.42 A coil current (v4 §X.1), linear within 1 % over the
full deflection range, settling time < 10 μs (measured by toggling the DAC
code and triggering a fast scope on the BSE signal at a fiducial-edge
position).*

This is the headline measurement of Stage A. If the deflection is linear and
fast and the AC loss budget holds, the cryogenic HTS deflection architecture
is empirically validated.

**Step 8: First exposure on test resist.** Replace the fiducial wafer with
an HSQ-coated test wafer (HSQ XR-1541 at 4 % concentration spun to ~80 nm
on a 4" Si wafer, baked at 80 °C, 2 min). Set the beam current to ~1 nA
(throttle via the gun extractor voltage). Expose a coarse cross-pattern by
driving the cryo-CMOS DAC with a pre-loaded GDS-II pattern (a 100 μm cross
with 1 μm arm width). Dose target: 2000 μC/cm² (high — HSQ is a slow
negative). After exposure, vent under N₂, develop in 25 % TMAH for 60 s,
rinse, and inspect under a standard SEM. *A visible cross pattern in HSQ is
the Stage A "first exposure" milestone.* The pattern fidelity is irrelevant
at this stage; the existence of the pattern proves the data path → DAC →
coil → beam → resist loop is closed end-to-end.

**Step 9 (test campaign begins).** From here on, the build is "complete" and
the team transitions to the 6-test validation campaign (v4 §"Tests it
validates"). Each test runs in ~1 month; some run in parallel. Total:
30 weeks to a full Stage A report.

---

## 12. Cost breakdown

Per the BOM in `v4_stage_A_prototype.md`, with vendor part numbers and order
URLs added where reasonable. Prices in 2026 USD; many items have moved ±20 %
since the v4 publication — these are point estimates, not quotes.

| Item | Vendor | Part / URL | Unit | Qty | Subtotal |
|---|---|---|---:|---:|---:|
| CFE gun (50 kV) | Thermo Fisher | custom CFE module, contact rep | \$50 k | 1 | \$50 k |
| Dual-tip Wehnelt mod (optional) | Thermo Fisher | engineering-spec | \$5 k | 1 | \$5 k |
| YBCO 2G tape, 4" | SuperPower | SCS4050 | \$10 k | 1 | \$10 k |
| YBCO patterning service | U. Alberta nanoFab / SuperPower | quote | \$30 k | 1 | \$30 k |
| Cryo-CMOS 16-bit DAC ES | Imec / Fraunhofer IPMS | engineering-sample, contact rep | \$10 k | 1 | \$10 k |
| Cryo InP photodiode | Hamamatsu | G12180-series | \$5 k | 1 | \$5 k |
| SFP+ optical TX 10G LR | Cisco | SFP-10G-LR | \$0.2 k | 1 | \$0.2 k |
| SMF + UHV feedthrough | Corning + Accu-Glass | SMF-28 + AG single-fiber CF | \$3 k | 1 | \$3 k |
| BSE detector | El-Mul | SE/BSE annular | \$30 k | 1 | \$30 k |
| 8" CF UHV chamber | Kurt J. Lesker | spec build, 6-port | \$60 k | 1 | \$60 k |
| Cryomech PT-90 + CP-289 | Cryomech | PT90 + CPA-1110 | \$30 k | 1 | \$30 k |
| Cryostat / cold finger assy | Janis (custom) | OFHC + bellows kit | \$25 k | 1 | \$25 k |
| 6-DOF piezo stage | Physik Instrumente | N-731 | \$50 k | 1 | \$50 k |
| ZMI interferometer head | Zygo | ZMI-2000 two-axis | \$25 k | 1 | \$25 k |
| 50 kV HVPS | Spellman | SR50PN | \$10 k | 1 | \$10 k |
| FPGA + workstation | AMD/Xilinx + Dell | Versal Premium VPK180 eval | \$20 k | 1 | \$20 k |
| Etched fiducial wafer | U. clean room (custom) | W-cross + grating + vernier | \$1 k | 5 | \$5 k |
| HSQ resist | DuPont / Allresist | XR-1541-006 | \$0.5 k | 2 | \$1 k |
| Vacuum infrastructure | Pfeiffer / Lesker | turbo + ion + RGA + valves | \$30 k | 1 | \$30 k |
| Granite optical bench + isolators | Newport | RS-3000 + S-2000 | \$15 k | 1 | \$15 k |
| HEPA / class-6 enclosure | Terra Universal | custom | \$3 k | 1 | \$3 k |
| Misc. (cables, tooling, gaskets, He) | various | — | \$10 k | 1 | \$10 k |
| Integration labour | — | engineer × month | \$15 k | 18 | \$270 k |
| **Stage A total** | | | | | **~\$667 k** |

The labour line is the dominant cost. Hardware-only is ~$397 k; with one
engineer at full freight for 18 months the total lands in the $600–700 k band
quoted in v4. A second engineer for the parallel-track build phase
(weeks 5–17) compresses the schedule to ~12 weeks total at a ~$60 k labour
delta, raising the total to ~$730 k for a faster build.

---

## 13. Common failure modes + recovery

What goes wrong, in roughly decreasing order of likelihood during the first
year of operation:

**Vacuum leak.** Symptom: pressure rises above 1 × 10⁻⁸ Torr with both
pumps running and no obvious cause. Root cause is usually a CF gasket that
loosened during a thermal cycle. Recovery: He leak detection on every joint,
in reverse order of last assembly. Common offenders are (a) the load-lock
gate valve (re-torque), (b) the cold-finger 8" CF (re-torque after first
cool/warm cycle is normal), and (c) the electrical feedthroughs (the Kapton
insulation in some Accu-Glass parts cold-flows under repeated bake cycles).

**HV arc on the gun.** Symptom: sudden current spike on the Spellman meter,
gun-vacuum readout jumps, possibly a visible flash through the viewport.
Recovery: back off HV to 0 immediately, let the gun rest at 0 V for 15 min,
ramp back up at 0.5 kV/min, expect more conditioning arcs in the first 30
min. If arcs persist above 30 kV for more than 1 h of conditioning, vent and
inspect the gun for whisker debris on the anode. CFE tips can fail
catastrophically after ~1000 hours; budget for one replacement tip
(~$3 k) per year.

**HTS quench.** Symptom: the YBCO coil suddenly stops carrying current, the
DAC output appears in compliance, and the cold platform shows a temperature
spike of ~1–5 K. Cause: the coil exceeded its critical current locally (a
solder-joint defect, a film thickness variation, or a temperature excursion
from AC loss). Recovery: cut the DAC drive immediately (the cryo-CMOS DAC has
an on-chip over-current trip — verify it tripped), let the cold platform
re-equilibrate to 77 K (~5 min), restart at lower drive. If quench repeats,
inspect the coil under SEM after a vent. Protect circuit: a 1 Ω current-limit
resistor in series with the DAC output bounds the worst-case fault current
at ~1 A (well below the YBCO trace's burnout threshold).

**Cryo-CMOS DAC failure.** Symptom: DAC outputs static, no response to
control words. Most common: an ESD event during a thermal cycle from
ungrounded handling. Recovery: vent, warm to 295 K, swap the DAC die on
the interposer (the interposer is socketed for this — the DAC is replaced as
a unit, ~$10 k per swap), re-cool, re-commission. Stage A keeps one spare
DAC in the parts cabinet.

**Stage drift.** Symptom: BSE registration loop fails to converge; ZMI shows
the stage walking 10–100 nm/hour without command. Cause: thermal drift in
the granite bench or in the cryostat-to-chamber mechanical interface.
Recovery: re-zero the ZMI, run a 1-hour static drift measurement to
characterise the drift rate, and add a per-shift recalibration loop in the
control firmware. If drift exceeds 100 nm/hour, suspect a vibration intrusion
(check that the cryocooler compressor is on its own isolation pad, that no
new equipment has been added to the lab floor) or a thermal intrusion (check
the HEPA enclosure temperature stability — a 1 K shift in the bench room
moves the granite by ~100 nm/m).

**Cryocooler compressor warning.** Symptom: Cryomech CPA-1110 controller
flags a high-pressure alarm or water-flow alarm. Recovery: shut down the cold
head load (cut DAC drive, no AC loss), inspect the water-cooling loop, top up
He if pressure has dropped below 200 psi static (the He charge in the PT-90
slowly leaks over ~5 years and needs occasional top-up). Re-start.

**Fiber-link bit errors.** Symptom: DAC output shows occasional wild
excursions inconsistent with the pattern stream. Cause: fiber polishing
degraded at the cold-side bulkhead after thermal cycles, or the cryo
photodiode has accumulated radiation damage from the column. Recovery: vent,
inspect fiber end-face under a fiberscope, re-polish if needed; if the
photodiode dark current has risen > 5× from baseline, swap the photodiode
(spare, ~$5 k, kept in parts cabinet).

---

## 14. Path forward

The first beam exposure (Step 8 above) is the "Stage A built" milestone.
The six-test validation campaign (HTS linearity, Meissner attenuation,
cryo-CMOS DAC INL/DNL, BSE registration loop closure, cryosorption capture
fraction, chuck thermal transient) then runs over months 5–15 of the
program, one test per ~month with parallelism.

At the end of month 18, the Stage A report goes to the funder. If all six
tests pass within design margin, the v4/v5 architecture is empirically
de-risked and the program advances to **Stage B** (16–64 beams, $3–5 M,
24 months) — a parallel-column build that scales the same cryogenic /
photonic / cryo-CMOS subsystems by ~32×, validates the photonic data path at
~1.5 Tbps aggregate, and produces the first scalable EBL exposures at
multi-beam densities.

The transition from Stage A → Stage B is *not* a redesign. Every Stage A
subsystem scales by replication: the same YBCO patterning recipe makes
32 coils instead of 1, the same cryo-CMOS DAC tile drives 32 channels
instead of 1, the same Accu-Glass feedthrough hosts 32 fibers instead of 1.
The Stage A build is *the proof* that each subsystem works at 1× scale; the
Stage B build is *the proof* that it scales linearly.

This manual is the bench-side companion to that program. The architecture is
ready for build. The bottleneck is funding and skilled hands, not specification
or science.

---

*Document: `v5_prototype_build_manual.md` · Compiled to `v5_prototype_build_manual.pdf`
via tectonic · Figures generated by `build_manual_figures.py`
(matplotlib + numpy) · Released CC BY 4.0 alongside the Morin (2026) v5 paper
and v4 supplementary materials.*
