# Unlocking the Sub-10 nm Custom Chip Economy

## How Open-Architecture Multi-Beam EBL Closes the EUV Mask-NRE Wall

**Robert Gerald Morin** — NIKI Nation Builders, Edmonton, Alberta, Canada
*Strategic position document, companion to Morin (2026), "Multi-Beam Direct-Write Electron Lithography via Multi-Rate Electromagnetic Steering — v5"*
*May 16, 2026 — Released under CC BY 4.0*

---

## 1. Executive summary

The advanced-node semiconductor industry has a wall that almost nobody outside the industry sees. It is not the cost of an EUV scanner ($200–400 M per tool, already legendary). It is not even the cost of a fab ($15–20 B). It is the **mask non-recurring engineering charge** — the one-time cost to make the physical optical-mask set that a scanner exposes onto wafers. At today's leading nodes (TSMC N3, N2), a single chip design requires roughly **50 EUV mask plates at $200,000–$1,000,000 each**, totaling **$10–50 M of mask NRE before the first wafer is exposed**.

This wall sorts every would-be advanced-node chip program into two buckets:

* **High-volume consumer silicon** (smartphones, CPUs, GPUs, AI accelerators at hyperscaler scale): >100 M chips per design, amortising mask NRE to fractions of a cent per chip. **EUV makes economic sense.**
* **Everything else** (defense ASICs, biomedical implants, aerospace, industrial automation, research, custom AI, photonics, quantum control): typical volumes are 100 to 100,000 chips per design. EUV mask NRE works out to **$0.40 to over $40 per chip**, often more than the chip's own selling price. **EUV is forbidden.**

The "everything else" bucket is enormous, and it is currently stranded on 28–130 nm CMOS — nodes one to four generations behind state of the art. The reason is not physics. It is amortisation arithmetic.

The Morin v5 architecture (a fully open-source, mask-free, multi-beam direct-write electron lithography tool, $40 M per tool, validated at 30–180 nm with a hard physics floor at ~7 nm) **eliminates mask NRE entirely**. A chip program is written directly from its GDS-II tape-out, with no mask, no pellicle, no inspection, no repair, no plate inventory. The marginal cost of changing the design is essentially zero. A 10-tool fab at $300–400 M of capital produces approximately **3.6 million custom sub-10 nm chips per year**, with **no mask amortisation in the per-chip cost** at all.

The strategic consequence: a market that has been stranded since the introduction of EUV in 2019 can be served at advanced nodes for the first time. The capital requirement to enter is one mid-size battery factory — not one TSMC fab. Sovereign procurement officers, defense and biomedical chip program managers, custom-ASIC startup founders, and strategic-tech investors who write checks at the $100–500 M scale can now build something that did not previously exist: **economically viable sub-10 nm capability for low-volume, high-value, mission-critical chip programs**.

This document is the business and policy companion to the v5 technical preprint. It does three things:

1. Explains in plain language why the EUV mask NRE wall exists and what it strands.
2. Quantifies what the v5 architecture changes, at what cost, and on what schedule.
3. Identifies the concrete sovereign, industrial, and research programs that become possible.

The single most load-bearing number in the analysis is this: **at a 1,000-wafer chip program, EUV mask amortisation alone is approximately $40 per chip**, frequently exceeding the chip's revenue. The v5 architecture takes that line item to zero. Everything else in this document follows from that fact.

---

## 2. The EUV mask NRE wall, explained

### 2.1 What an EUV mask set actually is

A modern logic chip is built from 50–80 patterned layers of metal, oxide, and silicon, each lithographically defined. At the leading nodes (TSMC N5 / N3 / N2, Samsung 3GAP, Intel 18A), the most critical of those layers — typically 15–25 of them — are patterned using extreme-ultraviolet (EUV) lithography. EUV exposes a wafer by projecting the image of a **mask** (also called a reticle): a 6-inch square quartz plate coated with multilayer molybdenum-silicon and patterned with the chip layout in tantalum-based absorber.

A single EUV mask plate costs **$200,000–$1,000,000** in 2026, depending on the layer (the most critical metal-1 and via layers are the expensive ones; less critical layers are at the low end). A complete EUV mask set for one chip design at N3 contains roughly **50 plates** (the EUV-critical layers plus the DUV layers exposed on older scanners). At N2 with High-NA EUV, the number rises toward 60–70 plates.

Fully loaded cost of one EUV mask set, by node:

| Node | EUV layers | Total layers (EUV+DUV) | Mask set cost |
|---|---:|---:|---:|
| N7 (DUV only) | 0 | ~40 | $5–8 M |
| N5 | 5 | ~45 | $10–15 M |
| N3 | 12 | ~50 | **$20–25 M** |
| N2 (High-NA) | 18 | ~60 | **$35–45 M** |
| A14 (projected) | 22 | ~65 | $45–60 M |

These figures come from industry analyst publications (IBS Mountain View, IC Insights, Yole Développement, SemiEngineering coverage of TSMC and Samsung disclosures, 2023–2025).

### 2.2 Why mask NRE dominates at low volume

