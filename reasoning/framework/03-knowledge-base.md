<!-- Asuka v8-v11 framework reference - migration handoff Section 3 - populated 2026-05-21, verbatim. -->

## SECTION 3 — KNOWLEDGE BASE INVENTORY
The Project knowledge base consists of **markdown rule files**, **xlsx activist exports**, **csv data feeds**, **pdf reference research**, and **one HTML dashboard mockup**. Each file is listed with: filename, what it is, why it matters, and either full content or an exhaustive structured summary. Every load-bearing rule, threshold, formula, definition, and worked example is preserved.
### 3.0 File list
```
RULES & FRAMEWORK (markdown):
  asuka-fund-framework.md ............................. Master framework (the constitution)
  position-book-current.md ............................ Live position book, May 2 2026
  position-book-yellow-hat-entry.md ................... Yellow Hat append entry (v10.2 canonical case)
  filer-roster-japan.md ............................... Per-filer playbook profiles
  crmc-archetype-rules.md ............................. CRMC four-lens decomposition rules
  pwer-methodology.md ................................. PWER formal definition + scenarios + gates
  damodaran-mapping.md ................................ Edge classification across Damodaran philosophies
  edinet-monitoring-protocol.md ....................... EDINET surveillance pipeline operations manual
  multi-activist-dynamics.md .......................... Wolf-pack handling, crowding metrics
  regime-context.md ................................... TSE governance reform / BOJ / yen macro overlay
  tse-backtest-v6.md .................................. Quantitative backtest methodology and audit
  asuka_v3_state.md ................................... Generated snapshot of active book (May 3 2026)
FRAMEWORK EXTENSIONS (versioned, all additive unless noted):
  asuka-framework-extension-v9.md ..................... Activist-target/annualized-PWER/wired-tripwires
  asuka-framework-extension-v9_1.md ................... Target≠EV, filed BVPS, liquidity discount, state distributions
  asuka-framework-extension-v10-shadow-follow-screening.md  Universal Five-Gates (Piolax lesson)
  asuka-framework-extension-v10_1.md .................. Fast Defensive Response sub-rule (Aichi Steel)
  asuka-framework-extension-v10_2.md .................. Gate 1.5 Realized Mode 1, Float-Retire Multiplier, DPS Modifier, M1-Internal/External (Yellow Hat)
  asuka-framework-extension-v10_3.md .................. WAC concealment detection (eleven techniques, ten-step protocol, True-WAC math)
DATA EXPORTS (xlsx/csv):
  Asuka_Fund_Portfolio.xlsx ........................... Portfolio export (the live book)
  Silchester_International_Investors_LLP.xlsx ......... Per-filer Activist Insight export
  Dalton_Investments_LLC.xlsx ......................... Per-filer Activist Insight export
  3D_Partners.xlsx .................................... Per-filer Activist Insight export
  Strategic_Capital_Inc.xlsx .......................... Per-filer Activist Insight export
  Ariake_Capital.xlsx ................................. Per-filer Activist Insight export
  Effissimo_Capital_Management...and_SMT_Partners...xlsx  Per-filer Activist Insight export (dual)
  LIM_Advisors.xlsx ................................... Per-filer Activist Insight export
  Grantham_Mayo_Van_Otterloo__Co_LLC.xlsx ............. Per-filer Activist Insight export (GMO-Usonian)
  MIRI_Capital_Management_LLC.xlsx .................... Per-filer Activist Insight export
  NSD_1_yrra1baj.xlsx ................................. Bloomberg NSD activism master pull
  NSD_1_ktcfydh0.csv .................................. Bloomberg NSD activism master pull (CSV form, 1,002 rows)
REFERENCE RESEARCH (pdf):
  Asuka_Claude_Prompt.docx ............................ The Project's onboarding doc (custom instructions in document form)
  Kitagawa_Seiki_investment_thesis_vF.pdf ............. LIM/SC dual-filer thesis writeup
  202602124_E.pdf ..................................... EDINET 大量保有 sample filing (Tamron Effissimo, per file id)
  JOI2019Zang10419.pdf ................................ Zang 2019 Murakami/Japan activism academic paper
  sapporopresentationen202304.pdf ..................... Sapporo Holdings 3D activist presentation (Mode 1b reference)
  SilchesterBank_of_Kyoto__English.pdf ................ Silchester Bank of Kyoto public letter (Tier 1.5 reclassification trigger)
  5343254.pdf ......................................... EDINET filing (likely Murakami / SC reference)
  enTorch_Capital_Partners_Presentation_SGHK.pdf ...... Activist presentation (small-cap thesis reference)
  20260424_SanyoDenki_6516_StrategicCapital_BoardContestEscalation_REVISED.pdf  Sanyo Denki board contest writeup
DASHBOARD MOCKUP:
  Asuka_Active_Book_Daily_Risk_v1.html ................ Visual template for the daily-risk dashboard
```
The PDFs and xlsx files are referenced when researching specific names; the **markdown rule files are the load-bearing framework**, and the **csv/xlsx are the load-bearing data**. Every rule below comes from one of the markdown files or from compiled chat history (user memories), and is preserved or summarized below.
---
### 3.1 `asuka-fund-framework.md` — The Master Framework
**What it is:** The constitution. Defines the fund's edge, position-sizing rules, hold horizons, exit triggers, distinctions vs adjacent strategies, and known risks.
**Why it matters:** Every other file extends or operationalises this one. If only one file is preserved, this is it.
**Full reproduction of all load-bearing content (exhaustive summary; full text reproduced where load-bearing):**
#### §1 — Core thesis (verbatim)
"The Asuka Fund is a concentrated, fully-deployed Japan equity strategy that monetises the gap between (a) the price the market sets when a credible activist or proven long-only quality investor publicly discloses a stake in a TSE-listed company and (b) the price that emerges 2–5 years later as the activist forces capital return, breakup, governance reform, or M&A — or as the long-only investor's underwriting of unrecognised quality is validated by the market."
Two complementary edges: **(1) activist co-investment** — when a credible activist crosses 5%+ in Japan, the announcement re-rates the stock by ~+1.8% on average; the eventual outcome at 15%+ stakes (4–7 years of engagement) is dramatically better but not priced day-one. **(2) Long-only quality compounder co-investment** — GMO-Usonian, Silchester, Ariake, MIRI, Zennor file = fundamental re-rating signal especially when paired with TSE governance reform pressure on sub-1x PBR, sub-8% ROE.
Fund is **long-only, public-equity, no leverage, daily-liquid**. Defining feature: captures activist-driven re-ratings without taking the activist seat. Reference state: **14–18 positions, 100% deployed, weighted-average PWER ≥ 25%, no cash drag**. Capital is rotated, not accumulated. New entry must be PWER-accretive against the lowest-PWER existing position — no "fund from cash" pathway.
#### §2 — Edge classification (Damodaran)
- **Informational — minor.** EDINET filings are public the instant they hit. Marginal edge = process discipline (faster ingestion, joint-holder aggregation, 重要提案行為 language parsing).
- **Analytical — secondary.** Four-scenario PWER, activist-specific historical base rates, dual-lens MoS, SOTP triangulation. Rigorous but reproducible.
- **Structural — PRIMARY.** Three features: (i) behavioural under-reaction (market treats 純投資 as passive — it isn't), (ii) cross-vehicle aggregation (Murakami/Effissimo/Dalton), (iii) TSE governance reform tailwind.
- **Temporal — PRIMARY.** Optimal entry T1–T2 (post-initial-5%-filing, pre-public-escalation). Compresses harvest to ~2.2 years (Effissimo closed-case mean) vs 4–7-year campaign duration.
#### §3 — Target universe rules
**Investor-signal gate (mandatory)** — name must have publicly disclosed 5%+ stake from one of:
- **Tier 1 active activists:** Effissimo + SMT Partners; Murakami network (ATRA, CIE, CIF, Reno, S-Grant, Aya Nomura, Yoshiaki Murakami, Minami Aoyama Real Estate); Oasis; 3D; Dalton + NAVF; Strategic Capital (+ UGS Sunshine LP series); LIM Advisors; Be Brave (Kazuto Izumida); SilverCape; Palliser; Elliott (Japan).
- **Tier 1.5 campaign-runner long-only:** Silchester (reclassified post-Bank of Kyoto).
- **Tier 2 engaged long-only:** GMO-Usonian (Drew Edwards); Ariake; MIRI; AVI Japan; Arcus; Zennor.
- **Tier 2 domestic activists:** Ueshima Kankuro / DOE5% / Naturali; City Index Eleventh; UGS.
**Fundamental screen (after investor gate):**
| Metric | Sweet spot | Notes |
|---|---|---|
| Market cap | ¥30B – ¥500B | activist sizing zone; mega-caps capped 3% NAV |
| PBR | <1.0x (TSE reform); <0.7x (deep value) | screener not thesis |
| ROE | <8% (TSE reform threshold) | gap to sector median |
| Net cash / market cap | >15% (capital return); >20% (deep AVI/GMO zone) | single most important capital-return-pressure ratio |
| Cross-shareholdings / market cap | >15% | float-expansion optionality |
| Foreign ownership | <15% | management not yet pressured |
| Independent director %, payout ratio | low | governance weakness score |
| Conglomerate / parent-sub | present | SOTP unlock |
| Founding family + cross-holder bloc | 30–50% MBO optionality; >50% no MBO catalyst = avoid | >30% diffuse large-cap consumer/pharma = Oasis failure pattern |
**Hidden-tech five-gate screen (pre-activist L2):** (1) PBR <1.3x AND 5-year return ≥40pp below TOPIX; (2) disclosed segment in advanced ceramics / semicon materials / AI infra / specialty films / EV-battery / precision motors; (3) segment ≥25% OP (≥40% high-conviction); (4) Tier-1 trigger ≤90 days (sell-side upgrade citing segment, CMD, buyback ≥3% float, cross-shareholding unwind); (5) cost-of-capital mismatch. **4/5 = 3% L2; 5/5 = 4–5%; +activist = L1 5–7%.** No WAC gate; floor = legacy business at sector PER.
**Disqualifiers:** "Pure investment" filing language is NOT a disqualifier (boilerplate). Founding family + cross-holder bloc >50% with no MBO catalyst + Oasis-failure-pattern = disqualifier. Mega-caps with ongoing accounting/governance scandals get hard 3% size cap until left tail closes (Nidec). **Activist-as-net-seller triggers WAC cross-check inversion rule.** Murakami Stage 5 confirmed when ALL FIVE: (i) aggregate stake declining from peak, (ii) buybacks completed, (iii) stock at 52-week high, (iv) price above consensus, (v) peak stalled below 33% veto.
#### §4 — Position sizing and concentration philosophy
| Layer | Description | Sizing | Target weight | Action bias |
|---|---|---|---|---|
| **L1** | Binary catalyst <6 mo, confirmed activist, imminent proposal | 7–12% per position | 50–60% pre-AGM, 20–25% post-AGM | ADD on dips, HOLD at full size, TRIM post-resolution |
| **L2** | New activist <6 mo OR 3–9 mo catalyst | 3–5% | 10–15% | Build through escalation tripwires |
| **L3** | Quality compounder + engaged long-only; 12–24 mo | 2–8% | 30–40% | Add on fundamental confirmation, harvest on multiple expansion |
| **L4** | Merger-arb sleeve (separate) | 1–3% | <10% | Annualised PWER ≥25%, days-weeks binary |
**Hard rules:**
- Single position cap: **12%** (L1 only)
- Per-activist cluster cap: **25%** of NAV
- Per-event cluster cap: **50%** of NAV (June AGM cluster)
- Position count: **14–18**
- Cash target: **0%** — rotated, not accumulated
- **PWER entry threshold: 20% absolute** (25% annualised for L4); new positions must be accretive against displaced
**PWER:** `PWER = Σ (Pᵢ × Rᵢ)` across four scenarios (Bear / Base / Bull / Extreme Bull). **PWER is a DISCRETE signal** (moves on EDINET filings, AGM outcomes, escalations, earnings) — NOT a continuous rebalancing input. Backtested: mechanical PWER-proportional rebalancing → 22.3% vs event-driven 23.3%.
**WAC cross-check:** if current px is **>15% above activist WAC**, co-investment edge is gone; standalone event-driven only. Canonical Sanyo Denki closing rule.
**MoS dual-lens:** Earn-MoS = (IV − Px)/IV with IV = 5-year OP × 0.7 / 0.08; Asset-MoS = (1 − PBR) × 100. Both accounting; activist edge = gap to strategic value tagged by strategic-source category.
#### §5 — Hold horizon and exit triggers
Default harvest **~2.2 years** (Effissimo closed-case mean). L4 = days–weeks. L3 = 12–24 mo. Fund explicitly avoids 4–7 year full-arc.
**Three-stage exit:** (1) Partial harvest 50–60% at catalyst resolution. (2) Trail-stop residual 40–50%; trim on PWER <15% or thesis dilution. (3) Full exit on activist signal reversal.
**Other exit triggers:** PWER compression <15% absolute; liquidity ceiling (10-day ADV); activist files reduction; cluster cap breach; bear case probability >40%; dividend/buyback announcement post-extraction = trim signal NOT add signal.
**NOT exit triggers:** stock above consensus; single-Q earnings miss with activist still accumulating; macro drawdown; calendar rebalancing.
#### §6 — Distinct features vs adjacent strategies
Asuka vs passive value: requires identified catalyst. Vs loud activist: rides coattail in liquid wrapper, harvests at 2.2yr. Vs US-style 13D: enters T1–T2 not T0 pop. Vs risk arb: L4 only. Vs quant value: name-by-name underwritten, no factor harvesting. Vs long-only Japan equity: near-zero index overlap.
**Cleanest one-liner:** "Asuka is a public-equity, liquid wrapper around the corporate-governance-change asset class that activists privately monetise."
#### §7 — Known risks and failure modes (full list, all load-bearing)
1. Activist trapped in stalemate (long-duration drag) — Mode 2/3 >20% can grind 4–6 yrs; Ricoh/Teijin live. Mitigation: 2.2yr default + partial harvest + cluster caps.
2. **Oasis failure pattern** — founding family bloc ≥30% + large-cap diffuse + consumer/pharma. Kao, Ain, Kusuri-No-Aoki = historical losses. Yakult Honsha currently fits — kept on watch list, NOT in portfolio.
3. SOTP-as-floor false security — point estimate not asset floor. Don't over-correct PWER on SOTP alone.
4. WAC drift past entry — rally 15%+ above WAC → co-investment edge closed. Sanyo Denki precedent.
5. Murakami internal redistribution misread as fresh accumulation — Change Report 15+ often internal transfers. Always read joint-holder section; ATRA direct-filer vs CIE-only = upgrade tripwire.
6. **Phantom data / aggregator drift** — kabupro/irbank/maonline lag/corrupt. EDINET XBRL primary fetch rule; DATA_QUARANTINE override on conflict; stamp `edinet_doc_id`.
7. Liquidity-induced stop-out — concentrated <¥20B mkcap thin float. ADV-based hard caps (Inui 1.5%, Pegasus 0.5%, micro-cap DOE5% basket as combined).
8. June AGM cluster correlation — up to 50% NAV in same binary quarter. Explicit 50% cluster cap.
9. **Activist regulatory regime change** — LDP/METI proposals to lift EGM-convocation and proposal-rights thresholds (300-vote route abolition; 1% → potentially 5%). Existing book at 5%+; impact on new entry, monitor 18–24mo lag.
10. Catalyst-passes-without-resolution drift — AGM votes down, activist persists but stock re-bases. Post-failed-AGM dislocation entry window = feature, not bug.
11. Behavioural drift / framework decay — refresh discipline rule (price ≤3d, EDINET ≤7d, news ≤7d) + `action_verified_date=today` stamp.
12. Fact-check failure (MoneyForward May 2026 lesson) — separate CONFIRMED FACTS (EDINET/IR/TDNet with date) from INFERENCE; verify fiscal year-end + 定款 before assuming AGM timing; pull 有報 大株主 list rather than estimating ownership.
---
### 3.2 `position-book-current.md` — Current Position Book (May 2 2026)
**What it is:** One-section-per-name reference for every Japanese name actively researched, watched, held, passed, or exited. ~80 entries. Status flags: **LIVE / WATCH / PASSED / EXITED**. Stale items marked `⚠ NEEDS REFRESH`.
**Why it matters:** This is the live book. The successor needs to know what is currently owned, the anchor activist, the PWER, the hard stops, and the upgrade tripwires for every name. Section F provides a master summary table.
**Reproduction strategy:** Section A (CORE PORTFOLIO — LIVE) is reproduced in essential detail below; Sections B/C/D/E/F are summarised exhaustively.
#### Section A — Core portfolio LIVE positions (the active book)
(Each entry below records the anchor activist, stake, current sizing, PWER, hard stops, upgrade tripwires, and open verification items.)
**Square Enix (9684) — L1 capped 12% NAV.** Anchor: 3D Investment Partners 18.53% (Mar 3 2026 EDINET); Dalton supportive. Tier R language; Cost-Cutting objective per Bloomberg; public 93-slide presentation Dec 8 2025. PWER ~+33% blended. Dashboard reads ¥2,488; bear/base/bull/x-bull = -10/+25/+60/+120% with weights 30/35/25/10. 3D underwater on latest add ¥2,500–2,600. Catalyst sequence: **May 12 2026 Q4 FY26 earnings → June 2026 74th AGM proxy battle (binary)** → 3D shareholder proposals filed in May convocation notice. **Hard stop**: bear case ¥2,240 (post-AGM defeat). Time stop: trim to L2 within 30 days post-AGM. Open: track 3D vs Fukushima 19.28% founder bloc.
**Ricoh (7752) — L1/L2.** Anchor: Effissimo + SMT Partners 24.77% (deep Mode 2). Tier P language for years; Toshiba-style silence pattern. PWER ~+8–10% pre-SOTP; ~22–25% under SOTP-as-floor (digital services unit). ⚠ NEEDS REFRESH price. Catalyst: multi-year private; no near-term binary; fundamental floor from net cash + separable segments. OA-sector MBO precedent (Konica/Toshiba). **Hard stop**: Effissimo trim filing = exit signal. SOTP caveat — point estimate, not floor; transformation costs consume book.
**Teijin (3401) — L2.** Anchor: Effissimo **16.44% → 19.26% Apr 14 2026** (Change Report S100XYZD, +5.05pt in 18 weeks ≈ 1.25pt/month, 3–4× normal). **Mode 1 → Mode 2 transition FIRED.** Goldman Sachs PB facilitation verified (GS NEW 5.0% Mar 31 → 1.74% Apr 22 = −3.26pt) vs Effissimo +1.73pt same week. PWER upgrade fired Apr 21 — recalibrate L2 → L1. ⚠ NEEDS REFRESH explicit PWER table. Catalyst: Healthcare hidden-asset SOTP unlock; PBR ~0.5x; conglomerate restructure. **Hard stop**: Effissimo <16% on next change report.
**Tamron (7740) — L2.** Anchor: Effissimo 12.04% Oct 2025 → 13.06% → 14.12% Dec 3 2025 → **15.3% Mar 11 2026**. WAC ¥507 vs current ~¥1,083 = **+113% above WAC → co-investment edge gone, standalone PWER only**. PWER ~+28–30% standalone (Mode 1 + Mode 3 simultaneously; Sony cross-shareholding unwind catalyst). Catalyst: April record date passed; **June 2026 AGM first hard binary**. Sony cross-shareholding disposal structurally separate. **Hard stop**: Effissimo reduction filing.
**Optex Group (6914) — L2 building toward 8%.** Anchor: GMO-Usonian 5.0% Feb 25 2026 initial. WAC **¥2,629** confirmed via EDINET. Tier 2 quality signal not catalyst engine. PWER ~+28%. Next binary: 変更報告書 showing GMO accumulating beyond initial 5.00% (H.U. Group precedent 5.19% → 10.8% over 32 months). **Hard stop**: GMO crosses below 5%. WAC ceiling: ¥3,023 (WAC × 1.15).
**Kansai Paint (4613) — L3 3% NAV.** Anchor: Silchester 5.05% (initiated). Tier 1.5 post-Bank of Kyoto reclassification — engaged not passive. Asuka WAC ¥2,511 (underwater). PWER +20.8% from ¥2,380. Activist PWER from Silchester WAC = +14.5%. Catalyst: TSE governance tailwind; May 11 2026 Q4 FY26 earnings; Kansai Nerolac India hidden growth; Africa divestiture optionality. **Hard stop**: Silchester reduces <4% = exit; or breaks ¥2,050 with Silchester 5%+ (deep-floor add opportunity NOT stop). Upgrade trigger: Silchester crosses 6%+.
**Shift Inc. (3697) — L2/L3.** Anchor: Arcus 7.14% (Apr 2026). Arcus WAC ¥737 vs ¥662.6 prior reference = Arcus underwater. Founder 30.62% controlling stake caps governance variance. Tier 2 deep-value signal, NOT activist. PWER ~+18% mid-band; earlier 29–33%. Catalyst: Q1 FY26 earnings Apr 14 (post-print integrated); margin recovery + AI pipeline; NO AGM proxy mechanism (founder bloc). **Hard stop**: Arcus <5%; founder forced sale.
**Jade Group (3558) — L3 2%.** Anchor: Arcus 6.06% + AVI Japan ~5.3% — dual engaged-investor. PWER ~+20% mid-band. M&A optionality (Ant Capital + Alpén). Catalyst: April 14 full-year earnings passed; M&A optionality on parent-sub with Ant. ⚠ Illiquidity ceiling at 2–3% NAV.
**Inui Global Logistics (9308) — REDUCE/EXIT.** Anchor: LIM 5.44% (Feb 20 2026, WAC ¥1,489) + MIRI 5.06% (Aug 2025). **Alphaleo confirmed NOT LIM** — Alphaleo = Dubai DIFC investment manager (2019 EGM history; peak 21.86% → 8.13%; Hokuetsu/Oasis-failure pattern with founder Inui family winning every contested vote). PWER collapsed after Q1 FY2026 EPS ¥10.70 vs ¥35.14 (-70% YoY net income). **Hard stop ALREADY TRIGGERED — fundamental break.** Execute reduction; redeploy to Ricoh, Kansai Paint, Pegasus.
**Hyakugo Bank (8368) — L3 2%.** Anchor: Ariake 5.06% (Jan 2026 near 52w trough). Tier 2 friendly engagement. PWER +14–28% range. Ariake estimated cost ~¥1,200–1,300 vs ¥961 March 2026 = underwater entry → **highest-conviction Ariake escalation signal pattern** (Ariake escalates fastest when underwater per Suruga/Hokkoku/Chiba Kogyo precedent). Catalyst: May 8 2026 earnings; June 2026 AGM. **Hard stop**: Ariake <5%.
**Seibu Holdings (9024) — Active L2.** Anchor: 3D 5.75% (CEO change catalyst Feb 2026). PWER ~+20–22%. Catalyst: CEO change; conglomerate SOTP unlock; June 2026 AGM watch.
**Senko Group (9069) — L1.** Anchor: **combined Dalton + NAVF ~18%** (NAVF 10.88% via Bloomberg ACTV supersedes earlier 7.1% single-filer). Conglomerate breakup pressure. Earlier reading +15% TRIM — **REVISED on NAVF dual-filer confirmation: re-rate to L1 high-conviction, REVERSE prior TRIM call.** Catalyst: June 2026 AGM; logistics pricing tailwind from 2024 trucking labour reform. **Hard stop**: combined Dalton+NAVF <15%.
**Sanyo Denki (6516) — NO ADD.** Anchor: Strategic Capital 17.0%. Apr 21 2026 board contest escalation (campaign website launched + shareholder proposal filed). SC WAC est **~¥3,400–3,800**. Original PWER 22–32%; **REVISED ~12–13% standalone after Apr 24 WAC cross-check — current ¥5,660 = 50–65% above SC WAC. Co-investment edge closed; queued add WITHDRAWN.** Per v10.2 DPS modifier (SC bucket-3 mid +57–66% HPR) → 0.5× L1 = 6% NAV cap → **marginal trim 7% → 6%**. Re-entry only ¥3,900–4,400. **Hard stop**: SC reduction filing. June 2026 AGM board contest binary.
**Tayca (4027) — L2 (DOE5% basket).** Anchor: Ueshima personal + Naturali + DOE5% combined. Active 変更報告書 Mar 16 2026. PWER ~+11–13%. Catalyst: June 2026 AGM DOE5% proposal binary; titanium dioxide specialty chemicals; sub-1x PBR; cash-rich. **Hard stop**: Ueshima/DOE5% reduction across basket. Sized as single correlated DOE5% basket position.
**Fujikura Kasei (4620) — L2 (DOE5% basket).** Anchor: Ueshima 5.21% + Naturali 2.46% + DOE5% 0.74% = **8.41% combined wolf-pack** (May 2 2026). Active 変更報告書 Mar 13 2026. PWER ~+10–12%. Catalyst: June 2026 AGM DOE5%. **Hard stop**: cluster <7%. Cost ¥1,100 blended estimate; ⚠ verify exact 取得資金 from EDINET.
**Gun Ei Chemical (4229) — L2 (DOE5% basket).** Anchor: Ueshima/Naturali/DOE5% cluster. PWER ~+10–12%. Catalyst: June 2026 DOE5% AGM demand binary. Paired with Miyoshi for sizing.
**Miyoshi Oil and Fat (4404) — L2/L3 (DOE5% basket).** Anchor: Ueshima/Naturali/DOE5% cluster. Micro-cap liquidity constraint. PWER ~+10–12%. Catalyst: June 2026 AGM. Sized smaller than Gun Ei due to ADV ceiling. **CORRECTION May 14/26 (memory):** Dec 31 FYE NOT March; 2026 AGM late March already passed (per IRBank E00881, 2025 AGM Mar 26). Reclassify L2→L3. Q1 FY26 +54% OP YoY. GS Intl/MS MUFG/Integrated Core (Asia) flagged 空売り (institutional short). Hold 1.5%, no add @¥2,106. Re-arm: fresh 変更報告/public letter/interim div/<¥1,850. **Rule: DOE5% basket FYE heterogeneous — do NOT size as single AGM calendar.**
**DaikyoNishikawa (4246) — L2 2%.** Anchor: Murakami Taketeru via MI2 5.01% + MI5 0.01% (combined 5.09% filed Apr 3 2026, obligation date Mar 27). Asuka entry ¥841. ⚠ Verify exact MI2 取得資金 from XBRL. PWER ~+21% at ¥841 (just clears 20% gate). Watch for: City Index Eleventh separate filing (PWER → ~28%, add to 3%); Murakami stake crosses 7%+; shareholder proposal pre-April 2026 record date (passed); buyback/dividend response. **Hard stop**: MI2 reduction; Toyota parent retaliation.
**Nidec (6594) — L2 2–3%.** Anchor: Oasis ~6.74% (Mar 11 2026) — Mode 4 Crisis Cleanup. Public engagement Day 1. PWER ~+20–22% with binary on TSE Special Alert de-designation by Oct 2026 (~75–80% probability). Catalyst: TSE de-designation October 2026; financial statement restoration; Nagamori 12% personal stake = forward overhang. **Hard stop**: TSE delisting decision; second accounting irregularity. Hard 3% size cap (mega-cap accounting scandal rule).
**Yellow Hat (9882) — L3 STARTER 3% NAV.** NEW LIVE ENTRY May 11 2026 — **canonical Realized Mode 1 / Gate 1.5 position under v10.2.** Anchor: Strategic Capital 13.83% (peak Dec 17 2024 standing). Tier R. SC blended WAC ~¥1,250–1,350. Filing language Tier R 純投資及び状況に応じて重要提案行為等. Accumulation paused 17 months; no public letter, no campaign site, no shareholder proposal. PWER **+23.9% blended** (post float-retirement multiplier). Gates: Gate 1.5 FIRES (45% payout + 100% TPR MTP FY26–28 ✓, 11.4% float retirement TTM ✓, SC paused 17 months no escalation ✓). G5 second-leg: 3 STRONG LEGS (MTP-locked TPR cadence + 2 consecutive ATH earnings + TSE PBR mandate at 1.04×). DPS modifier: SC bucket-3 mid → 0.5× standard L3 → 3% NAV starter. M1 sub-tag: **M1-Internal-Carry**. Strategic source: CASH primary, GOV secondary. Catalyst: Late June 2026 68th AGM (board refresh administrative); FY27/3 Q1 earnings ~Aug 2026. Entry zone **¥1,400–1,500**; do not chase >¥1,580; no add >+15% of SC WAC. Funded by Alfresa 2% → 0 and Daito Trust 2% → 1%. Hard stops: SC <13%; MTP downward revision; FY27/3 Q1 disappointment + capital return slowdown. Upgrade L3→L2: SC 15%; SC campaign site or public letter; specific ¥-denominated FY27 buyback ≥¥10B; UGS/Be Brave co-files.
#### Section B — Watch list (researched, not in book — summary)
| Ticker | Name | Anchor | Status |
|---|---|---|---|
| 6262 | Pegasus | Be Brave 11.87% (Feb 20 2026 CR No. 4), WAC ¥793 | L2 ENTRY PENDING 3–4% NAV funded by Inui reduction; entry ¥760–810; no chase >¥912; upgrade L1 on Be Brave >15%, co-filer (UGS/SC), public letter, May convocation proposal |
| 2267 | Yakult Honsha | Dalton Kizuna escalated Apr 24 2026 to board contest, 2 nominees for June 74th AGM | **DO NOT INITIATE** — Morningstar FV ¥1,311 vs ~¥2,600 = large-cap consumer Oasis-failure-pattern risk |
| 2972 | Sankei Real Estate | Tiger/Lion (Tosei+GIC) friendly TOB ¥125,000 Jan 6 2026, extended 6×; Murakami (CIE+Aya Nomura) 11.22 → 17.19 → 19.35% (CR No.6 Apr 6 2026) | L4 ARB 1.5% TARGET. Annualized +79% over 18 days to May 18; bear floor ¥110K (TOB withdrawal); Murakami reduction = stand down |
| 4493 | Cyber Security Cloud | SilverCape accumulation | WATCH conditional on 2nd institutional filer; PWER ~+69% |
| 2207 | meito | UGS Asset Management ~5% | WATCH limits ¥2,600–2,750; if SC co-files → flip immediately (TOB-capable joint vehicle) |
| 6675 | Saxa | AVI Japan 7.37% (No.2 Mar 16 2026), WAC ~¥5,800 | STARTER L3 1.5–2%; CASH source (¥240/sh div FY26-30) |
| 9742 | Ines | AVI 6.02% (No.1 Jan 23 2026) + Effissimo 12.35% dual-filer, WAC ~¥1,700 | STARTER L3 0.75%; SUB source |
| 8011 | Sanyo Shokai | AVI 11.55% lead (Mar 18 2026) + Sapphireterra ¥1,200/sh AGM proposal Apr 1 (rejected Apr 14), WAC ~¥3,500 | STARTER L3 0.75–1%; SUB source; May/June 2026 AGM binary |
| 5930 | Bunka Shutter | Dalton 15.48% (WAC ¥1,664) + SC ~5–6.5% ≈ combined 21% | L2 entry candidate near-ideal April 24 timing; PWER +28.6% at ¥1,829; April 26 proposal filing deadline; June 22 AGM; broken buyback ¥2B authorized May 2025–Mar 2026 zero shares purchased |
| 8923 | Tosei | GMO + Dalton dual-activist (RE sector) | WATCH; PWER +30.4%; June 2026 AGM cluster |
| 3994 | Money Forward | ValueAct 14.39% (S100XRVY Mar 24 2026), WAC ¥4,290 | WATCH L3 ~+22%; FY end Nov 30, AGM Jan-Feb (NOT June); Q2 FY26 Jul 26 print; Tsuji 16.27% (May 25 有報) |
| 5332 | TOTO | Palliser Capital top-20 Feb 17 2026; Value Enhancement Plan ¥554B / +55% upside on Advanced Ceramics ESC | WATCH — arrived too late; Asuka framework miss prompted Hidden-Tech Trigger module |
| 2802 | Ajinomoto | Palliser Phase 2 (formal Value Enhancement Plan) | L3 STARTER 3–4% candidate; passes 20% gate; May 7 earnings; ABF segment review |
| 6273 | SMC Corporation | Palliser Phase 2 Apr 26 2026 (¥600bn buyback proposal, 50% upside) | WATCH FRESH SIGNAL — deep dive needed |
| 7347 | Mercuria Holdings | SilverCape 5.10% May 2025 ¥831, Mode 1 | PASSED (below 20% PWER hurdle); reactivate on SilverCape >7% or public letter |
#### Section C — Exited / closed theses
- **Exedy (7278) — EXITED Apr 28 2026.** Murakami Stage 5 confirmed. Aggregate 22.45% peak Oct 2024 → 10.91% Feb 2026 (CR No.24). Reno 4.63→0.98%; CIF 3.20→6.05% via internal Reno transfer (NOT fresh). ¥45B+ buybacks (~14% float retired). Aisin parent 13.64→3.87% Jun 2024. Stock ¥6,130 at 52w high, +25% above ¥4,900 consensus. Protean Electric EV M&A capex risk. PWER −7%. **Re-entry watch ¥4,500–5,000 post-Murakami fully out.**
- **Daito Trust (1878) — EXITED.** Silchester 8.5%. Trimmed to fund Kansai Paint and Ajinomoto. PWER 6–10%.
- **Alfresa (2784) — EXITED.** Silchester 12.0%. PWER 9% (no catalyst).
- **Foster Electric (6794) — TRIMMED.** AVI Japan ~5% legacy.
- **Toyota Industries (6201) — EXITED Mar 30 2026** at premium TOB close. Elliott 7.14% → 0%.
- **Konica Minolta (4902) — PASSED.** Effissimo 9.55%; loss-making → activist needs balance-sheet capacity. No founder swing-vote.
- **Nikkon Holdings (9072) — TOO LATE.** Farallon 23% (WAC ~¥2,700) + Oasis 17% = ~40% (past 33.4%). Stock +67% 12M, +200%+ from Farallon entry. Re-entry ¥3,800–4,200 or stand down.
- **Hi-Lex (7279) — PASSED.** Zennor 7.4%; Tier 2 long-only, NOT hard activist. PWER ~+6% from ¥2,738.
- **KH Neochem (4189) — PASSED on WAC cross-check.** SC 5.49% → ~15% in 5 weeks; WAC ¥2,737. Current ¥2,927 = 7% above WAC. PWER ~7.6%.
- **Kitagawa Seiki (6327) — PASSED.** SC 5.01% (Feb 2026); LIM 18% accumulated 12 months 2025. PWER ~7.6% at ¥2,927 (7% above SC ¥2,737 WAC).
- **QOL Holdings (3034) — DATA QUARANTINE.** Will Field 8.69% (real per Will Field Oct 2025; claimed 17.73% in dashboard was phantom). Calibrated_at_price ¥1,369 (real spot ~¥1,790). Same flag on 7725, 3776, 4493.
#### Section D & E — Watch researched + names from brief without prior research
The list extends through Tokyo Steel (5423, Oasis 6.25% Apr 2 2026, Ikegaya 30% bloc = Oasis-failure danger zone), Niterra (5334 ex-NGK Spark Plug, ValueAct 5.27%), Obara Group (6877, Zennor 5.13% underwater −13.2%), Ohki Healthcare (3417, Capital Mgmt 5.01%), Sekisui Jushi (4212, NAVF, L3 candidate), Goldcrest (8871, Sapphireterra), Primo Global (PASSED, off-thesis), Inter Action (7725, SilverCape 14.85% + Kaname Capital combined 28.9%, DATA QUARANTINE flag), Broadband Tower (3776, SilverCape ~11%, liquidity-constrained), Enplas (6961, PASSED), Digital Holdings (2389, REFERENCE — canonical SilverCape Mode 3), Yamato International (8127, SilverCape 12.79%), Casio (6952, 3D 5.03% NEW, Nomura PB facilitation), MOL (9104, Elliott "significant" <5%, BLUE ACTION 2035 MTMP critique), NXHD (9147, Elliott 5.04% NEW S100Y15W), Iwabuchi (5983, Ueshima individual REFERENCE), Nippon Felt (3512, Ueshima+Naturali+DOE5% joint-holder structure REFERENCE), Chuo Hatsujo (5592 OR 5992 — ticker disambiguation), Rhythm (7769, DOE5% closed positive), YCP Holdings Global (9257, DOE5% pending), Showa Pax (3954, DOE5% combined 6.34% Dec 19 2025 — PASSED at high). Names with no prior research surfaced: DOWA Holdings (5714), Santen Pharma (4536), Daiwa Industries (6459), Sumitomo Metal Mining (5713), Okumura Group (1833), Hodogaya Chemical (4112), Chugoku Bank, Okinawa Bank, Shiga Bank (8366 REFERENCE — Ariake), Daidoh (REFERENCE — SC canonical win, +279%), Taiheiyo Cement (REFERENCE — Palliser P1).
#### Section F — Master summary table
Reproduces 82 rows of ticker × name × status × last PWER × refresh-needed flags. The 26 LIVE positions form the active book (Square Enix through Nidec plus DOE5% basket + DaikyoNishikawa + Sankei REIT watch + Yellow Hat NEW). 
#### Section G — Triage priorities
**Immediate refresh:** Tsurumi Mfg 6351 (confirm L1 status), Senko 9069 (recompute with combined Dalton+NAVF ~18%), Bunka Shutter 5930 (Apr 26 proposal filing deadline outcome), Nidec 6594 (TSE remediation timeline + Oasis stake), Money Forward 3994 (Q2 FY26 print Jul 26; AGM Jan-Feb not June).
**Fresh dives needed:** DOWA, Santen, Daiwa Industries, SMM, Okumura, Hodogaya Chemical, Chugoku/Okinawa Banks, Chuo Hatsujo ticker, Daidoh ticker.
**Stale price refresh:** Hyakugo Bank, Optex (WAC), Saxa, Ines, Sanyo Shokai.
---
End of Part 2. Part 3 will reproduce / summarise the remaining knowledge files: filer-roster-japan.md, crmc-archetype-rules.md, pwer-methodology.md, damodaran-mapping.md, edinet-monitoring-protocol.md, multi-activist-dynamics.md, regime-context.md, tse-backtest-v6.md, asuka_v3_state.md, and the v9 / v9.1 / v10 / v10.1 / v10.2 / v10.3 framework extensions. After Section 3 is fully covered I will move into Sections 4–10 (Methodology, Frameworks/Formulas/Thresholds, Inputs/Tools/Connectors, Outputs, Standing Rules, Worked Example, Implicit Knowledge & Gotchas).

### 3.3 `filer-roster-japan.md` — Per-filer playbook profiles
**What it is:** Comprehensive per-filer reference for every tracked filer. Each entry includes domicile/founder, archetype (CRMC Category), hold horizon, default filing language tier, recent campaigns with stakes/dates/outcomes, anomaly flags, and known entity aliases.
**Why it matters:** The lookup table the layer consults whenever a filing arrives. Without this, archetype-fit, base-rate calibration, and anomaly detection are not possible.
**Exhaustive structured summary (each filer carries archetype tier, key empirical base rate, signature playbook, and live Asuka book exposure):**
**Ariake Capital** — Tokyo; Katsunori Tanaka (ex-GS bank analyst, 19yr); ¥48B AUM long-only. **Tier 2 engaged long-only**; sector specialist: Japan regional banks exclusively. Friendly engagement (with management, not against). Multi-year (3–5+ yrs); files 5–6% and parks. Holdings: Hyakugo (8368), Ogaki Kyoritsu (8361), Aichi Financial Group (7389), Shiga (8366), Suruga (8358). Past escalations Suruga / Hokkoku FHD / Chiba Kogyo. Default Tier P (純投資). **Anomaly flag: underwater entry is the strongest escalation signal** (inverse of most activists). Empirical: low absolute return per campaign, high consistency — quality ballast, not catalyst engine.
**AVI Japan (Asset Value Investors Ltd / AJOT)** — London; AVI Japan Opportunity Trust plc LSE-listed; founded 1985, AVI Japan 2018. Joe Bauernfreund CIO. **Tier 1 hard activist** with constructive UK long-only style. Long-form engagement letters, detailed SOTP, board engagement. Synchro Food precedent (won board seat via EGM). November 2025 £38B raise underwriting fresh wave. 3–7yr holds; targets net cash + investment securities >50% mcap. Default Tier R (純投資・重要提案行為等). Holdings: Saxa (6675, 7.37% Mar 16 2026, WAC ~¥5,800, CASH tag), Ines (9742, 6.02% No.1 Jan 23 2026 + Effissimo 12.35% dual-filer, WAC ~¥1,700, SUB), Sanyo Shokai (8011, 11.55% lead Mar 18 2026, WAC ~¥3,500, SUB), Foster Electric (legacy ~5%), Jade Group (3558, 5.3% with Arcus). Empirical: n=39, mean +27.6%, median +18.8%, 46% >+20%. **Sapphireterra co-filing at Sanyo Shokai = explicit watch (aligned vehicle).**
**Be Brave (Kazuto Izumida 泉田和人)** — Tokyo Tamachi; vehicle Be Brave 株式会社 / ESG投資事業組合. **Tier 1 domestic hard-activist**. ~99% margin leverage via 立花証券 = forced urgency. Stealth fund. 12–18mo to win. Targets sub-1x PBR + weak governance + low foreign + cash-rich. Default Tier R. **Playbook signature: silent accumulation → monthly 変更報告書 ratchet → engage privately → vote-against-CEO if stalled → DOE + buyback win.** Holdings: Toyo Securities (8614, 2024 — CEO Kuwabara forced withdrawal 5 minutes before AGM via advance proxy; 4 co-filers Be Brave + UGS + Capital Mgmt + Epic Group; canonical wolf-pack), Nishikawa Rubber (5161, 2025 — DOE 8% adopted, div ¥44→¥204 4.6×, stock split, ¥7.4B buyback, +87% in 13mo — most-cited DOE win), Pegasus (6262, 11.87% CR No.4 Feb 20 2026, WAC ¥793 — Asuka L2 entry candidate), Tomoe (5301, smaller stake L3 starter).
**Murakami network / City Index Eleventh (umbrella entry)** — Tokyo; Yoshiaki Murakami 村上世彰. **Tier 1 hard activist** capital-return extractors via buyback-then-exit. Eight Japan campaigns running simultaneously in 2025 (3rd-busiest activist globally). Corporate structure (verified via 2020 Toshiba Machine TOB disclosure):

```
Yoshiaki Murakami
 ├─ ATRA (apex; Yoshiaki ~66.5%)
 │   └─ Office Support
 │        ├─ City Index Eleventh/First/Third/Maiko/Hospitality/Holdings
 │        ├─ Reno Corporation
 │        ├─ S-Grant Corporation
 │        ├─ Fortis Corporation
 │        ├─ C&I Holdings
 │        └─ Rebuild Corporation
 ├─ Aya Nomura 野村絢 (eldest daughter) — direct individual + Minami Aoyama Real Estate
 ├─ Takateru Murakami 村上貴輝 (son) — direct individual + MI2 + MI5
 ├─ Aphrodite — affiliated, verify joint-holder section
 └─ Historical: Emi Miura, Toshihide Suzuki, Fuminori Nakashima
```


**Five-step playbook:** (1) Silent accumulation across vehicles to 5%+ with "純投資・重要提案行為等を行うため" language. (2) Private capital-return demands (DOE/ROE targets, specific buyback amounts). (3) Public escalation if ignored (株主提案, AGM contests). (4) Stake escalation toward 33.4% veto. (5) Buyback-then-exit OR M&A trigger. 18–24mo target. JOI 2019: closed-case Murakami trades historically >20% annualised. Bloomberg ACTV: n=92, mean +20.4%, 44% >+20%. Default Tier R (純投資・重要提案行為等). Holdings: Exedy (7278 — peak 22.45% Oct 2024 → 10.91% Feb 2026 — Stage 5 confirmed; Asuka CLOSED Apr 28 2026 PWER −7%), DaikyoNishikawa (4246 — MI2 + Takateru 5.09% Apr 3 2026; Asuka L2 ¥841), Sankei REIT (2972 — CIE+Aya 11.22→17.19→19.35% CR No.6 Apr 6; three CIE filings in 8 days +5.96pt; Asuka L4 ARB 1.5%), Rengo (3941 ~5% combined, L3 ballast), Wavelock HD (7940 Nov 2025 — ATRA direct-filer + Aya Nomura + CIE = 14.93% canonical ATRA-direct precedent), Takashimaya (Aya built and exited near ¥2,479 peak ~¥205B notional, +50% from disclosure low), Fuji Media (~16% combined forced ¥235B buyback). **Anomaly flags:** ATRA-direct-filer = +1 sizing tier (Wavelock precedent); Internal redistribution at CR No.15+ = NOT fresh accumulation (Exedy No.24 canonical — CIF "buying" 6.05% was receiving 2.85pt from Reno selling); **Stage 5 confirmation requires ALL FIVE conditions firing simultaneously.**
**Dalton Investments / Nippon Active Value Fund (NAVF)** — Dalton: US Santa Monica, Jamie Rosenwald & Gifford Combs founded 1998. NAVF: LSE-listed, managed by Rising Sun Management (Rosenwald/Combs/Paul ffolkes Davis); Dalton sub-advisor. **Tier 1 dual-vehicle hard activist *when paired***. Dalton standalone Tier 1.5 (Activist Insight n=61, mean +21.9%, only 33% >+20%). **Combined NAVF+Dalton: n=18, mean +57.4%, 78% >+20% (top decile).** Treat as one filer for sizing. 1–2 yrs typical. Default Tier R (NAVF EDINET 保有目的: "経営の助言や重要提案行為"). Holdings: Tsurumi Mfg (6351, 11.67% combined, three tranches 2023–2026), Senko Group (9069, combined Dalton+NAVF ~18%; NAVF 10.88% via Bloomberg ACTV supersedes earlier 7.1% single-filer), Sekisui Jushi (4212 NAVF), Ezaki Glico (2206, 5%; Dalton WAC implies +36% above entry by Apr 2026 — WAC cross-check failed), Bunka Shutter (5930, 15.48% WAC ¥1,664 + SC ~5–6.5%), Yakult Honsha (2267 via Kizuna Fund; Apr 24 2026 escalated board contest, 2 nominees Jun 2026 AGM 74th — Asuka WATCH not in portfolio), Stella Chemifa historical canonical conglomerate value-trap. **Anomaly: dual-vehicle aggregation rule mandatory; only combined Dalton+NAVF hits Tier 1 PRIME quality.**
**DOE5パーセント Co. / Ueshima Kankuro / Naturali (cluster, single filer for sizing)** — Tokyo. **Mikkuro Ueshima 植島幹九郎** (Tokyo U engineering, founded Dream Career, runs UESHIMA MUSEUM Shibuya; also listed director of City Index Eleventh — personal link to Murakami network). **Tetsuji Fuwa 不破鉄二** CEO of DOE5% (ex-GS ECM → Morgan Stanley IM MD). **Tier 2 domestic activist** with explicit named-vehicle thesis. Friendly constructive style — NOT hostile proxy contests. **DOE5% does not manage external investor capital** — proprietary capital only, no LP redemptions, no harvest pressure (THE single most important behavioural feature). 5–12 months from escalation to capitulation when wins land. Targets sub-1x PBR mid/small-cap. Default Tier R/E. **DOE 5% adoption is the thesis statement**; the vehicle name is the demand. Holdings: Rhythm (7769 — 2024 proposal → June 2025 win; DOE 4% adopted, div ¥73→¥151.75 +107.8%, ¥1B buyback), Chuo Hatsujo (5992 — 8.35% Jul 2025 → 11.49% Aug; co pre-emptively announced ¥25B 6-year shareholder return plan Jul 30 2025), YCP Holdings Global (Aug 2025 self-tender/JDR buyback proposal pending), Gun Ei (4229 Asuka L2), Tayca (4027 Asuka L2 active 変更報告書 Mar 16 2026), Fujikura Kasei (4620 Asuka L2; Ueshima 5.21% + Naturali 2.46% + DOE5% 0.74% = 8.41% combined May 2 2026, active 変更報告書 Mar 13 2026), Miyoshi Oil & Fat (4404 Asuka L2/L3), Nippon Felt (3512 — Ueshima+Naturali+DOE5% combined 5.01% canonical joint-holder structure), Iwabuchi (5983 — Ueshima individual filing). **Renaming D&I Investment → DOE5パーセント Jan 27 2025 = thesis clarification, not new entity.** Cluster correlation cap: DOE5% basket treated as single position for sizing. **Ueshima ≠ Murakami network for aggregation despite CIE director link** (different playbook).
**Effissimo Capital Management / SMT Partners Cayman** — Singapore; founded by former Murakami Fund alumni (trio left M&A Consulting mid-2000s). Long-only value style (METI 2018: "long-only value with management improvement engagement when needed"). **Tier 1 PRIME dual-vehicle.** Three-mode framework: **Mode 1** (Capital Return Pressure) at 15–20% private demands for buybacks/dividends; **Mode 2** (Strategic Review / Forced Sale) at 20%+ non-core disposals or full sale; **Mode 3** (Blocking Position vs Lowball MBO) at 15–33%+ pivotal swing on 2/3 supermajority. Closed-case mean ~2.2 years; large stakes 3–10+ yrs. Mid-cap focus ~$200–800m; fund-size growth pushed into larger caps where returns compress (Zang 2019). ~1pp/quarter accumulation ratchet steady state; **Pacific Industrial blitz (5.54% → 69.22% in 5 months) is the high-end exception** — treated in framework as control-contest acceleration on existing Mode 2/3 spectrum, NOT a new "Mode 6." Tier P at entry ~57%; Tier R ~43%. **"純投資" does NOT mean passive** (Toshiba ran 4 years of "pure investment" before EGM appearance). Holdings: Ricoh (7752, 24.77% deep Mode 2), Teijin (3401, 19.26% Apr 14 2026 Change Report S100XYZD, +5.05pt in 18 weeks ≈ 1.25pt/month 3–4× normal — Mode 1→2 transition; GS PB facilitation), Tamron (7740, 15.3% Mar 11 2026, WAC ¥507 vs ~¥1,083 spot = +113% above WAC — co-investment edge gone), Ines (9742, 12.35% with AVI 6.02% dual-filer Jan 23 2026), Konica Minolta (4902, 9.55% PASSED — loss-making, no balance-sheet capacity), Soft99 (historical 35% → 53% MBO blocking Mode 3 canonical), Pacific Industrial (5.54%→69.22% in 5mo), Kawasaki Kisen (historical 5x return over 5 yrs ~38% IRR Mode 3 textbook), Toshiba (4 yrs silence then EGM appearance, eventual JIP take-private). Empirical: closed-case mean ~82% MOIC, ~100% closed-positive. Anomaly flags: filing burst (≥2 within 7d) = Bull +5pp / Bear −3pp; pre-AGM acceleration >1.5× = Bull +10pp; 12+ month silence after established cadence = Bull −10pp / Bear +15pp (quiet exit risk); stake reduction ≥1pp from peak when historical monotonic = severe.
**Elliott Investment Management** — NY/London; Paul Singer founded 1977; ~$80B AUM. **Tier 1 hard activist.** Disclosure-fast public-facing playbook — antithesis of Effissimo. 12–24 months typical. Bloomberg ACTV: n=16, mean +12.1% (Japan-only — calibrate down from global reputation). Tier R/E with media pressure. Holdings: MOL (9104, Mar 17 "significant" stake disclosed sub-5% no EDINET trigger; Apr 1 BLUE ACTION 2035 MTMP critique — asks Daibiru relisting/RE carve-out, vessel/RE gains, buyback/dividend, PBR ≥1.0x; June 2026 AGM binary), NXHD (9147, 5.04% NEW S100Y15W; PBR 1.23x atypical CASH/SOTP/GOV play; May 13 2026 earnings first binary; **capital rotation directly from Toyota Industries exit**), Toyota Industries (6201 EXITED Mar 30 2026 at premium TOB close 7.14%→0%), historical Tokyo Gas, Sumitomo Realty, Mitsui Fudosan. **Anomaly: capital rotation pattern (Elliott exits closed position then files NEW within ~4 weeks — Toyota Industries → NXHD canonical). Mega-cap underperformance ($10B+ activism mean +21.2%, only 27% >+30%) caps sizing 3% single / 6% mega-cap cluster.**
**GMO-Usonian (Grantham Mayo Van Otterloo Japan Value Creation sleeve)** — Boston (GMO LLC parent ~$60B AUM). **Drew Edwards** leads Usonian Japan Value Creation. **Sleeve must be distinguished from GMO's other strategies** (International Value, Quality Japan, systematic) — Japan 大量保有 filings show firm-level aggregate, NOT Usonian-specific. Validation requires Usonian factsheet listing. **Tier 2 engaged long-only / quality compounder.** Patient collaborative engagement; negotiated block transfers; considers take-private roles. EDINET formal filing = re-rating signal not catalyst. 18–36 months. Opens near 5% threshold and builds (H.U. Group: 5.19% June 2023 → 10.8% over 32 months). Bloomberg ACTV: n=17, mean +18.6%, 47% >+20% (Tier 2 low variance). Tier P → Tier R (Dec 2025 Oisix filing "純投資及び状況に応じて重要提案行為を行うこと"). Holdings: Optex Group (6914, 5.0% Feb 25 2026; Asuka L2/L3 toward 8% target; WAC ¥2,629 EDINET-confirmed), Oisix ra Daichi (3182, 10.48% Apr 2026 Change Report, +0.31pp; WAC ¥1,577 vs ¥1,437 px = GMO 8.9% underwater AND ADDING — max-conviction signal), Valqua (7995, 5.10%), Maxell (5.02%), Chugoku Marine Paints (5.02%), H.U. Group (canonical 5.19%→10.8% 32mo), Musashi Seimitsu (7220, 5.11% irbank confirmed — but ¥290B mcap 3-5× larger than usual ¥50-100B targets; 80% Honda customer concentration outside sector pattern; PBR 2.45x above usual entry; ~40–50% probability reflects pure Usonian vs multi-strategy aggregation). **Anomaly: threshold filing discipline** (GMO files exactly at/just above 5.00, 5.10, 5.02, 5.06); **crossing 10% historically precedes take-private moves** (2 of 41 portfolio Q4 2024); single-PM concentration risk (Optex+Oisix+Musashi = 15-18% NAV in Drew Edwards' judgement).
**Hibiki Path Advisors** — Singapore; Yuya Shimizu CIO. **Tier 2 engaged long-only** (to be added). Bloomberg ACTV: n=36, mean +30.3%, median +15.0%, 44% >+20%. 12–24mo holds. Tier R. Holdings: Tamai Steamship (9127, 7%+ Sep 2025 with formal three-demand letter — DOE 8% + ROE disclosure, terminate poison pill, Corporate Value Enhancement Committee. Late Oct 2025 +1pp + direct meeting with President Kiyozaki. Poison pill discontinued Nov 2025. Stock ¥1,400 entry → ¥4,590 by Mar 2026), Hi-Lex (7279 — Toyo Keizai hint at affiliated filer, verify). Anomaly: faster letter-then-meeting cadence than NAVF/SC; 6-month escalation horizon; most thesis often captured by time stake publicly identified — late-entry shadow-buy windows short.
**LIM Advisors** — Hong Kong; George Long founded 1995 (Asia's longest continuously operating Asia hedge fund). ~$1B AUM. Tokyo research since 2002. Restructured to event/activist focus 2019. **Tier 1 hard activist with patient capital.** Five-step playbook: (1) Acquire 5%+ quietly via HK vehicles. (2) Private engagement letter (poison pill removal, dividend/buyback authorization, board independence). (3) Patient sustained engagement (3–5 yrs). (4) Public escalation only if private fails. (5) Sometimes proxy fight at AGM (Pasona). 3–5 yr standard. Bloomberg ACTV: n=27, mean +26.1%, 48% >+20%. Tier P (純投資). Holdings: Kitagawa Seiki (built ~18% over 12 months 2025; demanded 12% ROE by 2030 + payout increase + improved disclosure; **trimmed 18% → 3% Mar 2026 after +214% rally from Dec 2024 — LIM trims aggressively into volatility-creating rallies, does NOT ride to fair value**), Inui Global Logistics (9308 5.44% Feb 13 2026, filed Feb 20; LIM + MIRI dual-filer ~10.5% combined; Asuka was watch/reduce due to FY OP profit warning), Pasona (historical proxy fight), GungHo Online, Noritz, Nakano Corp, Synchro Food (Feb 2025 director removal). **Alphaleo Capital Advisors** — HK vehicle with possible LIM affiliation (Inui 8.13% holding); verify EDINET joint-holder section before treating as alias.
**MIRI Capital Management** — US small-cap value. **Tier 2 engaged long-only.** Sub-¥20B Japan micro-cap first-mover. Bloomberg ACTV: all 13 Japan positions tagged "Stake Only: No Public Activism" — passive accumulation in Japan even though MIRI took control of STIC Investments Korea Jan 2026 in different jurisdiction. Multi-year. Tier P (passive). Holdings: Ichiyoshi Securities (8624, 12.61% combined — soft control via fragmented register; L3 compounder with activist optionality parallel to Oisix-under-GMO-Usonian), Inui (9308 5.06% Aug 13 2025, dual-filer with LIM 5.44%), NCD Co (4783), Syuppin (3179), Takara (7921), Japan System Techniques (multi-year compounder — Activist Insight Hp_Return **+292%**), STIC Investments Korea (≠ Asuka mandate). **Japan ≠ Korea playbook** (Korea active control deal-making does NOT transfer to Japan signals). Liquidity floor binds first — MIRI signals concentrate in <¥40B mcap where ADV-based Asuka caps (1.5%) bind before PWER drives sizing.
**Oasis Management** — Hong Kong; Seth Fischer CIO. **Tier 1 hard activist** — most aggressive public communicator. Press releases, campaign websites (protectkakaku-style URLs), open letters EN+JP, Tokyo press conferences, English-language media. Five-step: (1) Initial disclosure + private letter (~5%). (2) Public letter / campaign website. (3) Tokyo press + Western press (FT, Bloomberg, Reuters). (4) Formal AGM proposals or proxy contest. (5) Exit on capital-return success OR concede on stalemate. **Bimodal holds:** Fast cycle (M&A/strategic) 12–24mo (Tokyo Dome 13mo, Toshiba 24mo, Tsuruha 12–18mo); Long cycle (entrenched governance) 5–7+ yrs (Hokuetsu, Kao 3+, Kobayashi Pharma 2+). Median ~2–2.5 yrs; mean ~2.5–3.5. Bloomberg ACTV: n=82, mean +23.8%, 45% >+20% (likely bimodal — big M&A wins masked by entrenched losses). Tier R/E. Holdings (current and historical): Kakaku.com (2371, 5.23%), en Japan (4849, 7.93%), Kobayashi Pharma (4967, 13.74%), Kokuyo (7984, 9.91%), Nidec (6594, fresh ~6.7% accumulation 2026 — Step 1→2 transition; Asuka L2 2-3% NAV with hard 6% cap due to TSE Special Alert/SESC overhang; Apr 29 earnings first forcing event), Tokyo Steel (5423, 6.25% Apr 2 2026, obligation Mar 26, 6,884,398 shares; +20% pop but Ikegaya 30% bloc = Oasis-failure danger zone), Tokyo Dome (9681 Dec 2019→Jan 2021 Mitsui Fudosan bid 13mo WIN), Toshiba (Apr 2021→Mar 2023 JIP 24mo WIN), Tsuruha (3391 Jun 2023→2024 Welcia 12-18mo WIN), Hokuetsu (3865, 2019 18% stake, still active 2024+ 5+yr no resolution), Fujitec (May 2022→Feb 2023 WIN ~18-24mo), Kao Corp (5.2% multi-year, proposals REJECTED Mar 2025 AGM), DIC (11%+ multi-year, REJECTED Mar 2025), Ain Holdings + Kusuri-No-Aoki (historical LOSSES — founding-family bloc structural failure), Casio (exited Feb 2026 after Jan buyback; 3D filed NEW 5.03% Mar 26 2026 = continuous activist coverage handoff). **Anomaly: Oasis structural failure pattern (canonical danger zone)** — founding family ≥30% bloc + large-cap diffuse + consumer/pharma. Hokuetsu, Kao, Ain, Kusuri-No-Aoki, DIC all share. **Reject regardless of headline PWER. Tokyo Steel currently in this zone.** 2006 SFC Hong Kong fine ¥7.5M for Japan Airlines closing-price manipulation — on file, not current.
**Palliser Capital** — London; **James Smith** founded 2021 (ex-Elliott senior). Hidden-segment SOTP unlock + capital allocation + disclosure. **Five-phase tracker:** (1) Private letter leaked (FT/Bloomberg). (2) **Formal "Value Enhancement Plan" press release on BusinessWire — actionable entry.** (3) Sohn / 13D Monitor presentation. (4) Stake escalation top-15 → top-10. (5) Company response. 3–7yr. Mega-cap focus. Tier P → Tier E via Value Enhancement Plan letters. Holdings: Ajinomoto (2802, top-20, explicit "Break Up", Phase 2 = INVESTABLE), TOTO (5332, top-20 Feb 17 2026; Value Enhancement Plan claims ¥554B / +55% upside Advanced Ceramics ESC >50% OP, AI/NAND, 5yr moat; GS upgrade Jan 22 2026 was precursor +10-11% one day before Palliser disclosure +5% additional; stock +60% YoY to ¥5,425 by Apr 30 — **Asuka framework miss — Toto post-mortem prompted Hidden-Tech Trigger module addition**), Keisei Electric (9009, Phase 3 year 5), Japan Post Holdings (6178, Phase 3 top-15), Tokyo Tatemono (Phase 1-2), Taiheiyo Cement (Phase 1), SMC Corporation (6273, Phase 2 just published Apr 26 2026: "Maximising the Value of SMC Corporation – ¥600bn Share Buyback to Catalyse a Valuation Re-Rating" / 50% upside claimed — fresh signal). **Mega-cap activism underperforms** (n=68, mean +21.2%, only 27% >+30%). Palliser-Ajinomoto + Palliser-TOTO + Elliott-MOL + Oasis-Nidec = correlated mega-cap basket; cluster cap 6% NAV.
**SilverCape Investments** — Singapore-based single-family office incorporated in Cayman Islands. **Peter Kennedy** MD. Counsel: White & Case (TOB-readiness signal). Originally Tier 3, **upgraded to Tier 1 hard activist after Digital Holdings competing TOB precedent**. Three-mode mirroring Effissimo: Mode 1 (5-8% quiet); Mode 2 (10-15% dominant minority); Mode 3 (>14% hostile competing TOB). 6-18mo Mode 2/3. Default Tier R (every JP 大量保有 carries 「純投資・重要提案行為等を行うため」). Holdings: Digital Holdings (2389 — 5.27% Feb 2025 → 14.97% Sep 2025 → competing TOB ¥2,380 vs Hakuhodo ¥1,970 21% premium; withdrew after Hakuhodo won; **canonical Mode 3 precedent**), Inter Action (7725 — 5.02% Mar 2025 → 9.95% May → 11.92% Dec 12 → 14.85% Dec 18 2025 largest shareholder displacing Kaname Capital 14.07%; **Mode 2 confirmed**; combined SilverCape+Kaname ~28.9% canonical dual-engaged signal — but **DATA QUARANTINE flag in memory**), Broadband Tower (3776 — ~8.59% → 11.06% Feb 2026 largest shareholder; Mode 2; Mode 3 anti-MBO vs IRI/SBI; PWER bull on IDC M&A optionality), Yamato International (8127, 12.79% Oct 2025 Mode 2), Mercuria Holdings (7347 — 5.10% May 2025 ¥831 Mode 1; PWER ~+32%), Cyber Security Cloud (4493 — sub-¥20B WAF SaaS; AWS distribution moat; Asuka L3 watch conditional on 2nd institutional filer), Enplas (6961 +318% one-year — PBR-discount thesis consumed; PASSED), Mitsubishi Steel (5632 May 2026, verify), Saxa (6675 5.27% Feb 2025 — but AVI is lead per memory). **Conditional on second institutional filer** — Asuka treats SilverCape as Tier 1-quality only when 2nd institutional (Kaname, AVI, etc.) appears.
**Silchester International Investors** — London (UK FCA); long-only value; founded 1994 by **Stephen Butt**. **Tier 1.5 — reclassified from Tier 2 patient ballast in April 2026** after Bank of Kyoto May 2022 evidence + parallel chemical-sector engagement. **"Silchester is not an activist investor" treated as boilerplate equivalent to Effissimo's "純投資" language.** Slow-moving campaign-runner at Mode 1 (capital return) and Mode 2 (strategic review/merger). 5–10+ yrs; lower variance than Effissimo/Oasis/3D. Tier P at entry. Public letters at escalation only. Holdings: Bank of Kyoto / Kyoto Financial Group (5844 — May 2022 public letter at only 6.2%; called bank arguments "naïve and lacking financial acumen"; ¥132/sh special dividend proposal; credible EGM threat. 2023 modified ¥62 div / ¥5bn buyback — both lost at vote but forced pre-emptive concessions. April 2025 president Doi finally conceded cross-shareholding cuts and merger options. **Canonical Tier 1.5 reclassification trigger.**), Daicel (4202, 7.9%), Nippon Kayaku (4272, 12.0%), Tosoh (4042, 7.1%), Daito Trust (1878, 8.5% Asuka L3 ballast — TRIM bias paused), Alfresa (2784, 12%+ Asuka L3 TRIM paused), Kansai Paint (4613, Asuka L3 3% underwater entry — re-graded upward post-reclassification), Musashi Seimitsu (7220, Tier 2 long-only ballast), Suzuken (9987, recent stake, public engagement-flag ¥5,200 Apr 2025; Asuka 4% L2 candidate ≤¥5,600 with dry powder for May 14 2026 result), Obayashi (1802 historical), Chugin Hldgs, Iwate Bank.
**Strategic Capital Inc.** — Tokyo. **Tsuyoshi Maruki** founded 2012 (co-founded M&A Consulting 1999 — Japan's first activist fund ¥444B AUM peak 2006). **Tier 1 PRIME** — Bloomberg ACTV n=38, mean +52.2%, 61% >+20% (top-decile). **Sharpest legal toolkit in domestic Japan activism**: shareholder proposals, accounting book inspection, director minutes inspection, shareholder lawsuits, board nominees. Multi-year patient; builds to 15-17% and parks. Maruki: "If one always adopts a friendly engagement style... management would not change." Default Tier R. Holdings: Sanyo Denki (6516 — 5.49% Feb 2 2026 → 11.55% Feb 9 +6.06pt in 5d → 12.07% Feb 19 → 14.35% Mar 10 → ~15% current. **Apr 21 2026 dedicated campaign website launched + filed shareholder proposal — Mode 1 → Mode 1+Board Contest transition.** Asuka L1; WAC retrace required for further add (current >+57% above SC WAC = co-investment edge closed). June 2026 AGM binary), Daidoh Limited (historical canonical — SC 32%, 3 nominees received 51.73% / 51.15% / 50.70%; +279%), Noritake (9.22% Apr 17 2026 — prior 9.38%→8.20% Feb 24 non-monotone), KH Neochem (historical positive precedent), Keihanshin Building (8818, 11.99% Apr 30 +1.45pt; **co-investment vehicle Sunshine H LP with UGS**), Iwasaki Electric (UGS Sunshine D/E/G LPs 5%+ to 6.13% in 4mo), Toyo Securities (8614 — UGS Sunshine G/H + Be Brave + Capital Mgmt + Epic Group multi-year campaign 2022+; PBR 1.0x proposal Apr 2024), Yellow Hat (9882 — 5.02% Jul 26 2024 → 13.83% Dec 2024 standing; **canonical Realized Mode 1 — Asuka NEW L3 starter 3% May 11 2026**). **Anomaly: dedicated campaign website launch = Mode 1 → Mode 1+Board Contest transition (Sanyo Denki precedent; SC does not deploy microsites routinely). UGS Sunshine LP as SC co-executing partner** — UGS on SC playbook profiles treated Tier 1-adjacent (Keihanshin 2020, Iwasaki 2022, Toyo Securities 2022).
**UGS Asset Management** — Tokyo. Investment manager of Sunshine LP series (D/E/F/G/H). **Tier 2 domestic activist with TOB capability.** Strategic Capital co-executing partner of Sunshine H LP (Keihanshin Nov 2020 joint TOB — SC named 共同保有者). Stated philosophy identical to SC: "Focus on PBR, select stocks where corporate value is expected to rise through M&A or organizational restructuring." 12-24mo; willing to launch tender offers — among most aggressive domestic activists. Tier R. Holdings: Keihanshin (8818, Nov 2020 joint TOB), Iwasaki Electric (Sunshine D/E/G LPs 5%+ → 6.13% in 4mo), Toyo Securities (Sunshine G/H 2022+, defensive measures extended May 2025), Takihyo (9982, 5.03% Apr 20 2026 via Sunshine F LP — filing after ~15% pullback ¥2,270→¥1,833; UGS bought through the selloff; May 2027 AGM binary; Asuka L3 Watch 0.3-0.5%), meito (2207 — cost basis ~¥2,671; Asuka actionable only ¥2,600-2,750 or if SC co-files; **cross-shareholder thicket Kowa 9.22% + Takasago + Ogaki Bank + Toho Gas + Kikkoman ~21% = UGS-dream target**). **Strategic Capital as direct joint holder = single biggest UGS escalation tripwire — converts solo domestic to TOB-capable joint vehicle.**
**ValueAct Capital Management** — San Francisco. **Mason Morfit** CIO global; **Rob Hale** leads Japan. 2018 Olympus entry was test case (Hale joined Olympus board 2019 — first time fund manager served on Nikkei 225 board). **Tier 1 hard activist** with "quiet activism" / "transformational activism" style. Behind-the-scenes; rarely public. Targets technology transformation (Microsoft, Adobe, Salesforce US comps; Olympus / Money Forward / Niterra / Max Co Japan). 3-7yr on transformation. Japanese positions sometimes >20% of fund total capital (Olympus). Tier R/E. Holdings: Olympus (2018 entry, Hale board 2019, medical refocus), Money Forward (3994 — 5.62% combined ValueAct + ValueAct Japan Jul 2025 at ¥4,290 WAC; +23% pop. Underwater −34.8% by Apr 2026 (¥4,725 spot May 1 2026 vs WAC). Tsuji 16.27% per May 25 2025 有報. Q1 FY26 Apr 14 actuals: rev ¥14.67B, adjEBITDA ¥2.814B, NI ¥1.828B. **FY end Nov 30; AGM ~Feb (NOT June — fact-check correction May 2026)**), Max Co (6454, 7.31% Mar 12 2026; ¥1,631 cost post-split, ¥1,716 spot = +5.2%; active-intent first-filing language), Niterra (5334, 5.27% auto-transition tech basket), Sun Corp (−15.4% underwater Cellebrite spinout history). **Anomaly: auto-transition tech basket cap at 3 names. Premium-to-DCF risk** — ValueAct's growth-stock targets trade premium to DCF; downside is multiple derating not balance sheet floor. **Underwater + still adding** = canonical ValueAct signature.
**Zennor Asset Management LLP** — UK FCA-regulated; Luxembourg + UK UCITS launched February 2021. **Tier 2 long-only special situations. NOT a hard activist** — public engagement limited to commentary letters (Fuji Media 2025 alongside Dalton). Filing uses 重要提案行為等 optional clause but no escalation track record. PWER cap ~10-12%. Style: discount-to-intrinsic + parent/sub consolidation + M&A catalysts. Multi-year patient. **CORRECTION May14/26 (memory):** Zennor is CO-INVESTOR not lead at 6080 M&A Capital (Panah Master Fund is proposal filer). Zennor 5.07%→6.21% post Dec25 AGM rejection, WAC ¥3,125, 60d VWAP ¥3,318 (adds into uptrend = conviction in Panah-led campaign). T2 archetype UNCHANGED. PWER 10-12% solo / ~21% w/ Panah wolf-pack. 6080 BUY STARTER L3 ≤2% (founder 43.93% sizing cap). EDINET S100Y44X. Holdings: Hi-Lex (7279 — flagship 7.4% from July 16 2025 5.16% initial), NS United Kaiun (9110, 5.05% Jan 20 2026 NEW — largest disclosed Japan position in fund's history. Below-book floor entry. Asuka L3 2% — TRIM/HARVEST flag after stock nearly doubled to ¥7,070 (52w low ¥3,580 → +98%); PWER compressed +4%), Meiji Shipping (9115 — watch, tanker run distorted), Obara Group (−13.2% underwater), Appier (−24.2% underwater), Lifedrink (−21.8% underwater), Central Security Patrol (9704, 5.29% NEW). **Stake reduction during rally is NOT anomalous — this is the archetype. Zennor harvests into rally** (NS United Kaiun ¥3,580 → ¥7,070 captured most of thesis). Co-investor decision rule: trim alongside Zennor when rally has captured >70% of bull-case price target — do not wait for them to fall below 5%.
**3D Investment Partners** — Singapore; generally single-vehicle. **Tier 1 PRIME hard activist.** Three-mode taxonomy (canonical Asuka classification): **Mode 1a — AGM governance campaign** (outside director slate, buyback mandate, ROE commitment; mid/large cap with entrenched boards — Square Enix precedent). **Mode 1b — Conglomerate unlock** (separate real-asset/RE/SoTP from operating business; challenge "core business" designation — Sapporo precedent + IHI/Third Point). **Mode 2 — Forced privatization via strategic review** (20%+ stake, committee capture, irrevocable tender lock — Fuji Soft precedent + Toho Holdings live). 12-18mo Mode 1a; 18-36mo Mode 1b; 6-12mo Mode 2. Activist Insight: every completed campaign positive (Fuji Soft +150.8%, Sapporo +162.5%, Tohokushinsha +165.9%, Toho Holdings +34.9% ongoing). **Zero exits at a loss historically.** Tier P at entry; rapid escalation to Tier E. Holdings: Square Enix (9684, 18.53% Mar 3 2026 EDINET — was 5.47% Apr 28 2025; Mode 1a; June 2026 AGM binary; Dec 2025 most aggressive public attack document yet; Asuka L1 12% capped; ¥2,900 cost vs ¥2,598 current; May 12 2026 earnings near-term catalyst), Toho Holdings (8129, Mode 2 live; Oct 2025 management Response Policy; Apr 14 2026 evaluation period close; **Defender response Level 4–5** — point-by-point rebuttal + adverse Fuji Soft comparison + formal poison pill — canonical Mode 2 case), Sapporo Holdings (2501, Mode 1b closed +162.5%), Fuji Soft (Mode 2 closed +150.8%), Tohokushinsha Film (2329, closed +165.9%), Seibu Holdings (9024, 5.75% Nov 2024 was 5.01% May 2024 — **15+ month silence, then Feb 26 2026 CEO succession announcement = early 3D escalation pattern (mirrors Square Enix and Toho Holdings)**; Asuka 3% L2; upgrade tripwires: new EDINET past 6%/7% or 3D public letter), Casio (5.03% NEW Mar 26 2026; Nomura group PB facilitation ~9pt+ unwind; Oasis-to-3D handoff post-Feb 2026), NS Solutions (historical), Toshiba (historical Mode 2 partial). **Anomaly: Defender response Level 4–5** = compressed timeline binary outcome 3-6 months (Toho canonical); **15+ month silence after initial 5%+ is NOT exit — early-3D pattern, catalyst usually surfaces ~18-24mo post-entry**; Mode 2 wider scenario tails (X-Bull tender 40-70% premium 20-25% prob; Bear poison pill triggering 20-25% prob).
**Closing notes / Memory updates layered on top of file roster:**
**Kaname Capital LP** (E37907) — Tier 1.5 patient quality+active engagement. Boston 2018, Rodes+Ikauniks ex-GMO Team Asia, Makino ex-Misaki. ~$200M AUM JP small-cap, 3-5yr holds. Escalation: Proto 4298 anti-MBO Feb25; Fukuda Denshi 2025 AGM proposals. Holdings: Daihatsu Diesel 6023 14% flagship; Torex 6616 ~13% Tier R "重要提案行為等" Sep23 WAC ¥1,703; Inter Action 7725 dual SilverCape; CareNet 2150; Daito 4577; Freund 6312; Yamatane 9305; Wacom 6727; Neojapan 3921 5.07% WAC ¥1,582. Pershing-DLJ custody.
**Panah Master Fund** — T1.5 LO campaign-runner NOT T1. Mgr Seraya Investment Pte (SG MAS), CIO A.Limond (Oxford, ex-LGM/AIMS). <$500M AUM (HFJ2024). ~40 engagements/dec mostly private = Silchester-BoK mirror. 6080 M&A Capital entry Feb24 at 10yr-low; 20mo private→Oct3 AGM proposals rej Dec25 6.44%/6.68% (Nakamura 43.93%); Dec7 counter-rebut. Sub-5% — NO EDINET 大量保有 (kabupro). PWER ~19.8% STARTER L3 ≤2% @¥3,365.
**Universe expansion candidates (Bloomberg ACTV evidence):** Varecs Partners (n=19, mean +41.9%, 42% >+20%) still unresearched; United Managers Japan (n=27, mean +37.1%, 48% >+20%) still unresearched; Hibiki Path partially researched via Tamai. **To avoid:** Curi RMB Capital (n=18, mean −5.1%, 17% positive); Taiyo Pacific (54% positive, caution).
Always re-verify EDINET filer codes per individual filing — codes referenced inline above are from older registry drafts and have drifted. **XBRL-first rule (memory #22) supersedes any aggregator-derived data.**
---
### 3.4 `crmc-archetype-rules.md` — CRMC Four-Lens Decomposition
**What it is:** CRMC = **Category** (archetype tier) × **Reservation** (filing language) × **Mode** (campaign stage) × **Catalyst** (next dated forcing function). Every action signal — initiate/add/hold/trim/exit — is the output of a CRMC read.
**Why it matters:** Operationalises filer-specific behaviour into a deterministic signal-classification grid.
**Exhaustive summary:**
**§1 Archetype framework (Categories):**
- **Tier 1 hard activists** (default deployment) — Effissimo+SMT, Murakami network, Oasis, 3D, Dalton+NAVF, Strategic Capital+UGS Sunshine, LIM, Be Brave, SilverCape, Palliser, Elliott.
- **Tier 1.5 campaign-runner long-only** — Silchester (post-Bank of Kyoto + Daicel/Nippon Kayaku/Tosoh chemical-sector parallel campaigns).
- **Tier 2 engaged long-only / quality compounder** — GMO-Usonian, Ariake, MIRI, AVI Japan, Arcus, Zennor.
- **Tier 2 domestic activists** — Ueshima/Naturali/DOE5%, City Index Eleventh (umbrella'd separately), UGS Asset Management.
- **Tier 3 watch-only** — unconfirmed family offices, ambiguous foreign investors, sub-5% disclosures from unknown entities.
**§2 Per-archetype hold patterns, batting averages, signal calibration (the empirical anchor table):**
| Archetype | Avg stake | MC sweet spot | Avg hold | Avg return | Win rate | Default PWER prior |
|---|---|---|---|---|---|---|
| Effissimo / SMT | ~13-14% | $200-800m | 3-10+ yrs | ~82% MOIC | ~100% closed-positive | 25-30% abs, 18-22% ann |
| Oasis | ~7% | $1-5B | ~1.2 yrs | ~22% (active +36%) | ~73% | 20-24% bimodal |
| Dalton + NAVF | ~5% combined per vehicle | $1B+ | 1-2 yrs | ~18-20% | ~65% | 18-22% |
| 3D | varies by mode | mid/large | 1a ~12mo / 1b 18-36mo / 2 6-12mo | varies | high on Mode 2 | 20-28% mode-dep |
| Strategic Capital | ~5% (occ 17%) | small/mid | multi-yr, parks 15-17% | moderate | medium | 18-20% |
| Murakami network | 10-22% peak aggregate | small/mid | 18-24mo target | >20% annualised (JOI 2019) | high on stages 1-4 | 20-26% stages 1-3, NEGATIVE Stage 5 |
| Silchester (Tier 1.5) | 6-12% | regional banks, chemicals | 5-10+ yrs | moderate compounding | high on capital return | 12-18% |
| GMO-Usonian | 5-15%, builds 32mo | $100-500m | 18-36mo | high on re-rating | high (rare exits) | 22-28% EDINET-confirmed |
| LIM | 5-18% | small/mid TSE Standard | 12-18mo | moderate | medium | 12-18% |
| Be Brave | 5-15% monthly ratchet | small-cap sub-1x PBR | 12-18mo | DOE-driven, +87% Nishikawa precedent | high on Mode 2 | 22-28% confirmed esc |
| SilverCape | 5-17% builds quickly | TMT/digital infra | 6-18mo | high on Mode 3 | medium-high | 30-50% pre-esc |
| Palliser | top-15→top-10 | mega-cap | 3-7yr | high on segment unlock | medium | 15-22% mega-cap capped |
| Zennor (Tier 2) | 5-7% | small/mid below-book | multi-yr | moderate; rally-capture | medium | 10-15% |
| DOE5% / Ueshima | 5-12% combined | sub-1x PBR mid/small | 5-12mo to win | DOE adoption track (Rhythm/Chuo Hatsujo/Nishikawa Rubber) | high on capital return | 18-24% basket |
**Mega-cap correction (E.2):** activism on >$10B market cap underperforms (mean +21.2%, only 27% >+30%). Cap single mega-cap activist at 3% NAV and cluster at 6%. **Stake-size conviction ceiling:** 5-10% highest-return bucket; 10-15% underperforms (entrenchment); crossing 5→10% neutral, crossing 10→15% mildly negative, crossing 15→20% reactivates (Mode 2/3 territory). Do NOT auto-upgrade conviction at 10%.
**§3 Filing language tier mapping (Tier P/R/E/C):**
**Tier P — Passive boilerplate (NEUTRAL):**
| Japanese | English | Signal |
|---|---|---|
| 純投資 | Pure investment | NEUTRAL — boilerplate, does NOT mean passive |
| ポートフォリオ投資 | Portfolio investment | NEUTRAL — variant |
**Tier R — Activist-reserve (ELEVATED):**
| 投資及び状況に応じて重要提案行為等を行うこと | Investment with important proposals as appropriate | ELEVATED |
| 純投資・重要提案行為等を行うため | Pure investment and important proposals | ELEVATED — canonical Murakami/Effissimo |
| 経営陣への助言 | Advice to management | MODERATE |
| エンゲージメント / スチュワードシップ | Stewardship engagement | MODERATE |
**Tier E — Explicitly activist (HIGH):**
| 重要提案行為等 | Important proposal activities | HIGH |
| 株主還元の充実を求める | Seeking enhanced shareholder returns | SPECIFIC capital return campaign declared |
| 経営への関与 | Management involvement | HIGH |
**Tier C — Escalation / control (MAXIMUM):**
| 支配権の取得 | Acquisition of control | MAXIMUM |
| 取締役選任 | Director nomination | MAXIMUM |
| Specific text describing board nominees / restructuring | — | MAXIMUM |
**The transition rule:** purpose-tier upgrade between filings is the highest-signal event in framework. Empirically **purpose-tier transition precedes public demands by 4–8 weeks**. Fund the upgrade trade out of lowest-PWER cluster member.
**§4 Anomaly detection rules per filer:**
- **Effissimo:** Filing burst (≥2 within 7d) +5pp Bull/-3pp Bear (Pacific Industrial Sep 2025); pre-AGM acceleration >1.5× +10pp/-5pp; 12+mo silence -10pp/+15pp quiet-exit risk; reduction ≥1pp from peak = Mode 2 → exit transition.
- **Murakami:** CR No.15+ with new individual vehicle 5%+ likely internal redistribution NOT fresh (Exedy No.24 canonical); ATRA-direct-filer = +1 sizing tier (Wavelock HD Nov 2025); Stage 5 = all five conditions firing simultaneously.
- **Oasis:** Founding family ≥30% + large-cap diffuse + consumer/pharma = structural failure (Hokuetsu/Kao/Ain/Kusuri-No-Aoki/DIC); public letter or campaign site with stake static = upgrade L1; stake reduction in 1pp increment = harvest signal.
- **3D:** Mode confusion (large-cap no named takeover candidate = Mode 1a default); Defender response Level 4-5 = binary 3-6mo (Toho); 15+mo silence after initial 5%+ NOT exit (Seibu HD pattern).
- **Strategic Capital:** Dedicated campaign website launch = Mode 1 → Mode 1+Board Contest (Sanyo Denki Apr 2026 canonical); UGS Sunshine LP filing on SC playbook profile = Tier 1-adjacent signal even if SC not named filer (Keihanshin 2020, Iwasaki 2022, Toyo Securities 2022 precedents).
- **Silchester:** Public letter (Bank of Kyoto May 2022) = Tier 1.5 reclassification confirmation; parallel campaigns across industry vertical (chemicals trio) = programme behaviour not single-name patient hold.
- **GMO-Usonian:** Sustained sub-5% → 5%+ filing (32-mo H.U. Group precedent); crossing 10% precedes take-private (2 of 41 Q4 2024).
- **Be Brave:** Monthly 変更報告書 ratchet = active accumulation (Pegasus/Tomoe pattern); upgrade tripwires at 8.5% / 10% / co-filer; DOE adoption at any Be Brave target (Nishikawa Rubber 2025) → signal extends to other Be Brave names.
- **Palliser:** Phase 2 transition (private letter → BusinessWire formal Plan) = actionable entry (Ajinomoto Apr 2026); stake escalation top-15 → top-10 = L1 upgrade.
- **SilverCape:** Crossing 14.85% = Mode 2 (Inter Action precedent); Counsel White & Case = TOB-readiness signal at Mode 3.
- **Zennor (Tier 2):** Reduction during rally NOT anomalous (archetype); trim alongside Zennor when rally captures >70% of bull-case target.
- **DOE5%/Ueshima:** Wolf-pack signal when DOE5% files alongside Ueshima personal + Naturali (Fujikura Kasei 8.41% precedent); D&I Investment → DOE5パーセント renaming = thesis declaration.
- **Filing-language cross-archetype anomalies:** P→R within same campaign = transition signal upgrade; R→E = full escalation L1 sizing; E→P regression = campaign wind-down harvest signal.
**§5 Position trim signals (the trim decision matrix):**
**Follow them out (full or partial exit):**
- Activist files stake reduction ≥1pp without renewed public action (standard 30-60 day lead time before they're at disclosure floor)
- Filing language regresses Tier E → R or R → P at same filer (campaign wind-down)
- Aggregate group stake declining from peak (Murakami Stage 5)
- Activist Hp_Return >+50% without renewed escalation (median realised closure +14%; +50% at fat-tail end)
- Stake_End_Date populated on Bloomberg (filer dropped below 5%) — 5-trading-day exit unless Tier 1 replacement picks up ≥5%
- Catalyst delivered: AGM passed, MBO announced, capital return committed → harvest 50-60% immediately
**Hold through (do NOT follow out):**
- Internal redistribution between vehicles (Murakami-network high-numbered CRs); read joint-holder section
- Single-quarter earnings miss with activist still at full stake or accumulating (ADD, don't trim)
- Stake static at minimum disclosure floor 6+ months (passive holding, not exit)
- **Activist underwater + still adding below their own cost basis = MAXIMUM-CONVICTION SIGNAL (Shift Inc. pattern)**
- Post-failed-AGM dislocation — first AGM proposal voted down but activist holds same/higher stake with no reduction (counter-trend add, not exit)
**Mandatory trim review (no auto-action, written re-read):**
- Activist Hp_Return between −5% and +10% with AGM ≤90 days = binary-hold window (no discretionary action)
- Activist Hp_Return below −15% with concurrent stake growth = mandatory upgrade review
- Mega-cap activist cluster aggregate >6% NAV → force trim to lowest-PWER cluster member
- Liquidity ceiling breach (10-day ADV exit threshold)
**The Zennor exception:** Zennor harvests into rally. Trim alongside Zennor when rally has captured >70% of bull-case price target — do NOT wait for them to fall below 5%.
**§6 Multi-activist co-presence (wolf-pack handling):**
**Type A — Coordinated network (single beneficial owner across multiple vehicles):** Murakami umbrella, Effissimo+SMT, Dalton+NAVF, DOE5% cluster. **Rule: always sum. Aggregate is true economic interest. Read joint-holder section of every 大量保有報告書.**
**Type B — Co-executing partnership:** Strategic Capital + UGS Sunshine LP series. **Rule: treat as Tier 1-adjacent signal even when SC not named filer; upgrade when SC files as direct joint holder.**
**Type C — Independent convergence:** Two unrelated Tier 1 filers cross 5% on same target within 12 months. Live examples: Senko (Dalton + NAVF combined ~18%); Ines (AVI 6.02% + Effissimo 12.35%); Inter Action (SilverCape 14.85% + Kaname 28.9% combined). Historical: Square Enix (3D + Dalton), Toyo Securities (UGS + Be Brave + Capital Mgmt + Epic — four co-filers, won at AGM). **Rule: combined signal exceeds either alone; sizing weight increment of +1 layer (L3→L2, L2→L1).**
**Type D — Sequential PB-warehouse convergence:** Major PB (GS International, Nomura International) crosses 5%+ → activist files NEW or +pt within 30-90d → PB unwinds concurrent. Apr 2026 confirmed: Teijin (GS NEW Mar 31 → -3.26pt vs Effissimo +1.73pt same week); Sankei REIT (GS+Nomura -7pt vs CIE +5.96pt over 8d); Casio (Nomura group -9pt+ vs 3D NEW 5.03%). **Rule: PB NEW 5%+ on JP name = 30-90d advance signal; pre-position with starter sizing; WAC ≈ block-trade unwind price.**
**Aggregation and sizing rules:**
1. Always sum coordinated network vehicles before computing stake %.
2. Multi-activist independent convergence (Type C) = +1 layer upgrade ONLY if both filers in same archetype tier or higher. Tier 1 + Tier 2 = +0.5 (round up if Tier 2 is GMO-Usonian on re-rating fundamental; round down if Tier 2 is patient ballast).
3. Combined stake crossing forcing thresholds discrete signal: 15% (near-veto ordinary), 33.4% (de facto veto special), 50% (effective control).
4. Cluster cap discipline: per-activist ≤25% NAV; per-event ≤50% NAV; mega-cap activist cluster ≤6%.
5. Wolf-pack disagreement: if two filers in Type A network move opposite directions, aggregate direction matters; internal redistribution not signal of conviction change.
6. Cross-tier wolf-pack: Tier 1 entry is upgrade catalyst; Tier 2 cluster pre-existence does NOT auto-trigger upgrade unless Tier 1 explicitly names Tier 2 as joint holder.
---
### 3.5 `pwer-methodology.md` — PWER Formal Methodology
**What it is:** Replication-grade methodology for computing Probability-Weighted Expected Return — the fund's primary position-sizing metric.
**Why it matters:** PWER is the north star for all sizing decisions. This file specifies the formula, scenario construction, calibration, the two-observable-signal rule, asymmetry, carry treatment, IRR conversion, override conditions, comparisons to adjacent metrics, and worked examples.
**Exhaustive structured summary (full math reproduced):**
**§1 Formal definition:**

```
PWER = Σᵢ (Pᵢ × Rᵢ)
Rᵢ = (Targetᵢ − Current)/Current + Carryᵢ
Carryᵢ = (annualised dividend yield + annualised buyback yield) × (Monthsᵢ/12)
where Σ Pᵢ = 1.00
```


Entry gate: **PWER ≥ 20% absolute** (or ≥20% annualised on dated catalysts <12 months). Harvest review triggered when forward PWER < 15%. PWER is a probabilistic ranking metric for capital deployment decisions, NOT a forecast.
**§2 Scenario construction defaults:**
Standing convention: **four discrete scenarios** Bear / Base / Bull / Extreme Bull. Three-scenario tables permitted for non-activist L3 compounders where MBO/tender optionality is genuinely zero. Two-scenario binary collapses FORBIDDEN for theses with continuous outcome space.
Standard probability ranges:
| Scenario | Definition | Default prob |
|---|---|---|
| Bear | Stalemate; activist exits without forcing function, AGM defeat, earnings deterioration, mean-reversion | 15-30% |
| Base | Partial concession; buyback announced, dividend hike, minor governance change, modest re-rating | 35-50% |
| Bull | Full restructuring; strategic review, board capture, segment divestiture, material capital-return | 20-30% |
| Extreme Bull | MBO, tender at premium, strategic sale, full take-private | 5-15% |
**Empirical calibration of return targets:**

```
Bear = 25th percentile of completed campaign returns
Base = median completed campaign return
Bull = 75th percentile
Extreme Bull = max return, capped 2.5× base
```


Below 8 completed campaigns: MEDIUM confidence; analyst override needs second confirming signal. Below 5: LOW confidence; direct construction without empirical anchor.
**Empirical calibration of probabilities (default mapping from playbook dataset):**

```
P(Bear) = 1 − combined_win_rate
P(Base) = partial_win_rate
P(Bull) = full_win_rate
P(Extreme Bull) = MBO/tender_exit_frequency
```


**§3 Probability anchoring — TWO-OBSERVABLE-SIGNAL RULE (standing discipline):**
No probability shift without two independent observable signals. Failure mode being prevented: one-anecdote inflation (single news/filing inflates bull case 5-10pp without second confirming source).
**Tier A signals (each counts as one):**
- EDINET 大量保有 / 変更報告書 with stake change ≥ 1pp
- TDNet 適時開示 of buyback, dividend hike, structural disposal, governance reform
- Public letter or campaign material from activist
- AGM voting result with shareholder-proposal support ≥ 30% of voted shares
- Cross-shareholder reduction filing on same target
- New activist filing on same name (multi-activist convergence)
- Sell-side rating upgrade citing value-source activist is targeting (GS on TOTO ESC ahead of Palliser disclosure)
**Tier B signals (two Tier B = one Tier A equivalent):**
- Earnings beat/miss vs consensus by >5%
- Yahoo Finance Japan board or kabupro chatter inflection
- Bloomberg news flow on activist or company >3 articles in 7 days
- Sector regime data (JPY/USD shock for export-sensitive names)
**Application:**
- Bull probability up by 5pp+: two Tier-A or four Tier-B signals required
- Extreme Bull up at all: ≥1 Tier-A specifically suggestive of tender path (MBO chatter, strategic enquiry, dual-track disposal)
- Bear-side adjustments: single Tier-A where unambiguously negative (activist reduction filing, AGM defeat, profit warning)
Square Enix March 2026 clean two-signal example: 3D AGM proposal filing (Tier A) + sell-side upgrade citing IP monetisation (Tier A) → supports 7pp Bull lift cleanly.
**§4 Anchor entry back-solving — WAC CROSS-CHECK RULE:**
Standing rule: **if current price >15% above anchor activist's WAC, co-investment edge is gone**; PWER must be justified on standalone event-driven terms with bull case capped at existing market expectation, not activist's targeted re-rating.
**WAC sources by archetype:**
| Archetype | Primary | Fallback |
|---|---|---|
| EDINET 5%+ single filing | 取得日 + 取得価額 / share count | VWAP [filing−30, filing] |
| Multi-filing accumulation | Volume-weighted across all 取得 in 大量保有 + 変更報告書 chain | VWAP [first filing−30, latest filing+5] |
| Sub-5% engagement (Palliser, AVI, Silchester pre-filing) | VWAP 6 months preceding first public confirmation | Mid-point 52-week range at confirmation |
| Dual-vehicle (Effissimo+SMT, Dalton+NAVF) | Vehicle-share-weighted across all filings | Aggregate VWAP earliest-vehicle entry to latest filing |
| Domestic individual (Murakami, Ueshima) | Each named vehicle filing summed; treat individuals + corporate vehicles as one economic unit | VWAP over earliest joint-holder filing |
**Accumulation patterns by archetype (calibrates expected hold duration):**
- **Effissimo / SMT:** ~1pp/quarter ratchet post initial 5%. Avg closed holding 805 days (~2.2yr). Mode 2/3 runs 4-6 yrs. Exit profile: 40% open market, 20% demand-for-repurchase, 40% TOB/MBO.
- **Murakami:** Five-stage playbook. Stage 5 reductions = harvest signal. 18mo to 4yr.
- **Dalton/NAVF:** Mid-cap public-demand, 1-2yr. Avg 5% stake, escalates via AGM proposals not stake size.
- **3D:** Combative public, severe exit liquidity at large stakes. AGM binary primary driver. 2-3yr.
- **Strategic Capital:** Domestic governance specialist. 3-5yr, slow-cooker. Many one-proposal cycles.
- **Silchester/Ariake/GMO-Usonian:** Patient capital, no forcing function. 5-10+ yrs. WAC discipline still applies but bull = gradual SOTP closure not forced.
- **Palliser/AVI Japan:** Public-letter engagement with sub-5%. Multi-year, catalysts from Sohn/13D Monitor not EDINET.
**§5 Asymmetry ratio:**

```
Asymmetry = (P(Bull) × R(Bull) + P(XB) × R(XB)) / |P(Bear) × R(Bear)|
Simple = R(Bull) / |R(Bear)|
```


| Asymmetry | Action |
|---|---|
| < 1.5 | Reject (reward-to-risk insufficient regardless of PWER) |
| 1.5 – 2.5 | Conditional accept; size minimum L-tier (3% L2, 2% L3 floor) |
| > 2.5 | Standard sizing; upgrade path open |
| > 4.0 | Convex setup; permits sizing premium +1-2pp NAV at initiation |
**Bear must be a FLOOR**, anchored to: (a) net cash + 50% book value, (b) 52w low less 10%, (c) sector PER applied to legacy business in SOTP, or (d) prior cycle trough multiple. Optex L3 illustration: bull ¥4,800 / base ¥3,600 / slow ¥2,900 / bear ¥1,800 (net cash + book floor). At ¥2,634: asymmetry = (¥4,800−¥2,634)/(¥2,634−¥1,800) = 2.60. Above 2.5; standard sizing.
**§6 Dividend carry treatment:**

```
Carry_i = (Div_yield_fwd + Buyback_yield_fwd) × (Months_i/12)
```


Kansai Paint at ¥2,378 with Silchester: div 4.6%, buyback ~2% → 6.6% annualised; base 18-24mo hold → ~12% carry accrual; price-only base +18%; with carry +30%; **PWER lifts 18.2% → ~24% — clears 20% gate as income-adjusted patient compounder.**
What carry does NOT do: not added to Extreme Bull (tender accelerates exit before annual declarations); not added to Bear (where dividend cut is part of thesis); added to Base only at half-weight where management hasn't committed to maintaining payout through downturn.
**§7 IRR conversion:**

```
IRR_i = (1 + R_i)^(12/Months_i) − 1
PW-IRR = Σᵢ (Pᵢ × IRR_i)
```


- **L1 dated-binary positions** (Square Enix Jun AGM, DOE5% basket): Use PW-IRR. 20% gate becomes 20% annualised. 6mo +12% = 25% IRR clears. 24mo +25% = 12% IRR fails.
- **L2/L3 multi-year:** Use absolute PWER. Annualising over 36mo mechanically discounts.
- **L4 merger-arb:** Annualised IRR mandatory. ≥25% ann = BUY, 10-25% HOLD, <10% SELL.
Kakaku post-EQT example: +9% abs over 6-9mo wind-down, 7mo to realisation, IRR (1.09)^(12/7)−1 = **15.9% annualised** — below 20% gate → harvest not add.
**§8 Override conditions — five conditions force override or suspension:**
1. **Anchor exit signal.** Activist files reduction (変更報告書 with stake delta <0) before catalyst window closes → WAC framework inverts. Downgrade by one full layer (L1→L2, L2→L3, L3→exit) on first reduction. Second reduction → full exit. Murakami Stage 5: aggregate declining + buybacks completed + 52w high + price above consensus + peak below 33% veto.
2. **Velocity trigger.** Parabolic move — 50%+ in single month, or 2x+ in <18 months — mechanically forces recalibration. LIM Kitagawa 18% → 3% Mar 2026 canonical. Trim one full layer minimum.
3. **Regime break.** JPY/USD breaching cycle extremes; TSE policy reversal; major Japan banking event; sector shock affecting >30% book → suspend new initiations until scenario sets rebuilt; existing positions reviewed within 5 trading days.
4. **Data quarantine.** Stored PWER inputs conflict with primary-source EDINET or external price → quarantine (red ⛔). Reset probabilities, re-derive. Trigger: stake_confirmation tilt without last_filing.date stamp; calibrated_at_price >5% off verified spot.
5. **Pre-mortem failure.** Any thesis without at least 5 plausible thesis killers explicitly enumerated and probability-weighted does NOT pass commit.
**§9 Comparison with adjacent metrics:**
- **PWER vs Kelly:** Kelly answers growth-optimal fraction; PWER answers whether trade clears deployment hurdle. Kelly per position clamped to layer ranges (L1 7-12%, L2 3-5%, L3 2-8%); if Kelly outputs above L1 cap on high-prob binary, cap holds — concentration risk dominates growth optimality at fund level.
- **PWER vs Sharpe:** Sharpe is portfolio metric. PWER feeds numerator; says nothing about correlation. Activist-cluster correlation (DOE5% basket as single position) is Sharpe-side discipline PWER alone misses.
- **PWER vs CVaR:** Bear single-point estimate understates tail. Fix: bear-case CVaR floor cross-check — 5th percentile bad outcome from activist's historical campaign distribution must be no worse than −40% from current price for L1, −50% L2, −60% L3. Below floor → downgrade one layer.
**§10 Worked examples (canonical):**
**10.1 KH Neochem (Strategic Capital) — disclosure-alpha-vs-resolution-alpha.**
Initial at ¥2,494 (below SC ¥2,737 WAC):
- Base 45% ¥3,100 +24.3% | Bull 25% ¥3,600 +44.3% | XB 10% ¥4,500 +80.4% | Bear 20% ¥2,000 −19.8%
- PWER ≈ 26%, asymmetry ≈ 2.2 → L2 init 3%
Price → ¥2,927 (+17%, 7% above SC WAC):
- Base 45% +5.9% | Bull 25% +23.0% | XB 10% +53.7% | Bear 20% −31.7%
- **PWER = +7.6% → fails 20% gate; do not initiate**
Lesson: +17% pop was disclosure alpha not resolution alpha. Recompute PWER at post-announcement prices. Re-entry watch ¥2,400-2,550 or formal proposal filing before April record date.
**10.2 Kansai Paint (Silchester) — total-return PWER lift.**
At ¥2,455 (below Silchester ¥2,511 WAC):
- Bear 20% −10.4% | Base 45% +26.3% | Bull 25% +46.7% | XB 10% +83.4%
- PWER = +29.7%, asymmetry = 4.5 → L3 init 3%
At ¥2,378 (deeper below WAC, lower bull/base targets reflecting Nerolac India concerns): price-only PWER = +18.2% fails gate, but with div + buyback carry over 18-24mo hold (~12pp accrual), total-return PWER lifts ~24-26% — clears as patient compounder.
**10.3 Sanyo Denki (Strategic Capital) — anchor exit signal.**
SC WAC ~¥3,400-3,800; current ¥5,660 = 50-65% above WAC. Co-investment edge closed by §4. Standalone PWER ~12-13% on remaining governance optionality. Queued add WITHDRAWN. Re-entry: pullback within 15% of SC WAC, or fresh activist convergence.
**10.4 Effissimo Mode 2 names — long-duration template.**
Ricoh (24.77%) and Teijin (16.44-19.26%) textbook large-stake Mode 2/3. Historical base rate at these stakes: 2-4x MOIC over 4-6 yrs → 18-30% IRR. Bear case = grinding stalemate where Effissimo trapped by own position size (poor exit liquidity >15%). **PWER must be annualised** — 2.5x MOIC over 5 yrs = 20% IRR, not headline 150%.
**Appendix A — Default formula reference:**

```
PWER         = Σᵢ (Pᵢ × Rᵢ)
Rᵢ           = (Targetᵢ − Current)/Current + Carryᵢ
Carryᵢ       = (div_yield + buyback_yield) × (Monthsᵢ/12)
IRRᵢ         = (1 + Rᵢ)^(12/Monthsᵢ) − 1
PW-IRR       = Σᵢ (Pᵢ × IRRᵢ)
Asymmetry    = (P_bull × R_bull + P_xb × R_xb) / |P_bear × R_bear|
Gates:
  Entry    : PWER ≥ 20% AND Asymmetry ≥ 1.5
  Harvest  : PWER < 15% OR Asymmetry < 1.2
  Override : Anchor reduction, velocity trigger, regime break, quarantine
```


**Appendix B — Default probability anchors by archetype:**
| Archetype | P(Bear) | P(Base) | P(Bull) | P(Extreme Bull) |
|---|---|---|---|---|
| Effissimo Mode 2 | 20% | 40% | 25% | 15% |
| Effissimo Mode 1 (capital return) | 15% | 50% | 25% | 10% |
| Dalton public-demand | 25% | 40% | 25% | 10% |
| Murakami Stage 1-3 | 25% | 35% | 25% | 15% |
| Strategic Capital | 30% | 45% | 20% | 5% |
| Silchester / Ariake (no forcing) | 25% | 50% | 20% | 5% |
| GMO-Usonian | 25% | 50% | 22% | 3% |
| Palliser / AVI engagement | 30% | 40% | 25% | 5% |
| L4 Merger arb (post-TOB filing) | 15% | 0% | 75% | 10% |
---
### 3.6 `damodaran-mapping.md` — Damodaran Philosophy Mapping
**What it is:** Codifies how the Asuka Fund and tracked investors sit within Aswath Damodaran's *Investment Philosophies* taxonomy.
**Why it matters:** Disciplines edge attribution, prevents style drift, provides vocabulary for stress-testing new ideas across philosophical lenses.
**Exhaustive summary:**
**§1 Damodaran's seven philosophies (Asuka usage):**
- Charting / Technical — Asuka rejects entirely; no tracked investor here; no sizing decision justified by chart pattern.
- Information Trading — EDINET pipeline operates here narrow edge: faster ingestion, joint-holder aggregation, language parsing — process discipline NOT informational asymmetry.
- Market Timing — Asuka does NOT time markets; stays 100% deployed regardless of regime.
- Passive (Classical) Value Investing — Graham-Dodd; mean-reversion via fundamental delivery not active intervention.
- Activist Value Investing — buy undervalued AND force value-realisation event. Catalyst manufactured not awaited.
- Growth Investing (split GARP) — sustainable above-average growth market underestimates.
- Arbitrage — closed-form mispricings; merger spreads, dual-listed pairs, convertible-to-common, index-rebalancing flow.
**§2 Where Asuka sits:** Primary classification **Activist Value Investing** with deliberate refinement: fund is a **public-equity coattail expression** of activist value rather than campaign-runner. Edge attribution: informational minor, analytical secondary, structural PRIMARY, temporal PRIMARY. Temporal is the critical refinement — activist captures resolution alpha over full campaign arc; Asuka captures gap between disclosure-day pricing and activist's eventual harvest, exiting at catalyst resolution rather than waiting for full restructuring. Same thesis, different time horizon, different liquidity profile, different operational cost structure.
Asuka explicitly is NOT: passive value (requires catalyst), information trader (public filings ≠ informational advantage strict sense), growth investor (L3 GMO sleeve has growth-compounder characteristics but sized as ballast not alpha engine), arbitrage (L4 sleeve only).
Cleanest one-line: "Asuka is a public-equity, liquid wrapper around the corporate-governance-change asset class that activists privately monetise."
**§3 Per-tracked-activist mapping:**
- **Effissimo+SMT:** Pure activist value. Mode 1/2/3 framework. Concentrated 15-30%+ stakes, multi-year, "pure investment" boilerplate. Closest to Damodaran archetype.
- **Murakami network:** Activist value with extraction bias. Five-step playbook; exit step (harvest via buyback) differentiates.
- **Oasis:** Activist value with public communication overlay (most aggressive communicator).
- **3D:** Activist value with operational restructuring bias.
- **Dalton+NAVF:** Activist value with dual-vehicle structure; broad portfolio approach.
- **SilverCape:** Activist value with single-family-office patient capital. TMT/digital infrastructure cluster.
- **City Index Eleventh + UGS:** Activist value, domestic. Distinct from foreign in regulatory toolkit and cultural access.
- **Silchester:** **Reclassified Tier 1.5 activist value** after Bank of Kyoto. Classical-value heritage remains but engagement willingness demonstrated.
- **Ariake:** Passive value with friendly engagement — regional bank specialist. Classical value with sector-specialist analytical edge.
- **GMO-Usonian:** Passive value / quality compounder.
- **MIRI:** Passive value small-cap specialist.
- **AVI Japan:** Activist value with constructive UK long-only style.
- **Arcus Investment:** **Classical (passive) value, NOT activist.** Cleanest non-activist signal in universe — London deep value, $2.3B AUM, no proxy contests, no AGM proposals, no public letters. Corporate activity is by-product of value-style discipline NOT manufactured catalyst.
- **Zennor:** Tier 2 long-only special situations.
- **ValueAct:** Activist value with **growth-investing overlay** — Olympus/JSR/MF/Takara playbook focuses on technology-transformation rather than balance-sheet unlock.
- **Ueshima/DOE5%/Naturali:** Activist value with explicit named-vehicle thesis ("DOE5%" = demand encoded in corporate name). Proprietary-capital structure (no LP redemptions, no quarterly pressure) gives patience of passive-value investor with demands of activist.
**§4 Cross-philosophy comparison:**
- Vs Classical Value — Asuka requires identified catalyst. Resona AM/Grid (5582) rejection canonical: founder 54.9%, no activist forcing, screened cheap, Asuka rejected. Classical investor might still own Grid; Asuka cannot.
- Vs Activist Value (campaign-runner) — Asuka doesn't bear operational cost; trade-off is can't capture full campaign-resolution alpha. Accepts trade for daily liquidity, no overhead, 2.2yr mean harvest vs 4-7yr.
- Vs GARP — Asuka L3 sleeve has GARP characteristics (Shift, I'LL, Syuppin) but sizing anchored to engaged-investor signal not PEG in isolation. I'LL analysis (PEG ~0.55, Fwd P/E 13.9x at ROE >100%) is explicit GARP layered on engaged-investor signal — both must be present.
- Vs Information Trading — EDINET filings public to all simultaneously; cross-vehicle aggregation discipline is small information-trading kicker but process advantage not informational asymmetry.
**§5 Useful philosophy lenses for stress-testing new ideas — every new idea should pass ≥2 independent philosophy lenses cleanly:**
- **Classical-value lens:** "If the activist disappeared tomorrow and the catalyst evaporated, would I still own this for 10 years on fundamentals alone?" If no, position is purely activist-coattail and depends on activist staying engaged — size accordingly. Tamron and Ricoh fail this; Hyakugo Bank and Optex pass.
- **Activist-value lens:** "What is the value-realisation mechanism, who controls it, on what timeline?" If mechanism unclear or activist lacks operational competence, thesis is a hope not a plan. Yakult Honsha Oasis-failure-pattern applies — Dalton has will to escalate but founding-family bloc + large-cap diffuse + consumer-staples sector trifecta historically blocks resolution.
- **Growth lens:** "Is bull-case multiple expansion supported by forward earnings growth, or pure multiple re-rating on capital return?" If both required, bull-case probability compounds two conditional probabilities. Money Forward, Shift, Syuppin live in this regime.
- **Information-trader lens:** "What does market not yet know that I do, and how quickly will it become consensus?" For Asuka usually = joint-holder aggregate, 重要提案行為等 language-parsing, cross-vehicle stake math. Consensus timeline ~30 days post-filing as financial press writes it up.
- **Arbitrage lens:** "What is closed-form payoff structure if deal happens vs doesn't, and what is spread?" Critical for L4; also applied to MBO-blocking situations (Effissimo Mode 3) where activist essentially sits on put on management lowballing take-private. Sankei REIT canonical L4 example.
- **Charting/market-timing:** Deliberately NOT used. If thesis only works under specific macro regime or chart setup, philosophy-discipline broken.
Discipline: if name only clears activist-value lens but fails classical-value (no fundamental floor) and growth lens (no forward-earnings story), position is single-thesis and fragile. Size at lower end of target band and set tighter exit tripwires.
---
### 3.7 `edinet-monitoring-protocol.md` — EDINET Surveillance Operations Manual
**What it is:** Operational specification for the EDINET surveillance layer feeding the Asuka activist event-driven pipeline. **Working directory: `C:\Users\GAO\GAO\Asuka_EDINET\`.** Cadence: Mon-Fri, 09:00 SGT primary scan + 18:00 JST end-of-day sweep.
**Why it matters:** Operational details of what data the layer ingests, how filings are classified, latency targets, anomaly triggers, and the alert priority taxonomy.
**Exhaustive summary:**
**§1 Filers under active surveillance (P1/P2/P3 priority tiers):**
P1 — Hard Activists (real-time priority): Effissimo Capital (Effissimo Pte + SMT Partners Cayman); Murakami network (17+ vehicles); 3D Investment Partners; Oasis Management; AVI Japan; Elliott; Palliser; ValueAct; SilverCape; Be Brave.
P2 — Engaged Long-Only & Domestic Activists (same-day email): Silchester (via Northern Trust AVFC nominee); GMO-Usonian; Dalton/NAVF; Strategic Capital + UGS Sunshine LP co-files; LIM Advisors; Ariake; MIRI; Hibiki Path; Ueshima/DOE5%/Naturali; CIE; UGS; Zennor.
P3 — Watch-Only & Universe Expansion (daily digest): Varecs Partners (n=19, +41.9% mean), United Managers Japan (n=27, +37.1% mean), Arcus Investment, Sapphireterra (AVI-aligned at Sanyo Shokai). Avoid: Curi RMB (-5.1% mean), Taiyo Pacific (caution despite 54% positive).
**§2 EDINET filing types monitored:**
| docTypeCode | JP | EN | Trigger |
|---|---|---|---|
| **350** | 大量保有報告書 | Large Shareholding Report — initial | Stake first crosses 5.00% |
| **360** | 大量保有報告書（訂正） | Large Shareholding Amendment | Correction to 350 |
| **370** | 変更報告書 | Change Report | Subsequent ±1pp move OR change in joint-holder composition/purpose/address |
| **380** | 変更報告書（訂正） | Change Report Amendment | Correction to 370 |
| 180 | 臨時報告書 | Extraordinary Report | AGM voting results, shareholder proposals — secondary filter, not real-time |
**PIT discipline:** signal anchor is `submitDateTime`, never `periodEnd`. EDINET requires filing within 5 business days but real cases run 1-10 days. Pipeline records both `filing_date` and `trigger_date` and computes `gap_days`.
**Doc 180 supplement:** AGM voting results (in-meeting board approvals, special-resolution outcomes, shareholder-proposal pass/fail) filed as 臨時報告書. Pipeline secondary scan against doc 180 keyed to May-June AGM calendar window catches binary outcomes for L1 positions without separate proxy-result feed.
**§3 Filing language decoder (Tier P/R/E/C):** Reproduces CRMC §3 verbatim. Transition recording: for every campaign, pipeline persists filing 1 purpose tier and stake → filing N tier and stake at transition → months from entry to first transition. Transition events are P1-priority alerts regardless of stake delta size.
**§4 Custody account aliases — foreign filer beneficial-owner mapping:**
| Custodian/nominee string | Resolves to | Source |
|---|---|---|
| Northern Trust Company AVFC Re: Silchester International Investors International Value Equity Trust | **Silchester** | Bank of Kyoto May 2022 letter — POA explicitly disclosed |
| JP Morgan Chase Bank — generic custody | UNKNOWN — verify via XBRL 取得資金 / 共同保有者 | "JPM 380055"-style numerical aliases require direct lookup |
| Citigroup / GS International / Nomura International PLC custody | Variable — see PB facilitation rule | Joint-holder section + PB-flow forensics |
Rule: any nominee-account string flagged `BENEFICIAL_OWNER_PENDING_VERIFICATION` until XBRL filer-entity field resolves underlying party. No PWER update until human PM verification.
**PB block-warehousing pattern (memory rule #23):** PB files NEW 5%+ → in-universe activist files NEW or ±pt within 30-90 days → PB unwinds concurrent. Confirmed Apr 2026: Teijin (GS NEW Mar 31 → -3.26pt vs Effissimo +1.73pt same week); Sankei REIT (GS+Nomura -7pt vs CIE +5.96pt over 8d); Casio (Nomura group -9pt+ vs 3D NEW 5.03%). Pipeline maintains separate `pb_warehouse_log`; entries auto-expire 90 days unless in-universe filer registers.
**Ueshima/DOE5%/Naturali cluster (domestic precedent):** Nippon Felt 3512 filing (S100XVOK) — Ueshima 3.54% + Naturali 1.16% + DOE5% 0.31% = 5.01% via joint-holder section. **Vehicle name "DOE 5 Percent" was thesis statement not coincidence.** Always read 共同保有者 section before treating individual filer string as full economic interest.
**§5 Anomaly trigger conditions (filer-specific):**
Universal triggers (all filers):
- Filing burst (≥2 within 7d) → +5pp Bull / -3pp Bear (Pacific Industrial Sep 2025 precedent)
- Pre-AGM acceleration ratio >1.5× (Feb-Apr rate vs baseline) → +10pp Bull / -5pp Bear
- 12+ month silence after established cadence → -10pp Bull / +15pp Bear (quiet exit risk)
- Stake reduction ≥1pp from peak when historical monotonic = severe → Mode 2 → exit transition
- Threshold crossings 10%, 15%, 20%, 33.4%, 50% each elevate alert priority by one tier; 33.4% = veto territory L1 upgrade candidate
- Filing gap days ≥10 near record dates = strategic timing flag (log don't auto-adjust)
Filer-specific (Effissimo, Murakami, Oasis, 3D, GMO-Usonian, Be Brave, Zennor) — already reproduced in CRMC §4 above.
**Severity scoring:**
- HIGH: initial 5% on in-universe target; transition to Tier C; threshold ≥33.4%; Stage 5 confirmation
- MEDIUM: stake change >1pp; transition R→E; defender Level 4-5 in target's response
- LOW: amendment no ratio change; address/corporate-name correction; Tier P filings on non-portfolio targets
Alerts grouped by issuer / holder group / same-day sequence so wolf-pack day surfaces as one alert not five.
**§6 Pipeline architecture (13-file Python system at `C:\Users\GAO\GAO\Asuka_EDINET\`):**

```
Asuka_EDINET\
├── config.py                  # Portfolio baselines, watchlist, thresholds, language tier mappings
├── state_manager.py           # Persists current_state.json + stake_history.json
├── edinet_fetch.py            # EDINET v2 API via edinet-tools (Subscription-Key required since Apr 2024)
├── filing_parser.py           # XBRL parse → ActivismSignal records
├── pwer_engine.py             # PWER delta recalculation
├── language_classifier.py     # Tier P/R/E/C classification
├── anomaly_detector.py        # §5 rules engine
├── joint_holder_extractor.py  # Custody/nominee/dual-vehicle aggregation
├── murakami_monitor.py        # Separate Murakami network module (08:30 + 18:00 JST)
├── run_daily.py               # Main entry — invoked by Task Scheduler
├── generate_dashboard.py      # 4-tab HTML (Positions/Alerts/Filings/Log)
├── email_alert.py             # SMTP via Google Workspace app password
├── cowork_agent.py            # Hand-off to Cowork (reads dashboard_latest.html at 09:15)
├── run_pipeline.bat           # Task Scheduler batch wrapper
└── output/
    ├── current_state.json
    ├── stake_history.json
    ├── murakami_state.json
    ├── pwer_report_YYYY-MM-DD.json
    ├── dashboard_YYYY-MM-DD.html
    └── dashboard_latest.html
```


Layer responsibilities:
- **Ingest:** `documents.json?date=YYYY-MM-DD&type=2`, filters to docTypes 350/360/370/380, returns typed `LargeHoldingReport` objects. Auth via `EDINET_API_KEY` Windows env var. Retry on 429s and 5xx.
- **Parse:** Three-layer matching: exact EDINET E-code → Japanese keyword → English keyword. XBRL fields: `filer_name`, `target_company`, `target_ticker`, `ownership_pct`, `prior_ownership_pct`, `ownership_change`, `purpose_text`, `important_proposal` flag, `joint_holders`.
- **Classify:** Tier P/R/E/C via regex+keyword. Anomaly rules against historical state.
- **Aggregate:** Dual-vehicle resolution (Effissimo+SMT, Dalton+NAVF, Murakami umbrella, Ueshima+DOE5%+Naturali) and PB custody. Same-day dual-filer detection auto-escalates.
- **Score:** Delta model: +3pp per 1pp stake increase asymmetrically (−4pp for decreases), +8pp NEW entry, −12pp full exit, ×1.5 proximity multiplier within 45 days of known catalyst.
- **Output:** 4-tab HTML, formatted email, Cowork morning brief.
Scheduling: Task Scheduler triggers `run_pipeline.bat` Mon-Fri 09:00 SGT (catches overnight EDINET batch). Murakami module runs separately 08:30 JST (safety net) and 18:00 JST (post-EOD ~17:30). Wake-from-sleep via wake timers. Exit code 1 triggers Cowork downstream; exit code 0 silent success.
Murakami sub-module separate: 17+ vehicles, internal redistribution patterns, sometimes multiple files/day. Separation avoids polluting primary state with internal-transfer noise.
**§7 Latency targets and known failure modes:**
| Filing type | Target | Median | Worst case |
|---|---|---|---|
| Initial 350 (in-universe target) | <60 min | ~25 min | ~4 hr (overnight batch lag) |
| 370 ±1pp on portfolio position | <60 min | ~25 min | ~4 hr |
| Tier-transition R→E or E→C | <60 min | ~25 min | next-day 09:00 SGT |
| 180 AGM voting result | next-day 09:00 SGT | next-day | next-day |
| P3 universe filings | daily digest 09:00 next day | daily digest | daily digest |
Known failure modes:
1. EDINET API key expiry (silent failures since Apr 2024 reqd) — weekly key-validity health-check.
2. EDINET API 429/5xx during batch publication (~17:30 JST evening batch) — exponential backoff 5 retries.
3. Aggregator drift on EDINET filer codes — XBRL-first rule supersedes.
4. Custody-string opacity — flagged BENEFICIAL_OWNER_PENDING_VERIFICATION until human PM verifies.
5. Bloomberg lag (MOF filings 30-min to several-hour lag) — EDINET direct primary; Bloomberg ACTV/FLNG reference only.
6. edinet-tools library schema shift — version pinned in requirements.txt; daily smoke-test.
7. SMTP app-password rotation — env var not in code; rotation runbook documented.
Health checks: daily logs/pipeline.log; weekly dashboard sanity-check; monthly roster review.
**§8 Maintenance cadence:** Quarterly filer roster review (Bloomberg ACTV base-rate query, promote P3→P2 above 30% mean/40% batting; demote on consecutive negative cases); custody alias refresh; anomaly threshold recalibration. Monthly: PB warehouse reconciliation; EDINET key validity; pending-verification items aged 30+ days. Weekly: log sweep; Friday close dashboard sanity. Daily: 09:00 SGT pipeline run + 09:15 SGT Cowork morning brief + any HIGH-severity alert → structured re-read + 100-word note.
**§9 Single source of truth hierarchy (when sources conflict):**
1. **EDINET XBRL** (filer's own filing) — supersedes everything
2. Pipeline `current_state.json` — authoritative for in-book stakes
3. Bloomberg ACTV / FLNG — secondary verification
4. kabupro.jp / irbank.net / Yahoo Finance JP — fallback only, must be stamped with EDINET doc ID
5. Sell-side / news aggregators — colour, never primary signal
Memory rule #22 (XBRL-first) is BINDING. Action signals never lock until human PM verification stamp `action_verified_date=today` applied.
---
### 3.8 `multi-activist-dynamics.md` — Wolf Packs, Crowding, Sizing Discipline
**What it is:** Standing reference on multi-activist convergence dynamics.
**Why it matters:** Operationalises wolf-pack detection, sizing penalties for crowding, and compression of catalyst horizons under multi-filer presence.
**Exhaustive summary:**
**§1 Wolf pack defined:** Two or more independent investors with separate capital structures and separate decision-making authority who arrive on same target within compressed window and pursue compatible (not necessarily identical) demands. Defining feature: **independence with alignment**.
**Distinguished from:** dual-vehicle structures (Effissimo+SMT, Dalton+NAVF, SC+Sunshine — single filer with disclosure plumbing); Murakami internal redistribution (sub-divisions of one beneficial owner); coincidental ownership (no coordination/compatible thesis).
**Asuka detection rule — three concurrent conditions:**
1. Separate beneficial owners verified through independent EDINET 大量保有 filings
2. Compatible filing language (typically Tier R across ≥2 filers, or Tier E with proposals from lead)
3. Overlap in demand surface (capital return, governance reform, M&A optionality) that compounds rather than competes
Canonical precedent: **Toyo Securities (8614) 2022-2024** — Be Brave + UGS Sunshine G/H + Capital Management + Epic Asset Management, four independent filers, aggregate ~30%, coordinated proxy mobilisation, CEO Kuwabara forced withdrawal 5 minutes before AGM. PBR 1.0x proposal Apr 2024; defensive measures extended May 2025. 13 months from initial filing to win — roughly half median Japan campaign duration.
**§2 Sequential vs simultaneous arrival:**
- **Simultaneous arrival** (multiple 5%+ within ~30 days) = coordinated wolf-pack formation, prearranged or quasi-prearranged. US equivalent: "13D cluster" (Brav/Jiang/Kim 2015 elevated abnormal returns when multiple 13Ds within 30 days). Tipping (Coffee/Palia). Operationally constrained in Japan because EDINET requires filing within 5 business days (tighter than US 10-business-day Schedule 13D).
- **Sequential arrival** (typical Japan) — lead filer crosses 5%, disclosure studied, then 2nd/3rd filers appear over weeks-to-months as they complete due diligence and accumulation. Sankei REIT (2972) J-REIT TOB defence canonical: CIE+Aya Nomura ratcheted 11.22% → 17.19% → 19.35% via CR No.6 Apr 6 2026, fresh joint-holder appearing on Apr 28 filing. **"共同保有者が増加したこと"** cover-sheet phrase = explicit tell new vehicle has joined active situation.
Sizing implication: simultaneous arrival harder to front-run (market sees cluster forming in real time, re-prices quickly); sequential creates series of discrete entry windows. Asuka's optimal entry remains T1-T2 on the lead filer — entering after 2nd/3rd typically means +8-15% above lead activist WAC = fails 15% WAC cross-check.
**Highest-quality wolf-pack signature: sequential arrival with Tier 2 long-only follower amplifying Tier 1 hard activist lead.** Ines Holdings (9742) — Effissimo at 12.35% with AVI at 6.02% on CR No.1 Jan 23 2026 — Effissimo provides campaign threat; AVI provides patient capital that won't fold under management stalling. Combined hold more than additive. In contrast, two Tier 1 hard activists on same name (Be Brave + UGS at Toyo Securities) creates speed but also raises exit liquidity risk.
**§3 Crowding metrics — three dimensions tracked separately:**
**Filer count:** Two = wolf pack; three = crowd; four+ = saturation event. Toyo Securities four-filer pattern rare in Japan. Crossing from two to three filers is the single most important inflection — materially compresses catalyst horizon and signals underlying thesis has become consensus rather than variant.
**Aggregate stake (thresholds matter for legal-resolution AND behavioural reasons):**
| Aggregate | Implication |
|---|---|
| <10% | Pre-visibility; market unaware |
| 10-15% | Negotiating power begins; management forced to engage |
| 15-20% | Effissimo Mode 1 → Mode 2 boundary; capital return demands escalate |
| 20-33.4% | Strategic significance; major transactions become difficult without consent |
| 33.4%+ | Special-resolution veto — blocks mergers, spin-offs, charter changes |
| 50%+ | Effective control; rare for external coalition |
**Free-float saturation (most often ignored):** When wolf pack accumulates 25-30% on name where founder + cross-shareholders + policy holders together hold 35-40%, floating shares available to activists substantially exhausted. Further accumulation requires forcing structural unwinds; exit mechanics illiquid. Inui Global Logistics reduction decision driven by this — at ¥159M average daily volume, dual-activist (LIM + MIRI) book itself was binding liquidity constraint regardless of thesis quality.
Inflection threshold: wolf-pack aggregate + founder/cross-shareholder bloc >50-55% of issued shares → price discovery function breaks down; natural sellers vanish; stock moves on filings rather than fundamentals; campaign outcome becomes binary. Sankei Real Estate post-April 6 operating in this regime.
**§4 US activist coordination — empirical anchors:**
- Brav/Jiang/Partnoy/Thomas (2008, J. Finance) and Brav/Jiang/Kim (2015) — hedge fund activism generates statistically significant abnormal returns ~5-7% in (-20, +20) window around 13D filing, persisting one year out, more pronounced when targets ultimately sold. Operating performance improvements at targets, rebuts short-termism critique. Dataset ~2,000 events 1994-2007.
- Coffee/Palia (2016) — legal-academic treatment of wolf-pack coordination without triggering 13(d) "group" status. Documents "tipping" (informal information sharing). In US explicit group declaration imposes joint filing; in Japan 共同保有者 disclosure mandatory once joint-holder relationship established.
- Becht/Franks/Mayer/Rossi on European engagement, Becht/Franks/Grant on cross-border — European data shows single-activist generates lower abnormal returns than US; coordinated/wolf-pack closes most of gap. **Japan with higher dispersion of cross-shareholders and weaker proxy access behaves more like Continental Europe — wolf-pack formation MORE important to campaign success in Japan than in US.**
Named US analogies: Trian+JANA+Pershing on McDonald's, Yahoo, Allergan (multi-activist convergence with distinct demand axes); Elliott+Starboard at multiple tech names ("polite wolf pack" — coordination operational not declared); Allergan/Valeant/Pershing 2014 cautionary on insider trading risk when coordination crosses into material non-public information sharing.
**§5 Japan-specific dynamics:**
- **共同保有者 disclosure regime:** Two or more entities as joint holders (sharing voting power, transferring shares, acting in concert) file single 大量保有 listing all parties with stakes summed. "(3) 共同保有の状況" section is single most important page for wolf-pack detection. Nippon Felt (3512) Ueshima filing canonical (vehicle literally named after policy demand).
- **Murakami network as serial co-filer:** Specific combination is a signal — CIE/CIF/Reno only = standard accumulation Mode 1; ATRA as direct co-filer = high-conviction Wavelock HD Nov 2025 precedent +1 sizing tier; Aya Nomura individual + ATRA roughly equal = family principal deployment highest conviction; high CR numbers (15+) with new individual vehicle 5%+ often internal redistribution (Exedy No.24 canonical — CIF "buying" 6.05% was receiving 2.85pp from Reno selling).
- **Strategic Capital / UGS Sunshine LP partnership:** SC and UGS are joint GPs on Sunshine LP series (D/E/F/G/H), used as TOB-execution vehicles. Keihanshin Nov 2020 canonical. **If SC subsequently files on name where UGS already present, TOB optionality probability jumps from ~15% to ~35%+.** Meito (2207) tripwire still in force.
- **Domestic-foreign cross-pollination:** Yakult Honsha Dalton Kizuna campaign positioned for June 2026 AGM with 2 director nominees; parallel Ariake regional banks. Pattern of foreign hard activist + domestic long-only + domestic hard activist rare but occurs — Sanyo Shokai (8011) AVI lead 11.55% + Sapphireterra co-filing AGM proposal Apr 1 2026. Joint-holder section needs explicit verification on every refresh.
**§6 Bimodal outcome distribution (wolf-pack situations do NOT produce normally distributed returns):**
Three structural reasons drive bimodality:
1. **Concentration of attention forces binary outcome.** Single 5% activist can be ignored 18 months. Three or four = corporate-governance event covered by financial media, ISS/Glass Lewis, FSA stewardship desk, TSE governance reform tracking. Management either capitulates within first AGM cycle (large win) or entrenches through defensive coalition (large failure). Middle ground collapses.
2. **Oasis-failure pattern is canonical drag-mode.** Founding family/foundation ≥30% bloc + large-cap diffuse + consumer/pharma = three structural danger signals. Activists have firepower but not voting math. Yakult Honsha currently fits all three; Morningstar fair value ¥1,311 vs ~¥2,600 current — gap is activism premium that may or may not close.
3. **Win-mode produces spectacular outliers.** Effissimo $4B excess profit on Kawasaki Kisen; Murakami JAFCO greenmail ~¥7B; Be Brave Nishikawa Rubber DOE 8% adoption +87% in 13 months = right tail. Dual-mode output → **portfolio-level expected value calculations must use scenario weights NOT arithmetic averages.** 25% prob +80% and 25% prob -25% is NOT same as 50% prob +27.5% even though means match.
Empirical cuts: Dalton standalone n=61, +21.9% mean, 33% >+20% Tier 1.5 at best; Dalton+NAVF n=18, +57.4% mean, 78% >+20% top decile; AVI n=39, +27.6% mean, +18.8% median; Effissimo closed-case ~82% MOIC; Murakami Bloomberg ACTV n=92 +20.4% mean, 44% >+20%. Wolf-pack situations sit at higher-mean/higher-variance end.
**§7 Position sizing rules when 3+ activists arrive — HALVE THE SIZE:**
Four supporting rationales:
1. **Crowding compresses entry alpha** — by 3rd filer, market fully aware, lead WAC +8-15% below current price; T1-T2 edge has decayed.
2. **Outcome distribution becomes more bimodal** — 12% L1 on assumption of smooth re-rating is mis-sized for binary outcome. Halving to 6% converts to option-like exposure that survives failure mode while capturing win mode.
3. **Exit liquidity risk multiplies** — all filers harvest within similar window post-catalyst; if aggregate filer holdings 25-30% of float, selling pressure compresses realised exit below modelled bull. Most acute in sub-¥50B mcap (Inui, Pegasus, Tomoe). Rule-of-thumb correction: cap position at 50% of three-day ADV rather than standard L2/L3 sizing band.
4. **Correlation penalty inside book** — positions with 3+ activists share same systemic catalyst window (June AGM) and same activist-quality factor. Sizing at standalone PWER materially overstates marginal portfolio contribution; correlation penalty on 12% L1 with 3+ activist crowding can run 30-40%.
Operational implementation — discrete check at every sizing decision:
1. Count independent beneficial owners on most recent 大量保有/変更報告書. Murakami=1, Effissimo+SMT=1, Dalton+NAVF=1, SC+UGS Sunshine=1 if joint, 2 if independent.
2. If count ≥3 → maximum sizing halved versus standard layer. L1 12% becomes L1-capped 6%; L2 5% becomes L2-capped 2.5%; L3 usually below threshold where halving matters.
3. Re-evaluate at each new filing. If count drops to 2 (one filer exits), cap can be relaxed — but **wait for confirmed exit on EDINET (変更報告書 showing reduction below 5%) before relaxing constraint.**
**§8 Compression of catalyst horizon under crowding (non-linear with filer count):**
- Single activist: 18-36 months avg campaign-to-resolution. Effissimo closed-case 2.2 yrs.
- Two activists (verified wolf pack): 12-18 months. Bilateral pressure; management can still play one off other.
- Three activists: 8-14 months. Toyo Securities 13mo; Be Brave Nishikawa Rubber DOE 8% adoption 13mo.
- Four+ activists: 6-12 months, sometimes less if AGM proximity forces resolution.
Compression NOT arithmetic. Three activists don't produce 3× pressure of one — qualitatively different campaign environment where corporate counsel's standard playbook (private engagement → board review → public letter response → AGM contest) gets compressed because each step produces media coverage that mobilises next filer.
Portfolio implication: forward-PWER recalibration. Standalone Murakami filing might support 24-month PWER +25% absolute (~12% annualised). Same filing in three-filer context might support 12-month PWER +30% absolute (~30% annualised) — but wider variance and halved position size. **Annualised return materially higher; dollar contribution to portfolio similar.** Correct trade for fund's structure: more event-driven turnover, faster capital recycling into next high-PWER situation, lower exposure to long-tail bear case in any single name. Catalyst-proximity tilt becomes more aggressive when filer count ≥3, because bimodal regime is structural rather than just temporal.
**§9 Operational summary (when new EDINET filing arrives on name already held):**
1. Identify all beneficial owners present (read 共同保有者 section in full; collapse Murakami/Effissimo+SMT/Dalton+NAVF/SC+Sunshine to single filer-units)
2. Classify arrival pattern (sequential or simultaneous; Tier 1 hard + Tier 2 long-only = highest-quality signature)
3. Re-measure crowding metrics (aggregate stake, free-float saturation, filer count)
4. Apply halve-the-size rule if filer count ≥3
5. Recompute forward PWER on compressed horizon if filer count ≥3 using bimodal scenario weights
6. Confirm liquidity ceiling (50% of 3-day ADV, not standard layer cap)
7. Set new tripwires for either further accumulation (upgrade) or first 変更報告書 reduction by any filer (downgrade signal that may justify pre-emptive trim)
**Framework treats wolf-pack arrival as an EVENT that resets position thesis, NOT as confirmation of existing thesis.** Most expensive sizing error: treating third filer as additional confirmation of original conviction, when in fact it is a regime change demanding smaller sizing on tighter horizon with bimodal scenarios.
---
### 3.9 `regime-context.md` — Macro & Regulatory Backdrop
**What it is:** Boundary condition document codifying macro and regulatory regime in which Asuka operates. Strategy's edge requires this regime to remain broadly intact. **[QUARTERLY]** refresh markers and **[ANNUAL]** refresh markers tag sections.
**Why it matters:** Identifies the regime conditions whose deterioration would force a strategy reset; identifies the regime tailwinds the fund is positioned to monetise.
**Exhaustive summary:**
**§1 Regulatory timeline (key dates, layered reinforcement):**
- **Feb 2014** First Stewardship Code (FSA voluntary, "comply or explain"). Light uptake initially; became real when GPIF made it manager-selection criterion.
- **Jun 2015** Corporate Governance Code adopted by TSE. First written governance benchmark.
- **May 2017** Stewardship Code revision — individual stewardship reports + voting record disclosure by resolution. Operationalised "engage or explain."
- **Jun 2018** CG Code revision — cross-shareholding policy disclosure and rationale + capital cost analysis. Cross-shareholding (政策保有株式) database era starts.
- **Mar 2020** Stewardship Code 2nd revision — ESG and sustainability.
- **Jun 2021** CG Code 2nd revision — Prime Market ≥1/3 independent directors, TCFD climate disclosure, nomination/comp committees with independent majorities. **Made activist board nominees pass-able** (ISS/Glass Lewis have code-defined benchmark).
- **Mar 31, 2023 — TSE PBR<1 DIRECTIVE. SINGLE MOST IMPORTANT POLICY EVENT FOR ASUKA STRATEGY.** "Action to Implement Management that is Conscious of Cost of Capital and Stock Price" request. Prime + Standard companies trading below 1.0x PBR required to disclose specific capital efficiency improvement plans. TSE began publishing monthly lists of compliant/non-compliant — public-shaming mechanism that turned voluntary guidance into enforceable forcing function. Activist campaigns: **58 in 2019 → 187 in 2024** (>3× expansion concentrated post-Mar 2023).
- **Jan 2024** New NISA — government-backed retail equity savings, permanent tax-free, lifetime ¥18M, annual ¥3.6M growth quota. Largest structural domestic flow change in two decades.
- **Mar 2024** BOJ ends NIRP and YCC — first hike in 17 years. Banks NIM up, insurers reinvestment yield up, JGB curve normalising. Cross-shareholding sales accelerate.
- **May 1, 2026 — EDINET 大量保有報告書 reform LIVE.** [QUARTERLY] Most significant disclosure regime change since 2007. Three changes: (i) みなし共同保有者範囲拡大 (deemed joint-holder scope expansion); (ii) 現金決済型デリバティブ算入 (cash-settled derivatives counted toward 5% threshold); (iii) 重要提案行為の整理 (clarification of "important proposal" reservations). **Dual-vehicle aggregation rule Asuka framework already applies analytically is now formally codified into law.** Several activists rushed pre-reform filings late April 2026 (Elliott NXHD Apr 28). Net effect: **cleaner signal**. Aggregate stake disclosure will more accurately reflect economic interest.
**§2 Current TSE governance pressure stack [QUARTERLY] — six reinforcing layers (mid-2026):**
1. Public listing of PBR<1 non-compliants (TSE monthly compliance list)
2. Capital cost disclosure mandate (every Prime CG report includes self-reported CoC and ROE-to-CoC gap)
3. Cross-shareholding (政策保有) disclosure with rationale (each policy holding named, valued, justified annually; most rationales "long-term business relationship")
4. Independent director ≥1/3 minimum on Prime
5. TSE 2026 cost-of-capital follow-up review (preparing follow-up of how companies have implemented Mar 2023 directive — expected to differentiate concrete plans vs platitudes)
6. **Bunka Shutter / Dalton institutional escalation precedent (Jan 2026)** — Dalton sent formal letter to METI, FSA, JPX about structural AGM and disclosure reforms (specifically targeting QUO-card retail-shareholder benefit defensive tactic). First documented case of foreign activist appealing directly to all three regulators on structural reform. Created precedent regulators have not yet rejected.
**§3 Cross-shareholding reduction trajectory:** [ANNUAL] Cross-shareholdings as % of TSE market cap declined ~50% early 1990s → ~10-13% mid-2020s and trending downward. NLI Research estimates ¥10-15T unwound post-Stewardship-Code. **Mechanism Asuka exploits:** when corporate cross-holder sells, three things happen sequentially — (1) selling company books large investment securities gain often material vs OP, (2) proceeds typically deployed into buybacks (pure cash deployment fails TSE capital efficiency test), (3) target company sees float expansion freeing activist accumulation runway. Sony → Tamron 12% is prototype Asuka case. DaikyoNishikawa ¥9.6B secondary share offering Jan 2026 (Nishikawa Rubber cross-holding unwind) is recent canonical — directly enabling Takateru Murakami accumulation runway.
Bank cross-holdings = residual problem [QUARTERLY] — megabanks (MUFG, SMBC, Mizuho), regional banks, life insurers slower to unwind because regulatory capital treatment makes timing optimisation different. **Ariake Capital's regional bank thesis (Hyakugo, Ogaki Kyoritsu, Aichi Financial Group, Shiga, Suruga) is direct play on next wave of bank-side unwinding.**
**§4 Macro overlay [QUARTERLY] — BOJ posture, JGB curve, yen, stagflation:**
- **BOJ posture:** Exited NIRP March 2024; cautiously raising. May 2026 policy rate at highest since 2008. Tapering JGB purchases gradually; curve steepens. Ueda's preferred phrasing "watching wage and inflation dynamics."
- **JGB curve:** 10y yield well above post-2016 range; steepening at long end. Long-duration "hold cross-shareholdings instead of bonds" trade no longer economic — JGBs offer real reinvestment yield first time in 15 years. Accelerates cross-shareholding unwind.
- **Yen:** [QUARTERLY] **May 1 2026 JPY broke 155 vs USD prompting ¥5T BOJ intervention — largest intervention day on record. Nikkei broke ¥60,000 on April 27.** Yen weakness driven by rate-differential gap, US fiscal trajectory, Japan persistent goods-trade-deficit shift. For Asuka: weak yen helps export-heavy industrials (Optex, Musashi, Tamron, Ricoh); hurts domestic consumption (Kokuyo, Kakaku, Kobayashi). **Yen reversal = critical regime risk** to which book is asymmetrically exposed in export-heavy cluster.
- **Stagflation framework — Japan's resilience:** Three structural reasons Japan exposure differs from US/EU — (i) net foreign creditor position (¥460T+ NIIP; yen weakness → foreign-asset revaluation gains flow back via dividend repatriation), (ii) domestic JGB ownership ~86-88% (BOJ + financials + retail/pensions; sovereign debt sustainability does not depend on cross-border capital — insulates from gilt-style funding stress), (iii) wage-price loop (wage growth moderate; labour market tightness produced single-digit base-pay increases that haven't generated wage-price spirals; inflation Japan has imported is largely supply-side/commodity-driven). Implication: Japan macro more resilient to global stagflation regime than export-heavy beta to global growth would suggest. **Asuka bottom-up activist alpha mechanically extractable across regimes that matter — strategy survives in three of four regime classifications (risk-on, risk-off/slowdown, crisis/deflation), with stagflation as specific vulnerability** (strong yen + global IA stall + cross-share unwind delays compound).
- **Iran / Hormuz dynamic:** [QUARTERLY] Oil $111+ as of Apr 2026 with Iran/Hormuz tensions elevated. Tanker rates spiked benefiting Japanese shipping (NS United, Meiji, MOL) but raising input costs for industrials.
**§5 Domestic flow dynamics — NISA, retail, insurance shifts:**
- **NISA-driven retail flow** [ANNUAL]: Sustained net retail inflows into Japan equity post Jan 2024 redesign. Concentrated in domestic equity index ETFs and selective high-dividend large-cap. For Asuka: index inclusion / high-dividend basket inclusion = meaningful re-rating mechanism (Be Brave Nishikawa Rubber DOE 8% template captures mechanical retail flow); retail floor on quality compounders (Takumi sleeve — Syuppin, Beauty Garage, I'LL) has firmed up; retail does NOT directly fund activist plays (no "activist ETF" Japan retail); NISA re-rates targets only after activist resolution makes them dividend-yielding compounders.
- **Insurance allocation shift:** Life insurers + trust banks rebalancing into JGBs as duration yields normalised, away from cross-shareholdings (and recently away from foreign-currency hedged USD bond strategies). Exit from cross-shareholdings directly funds Asuka thesis. Domestic insurers now vote much more frequently *with* governance proposals than against, particularly post-2021 Code revision.
- **Trust bank passive voting:** Master Trust and JTSB now vote algorithmically against management slate at PBR<1 + governance code threshold companies. Turns ISS recommendations into actual vote outcomes. Activist proposals at code-non-compliant companies now have reliable 8-12% institutional vote bloc before activist's own campaign mobilises single retail or active institutional vote — threshold for 33% block materially lower than pre-2021.
- **Foreign ownership:** Foreign holdings TSE total ~30%; activist-targeted names cluster at lower end (10-20%) — exactly the structural feature that makes them activist-vulnerable (domestic institutions now vote governance not incumbency).
**§6 How regime conditions interact with Asuka edge (five specific amplifications):**
1. **TSE PBR<1 listing is a co-campaigner** — when activist files on PBR<1 name, demand no longer adversarial in isolation; aligns with TSE's published expectation. Management defensive coalition shrinks. Post-2023 campaign success rates run materially above pre-2023 base.
2. **Cross-shareholding unwind is mechanical funding source** — activist demands for buybacks no longer require company to find new cash; cash sitting on balance sheet in cross-held investment securities awaiting unwind. Activist's role is to force timeline, not find funding. Collapses typical "we need to invest in growth" management defence.
3. **EDINET reform clarifies signal quality** — Post-May 2026 dual-vehicle structures and CFD wrappers fold into mandatory aggregate disclosure. Asuka's analytical aggregation rule now legal default. Removes class of false-negative signals where activist approaching 5% but visible filing reads 4.x%.
4. **BOJ rate normalisation kills policy-holding alibi** — when 10y JGB yielded zero, corporates could weakly argue cross-held equities were duration substitute. With curve normalised, no defensible economic rationale remains for non-strategic cross-holdings.
5. **Domestic flow dynamics provide post-resolution exit** — NISA-driven retail + trust bank passive flow are natural buyers when Asuka L1 resolves into dividend-paying compounder. Shortens harvest window and improves exit liquidity — both directly accretive to annualised PWER.
Combined effect: same activist + same target + same demand has materially higher probability of resolution today than pre-2023, with faster mean campaign-to-resolution and deeper post-resolution buyer base.
**§7 Triggers that would invalidate regime assumptions (in priority order):**
1. **TSE rolls back PBR<1 listing mechanism** — single load-bearing element. Any TSE softening of cost-of-capital review framework, suspending public listing, or extending compliance deadlines would compress all activist PWER scenarios. [QUARTERLY watch.] Monitor TSE statements ahead of 2026 follow-up review.
2. METI/FSA reverses on cross-shareholding pressure — Daiwa Institute / NLI quarterly tracker + annual METI Corporate Value Study Group reports.
3. BOJ reverses rate normalisation — would resurrect cross-shareholding-as-duration-substitute alibi. Probability low (Ueda anchored regime) but observable via forward guidance.
4. Government intervention against activist proposals — Bunka Shutter / Dalton METI+FSA+JPX letter precedent points other direction (regulators helping activists), but converse risk real. Any government framing activists as "destabilising" / "extracting" / "undermining" would shift backdrop. Foreign Exchange and Foreign Trade Act amendments already constrained — broader expansion of restricted sectors = trigger.
5. ISS/Glass Lewis voting policy shift [ANNUAL] — annual policy revisions (Nov-Dec) observable. Any softening on independent director thresholds, governance code compliance, or cross-shareholding disclosure quality compresses activist proposal win rates.
6. Yen reversal — JPY <130 would partially reverse export-heavy cluster earnings tailwind. 2026-vintage positions (Optex, Musashi, Tamron, Ricoh) carry asymmetric yen exposure. Strong yen + IA segment weakness = explicit stagflation vulnerability.
7. Domestic flow regime reversal — NISA retraction, reduced trust bank engagement voting, insurer cross-share buying (rather than selling). Probability low (politically committed flows) but observable via monthly NISA inflow data + trust bank stewardship reports.
**Base-case assessment:** regime durable through at least 2027-2028, with May 2026 EDINET reform actually strengthening rather than softening activist edge. Principal near-term watch items: TSE 2026 cost-of-capital follow-up review and JPY trajectory post May 1 ¥5T intervention.
---
### 3.10 `tse-backtest-v6.md` — TSE Activist Backtest Methodology
**What it is:** V6 backtest specification and results, with explicit provenance flags [CHAT-EMP] / [V6-SPEC] / [INFER]. Honest about gaps between V5 audit-era numbers and V6 not-yet-rerun targets.
**Why it matters:** Provides the empirical anchor table backing the framework's scenario probability defaults, return-target percentiles, and base-rate calibration. Also the honest record of what is and isn't quantitatively validated.
**Exhaustive summary:**
**§1 Universe:** 262 campaigns consolidated across 9 Tier 1/Tier 2 filers from (a) Activist Insight Bloomberg exports, (b) EDINET 大量保有/変更報告書 history per filer, (c) Murakami manual aggregation.
Decomposition [CHAT-EMP]: Dalton (incl NAVF) 68, Oasis 42, Strategic Capital 39-40, LIM 28, Effissimo+SMT 20-21, 3D 13, MIRI ~15, Silchester ~12, Ariake ~8, GMO-Usonian ~10 EDINET reverse-lookup, Murakami network ~25 manual.
Earlier "211 campaigns" master database is pre-Feb-2026 cut. 262 adds new EDINET filings since plus manual Murakami aggregation not in original Activist Insight scope. Time period 2010-01-01 to 2026-04-30; walk-forward expanding-window starting 2013-2019 train / 2020-2021 validate, then expanding annually.
**Screening criteria:**
- Filer eligibility: tracked roster (Tier 1 + Tier 2), "filer" defined at aggregated economic-interest level (Effissimo+SMT=1; Dalton+NAVF=1; full Murakami tree=1)
- Target eligibility: TSE-listed at time of first 5%+ filing (Prime/Standard/Growth); mcap ≥¥10B at first filing; at least one 大量保有 with stake ≥5%
- Exclusions: 誤記訂正 (correction-only); sub-5% voluntary disclosures
**Sample size for prediction modelling:** 5 cleanest filers (Dalton 68, Strategic 39, LIM 28, Effissimo 20, 3D 13) → ~250-300 activist events across 15 years. **Materially below what required to train stable XGBoost without severe overfitting** — structural reason V6 abandons "single-classifier-on-all-activists" in favour of activist-mode stratification.
**§2 Signal definitions:**
- **Anchor event:** first EDINET 大量保有報告書 by tracked filer (docType 350 initial, or 360 initial via tender). `submitDateTime` is anchor, never `periodEnd`. Filer name matched via EDINET-entity substring across standardised list.
- **Threshold rules:** 5% initial 100% by definition; 10% confirmation of accumulation intent ~52% of campaigns reach [CHAT-EMP]; 15% Effissimo Mode 1→2 ~28%; 20% forced strategic review territory ~14%; 33.4% special resolution blocking minority ~5%; 50% de facto control <2%.
- **Holding-purpose language tier mapping:** four-tier ordinal Tier 0/1/2/3 (matches CRMC §3 Tier P/R/E/C). Purpose-tier upgrade between filings is itself signal event in backtest.
- **Composite signal score:** v5 was 70% XGBoost / 30% Cox; **V6 abandons in favour of three specialist classifiers** (capital-return / governance-board / strategic-transaction) with weights determined by `activist_escalation_mode` feature. Cox weight reduced to 0% pending real campaign-duration data; audit found synthetic-data Cox C-index **0.47 — below random**.
**§3 Return computation:**

```
hp_return       = (exit_price − entry_price) / entry_price × 100
duration_months = (exit_date − entry_date) / 30.44
annualised_ret  = ((1 + hp_return/100) ^ (12 / max(duration_months, 1)) − 1) × 100
```


Prices via Bloomberg `HistoricalDataRequest` `PX_LAST` with `DPDF_ADJ_FACTOR`. Entry = first filing date; exit = last filing showing reduction or today for active. Corporate actions via `DVD_HIST_ALL`, `SHARE_REPURCHASE_SUMMARY`, `STOCK_SPLIT_HIST`. M&A via `MERGERS_AND_ACQUISITIONS`; tender-exit takes tender price as exit. Survivorship-bias free — campaigns ending in delisting/bankruptcy retain final traded price (40% of Effissimo's 10 closed exits in Zang sample were TOB/MBO acceptance — ignoring delisting introduces positive bias).
**§4 Backtest headline metrics:**
**V5 audit-era results (pre-rebuild):**
| Metric | v5 value | Audit verdict |
|---|---|---|
| Validation AUC | **0.9863** | **Implausibly high** — flagged critical. Realistic Japan activist prediction AUC 0.65-0.78. Indicates target leakage, insufficient purge gap, or universe memorisation |
| Cox C-index | **0.47** | **Below random** (0.50). Synthetic duration data. Zero out Cox weight |
| Reported Sharpe | **1.34** | **Pre-cost**. Tiered TC compression 0.15-0.25 → post-cost 1.09-1.19 |
| Purge gap | 63 days | **Insufficient**. Activist campaign info persists 12-18 months; effective purge ≈ zero |
**V6 specification (expected ranges — NOT YET PRODUCED):**
- Validation AUC: targeted to fall to 0.65-0.72 under proper walk-forward with 12-month minimum purge gap
- Sharpe (post-cost): 0.9-1.2 under tiered TC model
- IR vs TOPIX: not formally specified
**This is a real gap. Clean V6 IR/Sharpe/Max-DD table requires post-rebuild rerun and has not been produced.**
**Hit rate & realised return distribution [CHAT-EMP]:**
- % of campaigns positive Hp_Return: ~60-65% cross-activist average
- Effissimo win rate ~100% (small sample ~20)
- Dalton win rate ~65% (n=68)
- Oasis win rate ~73% (n=42)
- Strategic Capital varies by mode (capital-return ~70%; break-up ~40%)
- Top-decile MOIC (>15% stakes) 4-8x — top 5 campaigns = 80% of excess profit
- Middle 60% MOIC (>15%) 1.5-2.5x
- Bottom 30% MOIC (>15%) 0.7-1.2x
**Notable individual campaign returns:**
- Japan System Tech / MIRI: **+292%**
- Daidoh / Strategic Capital: **+279%**
- Kawasaki Kisen / Effissimo: +247-248%
- Sapporo Holdings / 3D: +162%
- Aizawa Securities / Dalton+NAVF: +124%
- Yodogawa Steel / Strategic: +112%
- Bunka Shutter / Strategic: +91%
- NHK Spring / Dalton: +78.9%
- Anicom Holdings / Dalton: +73.7%
- Impress Holdings / MIRI: -57%
- Rohm / Dalton: -31.2%
- Seven & i / Dalton: -13%
**Max drawdown:** audit explicitly flagged no formal max-DD by archetype produced in v5. V6 spec calls for max-DD decomposition by (a) activist filer, (b) escalation mode, (c) mcap tier, (d) pre/post-2022 TSE-reform regime — not produced. Single most strategically damaging finding: v5 engine missed **Kanto Denka Kogyo (4047, Effissimo 19.83%, +104%) and Fudo Tetra (1813, 27.28%, +80%)**.
**§5 Factor decomposition:**
- Market beta: long-only Japan equity book, beta to TOPIX ~1.0 with modest small/mid-cap tilt. Baseline beta = strategy's largest single factor exposure. Strong-beta rallies (Nikkei 2013 +56.7%) → single-name underperformer like Strategic Capital that year (-0.69%) produced **massive negative IR contribution** (Zang flagged). Framework's "avoid post-rally entry" discipline (KH Neochem, Enplas rejections) is direct response.
- Size: Negative — strategy's highest realised alpha in SME/mid-cap. 14-18 position cap may be artificially capping exposure to highest-Sharpe sub-strategy.
- Value: Positive — PBR<1.0x and net-cash/MC>20% screens are entry gates.
- Quality: Mixed — Tier 2 long-only quality-tilted; Tier 1 hard-activist anti-quality (low ROE, governance dysfunction IS alpha source).
- Momentum: Slightly negative — best entries at multi-year lows / forgotten names; weakest are post-rally chases.
**§6 Decay curves:**
V6 spec includes IC decay analysis. Forward-return profile by horizon [INFER, not rigorously backtested]:
| Forward window | Effissimo | Dalton | Oasis | Strategic Capital |
|---|---|---|---|---|
| 12mo | ~+15-25% (mid-stage compounding) | ~+10-15% | ~+18-22% | ~+8-12% |
| 24mo | ~+35-50% (Mode 2 forcing function) | ~+18-25% (capital return resolved) | ~+25-35% (board contest resolved) | ~+15-25% |
| 36mo | ~+60-90% (Mode 3 / strategic transaction) | ~+25-35% (mature campaigns) | ~+30-45% | ~+30-60% (slow grinder wins) |
**Effissimo closed-case mean 805 days (~2.2 years)** — Zang 2019 documents, vs US comparable 562 days. Japan activism harvests more slowly than US. Framework's 12-24 month L1/L2 harvest horizon is calibrated against this. Alpha realisation peaks around month 24, not month 12 as in US.
**Post-AGM reversal risk:** Zang explicitly flagged "any increase in stock price caused by activist proposals usually is not sustainable, and in some cases, the prices fall after the campaigns." Forward-return curve NOT monotonic — can reverse sharply after AGM dates. V6 must model post-AGM reversal as Bear-case scenario component.
**§7 V6 specific upgrades vs prior versions (eight implementation blocks):**
- **Block 0** — Day-one fixes: set Cox weight to 0; pre-mortem reconciliation against missed signals (Kanto Denka, Fudo Tetra).
- **Block 1** — Universe expansion: add MIRI / micro-cap activist filers (~¥20-50M ADV) with liquidity caps (3-4% NAV at ¥500M AUM); aggregate dual-vehicle filers at economic-interest level.
- **Block 2** — Dual-vehicle aggregation fix (single most urgent per audit; live-data corruption stems from un-aggregated entity views).
- **Block 3** — Eight new Japan-specific features:
  1. AGM proximity (days to next AGM, weighted by record-date logic)
  2. Cross-shareholder reduction velocity
  3. TSE Prime vs Standard listing flag
  4. Net-cash / market-cap ratio (single screening variable that empirically profiles 80% of targets per 211-campaign analysis)
  5. Founder-family-bloc percentage (MBO optionality vs blocking risk)
  6. Consecutive months below 1.0x PBR
  7. Independent director percentage gap to TSE recommendation
  8. Most recent EDINET filing language tier (0/1/2/3 ordinal)
- **Block 4** — Multi-class label redesign: replaces v5 single binary 6-month / 10% threshold with four-class ordinal — Class 0 underperform (<0% vs sector 12m), Class 1 base (0-20% 12m), Class 2 partial activist win (20-50% 12m), Class 3 strategic event / MBO / full restructuring (50%+ **24m** longer window for tail outcomes).
- **Block 5** — Walk-forward validation: 18-month purge gap (audit's recommended floor; v5 had 63d); expanding window from 2013-2019 train; time-decayed sample weighting with `weight(t) = exp(-λ × (T_current − t))` calibrated so 2015 obs ≈ 30% weight of 2024 obs; post-2022 multiplier of 1.5 to over-represent new regime; XGBoost hyperparameters tightened (max_depth 3-4, subsample 0.7, colsample_bytree 0.6, min_child_weight 5, alpha 0.1, lambda 1.0); isotonic regression calibration replacing Platt scaling.
- **Block 6** — AGM calendar integration: April record-date logic explicit; Feb-Apr "highest-signal window" coded as model feature.
- **Block 7** — Layer-aware portfolio constraints: L1 max 12%, L2 max 5%, L3 max 8% — replaces flat 5% cap which destroys fund's core sizing logic.
- **Block 8** — Tiered transaction cost model: TSE Prime large-cap 60bp round-trip; mid-cap (¥50-500B) 120bp; small-cap (<¥50B) 200-250bp. Expected to compress reported v5 Sharpe 1.34 by 0.15-0.25.
- **Block 9** — Operational architecture: sequence AGM calendar → universe builder → EDINET fetcher → dual-vehicle aggregation → Bloomberg data → 28-feature matrix → three specialist XGBoost + Cox → ensemble → layer-aware Kelly → PWER constructor → memo gen → SQLite write. Weekly model-health monitor reporting rolling 90-day OOS AUC, Brier score, calibration ECE, IC decay curve.
**§8 Known limitations and outstanding research questions (the honest list):**
- Sample size: 262 campaigns aggregated **structurally insufficient for stable XGBoost training**. V6 model best understood as scoring overlay rather than primary signal — helps rank candidates human-discretionary process already filtered, not replace that process.
- Regime non-stationarity: 2023 TSE PBR<1 reform is **structural break, not continuation**. Pre-reform Japan activism behaved differently (target selection, management response patterns, exit pathways). Time-decayed sample weighting partially addresses but does not fully resolve. Pre-2022 observations should be treated as calibration data, NOT ground truth for current regime.
- Survivorship in Activist Insight exports: export is point-in-time snapshot; campaigns closed and removed before export date may be missing; biases realised-return toward in-progress campaigns.
- Murakami aggregation incompleteness: family-tree aggregation partially manual; new vehicle entities (recent MI2, MI5; Aya Nomura's Minami Aoyama RE) detected reactively from EDINET rather than proactively. Internal-redistribution filings can read as fresh accumulation if joint-holder section not parsed correctly.
- **No clean V6 rerun has been produced** — V6 specification comprehensively scoped, but eight implementation blocks have not been run end-to-end on rebuilt infrastructure to produce headline IR/Sharpe/Max-DD/decay-curve outputs.
- Outstanding research questions: capacity analysis by AUM band; activist-specific calibration with <8 closed campaigns (Ariake, MIRI, GMO-Usonian); pre-disclosure detection (211-campaign factor scorecard found **volume spikes without news** are most actionable real-time pre-5% signal, **prior activist history** strongest single predictor (5× weight)); post-AGM reversal modelling; non-Tier-1 / non-Tier-2 cross-references.
---
### 3.11 `asuka_v3_state.md` — Generated Active Book Snapshot
**What it is:** Compact snapshot of active book derived from `dashboard_data.json`, generated 2026-05-03 JST. Version 3.1, 31 positions.
**Why it matters:** Shows the canonical output format for the live position state — total weight deployed, avg PWER, signal counts, positions by layer with WAC and px and PWER columns, activist concentration, recent changes.
**Full content** (reproduced verbatim in Section 6 of this handoff as a representative input format).
---
### 3.12 Framework Extensions v9 / v9.1 / v10 / v10.1 / v10.2 / v10.3
**Summarised together** as they form a coherent evolution chain. Each extension is additive unless explicitly noted as superseding a prior section. Most recent version is **v10.3 (May 12 2026)**; together they form the operating framework on top of the base v8 documented in `asuka-fund-framework.md`.
**v9 (May 3 2026) — "Activist-Target Value · Annualized PWER · Wired Tripwires"**
Closed three v8 gaps: no principal-activist hurdle-rate input; absolute PWER without annualization; falsification triggers as prose not first-class objects. Adds to position YAML:
- `activist_target.central` (single-point estimate where principal activist needs price to clear hurdle); `range`, `horizon_years`, `hurdle_basis`, `evidence_tier` ∈ {confirmed, inferred, speculative}, `data_source`.
- `annualized_pwer` — three numbers: absolute PWER (12m forward), activist-horizon PWER (campaign clock), annualized return on activist horizon. Both must pass gate.
- `tripwires` — minimum 3 per L1, 2 per L2, 1 per L3. Each must be observable event with defined evidence source and programmatic action.
**Activist hurdle-rate library** (calibrated from 9 Activist Insight holdings files), each row median + top-quartile HPR by stake band:
| Activist | Stake band | n | Median | Mean | TopQ | Base mult of WAC |
|---|---|---|---|---|---|---|
| **Effissimo** 5-15% (Mode 1) | 10 | +77% | +93% | top-25% | **1.77×** |
| Effissimo 15-25% (Mode 2) | 7 | **+46%** | **+63%** | top-25 ~110% | **1.46×** |
| Effissimo 25%+ (Mode 3) | 2 | +164% | +164% | n too small | 2.64× |
| **3D** 5-15% | 10 | +26% | +57% | +143% | 1.26× |
| 3D all | 13 | +18% | — | +143% | 1.18× |
| **Dalton** 5-15% | 49 | **+15%** | +30% | +38% | 1.15× |
| Dalton all | 66 | +14% | — | +38% | 1.14× |
| **Strategic Capital** 5-15% | 29 | +56% | +65% | +91% | 1.56× |
| SC 15-25% | 1 | +162% | +162% | n=1 | 2.62× |
| **Silchester** 5-15% | 4 | +11% | +16% | +42% | 1.11× |
| **GMO-Usonian** 5-15% | 16 | **+23%** | +22% | +37% | 1.23× |
| **Ariake** 5-15% | 10 | +49% | +66% | +70% | 1.49× |
| **LIM** all | 27 | +28% | — | +51% | 1.28× |
| **MIRI** 5-15% | 13 | +22% | +42% | +55% | 1.22× |
Key calibration insights: Effissimo's 5-15% band has higher returns than 15-25% (survival bias — small starter positions ratcheted into wins TOC +157%, MESCO +240%, Naigai +168%; at higher stakes returns compress because campaigns longer and entry timing already incorporates more of win). Dalton has lowest hurdle of any tracked activist (median +15%) — reinforces standing rule that Dalton positions need fundamental support beyond activist signal alone. Strategic Capital's 15-25% band has only n=1 (Sanyo Denki). Silchester at +11% median is barely above gate — L3 ballast role only. GMO-Usonian +23% consistent with quality-compounder mandate.
How to use library: for any new position, **Base scenario target = WAC × (1 + median_HPR_for_stake_band)**. PM can override but must document reason in `activist_target.hurdle_basis`.
**Annualized PWER gate logic** — position passes if either:
- Absolute PWER ≥20% over ≤18-month horizon, OR
- Annualized PWER ≥15% over activist's campaign horizon
If passes only on absolute: time-decay risk; max 70% of layer cap until catalyst window narrows. If passes only on annualized: sizing fine but conviction depends on patience tolerance.
**v9 amendments to standing rules:**
- WAC cross-check: +15% default; for dual-vehicle structures (Effissimo+SMT, Dalton+NAVF, Murakami family aggregate) ceiling **tightens to +10%** above blended WAC because exit liquidity constrained.
- Profit-taking rule: PWER compression computed against both absolute and annualized gates. Trim only when annualized falls below 15%.
**v9.1 (May 3 2026, same day) — "Target/EV Distinction · Filed Book Value · Liquidity-Adjusted Realized · Empirical State Distribution"**
Four corrections from ChatGPT critique on Ricoh activist-target memo:
1. **Target ≠ EV.** v9's `activist_target.central` conflated price activist needs at successful exit with probability-weighted expected value across ALL states. Different numbers; only EV feeds shadow-buyer PWER.
2. **Book value per share was inferred, not pulled.** Ricoh FY2025 BVPS is ¥1,809.90 (filed).
3. **Buyback accretion was mechanical.** Not enterprise-value-preserving share-count compression; cash leaves balance sheet. Accretion = (intrinsic − buyback price) × retired / remaining.
4. **Probability distributions were PM judgment.** v9.1 uses *empirical state-frequency* from principal activist's holdings file as prior, with PM judgment overlay only when documented.
5. **Exit liquidity discount** — neither flagged but emerged from math. Activist's target not cleanly realizable for concentrated stakes.
v9.1 schema additions:
- `activist_target_value` (success-conditional price)
- `activist_expected_value` (unconditional prob-weighted EV)
- `state_distribution` (the empirical prior, explicit)
- `exit_liquidity_discount` with `shares_held_m`, `adv_m`, `days_to_exit_at_25pct_adv`, `discount_pct`, `activist_realized_value`
- `annualized_pwer` with composite gate logic
- `company_filed_anchors` — BVPS, cost_of_equity, ROE/ROIC targets, all pulled from filings not inferred
**Liquidity discount methodology:**

```
days_to_exit = shares_held / (ADV × 0.25)
discount_pct = min(15, days_to_exit / 30)
realized_value = expected_value × (1 − discount_pct/100)
```


25% of ADV = realistic absorption rate; 1pp discount per 30 days reflects observed Toshiba/UACJ/Kawasaki Kisen exit patterns; 15% cap reflects strategic exit path (TOB, secondary, block sale).
**Composite gate matrix:**
| Absolute (EV ≥+20%) | Annualized (realized ≥+15%) | Composite | Sizing rule |
|---|---|---|---|
| PASS | PASS | PASS | Full layer cap available |
| PASS | FAIL | ABSOLUTE_ONLY | Cap at 70% of layer max; harvest aggressively |
| FAIL | PASS | ANNUALIZED_ONLY | Cap at 70% of layer max; longer carry tolerance |
| FAIL | FAIL | FAIL | No fresh capital; existing exits at first tripwire |
**Empirical state distributions (from holdings files):**
Effissimo 15-25% band n=7 (for Ricoh, Teijin, Tamron): fail (<+10%) 0.00; modest (+10-40%) 0.43; solid (+40-80%) 0.29; strong (+80-150%) 0.14; home_run (>+150%) 0.14. Mode 2 has zero observed failures at 15-25% — entry discipline at this size is selective.
3D 5-25% band n=10 (for Square Enix): fail 0.30; modest 0.40; solid 0.00; strong 0.10; home_run 0.20. **Distribution bimodal — 70% in fail/modest cluster vs 30% in strong/home_run, no middle. Sizing must reflect binary character.**
Strategic Capital 5-25% n=30 (for Sanyo Denki): fail 0.17; modest 0.17; solid 0.30; strong 0.27; home_run 0.10. Cleanest distribution; well-spread, no bimodality, supports systematic sizing.
**Tier 1 reruns — net portfolio takeaways:**
- Three of four Tier 1 positions ABSOLUTE_ONLY (pass on EV, fail on liquidity-adjusted annualized). **Structural feature of mid-cap Japan activism v8 did not surface.**
- Sanyo Denki clearest action change — both gates fail. Downgrade L1→L2 (later confirmed by v10.2 DPS modifier 7%→6% trim).
- Teijin largest discoverable upgrade pending verification of inferred anchors.
- Square Enix sits exactly on gate — June 2026 AGM is binary that resolves.
- Ricoh tighter add ceiling ¥1,400 vs v9's ¥1,435.
Wtd avg PWER from v9.1 lowers from ~25.5% to roughly ~22-23%. **Book still above 20% portfolio gate, but margin of safety compressed. Framework working as designed — v9.1 more honest about expected outcomes.**
**v10 (May 9 2026) — "Shadow-Follow Setup Screening · Universal Activist & Transaction Application"**
**The Piolax lesson, generalized.** Piolax (5988) Murakami campaign Aug 2024 – Mar 2025: principal +5.8% on tendered slug (¥2,359 WAC → ¥2,497 TOB price March 2025) while follower mirror-buy at Aug 2024 5%+ filing realized **−28% to today's ¥1,648**. Base rate hides divergence because tender-exited principals print positive even when residual that follower can't tender collapses post-extraction.
v10 deploys **five gates + one calibration rule** that screen for asymmetry before initiation, applicable to every filer archetype.
**Universal archetype taxonomy** (every Asuka-tracked filer maps to one of four exit-mechanic archetypes):
| Archetype | Exit mechanic | Principal-follower divergence | Filers |
|---|---|---|---|
| **Tier R — Capital-return extractors** | TOB / self-tender / large buyback; principal often has off-market block or coordinated tender | **HIGH** (Piolax-pattern risk) | Murakami, Be Brave, Ueshima/DOE5%, CIE, UGS |
| **Tier P — Patient blockers** | Multi-year re-rating; exit via market over years; no privileged exit path | **LOW** | Effissimo+SMT, Silchester, Ariake, MIRI, Kaname, Zennor |
| **Tier E — Engagement campaigners** | Operational reform, board contest, AGM proposals; exit on win or stalemate | **MEDIUM** | 3D, Oasis, Strategic Capital, LIM, AVI Japan, Palliser, Dalton+NAVF |
| **Tier Q — Long-only quality** | No "exit event"; multi-year compounding with minor re-rating | **MINIMAL** | GMO-Usonian, Silchester quality sleeve, Arcus, Ariake quality sleeve |
**Rule:** archetype tagging is prerequisite; no setup runs through v10 gates without archetype assignment. If filer straddles archetypes (Effissimo Mode 1 vs Mode 3), tag specific campaign mode.
**The Five Gates:**
**Gate 1 — Pre-existing Concession Test.** At moment of principal's first 5%+ filing, had target already done meaningful pieces of activist's typical playbook?
- Tier R: (a) payout ratio ≥80% prior FY; (b) explicit DOE / dividend floor disclosed; (c) capital policy statement ≤24mo pre-filing; (d) buyback announced ≤6mo pre-filing
- Tier P: (a) public strategic review or restructuring ≤12mo pre-filing; (b) cross-shareholding reduction trajectory disclosed; (c) governance overhaul ≤24mo pre-filing
- Tier E: (a) cost-program / margin-recovery plan announced ≤12mo pre-filing; (b) divestiture trajectory publicly disclosed; (c) board structure already independent-majority
- Tier Q: gate does not apply (fundamentals-driven not catalyst-driven)
Action thresholds: 3+ points + no Gate 5 second leg → **REJECT**; 2 points → DOWNGRADE one tier (requires explicit second-leg justification); 0-1 → proceed to Gate 2.
**Gate 2 — Threshold Progress Test.** Is principal making credible progress toward archetype-specific credible-threat threshold, or stalling? Stall trigger: stake stalls below threshold for stall window AND target announces defensive action in same window (buyback, dividend hike, TOB, M&A counter-bid, white knight) AND no public letter or proposal from principal in window. All three conditions must fire. Stall trigger fires REJECT or DOWNGRADE.
**Gate 3 — Internal Rotation Penalty (with directionality test).** Filer-network internal redistribution flattering apparent stake momentum without fresh capital? Compute `delta_aggregate_stake`, `delta_from_reshuffle`, `delta_fresh_capital`. Action: `delta_fresh_capital < 0.5pp` AND reshuffle present → DOWNGRADE one tier (Piolax Oct 2024 fits: CIT→Reno full transfer 4.68pp + market adds ~0.3pp = 0.32pp fresh, sub-0.5). `≥0.5pp` AND reshuffle present → no penalty (Sankei REIT Apr 2026: aggregate +2.16pp with reshuffle <2pp = clear fresh deployment). High Change Report numbers (No.15+) with new individual vehicle 5%+ → fires regardless of directionality math.
**Gate 4 — Residual Liquidity Test (mandatory in PWER).** When Bull or X-Bull scenario terminates in liquidity event (TOB, self-tender, large buyback, third-party MBO, off-market block), what fraction of follower's position actually clears at headline event price?

```
acceptance_ratio = min(tender_size_shares / tender_supply, 1.0)
follower_tendered = follower_stake × acceptance_ratio
follower_residual = follower_stake × (1 - acceptance_ratio)
blended_return = (acceptance_ratio × return_tendered) + ((1-acceptance_ratio) × return_residual)
```


Acceptance ratio defaults: self-tender/TOB small-cap (<¥100B) known activist on register → assume **45-60%** (oversubscription typical); mid-cap (¥100-500B) → 60-75%; large-cap (>¥500B) → 75-90%; third-party MBO at premium → 100%; open-market buyback → 0% follower acceptance.
Post-event price defaults: self-tender funded buyback → −10 to −25% from tender price; third-party MBO succeeded → tender price (delisted); third-party MBO failed → −15 to −40% from pre-bid level; open-market buyback → +3 to +8% above pre-announcement.
**Trigger:** if `blended_return < (return_tendered × 0.6)`, flag setup as **TOB-pro-rata trapped**. Reject or downgrade two tiers.
**Gate 5 — Second-Leg Requirement.** After principal's first concession is captured by management, what does activist have left to demand? Universal taxonomy of second-leg candidates: SOTP/spin-off; Governance overhaul; Strategic transaction; Cross-shareholding unwind; Parent-subsidiary resolution; Operational reform; Regulatory / TSE governance. Zero candidates with required evidence → **REJECT**; one weak → L3 maximum with explicit upgrade tripwire; two+ → standard sizing per archetype.
**Principal-Follower Divergence Haircut (calibration rule):**
| Archetype | Mean haircut | Top-decile haircut |
|---|---|---|
| Tier R (capital-return extractors) | −5pp | −10pp |
| Tier P patient blockers | −2pp | −5pp |
| Tier E engagement campaigners | −3pp | −7pp |
| Tier Q long-only quality | 0pp | −2pp |
**v10.1 (May 9 2026, same day) — "Fast Defensive Response Sub-Rule · Aichi Steel Worked Example"**
Adds Fast Defensive Response sub-rule to Gate 2 as parallel trigger that fires regardless of stake position when target moves defensively within 30 days of any threshold crossing. Aichi Steel (5482) Murakami campaign retro-screen surfaced design gap: campaign played out as textbook Defensive Stage 5 — first 5%+ filing, target announces payout policy upgrade + ToSTNeT-3 buyback within 33 days, principal exits via ToSTNeT-3 block at 91 days — but v10.0 Gate 2 did NOT formally fire because network crossed 10% credible-threat threshold via Reno off-market block at ¥1,735 on Feb 14 2025 (~21 days post-T0).
**Fast Defensive Response Sub-Rule trigger:** target announces ANY within 30 calendar days of T0 OR within 30 cal days of any subsequent threshold crossing (5% → 10%, 10% → 15%, 15% → 20%):
- Capital policy upgrade (payout ratio, dividend floor, DOE target)
- ToSTNeT-3 / 立会外買付 bilateral block buyback
- Public TOB / self-tender
- Dividend acceleration or special dividend
- Buyback announcement (open-market or pre-announced)
- Strategic review / restructuring timed to activist filing
Status: fires as **Concession-Captured warning**, regardless of stake position. NOT outright reject — combines with Gate 5 score per matrix:
| Gate 2 fires | G5 second legs | Verdict |
|---|---|---|
| Stall fires | 0 legs | REJECT |
| Stall fires | 1 weak leg | DOWNGRADE two tiers |
| Stall fires | 2+ strong legs | DOWNGRADE one tier, L3 cap, monitor closely |
| FDR fires | 0 legs | REJECT |
| FDR fires | 1 weak leg | DOWNGRADE two tiers |
| FDR fires | 2+ strong legs | **L3 conditional cap with explicit tripwires (Aichi Steel template)** |
| Both fire | any | take more conservative |
**Aichi Steel realized outcome at L3 sizing (+364% on initial position = +10.9% NAV at L3 sizing):** Jan 24 2025 T0 entry ¥1,699 → Feb 27 2025 first buyback announced FDR fires retrospectively, ¥2,200 → May 16 2025 Murakami exits via ToSTNeT-3 trim trigger ¥2,118 → Jun 3 2025 Toyota Industries privatization announced ¥2,500 → Aug 25 2025 Nikkei "Second Toyota Industries" PBR1× thesis ~¥4,500 → today May 9 2026 spot **¥7,880**.
**The L3 conditional sizing exactly captured the asymmetry**: protected against realized scenario where Murakami exited early via ToSTNeT-3 (zero pro-rata access), while preserving exposure to second-leg thesis that drove +364% rally. Framework working as designed.
**v10.2 (May 11 2026) — "Realized Mode 1 · Float Retirement Multiplier · Distribution-Position Sizing · Internal-vs-External Carry Tag · Yellow Hat Worked Example"**
Yellow Hat (9882) Strategic Capital campaign retro-screen surfaced four gaps not corner cases — they affect every Tier R and Tier E setup where principal activist's Mode 1 thesis has materially played out *without* requiring public escalation. SC filed initially Jul 26 2024 at 5.02%, accumulated to 13.83% by Dec 2024, then sat. In same window target institutionalized 45% payout ratio + 100% TPR MTP over FY26-28, retired 11.4% of float, refreshed board, confirmed two consecutive record-high earnings years. No campaign website. No shareholder proposal. No public letter. The thesis simply executed.
Four design gaps closed:
- **Gap A — Successful Quiet-Win status missing.** No node for "principal's Mode 1 demands met by target without escalation." Risk of mis-reading as "stalled" (REJECT) or "active accumulation" (full-edge BUY).
- **Gap B — Float retirement velocity unweighted in PWER.** Names with institutionalized cancellation programs deliver mechanical EPS uplift scenario table treats as binary.
- **Gap C — Bucket-position-aware sizing missing.** Filer-specific empirical HPR distributions (per v9.1) tell us where in distribution candidate sits — that input does not currently feed sizing.
- **Gap D — Mode 1 internal-vs-external conflation.** Lumps Sankei REIT-style external concession extracted from third party via stake leverage (binary, ARB-like) with Yellow Hat-style internal concession institutionalized by target willingly (structural, carry-like). Different risk profiles, different time horizons; L3-vs-L4 sleeve decision depends on distinction.
**Gate 1.5 — Realized Mode 1 Status Flag (NEW).** Inserts between Gate 1 and Gate 2. Where Gate 1 asks "did management pre-empt the activist?" — Gate 1.5 asks "did management deliver to activist after entry?" Trigger conditions:
| Indicator | Required threshold |
|---|---|
| **(a) Institutionalized capital return policy** | Multi-year MTP committing to payout ratio ≥40% OR total payout ratio ≥80% cumulative over ≥3 fiscal years |
| **(b) Float retirement** | ≥5% of pre-filing shares outstanding retired via treasury cancellation in trailing 12 months OR ≥10% cumulative since filing |
| **(c) Principal accumulation paused** | No new ≥1pt 変更報告書 from principal in trailing 6 months from most recent prior threshold crossing, AND no public letter/proposal/campaign-website launch in same window |
All three must fire concurrently. (c) is critical disambiguator. Accumulation pause must be observable post-target-action.
**Treatment when Gate 1.5 fires** — NOT a REJECT. Positive existence flag for L3 carry positioning with capped activist-co-investment ceiling:
- Layer assignment ceiling: L3 maximum (no L1 or L2 sizing regardless of other gates)
- PWER measurement basis: standalone fundamental + locked-in capital return program carry. **Activist co-investment edge = ZERO** added to PWER.
- WAC cross-check binding: YES — entry only 0% to +15% of activist WAC; above +15% = stand down
- DPS modifier mandatory application
- Strategic source: re-tag with CASH primary if not already; secondary captures durable second leg
- Mode 1 sub-tag: **M1-Internal-Carry**
- Time horizon: 12-24 months (multi-year MTP execution)
Upgrade L3→L2 tripwires: principal files 変更報告書 crossing next archetype threshold (SC 15%, Effissimo 20%, Murakami 33.4%); principal launches public campaign website OR files shareholder proposal; co-filer enters (Type A network or Type C independent).
Exit immediately on: principal files 変更報告書 reducing stake ≥2pt from peak (Stage 5 distribution); target announces unilateral capital allocation reversal (MTP credibility broken); target downward revises MTP payout commitments.
**Float-Retirement PWER Multiplier (NEW).** Triggers when ALL met: activist filer ≥5% currently standing; institutionalized MTP commitment total payout ratio ≥80% cumulative over ≥3 FY formally disclosed; track record ≥5% of float retired via treasury cancellation in trailing 12 months; time horizon Base-case 12-36 month hold.
Formula:

```
PWER_base_adjusted = Prob_base × Return_base × (1 + Proj_3yr_Float_Retirement_pct)
Proj_3yr_Float_Retirement = min(
  trailing_12m_retirement_pct × (remaining_MTP_years / 1),
  MTP_total_payout_ratio × net_income_3yr_projected / current_market_cap
)
```

Cap at 25%. Conservative — only Base, not Bull/X-Bull/Bear.
Yellow Hat: trailing 12m float retirement 11.4%; MTP 100% TPR FY26-28; remaining 2.83 yrs; projected 3yr min(11.4% × 2.83, 100% × ¥34B / ¥128B) = min(32%, 27%) → cap **25%**. Standard Base Prob 40% × +17% = +6.8% PWER contribution; adjusted Prob 40% × +17% × 1.25 = +8.5% = **+1.7pp lift**. Total PWER pre-multiplier +22.2% → post-multiplier **+23.9%**. Multiplier converts Yellow Hat from "marginal pass" to "clean L3."
**Distribution-Position Sizing (DPS) Modifier (NEW):**
| Principal current realized HPR | Bucket | Sizing modifier |
|---|---|---|
| Below bucket-1 boundary (<+10%) | fail / starter vintage | **1.5× standard layer sizing** (best vintage; full edge) |
| Within bucket-2 (+10% to +40%) | modest | **1.0× standard** (median expected) |
| Within bucket-3 (+40% to +80%) | solid | **0.5× standard, L3 max** (median outcome reached; residual edge only) |
| Within bucket-4 (+80% to +150%) | strong | **0.25× standard, L3 starter only, hard 1.5% NAV cap** |
| Bucket-5 (>+150%) | home-run | **Stand down or watch only** (mean-reversion risk dominates) |
Bucket boundaries filer-specific — pull from v9.1 §3 tables and refresh annually. **DPS modifier and Gate 1.5 layer ceiling stack but do not multiply.** Sequence: v10.0 Five Gates produce verdict → Gate 1.5 caps at L3 max if fired → DPS modifier scales within layer ceiling.
Yellow Hat: SC bucket-3 mid (+55.7% HPR vs +56.6% bucket mean) → 0.5× standard L3 → **3% NAV starter**. Sanyo Denki: SC HPR +57% to +66% → mid bucket-3 → 0.5× L1 standard = 6% NAV cap → marginal trim 7%→6%.
**M1-Internal-Carry vs M1-External-Binary Tag (NEW):**
| Sub-tag | Source of concession | Risk profile | Horizon | Sleeve |
|---|---|---|---|---|
| **M1-Internal-Carry** | Target firm itself, unilateral decision (MTP, DOE policy, buyback authorization) | Structural; low day-to-day vol; execution-on-cadence risk only | 12-24mo | **L3** |
| **M1-External-Binary** | Third party extracted via stake leverage (TOB price raise, merger consideration adjustment, hostile bidder withdrawal) | Binary, days-to-weeks; bear-floor explicit | Days-weeks | **L4 ARB** |
Diagnostic: who has to act for alpha to realize? Internal: target's board. External: bidder, partner, counterparty whose hand was forced by activist's stake.
Reference cases: Yellow Hat M1-Internal-Carry L3 (3%); Sankei REIT M1-External-Binary L4 ARB (1.5%); Aichi Steel M1-External-Binary; Sanyo Denki M1-Internal→External transition (campaign website + proposal); Pegasus M1-Internal-Carry tentative; Gun Ei/Tayca/Fujikura/Miyoshi M1-Internal-Carry basket.
**Yellow Hat (9882) — canonical Realized Mode 1 example.** Full Gate application produces L3 starter 3% NAV at ¥1,400-1,500 entry; PWER +23.9%; M1-Internal-Carry; CASH primary + GOV secondary strategic source. Funded by Alfresa 2% → 0 and Daito Trust 2% → 1%.
**v10.3 (May 12 2026) — "WAC Concealment Detection — Eleven Techniques, Forensic Protocol, True-WAC Math"**
Every WAC-based rule (v8 +15% co-investment ceiling, v9.1 +10% dual-vehicle tightening, v10.1 Gate 4 WAC-cross-check, inversion rule, Stage 5 buyback-then-exit check) assumes disclosed WAC = activist's true economic basis. **That premise false often enough to matter.** Three documented concealment cases:
1. Exedy 7278 CR No.24 — CIF "buying" 2.85pp at recent-market WAC was internal transfer from Reno (selling 3.65pp); aggregate fell 1.06pp. CIF WAC was transfer price, not market-purchase price.
2. Aichi Steel 5482 Feb 14 2025 — Reno absorbed 1.96M shares from Toyota Industries at ¥1,735, ¥442 below market. Bilateral block reflecting Toyota Industries' unwind, not Reno's marginal-buyer thinking.
3. Sankei REIT 2972 Apr 28 2026 — "共同保有者が増加したこと" cover-sheet. New vehicle joins active situation; aggregate stake rises through joint-holder addition, not fresh buying by lead filer.
**Eleven concealment techniques (C1-C11) in four families:**
**Family A — Vehicle-Level Masking (intra-network):**
- C1 — Cross-vehicle internal transfer at non-market price (Exedy No.24 canonical) — severity 3
- C2 — New family-member / affiliate vehicle 5%+ filing late in campaign (Murakami daughter Aya Nomura's Minami Aoyama RE; Takateru MI2/MI5 line) — severity 2
- C3 — Custodian / nominee-account beneficial-owner masking (Silchester via Northern Trust at Bank of Kyoto) — severity 1 if resolution pending, 0 if resolved
- C4 — Vehicle-level WAC stasis across multiple filings (vehicle isn't actually transacting; holding shell) — severity 2
**Family B — Execution-Channel Masking:**
- C5 — ToSTNeT / 立会外取引 off-market block at non-market price (Aichi Steel Feb 14 2025 canonical) — severity 1
- C6 — Cash-settled equity swap / derivative pre-position (GS/Nomura PB warehousing at Teijin, Sankei REIT, Casio) — severity 2
- C7 — Prime-broker block warehouse handoff (sister to C6) — severity 1
**Family C — Disclosure-Timing Masking:**
- C8 — Late-cadence consolidated filing (period-average WAC; up to 5 business days between threshold-crossing and filing) — severity 1
- C9 — Pre-5% silent accumulation embedded in first 5% disclosure (activist accumulates 4.99% silently over months, crosses 5% on single buying day, then discloses WAC as VWAP of entire silent-accumulation period) — severity 1
- C10 — Joint-holder addition masking lead-filer harvest ("共同保有者が増加したこと" Sankei REIT canonical) — severity 3
**Family D — Instrument-Level Masking:**
- C11 — Convertible / warrant / preferred-share blending (rare in mainstream JP activism; appears in post-MBO / post-restructuring; AVI Japan / Palliser structured stakes occasionally) — severity 2
**Ten-step forensic detection protocol** stamps each filing with `concealment_risk_score` (0+):
1. XBRL fetch and 取得対価 field inspection (non-cash → C11)
2. Transaction-date span check (>60 days first 大量保有 → C9; >30 days change report → C8)
3. Volume reconciliation
4. Per-filer joint-holder delta (C1, C10)
5. Nominee account scan (C3)
6. TDNet ToSTNeT print cross-reference (C5)
7. VWAP-vs-reported-WAC delta (Δ >5% → off-market component)
8. Vehicle incorporation date check (法人番号 registry; incorporation within 30 days of first filing → C2)
9. WAC stability stress test (3 consecutive CRs WAC stable ±¥10 / ±0.5% despite >15% intra-period range → C4)
10. Filing-cadence forensics (repeated late filings near 5-business-day limit → manual PM review)
**Severity weights and bands:**
| C-tag | Severity |
|---|---|
| C1 cross-vehicle internal transfer | 3 |
| C2 new family-member vehicle late campaign | 2 |
| C3 custodian veiling | 1 if pending, 0 if resolved |
| C4 vehicle WAC stasis | 2 |
| C5 ToSTNeT block | 1 |
| C6 swap pre-position | 2 |
| C7 PB warehouse | 1 |
| C8 late-cadence consolidation | 1 |
| C9 pre-5% silent accumulation | 1 |
| C10 joint-holder addition masking | 3 |
| C11 instrument blending | 2 |
Bands: 0 = no flag, use disclosed at face value; 1-2 = single low-medium severity, apply True-WAC adjustment with cheaper of (disclosed, VWAP-reconstructed); 3-4 = material, use most conservative WAC, tighten +15% ceiling to +10%; 5+ = severe, default REJECT new entries; existing positions require explicit PM re-underwrite memo

.

**Six True-WAC reference prices** (ranked by conservatism — rule is use price that produces highest "above WAC" reading):
1. Disclosed group WAC (naive default; use only when score = 0)
2. Disclosed lead-filer WAC (when C1 / C10 fire — reflects actual cheap-stock position not new-vehicle dilution)
3. VWAP-reconstructed open-market WAC (when C5 / C6 / C7 fire)
4. Cross-day price (when C9 fires — strip silent pre-5% accumulation)
5. Network earliest-vehicle entry price (when C4 fires)
6. Blended-instrument WAC (when C11 fires — manual)

**Decision matrix — concealment band × position state:**

| Band | New entry | Existing add | Existing hold | Existing trim |
|---|---|---|---|---|
| 0 clean | Per v10.1 5-gate | Per gates | Per gates | Per gates |
| 1-2 low-medium | Recompute PWER w/ True-WAC; gate at v9.1 +10% ceiling | Require PWER ≥25% (5pp above standard) at True-WAC | Hold; tag for refresh | Trim per existing |
| 3-4 material | Require Tier 1 second-leg G5 ≥2 AND True-WAC PWER ≥25% | DEFER add; require next change-report clarification | Hold capped — no upgrade tier | Accelerate trim toward L4 watch |
| 5+ severe | REJECT | REJECT | Mandatory PM re-underwrite | EXIT |

Override conditions: Override-up if score ≥3 BUT activist is Tier 1 PRIME (3D, Effissimo Mode 2/3, Murakami pre-Stage-5) AND masking pattern consistent with archetype (Murakami internal redistribution is *normal*, not signal of conviction loss when at Stages 2-3) — requires explicit memo. Override-down if score = 0 BUT activist has historical disclosure-engineering record (Strategic Capital's UGS Sunshine-LP co-filing pattern when SC isn't directly named) — apply band 1-2 regardless.

Eight standing rules added in v10.3:
1. Concealment-aware WAC rule — all WAC cross-checks apply against True-WAC, not disclosed
2. Mandatory concealment scan — every shadow-follow at T0 and every refresh triggers ten-step protocol; skipping = memo-validity failure
3. Conservative-reference rule — default to highest of candidate references when multiple flags fire
4. Override-down memory rule — SC filings on names with prior UGS Sunshine-LP joint history auto-tagged band 1-2
5. Pre-5% silent accumulation rule — first 大量保有 with transaction-date span >60 days → entry-price reference is cross-day price, not disclosed period-weighted WAC
6. Vehicle-stasis rule — three consecutive CRs WAC stable ±¥10 / ±0.5% despite >15% intra-period range = paper-only redistribution
7. Internal-transfer-doesn't-improve-edge rule — when C1 fires, group-blended WAC may move favorably (lower) but shadow follower's economics unchanged
8. PB-warehouse anchor rule — when C7 fires, activist's intent-formation price anchored to PB warehousing window's VWAP, not disclosed handoff WAC; *good for thesis durability, NOT a reason for follower to relax +15% cross-check*

---

### 3.13 xlsx / csv data exports (filer per-name HPR datasets)

**What they are:** Per-filer Activist Insight Bloomberg exports (one xlsx per filer for Silchester, Dalton, 3D, Strategic Capital, Ariake, Effissimo+SMT, LIM, GMO LLC, MIRI) + portfolio snapshot xlsx + Bloomberg NSD master pulls (xlsx + csv).

**NSD CSV (NSD_1_ktcfydh0.csv, 1,002 rows):** Master Bloomberg activism event tracker. Fields: Flag (event ID), Company, Activist_Group, Start_Date, Stake_End_Date, Objectives, Hp_Return, Market_Cap_At_Start, Stake_At_Start, Start_Link (Bloomberg DOCV /ID ref), News_Search, Start_Date_And_Time, Current_Ticker. This is the data feed that backs the HPR distribution tables in v9.1 / v10.2 (Distribution-Position Sizing modifier requires `Hp_Return` lookups by activist).

**Why it matters:** These files are the empirical source of all base-rate calibration tables. Successor pipeline should refresh quarterly per `edinet-monitoring-protocol.md` §8.

### 3.14 PDF reference research

- **JOI2019Zang10419.pdf** — Zang 2019 Murakami/Japan activism academic paper. Source of the **805-day closed-case Effissimo holding period** and the Zang post-AGM reversal warning ("any increase in stock price caused by activist proposals usually is not sustainable, and in some cases, the prices fall after the campaigns").
- **SilchesterBank_of_Kyoto__English.pdf** — Bank of Kyoto public letter; Tier 1.5 reclassification trigger document.
- **sapporopresentationen202304.pdf** — 3D activist presentation; canonical Mode 1b conglomerate unlock reference.
- **Kitagawa_Seiki_investment_thesis_vF.pdf** — LIM/SC dual-filer thesis writeup.
- **202602124_E.pdf**, **5343254.pdf** — EDINET filing samples.
- **20260424_SanyoDenki_6516_StrategicCapital_BoardContestEscalation_REVISED.pdf** — Sanyo Denki board contest escalation memo (Apr 21 2026 SC campaign website launch).
- **enTorch_Capital_Partners_Presentation_SGHK.pdf** — small-cap activism reference.
- **Asuka_Claude_Prompt.docx** — onboarding doc / custom instructions in document form.

### 3.15 `Asuka_Active_Book_Daily_Risk_v1.html` — Dashboard Mockup

**What it is:** HTML visual template for daily-risk dashboard. Bloomberg terminal aesthetic — dark theme, Fraunces + Inter Tight + JetBrains Mono fonts, kanji branding (赤 accent), KPI grid, priority panel, today's filings, layer sections (L1/L2/L3/Watch). Key colour semantics in CSS variables: green = pass, amber = warn, red = stop, gold = highlighted action, blue = neutral info.

**Why it matters:** The output rendering target. Layer responsibilities for the successor's `generate_dashboard.py` are documented in §6 of `edinet-monitoring-protocol.md`.

---

End of Part 3. Sections 4-10 of the handoff (Analytical Methodology; Frameworks/Formulas/Thresholds; Inputs/Tools/Connectors; Outputs; Standing Rules/Special Cases; Worked Example; Implicit Knowledge & Gotchas) follow in Part 4.
