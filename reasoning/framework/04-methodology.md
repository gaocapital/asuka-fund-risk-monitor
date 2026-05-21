<!-- Asuka v8-v11 framework reference - migration handoff Section 4 - populated 2026-05-21, verbatim. -->

## SECTION 4 — ANALYTICAL METHODOLOGY
This section specifies, step-by-step, the process the reasoning layer runs every time it processes a new day's data or an ad-hoc question. The goal is procedural: another analyst should be able to execute the same workflow and arrive at the same outputs.
### 4.1 The daily run (the standing slate)
Every Tokyo trading day at or after 17:00 JST, the layer runs the following sequence unconditionally. Each step has stop-gates that flag the position rather than push it through.
**Step 1 — Freshness sweep.** For every position in the active book (the 26 names listed in Section 3.2 plus Yellow Hat), verify four inputs:
- Spot price ≤ 2 trading days old (the daily-sweep standard; the broader STALE_INPUTS rule allows price ≤ 3 trading days for non-sweep contexts)
- Activist WAC verified against latest 変更報告書 with EDINET doc ID stamped
- EDINET filings checked ≤ 7 days (via the Asuka_EDINET pipeline `current_state.json`)
- News scan ≤ 3 days for the daily sweep; ≤ 7 days for non-sweep contexts
Any input older than the threshold → flag `STALE_INPUTS` and **quarantine the position from verdict updates until refreshed**. The position stays at last verdict but cannot move to a new action signal (BUY/ADD/TRIM/EXIT) until refresh completes. Write the freshness state to `sweep-log/YYYY-MM-DD-sweep.md`.
If `STALE_INPUTS` is present, do **not** skip the position silently — log it explicitly in the sweep file with the specific input that's stale and the age. Skipped sweeps are logged, not silent.
**Step 2 — Hard-stop check (top of every response).** For every position, run the name's stock-specific hard-stop list from `position-book-current.md`. Stop types:
- (a) anchor activist reduction below threshold (e.g., Effissimo trim from peak; Strategic Capital reduces below set threshold)
- (b) fundamental break (profit warning, guidance cut, accounting irregularity, regulator action)
- (c) price gap above ceiling without supporting catalyst (parabolic move — Velocity Trigger from PWER §8.2: 50%+ in single month or 2x+ in <18mo)
- (d) WAC inversion >15% above anchor activist's WAC (or +10% for dual-vehicle structures per v9 amendment, applied against **True-WAC** per v10.3)
- (e) name-specific entry tripwire violation
Any hard-stop hit must produce a `⛔ HARD STOP ALERT` header at the top of the position's section with explicit action (trim / exit / freeze). Never skip. This is the standing rule from the memory: "EVERY position refresh runs HARD STOP CHECK at top of response citing name's OWN stops."
**Step 3 — New filing decode.** For each new EDINET document (doc types 350/360/370/380, plus 180 for AGM voting and shareholder proposals) and each new TDNet timely disclosure on a name in the in-universe roster:
(i) **Apply the EDINET XBRL First Rule** (memory rule #22). Fetch the primary XBRL filing from `disclosure.edinet-fsa.go.jp` using the doc ID (S100XXXX format). Aggregators (kabupro, irbank, maonline, ufocatch, note, Yahoo JP) are fallback only; aggregator data must be stamped with EDINET doc ID or flagged `STALE_INPUTS`. Stamp `edinet_doc_id` on every action signal.
(ii) **Read the joint-holder (共同保有者) section in full** before treating any individual filer string as the full economic interest. Collapse coordinated network vehicles to single filer-units:
- Murakami umbrella = 1 (ATRA, Office Support, CIE/CIF/Reno/S-Grant/Fortis/C&I/Rebuild, Aya Nomura individual, Yoshiaki direct, Takateru direct, MI2/MI5, Minami Aoyama RE, Aphrodite-verify)
- Effissimo + SMT Partners Cayman = 1
- Dalton + NAVF + NAVF Select LLC + Rising Sun + Kizuna = 1
- Strategic Capital + UGS Sunshine LP series D/E/F/G/H = 1 if joint, 2 if independently filed
- Ueshima individual + Naturali + DOE5% = 1
- Be Brave 株式会社 + ESG投資事業組合 + Izumida personal = 1
- Palliser + named SPVs = 1 (verify each filing)
(iii) **Apply the four-lens verdict engine** (the multi-lens framework added post-Musashi May 2026):
- **L1 archetype-fit** — does filer's CRMC Category, default mode, default purpose tier, and typical accumulation path match what's in this filing? Match → proceed. Mismatch → re-tag attempt mandatory.
- **L2 macro regime** — does the regime (TSE PBR<1 pressure stack, BOJ rate normalisation, cross-shareholding unwind trajectory, yen position, June AGM cluster window) support the thesis the filing implies?
- **L3 fundamentals** — does the target's PBR / ROE / net cash / cross-shareholding overhang / founder-bloc structure support the thesis?
- **L4 strategic-source tag** — assign the PRIMARY + SECONDARY tag from the 17-tag taxonomy (IP, RE, SOTP, CASH, FWD, TOB, GOV, SUB, CYC, ARB + hybrids SUB+TOB, CASH+SUB, GOV+CASH, IP+GOV, RE+SUB, TOB+ARB, SOTP+CASH, FWD+IP).
**Verdict rule:** PWER must clear 20% with ≥2 lenses supporting. **Single-lens REJECT triggers MANDATORY L4 re-tag attempt;** if a non-canonical tag fires with L2/L3 support, override REJECT → BUY/STARTER. Document both veto lens AND override lens. Hard-kill conditions (fraud, regulatory delisting, controlling family >50%) bypass override.
(iv) **Classify filing language to Tier P/R/E/C** via the canonical phrase dictionary in CRMC §3 / EDINET protocol §3. **A purpose-tier transition (lower → higher tier) at the same filer on the same target is the highest-signal event in the framework** — empirically precedes public demands by 4-8 weeks. If transition detected: upgrade layer assignment immediately; fund the upgrade trade out of the lowest-PWER cluster member.
(v) **Run the v10.3 ten-step concealment forensic protocol** on every new filing. Stamp the position memo with the concealment risk score (0+) and the True-WAC reference selection. Skipping the scan is a memo-validity failure — the action signal cannot lock without it.
(vi) **Run the v10/v10.1/v10.2 gates** for any new shadow-follow candidate, in order: G1 Pre-existing Concession → G1.5 Realized Mode 1 → G2 Threshold Progress (incl. Fast Defensive Response sub-rule) → G3 Internal Rotation Penalty → G4 Residual Liquidity → G5 Second-Leg Requirement.
(vii) **Apply CRMC anomaly rules** for the filer's archetype (Effissimo filing burst / pre-AGM ratio / silence / reduction from peak; Murakami CR No.15+ / ATRA direct / Stage 5; Oasis failure pattern / public letter; 3D Defender response Level 4-5 / mode confusion; SC dedicated campaign website; Silchester public letter / parallel industry vertical; GMO threshold filing discipline / underwater+adding / 10% crossing; Be Brave monthly ratchet / DOE adoption; Palliser Phase 2 transition; SilverCape 14.85% crossing / White & Case counsel; Zennor harvests into rally; DOE5%+Ueshima+Naturali wolf-pack signal).
**Step 4 — WAC cross-check (the load-bearing discipline).** For every position where the principal activist is the thesis driver:
(i) Determine principal activist's **True-WAC** per v10.3 (use disclosed only when concealment score = 0; otherwise apply v10.3 §3 decision rule).
(ii) Compute current price as % above/below True-WAC.
(iii) **Apply v8/v9/v9.1 ceiling against True-WAC:**
- Single-vehicle activist: +15% above WAC → co-investment edge gone (Sanyo Denki precedent)
- Dual-vehicle (Effissimo+SMT, Dalton+NAVF, Murakami family aggregate): **+10%** ceiling
- Concealment band 1-2: broaden +10% treatment to any position with score ≥1 regardless of formal dual-vehicle structure
- Concealment band 3-4: use most conservative WAC reference
(iv) **Apply the WAC inversion rule** when principal activist is a NET seller (aggregate stake declining from peak): co-investment framework inverts entirely — activist is distributing TO you, not co-investing with you. PWER must reflect distribution dynamics regardless of WAC arithmetic. **Murakami Stage 5 confirmed when ALL FIVE TRUE:** aggregate stake declining from peak, company buybacks completed, stock near 52-week high, price above consensus, peak stalled below 33% veto threshold.
(v) If aggregate-increase decomposes into C1 or C10 patterns (joint-holder mask), the inversion fires on lead-filer direction even when aggregate reads flat or up.
**Step 5 — Catalyst calendar.** Surface every position with a binary catalyst inside the next 18 trading days:
- AGM dates (Q1 record date typically early April for June AGM; full convocation notice on TDNet ~3 weeks pre-AGM; voting results filed as 臨時報告書 doc 180)
- Quarterly earnings (verify date from company IR calendar primary — aggregator dates are secondary)
- MBO deadline / TOB resolution date / 臨時報告書 forecast revisions
- Expected proposal filing (8-week submission deadline before AGM; April record date for June AGM)
- Expected stake-cross filing (within 5 business days of crossing 5%, 10%, 15%, 20%, 33.4%)
Confirm **Catalyst-Window Patience (CWP) regime** — inside the binary window (typically 60 days pre-binary), only hard stops fire; momentum / PWER-decay-on-rally / silence (<12 wk) / Q-margin signals are SUSPENDED. The v10.3 T1-T5 gate framework is SUSPENDED 60d pre-binary.
**Step 6 — PWER recompute and basket reconciliation.** For each position whose inputs moved materially (filing, earnings, AGM, catalyst slip, WAC update, anchor stake change, regime break) — recompute PWER under all four scenarios (Bear / Base / Bull / Extreme Bull) and re-anchor the layer (L1 / L2 / L3 / L4 / Reduce / Exit).
(i) Use the canonical formula `PWER = Σ (Pᵢ × Rᵢ)` with `Rᵢ = (Targetᵢ − Current)/Current + Carryᵢ` and `Carryᵢ = (div_yield + buyback_yield) × (Monthsᵢ/12)`.
(ii) For dated binary catalysts <12 months out, compute IRR-annualised: `IRRᵢ = (1+Rᵢ)^(12/Monthsᵢ) − 1; PW-IRR = Σ (Pᵢ × IRRᵢ)`. Gate 20% becomes 20% annualised.
(iii) Apply the **v9.1 composite gate matrix** for ABSOLUTE_ONLY vs ANNUALIZED_ONLY vs PASS vs FAIL handling. Position sized at 70% of layer cap if only one gate passes; full layer cap if both pass; no fresh capital if both fail.
(iv) Apply the **v10.2 Float-Retirement PWER Multiplier** when all four conditions met (activist ≥5%; MTP total payout ratio ≥80% over ≥3 FY; ≥5% float retired in trailing 12m; Base-case 12-36mo horizon). Multiplier on Base only; cap 25%.
(v) Apply the **v10.2 Distribution-Position Sizing (DPS) Modifier** based on principal activist's current realized HPR bucket against the v9.1 empirical distribution. Sequence: v10.0 Five Gates verdict → Gate 1.5 caps at L3 max if fired → DPS modifier scales within layer ceiling.
(vi) Apply the **two-observable-signal rule** before any probability shift ≥5pp. To shift Bull probability up by 5pp+: require two Tier-A signals or four Tier-B signals. Bear-side adjustments can be made on a single Tier-A signal if unambiguously negative.
(vii) Apply the **principal-follower divergence haircut** (v10 §3) before PM overlay:
- Tier R: −5pp mean, −10pp top-decile
- Tier P: −2pp mean, −5pp top-decile  
- Tier E: −3pp mean, −7pp top-decile
- Tier Q: 0pp mean, −2pp top-decile
(viii) **Bear must be a FLOOR**, anchored to one of: (a) net cash + 50% book value, (b) 52w low less 10%, (c) sector PER applied to legacy business in SOTP, (d) prior cycle trough multiple. Without anchored floor, asymmetry is meaningless.
(ix) **Asymmetry gate** (the second gate alongside PWER threshold): Asymmetry = (P_bull × R_bull + P_xb × R_xb) / |P_bear × R_bear|. <1.5 reject; 1.5-2.5 conditional accept at minimum L-tier; >2.5 standard sizing; >4.0 convex setup permits +1-2pp NAV premium.
(x) **Confirm portfolio remains within hard rules:** 100% deployed (0% cash target), 14-18 positions, weighted-avg PWER ≥25%, no single position >12%, no single activist cluster >25% NAV, no single event cluster >50% NAV, mega-cap activist cluster ≤6% NAV.
**Step 7 — Sweep log.** Write an audit file to `sweep-log/YYYY-MM-DD-sweep.md` for every run, regardless of whether a verdict changed. Increment the HTML dashboard (`dashboard_YYYY-MM-DD.html` + `dashboard_latest.html`) only on verdict change. Skipped sweeps are logged explicitly, not silent.
### 4.2 How to read a single filing — concrete sequence
Given a new EDINET 大量保有報告書 or 変更報告書 (the bread-and-butter daily event), the layer runs:
1. Verify primary source (EDINET XBRL not aggregator). Stamp `edinet_doc_id`.
2. Extract filer name, target ticker, ownership %, prior ownership %, ownership change, purpose text, joint-holder list, 取得日 grid (transaction dates + shares + unit prices), 取得対価 (cash vs non-cash consideration).
3. Resolve filer to single beneficial owner via aggregation rules.
4. Apply 10-step concealment protocol → score 0+ and stamp.
5. Map purpose text to Tier P/R/E/C; record transition if prior filing tier exists.
6. Compute True-WAC per v10.3 §3 decision rule.
7. Compute current spot vs True-WAC; flag if >+15% single-vehicle, >+10% dual-vehicle, >+10% if concealment band ≥1.
8. Apply CRMC archetype anomaly rules for this specific filer.
9. Run the four-lens verdict engine (archetype-fit, macro, fundamentals, strategic-source tag).
10. Score the filing in the v10 Five Gates (G1 → G1.5 → G2 → G3 → G4 → G5).
11. Apply v9.1 state distribution priors for scenario probabilities.
12. Compute PWER (absolute + annualised) for each plausible scenario set.
13. Apply float-retirement multiplier if triggered; apply DPS modifier from current HPR bucket; apply principal-follower divergence haircut.
14. Compute composite gate verdict (PASS / ABSOLUTE_ONLY / ANNUALIZED_ONLY / FAIL).
15. Cross-check against name's existing hard-stop list; cross-check against cluster caps, ADV caps, single-position cap.
16. Generate action signal (NEW / ADD / HOLD / TRIM / EXIT) with explicit sizing, entry zone, upgrade tripwires, hard-stop tripwires.
17. Mark `action_verified_date = today`. Without this stamp, the action signal does not lock.
### 4.3 How to decide whether a filing changes a thesis
A filing changes a thesis when one or more of the following fires:
- **Layer reassignment.** Tier-transition R→E or E→C, threshold crossing into new band (5/10/15/20/33.4%), Mode 1→2 transition by accumulation pace (Teijin Apr 14 2026 +5.05pt in 18 weeks = 1.25pt/month = 3-4× normal cadence).
- **WAC inversion or anchor reduction.** Principal activist's first reduction filing → downgrade by one full layer (L1→L2, L2→L3, L3→exit). Second reduction → full exit. Murakami Stage 5 confirmation (all five conditions) → exit even when arithmetic looks positive.
- **Wolf-pack arrival.** Third filer crosses 5% → halve the size (per multi-activist-dynamics §7). The third arrival is a regime change, not confirmation of existing thesis.
- **Concealment band escalation.** Score moves from clean to material (3-4) or severe (5+) → tighten WAC ceiling, may require defer/exit.
- **Fundamental break.** Profit warning, guidance cut, accounting irregularity → re-rate scenarios with Bear weight up materially, may trip hard stop.
- **Catalyst pass/fail.** AGM resolution passes (50-60% partial harvest immediate); AGM defeat with continued activist accumulation (counter-trend add, not exit); MBO bid announced (harvest 50-60%; trail-stop residual).
- **Regime break.** TSE policy reversal, BOJ rate reversal, yen breach of cycle extremes, sector shock affecting >30% of book → suspend new initiations 5 trading days for portfolio review.
A filing does **NOT** change a thesis when:
- Stake static at minimum disclosure floor for 6+ months (passive holding, not exit)
- Single-quarter earnings miss with activist still at full stake or accumulating (add, don't trim)
- Murakami internal redistribution between vehicles at CR No.15+ (read joint-holder section; sum aggregate group direction; internal transfer is not a signal of conviction change)
- Stock above consensus target (consensus is not a thesis killer)
- Macro-regime drawdown (Japan beta is not a position-level signal)
- Calendar-based rebalancing pressure
- Sell-side rating downgrade in isolation (Tier B signal; needs a second to move probabilities)
### 4.4 How to derive every metric
**PWER:** `Σ (Pᵢ × Rᵢ)` with `Rᵢ = (Targetᵢ − Current)/Current + Carryᵢ` over four scenarios summing to 1.00.
**Annualised PWER (PW-IRR):** `Σ (Pᵢ × IRRᵢ)` with `IRRᵢ = (1+Rᵢ)^(12/Monthsᵢ) − 1`.
**Asymmetry:** `(P_bull × R_bull + P_xb × R_xb) / |P_bear × R_bear|`.
**True-WAC:** apply v10.3 §3 decision rule based on concealment flags fired.
**Float-Retirement Multiplier:** `min(trailing_12m_retirement × (remaining_MTP_years / 1), MTP_total_payout × NI_3yr_projected / current_mcap)`, capped 25%. Applied to Base scenario only.
**DPS Modifier:** look up principal activist's current Bloomberg ACTV / NSD Hp_Return against v9.1 §3 distribution bucket boundaries. Apply 1.5×/1.0×/0.5×/0.25×/stand-down sizing modifier to layer ceiling.
**Liquidity discount:** `days_to_exit = shares_held / (ADV × 0.25); discount_pct = min(15, days_to_exit / 30); realized_value = expected_value × (1 − discount_pct/100)`.
**Concealment risk score:** sum of severity weights of fired C1-C11 flags (see v10.3 §2 weights: C1=3, C2=2, C3=1 if pending 0 if resolved, C4=2, C5=1, C6=2, C7=1, C8=1, C9=1, C10=3, C11=2).
**Cluster aggregate stake:** sum across all coordinated vehicles in beneficial-owner network; never compute on per-vehicle basis.
**Days-to-AGM:** for June AGM, count from current date; record date typically early April (proposals must be filed before April record date); 8-week proposal submission deadline.
### 4.5 Decision logic in order — the canonical pipeline
When the layer is handed a question and must produce an action signal, the procedural order is rigid:
1. **Freshness check** — if STALE_INPUTS, do not produce a verdict; refresh first.
2. **Hard-stop check** — if any hard stop fires, halt; produce `⛔ HARD STOP ALERT` with explicit action.
3. **Concealment scan** — run 10-step protocol; stamp score and True-WAC.
4. **WAC cross-check against True-WAC** — if +15% single-vehicle / +10% dual-vehicle / +10% if band ≥1: co-investment edge closed; PWER must be justified on standalone event-driven terms only.
5. **WAC inversion check** — if principal is net seller from peak (or all five Stage 5 conditions for Murakami): downgrade one full layer; on second reduction, exit.
6. **Multi-lens verdict (4 lenses)** — archetype-fit, macro, fundamentals, strategic-source tag. If REJECT on single lens, mandatory L4 re-tag attempt; if non-canonical tag with L2/L3 support fires, override REJECT.
7. **Five gates** — G1 → G1.5 → G2 → G3 → G4 → G5. Apply v10.1 Fast Defensive Response sub-rule combined verdict matrix with G5 score.
8. **PWER recompute** — four scenarios, two-observable-signal rule for probability shifts, divergence haircut applied, asymmetry computed.
9. **Composite gate** — PASS (full layer cap) / ABSOLUTE_ONLY (70% of layer cap, harvest aggressively) / ANNUALIZED_ONLY (70% of layer cap, longer carry tolerance) / FAIL (no fresh capital; existing exits at first tripwire).
10. **Sizing** — Gate 1.5 (if fired) caps at L3 max → DPS modifier scales within ceiling → liquidity cap (50% of 3-day ADV) → single-position cap 12% → cluster caps.
11. **Tripwires** — minimum 3 for L1, 2 for L2, 1 for L3. Each must be observable event with defined evidence source and programmatic action.
12. **Stamp `action_verified_date = today`** — the action signal locks only after this stamp.
13. **Write sweep log** to `sweep-log/YYYY-MM-DD-sweep.md`; increment dashboard if verdict change.
---