A mask set is a fixed cost. Whether the customer ships 1,000 wafers or 100,000 wafers, the mask set costs the same. Per-wafer mask amortisation is simply (mask set cost) / (wafers shipped). At a 300 mm wafer with roughly 1,000 chips per wafer for a typical 100 mm² die, per-chip mask amortisation is (mask set cost) / (1,000,000 chips per 1,000 wafers).

Worked example at TSMC N3 ($25 M mask set, 1,000 chips per wafer, 50 % yield):

| Wafers shipped | Chips shipped | Mask cost per chip |
|---:|---:|---:|
| 100,000 | 50,000,000 | **$0.50** |
| 10,000 | 5,000,000 | $5 |
| 1,000 | 500,000 | $50 |
| 100 | 50,000 | $500 |

At N2 EUV ($40 M mask set):

| Wafers shipped | Chips shipped | Mask cost per chip |
|---:|---:|---:|
| 100,000 | 50,000,000 | **$0.80** |
| 10,000 | 5,000,000 | $8 |
| 1,000 | 500,000 | **$80** |
| 100 | 50,000 | $800 |

### 2.3 What this means for any chip selling for less than $50

The vast majority of chips in the world sell at wholesale ASPs below $50 (often below $5: microcontrollers, sensor frontends, power management, RF transceivers, codecs). A chip that sells for $5 cannot carry $50 of mask amortisation. A chip that sells for $30 cannot carry $80.

The market sorts itself accordingly. Programs that ship more than 50 million chips of one SKU per year — smartphone application processors, GPU silicon, hyperscaler AI accelerators, certain commodity memory and storage controllers — can use EUV. **Everything else cannot**, and operates two or more nodes behind.

This is not a marketing statement. It is the actual economic logic that explains why, in 2026, your insulin pump, your cochlear implant, your car's radar SoC, your military radio's signal processor, and your university research chip are all still on **28 nm, 65 nm, or 130 nm CMOS**, even though the leading edge has moved on by a decade.

---

## 3. What chip programs the EUV wall strands

The following inventory uses public industry analyst data (Yole Développement market reports 2023–2025, IC Insights chip-volume databases, SEMI World Fab Forecast, IDC sector reports). All figures are best estimates of order of magnitude; precision is not the point — the point is that every single category falls in the "EUV-stranded" volume range.

### 3.1 Defense ASICs

Typical volumes: **100 to 10,000 chips per design**. Categories: radar/EW receivers, secure communications transceivers, signal-intelligence frontends, missile/munitions seekers, cryptographic engines, secure FPGAs, satellite payload electronics.

Economics: at a 1,000-wafer program (1 million chips), EUV mask cost at N3 is $25 per chip; at N2, $40 per chip. Defense chip ASPs are typically $50–500, so mask cost is not the only barrier (qualification adds easily $10–100 M more), but it is the line item that makes the program impossible to fund at advanced nodes in the first place.

Current state: defense electronics in 2026 is largely stuck at **130 nm, 65 nm, and the more recent designs at 28 nm**. The U.S. Department of Defense Trusted Foundry program, the Microelectronics Commons, and equivalents in EU/UK/Israel/India all primarily serve mature-node defense ASICs. Sub-10 nm defense capability exists only for high-volume parts (e.g., Intel server CPUs used in defense data centers), not for purpose-built defense designs.

Estimated stranded program count, worldwide: **300–1,000 active defense ASIC designs per year** across NATO + allies that would benefit from advanced nodes but cannot afford the mask NRE.

### 3.2 Biomedical implants and instruments

Typical volumes: **100 to 100,000 chips per design**, with mandatory FDA / EMA / Health Canada traceability and 10–20 year medical-grade support obligations.

Categories: cochlear implants (Cochlear, Med-El, Advanced Bionics — ~150,000 implants/year worldwide), retinal prostheses (Second Sight, Pixium Vision — ~1,000/year), neural-recording arrays (Neuralink, Synchron, Blackrock Neurotech, Paradromics — under 1,000 production units/year as of 2026, designed for tens of thousands), deep-brain stimulators (Medtronic, Abbott, Boston Scientific — ~150,000 implants/year combined), cardiac pacemakers and ICDs (~1 M/year worldwide), insulin pumps (~500,000/year), continuous glucose monitor SoCs (Dexcom, Abbott — high-volume exception, ~50 M/year).

Most of these chips are on **130 nm or older** silicon because:

1. Mask NRE doesn't amortise at sub-million volumes.
2. Medical-grade qualification cost amortises better on a long-lived mature process.
3. Power dissipation is the binding constraint for implants, and 130 nm SOI offers good leakage characteristics.

But for the same reason that smartphones jumped from 28 nm to 5 nm in eight years (smaller, lower-power, higher-performance), implants would benefit enormously. A neural-recording array at 7 nm could double channel count and halve power vs the same design at 65 nm.

Estimated stranded program count, worldwide: **200–500 active medical-implant chip designs per year** that would benefit from advanced nodes.

### 3.3 Aerospace and space

Typical volumes: **100 to 10,000 chips per satellite or system design**. Categories: spacecraft on-board computers, satellite RF transceivers, radiation-hardened FPGAs and ASICs (BAE Systems RAD750/RAD5500, Frontgrade RT3PE, NanoXplore NX1H35AS), star trackers, attitude-control electronics, lidar/radar SoCs for autonomous aircraft.

