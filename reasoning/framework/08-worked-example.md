<!-- Asuka v8-v11 framework reference - migration handoff Section 9 - populated 2026-05-21, verbatim. -->

## SECTION 9 — WORKED EXAMPLE
A complete, end-to-end daily sweep memo. The scenario is constructed to exercise the full machinery: book state, two new EDINET filings, one news item, the Five Gates, the concealment scan, the WAC cross-check, the freshness sweep, the priority actions block, and the per-position diagnostics. Names are from the actual book.
---
### Input bundle (what arrives at the start of the run)
**`dashboard_data.json` (slice — book state at close of prior day):**
```json
{
  "as_of": "2026-05-19T17:00+09:00",
  "version": "v11.0",
  "portfolio": {
    "total_positions": 16,
    "weight_deployed_pct": 96.0,
    "cash_buffer_pct": 4.0,
    "wtd_avg_pwer_pct": 27.4
  },
  "positions": [
    {"tk":"9684","name":"Square Enix","layer":"L1","activist":"3D","stake_pct":17.50,"wac":2900,"px":2552,"pwer_pct":38.4,"wt_pct":12.0,"action":"HOLD_AT_CAP","last_filing":"2026-03-03"},
    {"tk":"7752","name":"Ricoh","layer":"L1","activist":"Effissimo+SMT","stake_pct":24.77,"wac":1200,"px":1612,"pwer_pct":22.0,"wt_pct":8.0,"action":"HOLD","last_filing":"2026-04-10","note":"WAC inversion +34% → downgrade ADD→HOLD May 2026"},
    {"tk":"3401","name":"Teijin","layer":"L2","activist":"Effissimo","stake_pct":19.26,"wac":1350,"px":1689,"pwer_pct":36.5,"wt_pct":5.5,"action":"HOLD","last_filing":"2026-04-14"},
    {"tk":"7740","name":"Tamron","layer":"L2","activist":"Effissimo","stake_pct":15.30,"wac":3950,"px":4380,"pwer_pct":24.0,"wt_pct":3.5,"action":"HOLD","last_filing":"2026-04-22"},
    {"tk":"6516","name":"Sanyo Denki","layer":"L1","activist":"Strategic Capital","stake_pct":14.35,"wac":3600,"px":5640,"pwer_pct":13.0,"wt_pct":6.0,"action":"NO_ADD","last_filing":"2026-04-21","note":"DPS modifier 0.5× → trim 7→6% Apr; campaign-site launched Apr 21"},
    {"tk":"6914","name":"Optex Group","layer":"L2","activist":"GMO-Usonian","stake_pct":5.00,"wac":2629,"px":2885,"pwer_pct":16.0,"wt_pct":5.0,"action":"HOLD","last_filing":"2026-02-25"},
    {"tk":"6262","name":"Pegasus","layer":"L2","activist":"Be Brave","stake_pct":11.87,"wac":793,"px":855,"pwer_pct":29.0,"wt_pct":3.0,"action":"FLAG_L2_CAP","last_filing":"2026-02-20","note":"v10.1 Concession-Captured warning active"},
    {"tk":"4246","name":"DaikyoNishikawa","layer":"L2","activist":"Murakami MI2","stake_pct":6.20,"wac":841,"px":648,"pwer_pct":35.5,"wt_pct":3.0,"action":"HOLD","last_filing":"2026-04-03"},
    {"tk":"3182","name":"Oisix ra Daichi","layer":"L3","activist":"GMO-Usonian","stake_pct":10.48,"wac":1576,"px":1428,"pwer_pct":28.0,"wt_pct":5.0,"action":"HOLD","last_filing":"2026-04-15"},
    {"tk":"4493","name":"Cyber Security Cloud","layer":"L3","activist":"SilverCape","stake_pct":9.50,"wac":1735,"px":1515,"pwer_pct":46.7,"wt_pct":2.5,"action":"BUY","last_filing":"2026-04-09"},
    {"tk":"4613","name":"Kansai Paint","layer":"L3","activist":"Silchester","stake_pct":5.05,"wac":2511,"px":2168,"pwer_pct":35.0,"wt_pct":3.0,"action":"HOLD","last_filing":"2026-03-15"},
    {"tk":"8368","name":"Hyakugo Bank","layer":"L3","activist":"Ariake","stake_pct":5.06,"wac":620,"px":712,"pwer_pct":21.0,"wt_pct":2.0,"action":"HOLD","last_filing":"2026-01-30"},
    {"tk":"9882","name":"Yellow Hat","layer":"L3","activist":"Strategic Capital","stake_pct":13.83,"wac":1378,"px":1465,"pwer_pct":22.0,"wt_pct":3.0,"action":"HOLD","last_filing":"2024-12-17","note":"Realized Mode 1 carry, M1-Internal-Carry, DPS 0.5×"},
    {"tk":"4071","name":"Plus Alpha Consulting","layer":"L2","activist":"Oasis","stake_pct":8.02,"wac":2063,"px":2110,"pwer_pct":33.0,"wt_pct":3.0,"action":"HOLD","last_filing":"2026-03-28"},
    {"tk":"2972","name":"Sankei REIT","layer":"L4-ARB","activist":"Murakami CIE+Aya Nomura","stake_pct":19.35,"wac":123000,"px":127500,"pwer_pct":4.2,"pwer_annualized_pct":85,"wt_pct":1.5,"action":"HOLD","last_filing":"2026-04-28"},
    {"tk":"3941","name":"Rengo","layer":"L3-WATCH","activist":"Murakami group","stake_pct":5.00,"wac":1180,"px":1232,"pwer_pct":14.0,"wt_pct":0.0,"action":"WATCH","last_filing":"2026-04-22"}
  ]
}
```
**New EDINET filings (overnight batch picked up at 09:00 SGT):**
1. **Effissimo Capital Management Pte Ltd — Ricoh (7752) 変更報告書 No. 12, doc `S100ZBKL`, filed 2026-05-19 17:38 JST.** Stake 24.77% → **26.50% (+1.73pt over 19 trading days)**. Joint holder section: Effissimo + SMT Partners Cayman unchanged in proportion. 取得対価: 現金 (cash). Transaction grid: 8 rows spanning 2026-04-23 → 2026-05-15. Disclosed WAC ¥1,395 across the increment; group-blended WAC ¥1,219 post-add. Purpose text: `純投資及び状況に応じて重要提案行為等を行うこと`.
2. **Strategic Capital Inc — Sanyo Denki (6516) 変更報告書 No. 9, doc `S100ZBQM`, filed 2026-05-19 18:12 JST.** Stake 14.35% → **15.08% (+0.73pt)**. Single-vehicle. Disclosed WAC for increment ¥5,180; group-blended WAC ¥3,775 post-add. Purpose text unchanged: Tier R. **Threshold 15% crossed.**
**News overnight (TDNet + JP press):**
- **Square Enix (9684), 17:30 JST May 19** — TDNet adhoc: company files notice of proposed AGM agenda items, including 3D's two director nominees and one capital-policy proposal. Board has rejected 3D's nominees; recommends "vote against." First binary clarity for June 27 AGM.
- **Bunka Shutter (5930), 16:45 JST May 19** — TDNet adhoc: company announces ¥3B buyback authorisation FY27 (acquisition period May 20 2026 – Mar 31 2027); broken-buyback flag from prior cycle (¥2B / 0 shares) now superseded.
- **Macro:** USD/JPY 154.20 (−0.6% session); TOPIX +0.8% prior session.
**Today's date: Wednesday, May 20, 2026.**
---
### Generated output — daily sweep memo, in standard format
```
╔══════════════════════════════════════════════════════════════════════════╗
║  ASUKA FUND — DAILY SWEEP MEMO                                           ║
║  As of: 2026-05-20 09:30 SGT / 10:30 JST                                 ║
║  Pipeline: edinet_pipeline run 09:00 SGT OK · 53 docs scanned · 2 hits   ║
║  Last sweep: 2026-05-19 17:00 JST · this is increment over prior         ║
╚══════════════════════════════════════════════════════════════════════════╝
```
#### Top-of-Page Summary
Two new in-universe filings overnight, both material. **Effissimo Ricoh +1.73pt (24.77% → 26.50%)** is a Mode 2 acceleration — first sub-25pt increment in eight weeks, and the new disclosed-WAC increment ¥1,395 closes the WAC inversion gap from +34% above to +24% above. **Strategic Capital Sanyo Denki crosses the 15% threshold** (15.08%), the Mode-1-to-Board-Contest tripwire identified in the April 21 campaign-site monitor. Square Enix board has formally recommended a vote against 3D's two director nominees — June 27 AGM is now a clean binary at T-38 days. Bunka Shutter ¥3B new buyback supersedes broken-buyback flag — watch-list re-arm.
No `STALE_INPUTS` flags; no `DATA_QUARANTINE` hits today. All 16 positions have px stamp ≤ 1 trading day. Pipeline health: green.
#### Priority Actions — Today
1. **⛔ HARD STOP CHECK — Ricoh (7752) WAC inversion reassessment.** Effissimo's new +1.73pt at ¥1,395 disclosed-WAC moves the group-blended WAC from ¥1,200 to ¥1,219. Spot ¥1,612 = +32% above new WAC (was +34%). Still **above the +15% inversion ceiling per memory rule #8.** Position remains HOLD; do NOT add. Standalone Mode 2 thesis (digital services SOTP, May 12 earnings already digested) intact but adds require fresh standalone justification. Status: HOLD unchanged.
2. **Sanyo Denki (6516) — 15% threshold crossed. Mode 1 → Board Contest confirmed.** Strategic Capital +0.73pt to 15.08% triggers `asuka-framework-extension-v10_2.md §5.4` upgrade tripwire #1 (SC files 変更報告書 crossing 15%). However: spot ¥5,640 = +49% above new group WAC ¥3,775 — co-investment edge remains CLOSED (memory rule #8). M1-Internal-Carry transitioning to M1-External-Binary per v10.2 §4.4 diagnostic (board contest = named external counterparty = SC's nominees vs current board). DPS modifier 0.5× × L1 standard 12% = L1 cap 6%. Currently at 6.0%. **No size change.** Tripwire upgrade-to-L1-uncapped requires SC <+15% WAC delta, which would need ¥4,341 entry — not realistic from here.
3. **Square Enix (9684) — board recommends vote against 3D nominees. T-38 days to AGM.** First binary clarity. Hold at 12% cap (memory rule #7). Do NOT add into the binary (per position-book stop). Re-underwrite scenario weights post-AGM: if 3D nominees pass, X-Bull weight rerates to 25% from 10%; if rejected, time-stop trim within 30 days. **Action: HOLD AT CAP unchanged today.**
4. **Bunka Shutter (5930, WATCH) — broken-buyback flag superseded.** New ¥3B authorisation FY27 = explicit Mode 1 met; Gate 1.5 b-condition now eligible if combined with payout-ratio MTP and Dalton accumulation pause. Re-arm watch. Next checkpoint: confirm Dalton's accumulation cadence over next 30 days; if paused = Gate 1.5 candidate for L3 entry.
5. **Rengo (3941, L3-WATCH) — no new filing today.** Watch trigger remains: (a) ATRA stake escalates >2% (Wavelock/Keikyu pattern, memory rule #11); (b) Change Report No. 2+ shows aggregate group 5% → 8%; (c) Rengo capital-return MTP commitment. None fired today. Status unchanged.
---
#### Today's Filings — detailed diagnostic
##### Filing 1 · Effissimo + SMT — Ricoh (7752) 変更報告書 No. 12 · `S100ZBKL`
**Filing facts (EDINET XBRL primary, memory rule #22):**
- Filer: Effissimo Capital Management Pte Ltd (E20136) + SMT Partners Cayman Limited (E26789)
- Target: Ricoh Company Ltd (7752)
- Prior stake: 24.77%
- New stake: **26.50% (+1.73pt)**
- 取得対価: 現金
- Transaction grid: 8 rows, 2026-04-23 → 2026-05-15 (22 calendar days, 15 trading days)
- Disclosed WAC, incremental: ¥1,395
- Group-blended WAC post-add: ¥1,219 (was ¥1,200)
- Joint-holder section: unchanged, Effissimo + SMT only
- Purpose: `純投資及び状況に応じて重要提案行為等を行うこと` (Tier R)
- Filing language tier: R (memory rule #1 — "純投資" is boilerplate; the `重要提案行為等` keeper escalates to Tier R)
**Concealment scan (v10.3 ten-step protocol — memory rule #22 + v10.3 Standing Rule #2):**
| Step | Check | Result |
|---|---|---|
| 1 | Acquisition-consideration type | Cash. Pass. |
| 2 | Transaction-date span | 22 calendar days for change report. Below the C8 60-day threshold. No flag. |
| 3 | Volume reconciliation | Filer's acquired shares = ~12.3M; TSE volume over span = ~58M; ratio ~21%. **Elevated; >15% threshold.** Flag potential **C5/C6**. → Step 6. |
| 4 | Joint-holder per-filer delta | Effissimo +1.30pt; SMT +0.43pt. Both positive; no internal-transfer signal. No C1/C10. |
| 5 | Nominee scan | No PB or custody nominees in joint-holder section. No C3/C7. |
| 6 | TDNet ToSTNeT cross-reference | One ToSTNeT-3 print on 2026-05-08, 4.2M shares at ¥1,378. Matches Row 5 of transaction grid. **C5 fires (1 share count match).** |
| 7 | VWAP-vs-WAC delta | Continuous-session VWAP (excluding ToSTNeT print): ¥1,418; reported incremental WAC ¥1,395 — Δ −1.6%. Below ±5% threshold. No additional flag. |
| 8 | Vehicle incorporation date | Effissimo (2006), SMT (2011); both long-established. No C2. |
| 9 | WAC stability stress test | Effissimo group WAC over last 3 change reports: ¥1,200 → ¥1,210 → ¥1,219; <0.5% drift. **However** spot range over period was ¥1,250 – ¥1,720 (38%) — vehicle WAC moving slowly is consistent with monotonic accumulation, not stasis. No C4 fire (per Standing Rule #6, C4 does NOT fire on monotonic accumulators). |
| 10 | Filing-cadence forensics | No filing-gap pattern; all filings well within 5 business days. No flag. |
**Concealment risk score: 1 (C5 only).** Band: **LOW**.
**True-WAC selection:** Disclosed group WAC ¥1,219 is appropriate (C5 alone with VWAP-reconstructed ¥1,418 actually HIGHER than disclosed — Standing Rule #3 says use the highest, so True-WAC = **¥1,418** for conservative reading).
**WAC cross-check (memory rule #8 + v10.3 Standing Rule #1):**
- Spot ¥1,612 vs True-WAC ¥1,418 = **+13.7% above True-WAC**.
- Still BELOW the +15% inversion ceiling (just). On disclosed-WAC reading: +32% above. **The concealment-aware reading actually unlocks the position from "ADD blocked" to "ADD eligible" — but margin is thin.**
**Five Gates re-screen at this filing:**
| Gate | Score | Detail |
|---|---|---|
| G1 Concession | 0/3 | Ricoh has no pre-existing 80% payout, no DOE floor, no public capital policy statement ≤24mo, no buyback ≤6mo. Clean. |
| G1.5 Realized Mode 1 | NO | Effissimo just accelerated +1.73pt — accumulation is NOT paused. c-condition fails. Realized Mode 1 does NOT fire. |
| G2 Threshold Progress | CLEAR | Effissimo crossed 25% (Mode 2 deep) and is now at 26.50%. Approaching 33.4% veto threshold. |
| G3 Internal Rotation | NO PENALTY | Both vehicles increased; no rotation. |
| G4 Residual Liquidity | YELLOW | Effissimo's 141M shares = 240+ days at 25% ADV (per v9.1 §4 Ricoh analysis). Exit-liquidity discount applied to Bull anchor. |
| G5 Second Leg | 2 STRONG LEGS | (i) SOTP digital-services unit re-rating (Konica/Toshiba OA-precedent MBO optionality); (ii) net cash + separable business segments. |
**PWER refresh (scenario table):**
| Scenario | Prob | Target ¥ | Return from ¥1,612 | Contribution |
|---|---|---|---|---|
| X-Bull (forced strategic review, partial spin or MBO bid) | 15% | 2,400 | +49% | +7.4pp |
| Bull (Mode 2 escalation: large buyback + segment divestiture) | 30% | 2,000 | +24% | +7.2pp |
| Base (continued ratchet, partial buyback, gradual re-rating) | 35% | 1,800 | +12% | +4.2pp |
| Bear (Mode 2 stalls, earnings miss, Effissimo holds but no progress) | 20% | 1,350 | −16% | −3.2pp |
| **PWER** | | | | **+15.6%** |
Annualized PWER over 18-month Effissimo Mode 2 horizon: **+10.4%**. **Both gates fail** (memory rule #6: 20% absolute or 15% annualized). However the position is already in the book at L1 weight 8% with carried P&L of +34% from entry — exit decision should not be driven by entry-PWER gate alone (memory rule #13: forward PWER compression is the trim trigger, not absolute gain).
**Decision:** **HOLD at 8% NAV (unchanged).** Do NOT add despite the concealment-unlocked True-WAC reading — forward PWER +15.6% is below the 20% gate for fresh capital deployment. Trim trigger requires further compression below +10%. **Watch tripwire: if Effissimo crosses 30% in the next change report, scenario weights shift toward X-Bull (Mode 3 veto-threat play emerges) and PWER recovers.**
##### Filing 2 · Strategic Capital — Sanyo Denki (6516) 変更報告書 No. 9 · `S100ZBQM`
**Filing facts (EDINET XBRL primary):**
- Filer: Strategic Capital Inc (E32xxx — re-verify per memory #22)
- Target: Sanyo Denki (6516)
- Prior stake: 14.35%; **new: 15.08% (+0.73pt)**
- 取得対価: 現金
- Transaction grid: 4 rows, 2026-05-12 → 2026-05-18 (6 days)
- Disclosed WAC incremental: ¥5,180
- Group-blended WAC post-add: ¥3,775
- Single vehicle (no joint-holder section)
- Purpose: Tier R, language unchanged
**Concealment scan:** No flags fire. Single-vehicle, short transaction window, no PB or custody, no ToSTNeT prints, WAC moves materially upward (¥3,600 → ¥3,775 = 4.9% drift on a 5% incremental position) — consistent with active continuous-session accumulation. **Concealment score: 0.** True-WAC = disclosed = ¥3,775.
**WAC cross-check:**
- Spot ¥5,640 vs True-WAC ¥3,775 = **+49% above WAC.**
- Inversion ceiling +15% breached materially. **Co-investment edge remains CLOSED.** Memory rule #8 binding.
**Status flag transitions:**
- v10.2 §4 M1 sub-tag: currently M1-Internal-Carry; with 15% threshold crossing + April 21 campaign site + filed shareholder proposal = **transitioning to M1-External-Binary** (named external counterparty: SC's director nominees vs incumbent board). Per v10.2 §4 reference cases, Sanyo Denki is the canonical "transition" case.
- DPS modifier: SC HPR at Sanyo Denki recalculated. Bloomberg ACTV mean for SC is +52.2% (n=38, 61% positive). Current HPR = (¥5,640 / ¥3,775) − 1 = **+49.4%**. SC bucket position: solidly mid-bucket-3 (+40% to +80% range). DPS modifier 0.5× × L1 standard 12% = **L1 cap 6%**.
- Layer ceiling: confirmed L1 6% cap.
**Five Gates re-screen at this filing:**
| Gate | Score | Detail |
|---|---|---|
| G1 Concession | 0/3 | No pre-emption in place. |
| G1.5 Realized Mode 1 | NO | SC actively escalating (campaign site, shareholder proposal). c-condition fails. |
| G2 Threshold Progress | CLEAR | SC crossed 15% — credible-threat threshold met. |
| G3 Internal Rotation | N/A | Single vehicle. |
| G4 Residual Liquidity | TRAPPED | WAC inversion +49% — shadow follower marginal entry is far above SC's economics. |
| G5 Second Leg | 2 STRONG LEGS | (i) Sub-1.0x PBR + cash-rich industrial (CASH+SUB hybrid); (ii) Board contest at June AGM = explicit named external action. |
**PWER refresh (scenario table at current ¥5,640):**
| Scenario | Prob | Target ¥ | Return | Contribution |
|---|---|---|---|---|
| X-Bull (board contest passes, full capital return programme, +¥30B buyback) | 15% | 8,500 | +51% | +7.6pp |
| Bull (partial AGM win — 1 of 2 nominees, ¥15B buyback, DOE 6%) | 30% | 7,000 | +24% | +7.2pp |
| Base (campaign fails AGM but forces management concession over 12mo) | 35% | 6,200 | +10% | +3.5pp |
| Bear (AGM defeat + no concession + capital cost rises) | 20% | 4,500 | −20% | −4.0pp |
| **PWER** | | | | **+14.3%** |
Annualized over 13mo to AGM + follow-through: **+13.2%**. **Both gates fail.** This is consistent with the "co-investment edge closed" reading. **However:** the position is already in book at L1 weight 6.0% and is the canonical M1-Internal-→-External transition case. The decision to hold at L1 6% (not trim further) is governed by:
- DPS modifier prescribes L1 cap 6% — currently at 6.0%, exactly at cap.
- Hard stop (per position-book): SC trims below 13% → exit. Today SC is at 15.08% with active accumulation. No hard stop triggered.
- Forward PWER is +14% on standalone event-driven terms (not co-investment edge). Below gate but the carried P&L (+57% from entry) + binary AGM catalyst at T-38 days argues against active trim.
**Decision:** **HOLD AT L1 6% (unchanged).** No add (WAC inversion). No trim (no hard stop, AGM binary). Re-evaluate post-June AGM:
- If SC wins board contest → upgrade scenario weights, possible 1pp marginal add if PWER recovers above 20%.
- If SC loses → time-stop trim 6% → 3% within 30 days.
---
#### Per-Position Diagnostic — full book sweep
(For positions with no new signal or material price move within ±3% today, abbreviated to one line. Material moves and active monitor positions get the full block.)
**L1 — High-Conviction Binary Catalysts**
- **9684 Square Enix · 12.0% NAV · HOLD AT CAP.** Board recommendation vs 3D nominees confirmed. PWER 38.4% intact. T-38d to AGM. No action. Post-AGM time-stop set.
- **7752 Ricoh · 8.0% NAV · HOLD.** Effissimo +1.73pt today; concealment-adjusted WAC unlocks position from "blocked" to "thin margin" but forward PWER +15.6% still below 20% gate. No add. Watch 30% threshold.
- **6516 Sanyo Denki · 6.0% NAV · HOLD AT DPS-MODIFIED CAP.** SC 15% threshold crossed; M1 sub-tag transition fired; no size change.
**L2 — Near-Term Events**
- **3401 Teijin · 5.5% NAV · HOLD.** No new filing. Px ¥1,689 (May 19 close), Effissimo WAC ¥1,350 = +25% above WAC; concealment scan from Apr 14 filing was concealment band 0 (clean). WAC inversion +25% > +15% ceiling per memory rule #8 → ADD blocked. May 7 earnings already digested. Next checkpoint: Effissimo 20% threshold.
- **7740 Tamron · 3.5% NAV · HOLD.** Effissimo monthly cadence intact; px ¥4,380 vs WAC ¥3,950 = +11% above WAC, inside ceiling. PWER 24% holds. No action.
- **6262 Pegasus · 3.0% NAV · FLAG L2 CAP.** v10.1 Concession-Captured warning active. Px ¥855 vs Be Brave WAC ¥793 = +7.8%, inside ceiling. T-X days to May 27 earnings (verify via IR calendar primary per memory rule #21). Tripwire: any further company defensive action within 30 days of next threshold crossing → downgrade L2 → L3.
- **4246 DaikyoNishikawa · 3.0% NAV · HOLD.** Px ¥648 vs MI2/Takateru WAC ¥841 = **−23% BELOW WAC** — cleanest entry zone in book. PWER 35.5%. Hold position; do not chase >¥841. Watch for City Index Eleventh separate filing or aggregate Murakami family crossing 7%+ before May earnings.
- **4071 Plus Alpha Consulting · 3.0% NAV · HOLD.** Oasis 8.02%; founder-led SaaS. X-Bull probability capped at 10% (memory rule #28). PWER 33% holds. May 14 earnings already digested per IR calendar primary (memory rule #21).
- **6594 Nidec · 2.5% NAV · HOLD (special).** Oasis governance-crisis style; SESC overhang; hard 6% cap. PWER 17% below gate but position retained as special-handling (special alert / delisting bear case). No action.
**L3 — Compounders & Patient Engagement**
- **6914 Optex Group · 5.0% NAV · HOLD.** Px ¥2,885 vs GMO WAC ¥2,629 = +9.7% above WAC. Tier Q exempt from G1/G2/G3; quality compounder thesis. No action.
- **3182 Oisix · 5.0% NAV · HOLD.** Px ¥1,428 vs GMO WAC ¥1,576 = −9.4% BELOW WAC. GMO underwater + still adding = max-conviction signal per `crmc-archetype-rules.md`. No action.
- **4613 Kansai Paint · 3.0% NAV · HOLD.** Silchester 5.05%; px below WAC. Long-only patient. PWER 35% holds.
- **9882 Yellow Hat · 3.0% NAV · HOLD (Realized Mode 1 carry).** M1-Internal-Carry tag active. Px ¥1,465 vs SC WAC ¥1,378 = +6.3% above WAC, inside ceiling. Float retirement velocity 11.4% trailing 12mo holding. No action.
- **4493 Cyber Security Cloud · 2.5% NAV · BUY (verify SilverCape filings).** Px ¥1,515 vs SilverCape WAC ¥1,735 = **−12.7% BELOW WAC** — clean entry. PWER 46.7%. Standing rule: only deploy beyond 2.5% on second institutional 5%+ filer. No new co-filer today.
- **8368 Hyakugo Bank · 2.0% NAV · HOLD.** Ariake long-only; TSE PBR mandate exposure. PWER 21% just above gate. No action.
**L4-ARB**
- **2972 Sankei REIT · 1.5% NAV · HOLD.** Annualized PWER +85% to May 18 TOB deadline (already passed in this scenario — verify; if extended again, re-stamp annualized PWER on new deadline). Bear floor reservation ¥110K explicit. No new filing today.
**L3-WATCH**
- **3941 Rengo · 0.0% NAV · WATCH.** Murakami group ~5% combined; ATRA present in joint-holder section = canonical bullish setup per memory rule #11. Trigger: ATRA stake >2% individual, or aggregate crosses 8%.
---
#### Asymmetry & Risk Panel
**Highest-conviction asymmetry today:** DaikyoNishikawa (4246) at −23.9% below WAC with PWER 35.5% and T-X days to May 11 earnings. Already at 3% NAV; capacity for 1pp marginal add if Murakami aggregate crosses 7% before earnings.
**Highest-risk position today:** Sanyo Denki (6516) — board contest binary at T-38 days, +49% above SC WAC means follower has no co-investment cushion, and a Bear-case AGM defeat would drive ~−20%. Hard-stopped at SC <13% (no trigger today) but the position is highly sensitive to AGM outcome.
**Concentration check:**
- Effissimo cluster: Ricoh 8.0 + Teijin 5.5 + Tamron 3.5 = **17.0%** — within 25% per-activist cap (memory rule #7).
- GMO-Usonian cluster: Optex 5.0 + Oisix 5.0 = **10.0%** — within cap; Drew Edwards single-PM exposure 10% (below 15% guidance, edge case 8.5).
- Murakami cluster (incl. DaikyoNishikawa 3.0 + Sankei REIT 1.5 + Rengo 0) = **4.5%** — well within cap.
- Strategic Capital cluster: Sanyo Denki 6.0 + Yellow Hat 3.0 = **9.0%** — within cap.
- June AGM event cluster (Square Enix + Sanyo Denki + Pegasus + Plus Alpha + Yellow Hat + Oasis/Dalton/AVI overlaps): **30.0%** — within 50% per-event-cluster cap.
**Portfolio weighted-average PWER:** recomputed against today's updated reads = **27.0%** (was 27.4% yesterday; small compression on Ricoh PWER refresh). Above 25% portfolio target.
**Cash buffer:** 4.0% — at the lower end of acceptable 5–10% v11 buffer band. **Watch:** if Yellow Hat or Sanyo Denki delivers AGM win, consider trimming Foster Electric or Daito Trust residual to lift buffer toward 7%.
#### Calendar — next 7 days
| Date | Event | Position(s) affected |
|---|---|---|
| May 21 | Bunka Shutter ¥3B buyback program start | 5930 (watch) |
| May 22 | DaikyoNishikawa Q4 earnings (IR calendar primary verified) | 4246 |
| May 27 | Pegasus Q4 earnings (verify) | 6262 |
| Jun 02 | Effissimo expected next 変更報告書 window | 7752, 3401, 7740 |
| Jun 27 | Square Enix 74th AGM — 3D nominees binary | 9684 |
| Jun 27 | Sanyo Denki AGM — SC board contest binary | 6516 |
#### Open questions / tripwires for the desk
1. **Ricoh:** does Effissimo cross 30% in the next 30 days? If yes, X-Bull scenario weight rerates and PWER recovers above gate.
2. **Sanyo Denki:** SC files a 2nd public letter (post-campaign-site)? Would confirm full M1-External-Binary transition and unlock L1 ceiling beyond DPS-modified 6%.
3. **DaikyoNishikawa:** Murakami aggregate >7%? Confirms accelerating stage-2 transition; 1pp add eligible at current price.
4. **Sankei REIT:** TOB deadline pass/extend? Annualized PWER must be re-stamped on new deadline if extended.
---
*End of sweep memo. Logged to `sweep-log/2026-05-20-sweep.md`. Dashboard increment pending verdict-change on Ricoh (concealment-band reclassification noted but no action change).*
---