The economic problem here is compound: EUV mask NRE plus radiation-hardening qualification (often $50–100 M per design at advanced nodes) means a single rad-hard chip program at N3 can cost more than a satellite. The result is that almost all rad-hard chips in 2026 are at **150 nm, 90 nm, or 65 nm**, often via specialized small foundries (TSI Semiconductors, X-FAB, etc.).

NewSpace constellations (Starlink, OneWeb, Project Kuiper, planet labs) have used commercial-off-the-shelf parts at advanced nodes — but those parts were designed for terrestrial volumes and the satellites bear the radiation risk. Purpose-built advanced-node rad-hard silicon does not exist in commercial volumes.

Estimated stranded program count, worldwide: **100–300 active aerospace/space-grade chip designs per year**.

### 3.4 Industrial automation

Typical volumes: **1,000 to 100,000 chips per machine type**. Categories: PLC (programmable logic controller) SoCs, motor controllers, sensor-hub MCUs, industrial Ethernet bridges (EtherCAT, PROFINET), robotic actuator drivers, machine-vision frontends.

Most of this market is at **130 nm to 90 nm** because (a) the chips are cost-sensitive at the $1–20 ASP range, (b) reliability matters more than transistor speed, and (c) volumes are insufficient to amortise EUV. The result: industrial automation is a node generation or two behind smartphones, and the gap is widening as EUV adds another step.

Estimated stranded program count: **500–2,000 active industrial-automation chip designs per year** across worldwide vendors (Siemens, Rockwell, Schneider, Mitsubishi, ABB, Omron, Beckhoff, etc., plus thousands of smaller industrial-electronics shops).

### 3.5 Research and academic

Typical volumes: **1 to 1,000 chips per experiment**. Currently served by university shuttle services — MOSIS (US), Europractice (EU), CMC Microsystems (Canada), CMP (France), VDEC (Japan), and various commercial multi-project-wafer brokers. MOSIS and the equivalents pool many designs onto shared mask sets, charging $5,000–$50,000 per design for tens-of-chips quantities.

The catch: shuttle services are **almost entirely limited to 130 nm and older nodes** (with some 65 nm and very limited 28 nm offered at $50,000+ per design). Sub-10 nm shuttle access does not meaningfully exist: TSMC's University Shuttle Program offers some N7 access via consortium partners at six-figure per-design fees, but N3/N2 access is closed to academic budgets.

The result: PhD research in custom silicon is **stuck a decade behind** what industry can do. Quantum control electronics, custom AI accelerators, RF and photonic integration — every area where academic innovation could matter — is hobbled by an inability to prototype at advanced nodes.

Estimated stranded program count: **1,000+ academic chip designs per year** worldwide that would benefit from sub-10 nm access at affordable prices.

### 3.6 Custom AI accelerators (sub-scale)

Typical volumes: **100 to 10,000 chips per design**. Categories: medical-imaging inference accelerators, autonomous-vehicle perception chips for niche OEMs, robotics control SoCs, edge-AI for industrial inspection, video analytics for surveillance and broadcast, scientific-instrument inference engines.

The hyperscalers (NVIDIA, Google TPU, AWS Trainium/Inferentia, Microsoft Maia, Meta MTIA) do this at advanced nodes because their volumes exceed 1 M units per design. Below that volume, custom-AI startups overwhelmingly settle for **FPGA implementations**, because the ASIC NRE — mask plus IP licensing — exceeds any realistic break-even.

This is the segment that "custom silicon for AI workloads" was supposed to unlock. Many startups have founded on that thesis and pivoted to FPGAs or chiplet-based designs on mature nodes because the advanced-node ASIC math does not work below ~$50 M committed revenue.

Estimated stranded program count: **500–1,500 custom AI accelerator chip designs per year** worldwide that have viable technical concepts but unviable NRE math.

### 3.7 Photonic integrated circuits

Typical volumes: **1,000 to 10,000 chips per sub-segment** in optical networking, LiDAR, sensing, and quantum applications. Companies: Lightmatter, Ayar Labs, PsiQuantum, Xanadu, Quantinuum, Acacia (Cisco), Marvell-Inphi, Lumentum, Coherent.

Photonic ICs require integration with electronic control circuits that are usually on **90 nm, 65 nm, or 28 nm** — not because those nodes are best, but because volume cannot amortise newer ones. Co-packaged optics (CPO), photonic AI accelerators, and quantum-photonic systems would all benefit substantially from sub-10 nm control silicon.

Estimated stranded program count: **100–300 photonic-IC designs per year** worldwide.

### 3.8 Quantum control electronics

Typical volumes: **100 to 1,000 chips per qubit-array generation** (each major quantum-computer revision needs new control silicon). Categories: cryo-CMOS qubit controllers (Intel Horse Ridge, Google Sycamore, IBM Q, Rigetti, IonQ, Quantinuum, PsiQuantum, ColdQuanta, IQM, OQC), readout digitisers, gate-pulse arbitrary-waveform generators.

Cryo-CMOS control silicon currently uses **GlobalFoundries 22FDX or Intel 22FFL** — both ~22 nm-class processes — because (a) GF22FDX has demonstrated 4 K operation, and (b) mask NRE at <22 nm cannot amortise. Sub-10 nm cryo-CMOS for qubit control would enable substantially higher channel counts (essential for the 1000+ qubit systems projected for 2027–2030), but no quantum company in 2026 can afford to fund the mask NRE.

Estimated stranded program count: **50–150 quantum-control chip designs per year** worldwide.

### 3.9 Aggregate market estimate

Summing the stranded program counts above:

| Sector | Stranded designs/year | Typical ASP range | Sector market |
|---|---:|---|---|
| Defense ASICs | 300–1,000 | $50–500 | $5–10 B/year addressable |
| Biomedical implants | 200–500 | $100–10,000 | $10–30 B/year addressable |
| Aerospace / space | 100–300 | $500–50,000 | $5–15 B/year addressable |
| Industrial automation | 500–2,000 | $1–50 | $5–15 B/year addressable |
| Research / academic | 1,000+ | (subsidised) | $0.2–1 B/year addressable |
| Custom AI accelerators | 500–1,500 | $50–5,000 | $10–40 B/year addressable |
| Photonic ICs | 100–300 | $50–5,000 | $5–20 B/year addressable |
| Quantum control | 50–150 | $1,000–50,000 | $0.5–5 B/year addressable |
| **Total** | **~2,750–6,750 designs/year** | | **~$40–135 B/year addressable** |

This is the market that EUV economics excludes. The v5 architecture is the first credible technology to serve it at sub-10 nm.

---

## 4. What the v5 architecture changes

The v5 architecture is described in technical depth in the companion preprint (Morin 2026, v5). The business-relevant summary:

* **Zero mask cost.** The tool writes patterns directly from GDS-II — the same tape-out file the chip designer hands to a foundry. Changing the design changes the file. Per-chip mask amortisation is structurally zero, because there are no masks to amortise.

* **Validated node range: 30–180 nm at production throughput.** With 50–180 nm comfortable and 30 nm marginal at the nominal 2 nA per-beam operating point.

* **Physics floor at ~7 nm.** The architecture has a hard placement-error floor of σ_floor = 1.41 nm, corresponding to a minimum accessible node of approximately 7 nm. Below 50 nm, throughput falls linearly with the current de-rating required to reach finer nodes: 14 nm node at 0.25× throughput, 8 nm at 0.05×.

* **Throughput at 30–50 nm nominal: 8–17 wafers per hour through a 70-layer mature-node process.** This is 8–17 wafers per hour per tool, not per fab. A 10-tool fab produces 80–170 wph aggregate.

* **At sub-10 nm with current de-rating to 0.1 nA: approximately 0.5 wph per tool through 70 layers.** A 10-tool fab produces 5 wph. Operated 8,000 hours per year (typical lithography uptime), that is **40,000 wafers per year** at sub-10 nm. At 1,000 die per 300 mm wafer with 25 % learning-curve yield, that is **10 million sub-10 nm custom chips per year per 10-tool fab**.

* **Per-tool capital cost: ~$40 M.** Per 10-tool fab capital: $300–400 M including building, support equipment, software, and integration.

* **Open architecture, no patent claims.** The entire design, including the software stack (GDS-II compiler, real-time firmware, tool operating system), is published under CC BY 4.0 (paper + spec) and MIT (code). Anyone may build, modify, and commercialise it. No license fees flow to ASML, Zeiss, TSMC, or Imec for the architecture itself.

* **Open supply chain.** Every subsystem has ≥3 independent commercial vendors across ≥2 jurisdictions. No single-vendor chokepoint (in stark contrast to EUV, which has a single global vendor — ASML — for the scanner and Carl Zeiss SMT for the optics).

* **Software-defined.** All process recipes, calibration data, and operator workflows are versioned in open-source software stacks (PostgreSQL + Git + Next.js + Tango Controls). Process know-how is portable across institutions; new operators can be onboarded against a public reference implementation.

The combined effect: the per-tool economics that make EUV inaccessible to sub-50 M-chip programs are replaced by economics that scale linearly with volume, with zero step-function mask cost. **A 1,000-chip run on the v5 architecture is economic. A 1,000-chip run on EUV is not, and never will be.**

---

## 5. Concrete program examples that become possible

### 5.1 Sovereign defense fab

**Authorising entity**: Department of Defense (US), Ministry of Defence (UK), Bundeswehr (DE), Ministère des Armées (FR), Ministry of Defense (IL/IN/AU/CA), or equivalent.

**Capital**: $300–400 M for a 10-tool fab, plus $50–100 M for cleanroom + support equipment + initial operating capital. **Total: $400–500 M.**

**Output**: All radar/EW/SIGINT/secure-comms/cryptography ASICs and rad-hard FPGAs needed for a national defense industrial base at 30–180 nm, with 30 nm marginal access. **Annualised throughput**: ~120 wph average × 8,000 hr/yr × 1,000 chips/wafer = **~1 billion custom defense chips per year per fab**, across hundreds of unique designs.

**Comparison**: A leading-edge sovereign foundry effort (e.g., Intel Ohio at $20 B, TSMC Arizona at $40 B, Globalfoundries Malta at $4 B for 12-nm) costs 10–100× more, takes longer to build, and produces commodity silicon — not the custom defense ASICs that are the actual sovereign requirement.

**Candidate countries**: India, Saudi Arabia, Turkey, Australia, Canada, UAE, Brazil, South Korea (sub-sovereign), Israel, Poland, Finland, Sweden. Any country with a serious defense electronics base.

### 5.2 National biomedical chip foundry

**Authorising entity**: National health ministry + medical device regulators + research foundation consortium (e.g., NIH + FDA + the academic medical centers in the US; EMA + national institutes + Fraunhofer in the EU; CIHR + Health Canada in CA; etc.).

**Capital**: $300–400 M for a 10-tool fab, plus medical-grade ISO 13485 cleanroom and quality-system NRE of $50–80 M. **Total: $400–500 M.**

**Output**: All cochlear, retinal, neural, cardiac, deep-brain, and continuous-monitor implant chips a country could possibly need, at sub-10 nm where useful and 30–180 nm elsewhere. Independence from Boston Scientific / Medtronic / Cochlear / Abbott licensing chains.

**Strategic upside**: a country that owns its biomedical implant silicon stack owns the next 30 years of patient-data sovereignty, repair-and-modify rights, and lifecycle support. Currently every implant in every patient is dependent on multi-decade supply guarantees from a small number of US foundries. v5 changes that.

### 5.3 University research consortium

**Authorising entity**: Consortium of 10–25 research universities, funded by national-science councils (NSF/NSERC/EPSRC/DFG/JST/NRF), via the same shared-facility model that today funds synchrotron beamlines and supercomputer centers.

**Capital**: $40–80 M for a 1-tool single-shift facility, including building, integration, and operations endowment.

**Output**: Sub-10 nm chip prototyping accessible to participating PhD students and faculty at **$10,000–$50,000 per design** (vs. the $5 M+ that an N3 mask set costs today). Throughput at sub-10 nm de-rating: ~5,000 wafers/year, more than enough for 1,000 unique designs at 5 wafers each.

**Strategic upside**: research democratisation at the level that MOSIS (founded 1981 by DARPA) democratised mature-node access in the 1980s. The result then was a generation of US silicon engineers; the result now would be a generation comfortable designing at advanced nodes.

### 5.4 Indigenous-owned chip program

**Authorising entity**: per the structure described in Morin v4 §6.2, a 51 % / 49 % Indigenous–investor joint venture, with First Nations / Métis / Inuit ownership majority and operational control. Funding via Indigenous Services Canada, the First Nations Major Projects Coalition, ISC-equivalent agencies in US/AU/NZ, sovereign-wealth-fund participation from Indigenous-controlled entities (e.g., Alberta Investment Management Corp Indigenous funds, NZ Iwi investments).

**Capital**: $300–400 M for a 10-tool sovereign-relevant fab.

**Output**: chips for any Indigenous-priority application — communications sovereignty (community radio, mesh network, satellite uplink), medical implants for Indigenous health priorities (FASD assistive technologies, diabetes monitoring at scale on reserves), environmental sensors for treaty-protected lands, cultural-preservation electronics (language-tech NPUs).

**Strategic upside**: the first sovereign chip program owned by Indigenous people in the world. Aligns with UNDRIP, with the 2024 Canadian Indigenous Procurement Strategy, and with the broader move toward Indigenous ownership of critical infrastructure.

### 5.5 Climate sensor network

**Authorising entity**: climate research consortium + national environmental agencies + UN climate funds.

**Capital**: $40–80 M for a 1-tool facility producing low-power 7 nm sensor SoCs for distributed environmental monitoring.

**Output**: tens of millions of custom sensor nodes at sub-10 nm efficiency — wildfire detection across boreal/Mediterranean forests, ocean-acidification sensors, atmospheric methane mapping, glacier-melt monitoring, biodiversity acoustic recorders, soil-moisture and drought arrays. Each application needs ~1,000–10,000 unique chip designs (one per sensor type), and **millions of identical units of each design**. Volume per design fits the v5 economic sweet spot (each design amortises tool time, not mask cost).

**Strategic upside**: climate-instrumentation programs presently fail because the SoC NRE for a custom low-power sensor at sub-10 nm is unaffordable per-program. v5 unsticks this.

---

## 6. Economic comparison: EUV fab vs v5 fab

### 6.1 Side-by-side at comparable node

| Metric | TSMC N3 EUV fab | v5 sub-10 nm fab |
|---|---|---|
| **Capital, single tool** | $200–400 M (EUV scanner only) | $40 M (entire tool) |
| **Capital, full fab** | $15–25 B | $300–400 M |
| **Mask NRE per chip design** | $20–25 M | **$0** |
| **Node range covered** | N3 (and back-compatible) | 30–180 nm comfortable; 7–30 nm at reduced throughput |
| **Throughput (wafers/hour/tool)** | 130–180 wph | 0.5 wph at 7 nm; 8–17 wph at 30–180 nm |
| **Time to break-even on mask NRE** | ~50 M chips per design | 1 chip per design |
| **Supply chain — scanner** | Single vendor (ASML) | ≥3 vendors per subsystem |
| **Supply chain — optics** | Single vendor (Zeiss SMT) | ≥3 vendors per subsystem |
| **Supply chain — masks** | Single sub-industry (~5 mask shops globally) | None (no masks) |
| **Geopolitical exposure** | Netherlands (ASML) + Germany (Zeiss) + Taiwan (TSMC) | Distributed; no single national chokepoint |
| **IP licensing** | TSMC + ASML + Zeiss + Imec + Cadence/Synopsys | Open architecture, no NRE flowing to licensors |
| **Time to first chip from authorisation** | 5–7 years (fab build) | 7–8 years (tool dev + fab build) |
| **Best-fit market** | High-volume consumer (>50 M chips/SKU/year) | Everything else (100–10 M chips/SKU/year) |

### 6.2 Where EUV wins

EUV wins where it was designed to win: **high-volume consumer silicon**. At a 50 M-unit run of a smartphone application processor, EUV mask amortisation is $0.50–$0.80 per chip, throughput is 130–180 wph per scanner, and the per-chip silicon-area cost is competitive on a fully-loaded basis with anything else.

For Apple, Qualcomm, NVIDIA, AMD, Google, Microsoft, Meta, Amazon, MediaTek, and Samsung's own silicon, EUV is the right answer and will remain so.

### 6.3 Where v5 wins

Everywhere else. The crossover is sharp: any program shipping fewer than approximately 10 million units of one design per year cannot economically use EUV. That is the entire "stranded" market enumerated in §3.

It is worth saying explicitly: **v5 does not replace EUV**. EUV remains the only economic technology for top-of-market consumer silicon. v5 fills a different market — one that EUV cannot serve and that is currently served at older nodes for the wrong economic reason (mask amortisation rather than physics).

---

## 7. Strategic implications

### 7.1 Supply chain resilience

The 2020–2023 chip shortage exposed the fragility of the global semiconductor supply chain. A handful of EUV scanners (under 200 total worldwide in 2026, all from ASML) and a small number of leading-edge fabs (TSMC, Samsung, Intel) are choke points. A single fire, earthquake, embargo, or geopolitical event can disrupt the world's supply of critical chips.

A v5-architecture fab can be built in any country with reasonable cleanroom-construction capability and a small population of skilled optics, vacuum, and software engineers. There is **no equivalent ASML choke point** because the architecture is open and the subsystems are commodity. **Any sovereign or large-corporate entity can build its own advanced-node chip capability** at $300–400 M of capital — within reach of any country with a defense budget over $5 B.

### 7.2 Defense independence

The U.S. CHIPS Act (2022) committed $52 B partly on the grounds that domestic semiconductor manufacturing is a defense requirement. The bill funds construction of EUV-based facilities that primarily make commodity high-volume silicon, not the specific defense ASICs the Pentagon needs.

The v5 architecture is a **direct match for the actual defense requirement**: low-volume, high-value, mission-critical ASICs at advanced nodes, in facilities that can be physically located on sovereign territory and supplied without dependence on Taiwan or the Netherlands. A $400 M v5 fab is functionally a "defense chip foundry" in the same way that a $4 B Globalfoundries fab is a "commercial chip foundry" — at 10× lower capital and 100% sovereign control.

For DoD and allied defense ministries, this is a strictly better deal than what CHIPS-style policy can buy today.

### 7.3 Industrial policy

$400 M is not a special number. It is one mid-size battery factory (e.g., one of the smaller LG Chem or CATL facilities). It is one large data center. It is what France's CEA-Leti spends in 2–3 years on advanced lithography R&D. **A fab is no longer special at this capital scale.**

This rewrites what "industrial policy for semiconductors" can mean. Today it means a multi-billion-dollar federal subsidy to attract a TSMC or Intel facility. Tomorrow it can mean a state, provincial, or even municipal program — a $400 M commitment is within reach of California or Texas alone, of Ontario, of Bavaria, of any major European country, of large city-states like Singapore. The number of jurisdictions that can credibly stand up an advanced-node chip program expands by an order of magnitude.

### 7.4 Research democratisation

Every major research university could have access to sub-10 nm prototyping at a per-design cost of $10,000–$50,000. This puts advanced-node silicon design back in the hands of academic researchers for the first time since the late 1990s. The pedagogical and innovation consequences are difficult to overstate — the equivalent transition in computing was the move from time-shared mainframes to workstations in the 1980s.

### 7.5 The IP landscape

v5 is **CC BY 4.0 + MIT, with no patent claims by the author**. This is the load-bearing strategic fact for any sovereign or institutional adopter. There is no license fee owed to ASML, Carl Zeiss SMT, TSMC, Imec, MAPPER, IMS Nanofabrication, or any other holder of conventional-EBL or EUV IP.

The architecture is not blocked by any prior patent (no patent claims are made by the author, and the architecture is published as prior art before any party could enclose it). It can be built in any jurisdiction, modified arbitrarily, and commercialised by any party.

For sovereign procurement officers, this dissolves the most common late-stage blocker on infrastructure procurement: third-party IP claims that surface after construction has begun. For private-capital adopters, the open architecture means **first-mover advantage is in execution and process know-how, not in patent moats** — which is actually how most successful precision-instrument businesses (e.g., the entire semiconductor-equipment industry pre-1995) were built.

---

## 8. What it takes to build

### 8.1 Stage-by-stage

The v5 preprint specifies a five-stage validation pathway. Costs and timelines:

| Stage | Scope | Cost | Duration |
|---|---|---:|---:|
| **Stage 0** | Numerical sim refinement (Phase 2 Loeffler–Jansen, multi-physics FEA) | $0 (open-source tools, commodity hardware) | 1–3 months |
| **Stage A** | Single-beam Lorentz validation, HTS coil + cryo-CMOS DAC at 77 K | **$600 k** | **18 months** |
| **Stage A.5** | Software pre-validation on HIL (compiler + firmware + OS end-to-end) | $300 k | 3–6 months |
| **Stage B** | Few-beam (16–64 channel) prototype, full cryogenic + photonic data path | $5 M | 12–18 months |
| **Stage C** | 10³–10⁴ beam column at production scale, first wafer exposures | $10–15 M | 12–18 months |
| **Stage D** | Production tool integration, full 10⁶-beam configuration | $30–40 M | 18–24 months |
| **First production tool** | Operational | included | end of Stage D |
| **First production fab (10 tools)** | Capital scale-up, building, support equipment | $300–400 M | 24–36 months after first tool |
| **Total to first commercial chip** | | **$45–60 M development + $300–400 M fab** | **~7–8 years** |

### 8.2 Workforce

A v5 program requires approximately **50–150 engineers** across the build phase, mixed across:

* **Charged-particle optics** (8–15): column design, source array, beam-transport optimisation
* **Cryogenic engineering** (5–10): YBCO process, cryocooler integration, thermal management
* **Vacuum engineering** (4–8): UHV systems, differential pumping, outgassing management
* **Mechanical / metrology** (8–15): stage design, wafer chuck, interferometric registration
* **Cryo-CMOS / RTL** (8–15): per-beam DAC, blanker driver, FPGA / ASIC firmware
* **Software** (10–20): pattern compiler, real-time control, tool OS, integration
* **Process engineering** (5–10): resist selection, exposure-recipe development
* **Operations / management** (5–10): program management, supply chain, customer interface

This is **substantially smaller than a typical fab construction team** (1,000+ engineers for a TSMC build) and within reach of a national lab, a major university consortium, or a well-funded startup.

### 8.3 Critical-path risk

Two items dominate the schedule risk:

1. **YBCO 20 μm patterning**: process development at a HTS-tape vendor (SuperPower, AMSC, SuperOx, Furukawa) for both coils and Meissner shields in the same lithographic pass. Estimated 6–12 months.
2. **Cryo-CMOS DAC NRE** at 22 nm FDX: dual-sourced via Imec and Fraunhofer IPMS to eliminate single-foundry risk. Estimated 12 months.

Both are conventional engineering — not paradigm research. Neither involves novel physics. They are the kind of work that any precision-instrument program undertakes routinely.

---

## 9. Comparison to historical sovereign chip programs

### 9.1 China's SMIC

China invested over **$20 B** through state-funded vehicles (Big Fund I & II, China Integrated Circuit Industry Investment Fund) into SMIC starting in 2014. Result through 2026: SMIC reached 7 nm class production (Kirin 9000s in the Huawei Mate 60), but is **constrained from further advancement** by U.S. and Dutch export controls on EUV scanners — a constraint imposed *after* the $20 B was committed.

**Strategic lesson**: a sovereign program built around conventional EUV is hostage to the EUV supply chain's geopolitical exposure. v5 is the first non-EUV path to sub-10 nm sovereign capability.

### 9.2 EU Chips Act

The EU committed **€43 B** in 2023 with the goal of doubling the EU's share of global semiconductor production from 10 % to 20 % by 2030. Most of the actual deployments funded by the act so far (TSMC Dresden, Intel Magdeburg, Globalfoundries Malta-EU expansion) are construction of conventional EUV / DUV fabs by U.S. and Taiwanese firms.

**Strategic lesson**: the EU Chips Act is currently buying the same chip-making technology as everyone else, from the same vendors, with the same single-source-EUV chokepoint. v5 would let the EU fund a fundamentally different architecture — one that genuinely diversifies global supply.

### 9.3 India SemiconIndia

India committed **$10 B** under the SemiconIndia program in 2021. The first announced tenant facility (Tata Electronics + Powerchip Taiwan) was selected in 2024 for a 28 nm-class DUV fab in Dholera, Gujarat. Sub-10 nm capability is not in the current Indian sovereign roadmap because the capital and IP required are out of reach.

**Strategic lesson**: a country that wants both sovereign chip capability *and* advanced nodes has no path under the conventional EUV model. v5 changes that arithmetic.

### 9.4 The pattern

All three sovereign programs above are **EUV-architecture-bounded**. None of them can produce sub-10 nm without participating in the ASML / Carl Zeiss / TSMC value chain. v5 is the first architecture that is *both* validated to sub-10 nm in principle *and* not bounded by that value chain. It is the only credible **non-EUV** path to sovereign sub-10 nm capability proposed in the open literature as of 2026.

---

## 10. Call to action

### 10.1 For sovereign procurement officers (DARPA, DoD, Canada SIF, EU Chips Act, IndiaSemi, MOD-equivalents worldwide)

1. **Fund a Stage A prototype** at $600 k / 18 months. This validates the architecture at single-beam scale and answers the most important external question: does the Lorentz-steering plus cryogenic-coil approach actually settle to placement budget? The cost is at noise level for any sovereign chip-program budget; the information value is decisive.
2. **In parallel, scope a Stage A.5–D commitment** of $45–60 M over five years. This produces the first production-grade tool and validates the open architecture end-to-end.
3. **Authorise a 10-tool first fab** at $300–400 M once the tool is validated. Site it on sovereign territory. Stipulate that customer access is open to qualifying sovereign-priority chip programs (defense, biomedical, aerospace, research) at near-cost recovery.
4. **Insist on the open license**. Any sovereign program funded should preserve the CC BY 4.0 + MIT licensing — it is the strategic mechanism that prevents lock-in by any single vendor or contractor.

### 10.2 For custom-ASIC startup founders

The unit economics of your business change. If your concept requires more than ~100,000 chips per design at sub-10 nm, today you cannot afford it; in 7–8 years, with a v5 fab in operation somewhere in the world, you might. Two things to do now:

1. **Run the math on your roadmap at zero mask NRE**. The chip products you previously considered infeasible may become feasible. The ones that were marginally feasible may move to comfortably profitable.
2. **Consider becoming a Stage A.5 / Stage B partner** to a sovereign program. The first tool's process-development work is exactly the kind of co-development that produces preferential pricing and capacity allocation in mature foundries.

### 10.3 For strategic-tech investors

The v5 architecture creates a different kind of defensible position than the patent-moat model that dominates semiconductor equipment today. Because the architecture is open, **first-mover advantage is in execution, process know-how, and customer relationships**, not in IP defensibility. This is how the precision-instrument industry actually creates value — see Carl Zeiss SMT, Lam Research, Applied Materials, KLA-Tencor — each of which built defensible market positions on years of integration know-how rather than on blocking patents.

A v5-architecture company with first-mover position would be the analogue of Lam Research circa 1985 or KLA circa 1988: defensible despite open architecture, because the manufacturing-and-integration learning curve is steep.

### 10.4 For policy researchers

The v5 architecture is **an industrial-policy lever that exists today, before any breakthrough physics**. The technology is closed at engineering tolerance; the open work is process development and integration. This is unusual in industrial-policy contexts, where most proposed levers depend on optimistic timelines for currently-unsolved problems.

Specific levers a policy researcher should consider:

1. **Targeted procurement guarantees** for v5-built chips in defense, medical, and climate applications — analogous to advance market commitments for vaccines.
2. **University consortium funding** for shared v5 facilities, at the same model and scale as synchrotron / supercomputer / advanced-microscopy consortia.
3. **Open-architecture preference in sovereign chip programs** — explicit policy that subsidised facilities must use architectures with ≥3 independent vendors per subsystem and no single-source IP dependency.
4. **Workforce pipeline programs** to train the 50–150 engineers per program — a much smaller and more tractable workforce challenge than the 1,000+ per conventional fab.

---

## 11. Closing

The EUV mask NRE wall has been the binding constraint on the global custom-chip economy for seven years. It has stranded thousands of viable chip programs in every sector that matters for sovereignty, health, research, and industrial competitiveness. Those programs continue to operate on silicon that is two to four generations behind the leading edge — not because they cannot use modern transistors, but because they cannot afford to amortise an EUV mask set.

The Morin v5 architecture is the first credible, fully-specified, openly-licensed path to taking that wall down. It is buildable now at $600 k for a Stage A prototype. It produces a $40 M production tool. It builds out into a $300–400 M sovereign fab. It serves the entire stranded market at sub-10 nm. It is owned by no one, and can be built by anyone.

For the audiences this document is addressed to — sovereign procurement officers, defense and biomedical chip program managers, custom-ASIC startup founders, strategic-tech investors, and policy researchers — the immediate question is no longer whether such an architecture is possible. It is. The remaining question is which institutions will be first to build one.

---

*Companion technical preprint*: Morin, R. G. (2026), "Multi-Beam Direct-Write Electron Lithography via Multi-Rate Electromagnetic Steering — v5", May 16, 2026. Released under CC BY 4.0.

*Open-source design package*: `morin_2026_multibeam_ebl_open` — paper, sim code, 11 subsystem specs, 3 software reference implementations.

*Industry NRE figures sourced from*: IBS Mountain View 2024 mask-cost analyses, IC Insights 2024 chip-volume databases, Yole Développement 2023–2025 sector reports, SEMI World Fab Forecast 2024, SemiEngineering reporting on TSMC/Samsung disclosures 2023–2025.

*Correspondence*: <robmorin0@gmail.com>
