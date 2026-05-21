<!-- Asuka v8-v11 framework reference - migration handoff Section 5 - populated 2026-05-21, verbatim. -->

## SECTION 5 — FRAMEWORKS, FORMULAS & THRESHOLDS
This section consolidates every framework, scoring system, formula, tier definition, and numeric threshold the reasoning layer relies on. Every term and acronym is defined.
### 5.1 Glossary of acronyms and terms
- **AGM** — Annual General Meeting; Japan AGM season concentrates in June (~80% of TSE-listed companies).
- **AGM record date** — date determining which shareholders are entitled to vote at the AGM; typically early April for June AGM.
- **ADV** — Average Daily Volume.
- **BVPS** — Book Value Per Share.
- **CRMC** — four-lens decomposition: Category × Reservation × Mode × Catalyst.
- **CWP** — Catalyst-Window Patience; inside binary window (typically 60d pre-binary), only hard stops fire.
- **DOE** — Dividend on Equity; the demand encoded in DOE5% Co. Ltd.'s name (target every listed company should deliver DOE ≥5%).
- **DPS modifier** — Distribution-Position Sizing modifier (v10.2); scales sizing based on principal activist's current realized HPR bucket position.
- **EDINET** — Electronic Disclosure for Investors' NETwork; Japan's equivalent of SEC EDGAR.
- **EGM** — Extraordinary General Meeting.
- **FDR** — Fast Defensive Response (v10.1 Gate 2 sub-rule).
- **HPR** — Holding Period Return.
- **IRR** — Internal Rate of Return.
- **JGB** — Japanese Government Bond.
- **JTSB** — Japan Trustee Services Bank.
- **MBO** — Management Buyout.
- **MoS** — Margin of Safety (dual-lens: Earn-MoS + Asset-MoS).
- **MOIC** — Multiple On Invested Capital.
- **MTP** — Medium-Term Plan.
- **NAVF** — Nippon Active Value Fund (Dalton dual vehicle).
- **NIIP** — Net International Investment Position.
- **NIRP** — Negative Interest Rate Policy.
- **NISA** — Nippon Individual Savings Account.
- **PB** — Prime Broker.
- **PBR** — Price-to-Book Ratio.
- **PIT** — Point In Time.
- **PWER** — Probability-Weighted Expected Return.
- **PW-IRR** — Probability-Weighted IRR (PWER annualised).
- **SOTP** — Sum Of The Parts.
- **TC** — Transaction Cost.
- **TCFD** — Task Force on Climate-Related Financial Disclosures.
- **TDNet** — Timely Disclosure Network (TSE timely disclosures, 適時開示).
- **TOB** — Takeover Bid (tender offer).
- **ToSTNeT** — Tokyo Stock Exchange Trading Network System (off-market block trading facility); ToSTNeT-1/2/3 for cross-shareholder unwinds, repurchases, bilateral blocks.
- **TSE** — Tokyo Stock Exchange.
- **VWAP** — Volume-Weighted Average Price.
- **WAC** — Weighted Average Cost (basis).
- **XBRL** — eXtensible Business Reporting Language (EDINET filing format).
- **大量保有報告書** (Tairyou Hoyuu Houkokusho) — Large Shareholding Report; initial 5%+ disclosure.
- **変更報告書** (Henkou Houkokusho) — Change Report; subsequent ±1pp moves or joint-holder composition / purpose / address changes.
- **臨時報告書** (Rinji Houkokusho) — Extraordinary Report; AGM voting results, shareholder proposals.
- **共同保有者** (Kyoudou Hoyuusha) — Joint Holders.
- **重要提案行為等** (Juuyou Teian Koui Tou) — Important Proposal Activities; explicit activist intent.
- **純投資** (Junn Toushi) — Pure Investment; Tier P boilerplate that does NOT mean passive.
- **政策保有株式** (Seisaku Hoyuu Kabushiki) — Cross-shareholdings / policy holdings.
- **株主提案** (Kabunushi Teian) — Shareholder Proposal.
- **適時開示** (Tekiji Kaiji) — Timely Disclosure (TDNet).
- **定款** (Teikan) — Articles of Incorporation.
- **取得対価** (Shutoku Taika) — Acquisition Consideration.
- **取得日** (Shutoku-bi) — Acquisition Date.
- **取得資金** (Shutoku Shikin) — Acquisition Funds.
- **法人番号** (Houjin Bangou) — Corporate Number (国税庁 registry).
- **有報** (Yuuhou) — short for 有価証券報告書, the annual securities report.
- **自己株式取得** (Jiko Kabushiki Shutoku) — Treasury Stock Acquisition (buyback).
### 5.2 The five-tier CRMC archetype framework
- **Tier 1 — Hard activists** (default deployment): Effissimo+SMT, Murakami network, Oasis, 3D, Dalton+NAVF (only when paired), Strategic Capital+UGS Sunshine, LIM, Be Brave, SilverCape, Palliser, Elliott.
- **Tier 1.5 — Campaign-runner long-only**: Silchester (post-Bank of Kyoto).
- **Tier 2 engaged long-only / quality compounder**: GMO-Usonian, Ariake, MIRI, AVI Japan, Arcus, Zennor, Kaname Capital, Hibiki Path.
- **Tier 2 domestic activists**: Ueshima/DOE5%/Naturali, City Index Eleventh (umbrella'd separately), UGS Asset Management, Be Brave.
- **Tier 3 — Watch-only**: unconfirmed family offices, ambiguous foreign investors, sub-5% disclosures from unknown entities.
### 5.3 The four-archetype exit-mechanic taxonomy (v10)
- **Tier R — Capital-return extractors** (TOB / self-tender / large buyback; HIGH principal-follower divergence): Murakami, Be Brave, Ueshima/DOE5%, CIE, UGS.
- **Tier P — Patient blockers** (multi-year re-rating; LOW divergence): Effissimo+SMT, Silchester, Ariake, MIRI, Kaname, Zennor.
- **Tier E — Engagement campaigners** (operational reform, board contest, AGM proposals; MEDIUM divergence): 3D, Oasis, Strategic Capital, LIM, AVI Japan, Palliser, Dalton+NAVF.
- **Tier Q — Long-only quality** (no "exit event"; MINIMAL divergence): GMO-Usonian, Silchester quality sleeve, Arcus, Ariake quality sleeve.
### 5.4 The four-tier filing-language taxonomy (Tier P/R/E/C)
- **Tier P — Passive boilerplate (NEUTRAL):** 純投資, ポートフォリオ投資. Does NOT mean passive — archetype-level behaviour overrides language.
- **Tier R — Activist-reserve (ELEVATED):** 投資及び状況に応じて重要提案行為等を行うこと; 純投資・重要提案行為等を行うため (canonical Murakami/Effissimo); 経営陣への助言; エンゲージメント / スチュワードシップ.
- **Tier E — Explicitly activist (HIGH):** 重要提案行為等 (standalone); 株主還元の充実を求める; 経営への関与.
- **Tier C — Escalation / control (MAXIMUM):** 支配権の取得; 取締役選任; specific text describing board nominees / restructuring requests.
**Transition rule:** purpose-tier upgrade between filings is the highest-signal event in the framework — empirically precedes public demands by 4-8 weeks. Fund the upgrade trade out of the lowest-PWER cluster member.
### 5.5 The 17-tag strategic-source taxonomy
Single tags (10): **IP** (intellectual property / brand / patent moat), **RE** (real estate), **SOTP** (sum-of-the-parts unlock), **CASH** (capital return; balance sheet cash deployment), **FWD** (forward earnings inflection / margin recovery), **TOB** (takeover bid optionality), **GOV** (governance reform; board composition; comp), **SUB** (parent-subsidiary sub-book), **CYC** (cyclical recovery), **ARB** (merger arb spread).
Hybrid tags (7, added post-Musashi May 2026): **SUB+TOB** (parent-sub sub-book — Musashi 7220, DaikyoNishikawa 4246); **CASH+SUB** (Tayca, Fujikura); **GOV+CASH** (Bank of Kyoto, regional banks); **IP+GOV** (TOTO Advanced Ceramics); **RE+SUB** (Kokuyo, Sankei); **TOB+ARB** (Sankei v2); **SOTP+CASH** (Ricoh, Teijin); **FWD+IP**.
Each filing = PRIMARY+SECONDARY tag. Re-tag on data refresh.
### 5.6 The five Gates of v10/v10.1/v10.2 (sequenced)
**G1 — Pre-existing Concession Test.** Did target pre-empt the activist? (Tier R: payout ratio ≥80% prior FY; DOE/dividend floor disclosed; capital policy ≤24mo pre-filing; buyback ≤6mo pre-filing.) 3+ points + no G5 second leg → REJECT; 2 points → DOWNGRADE one tier; 0-1 → proceed.
**G1.5 — Realized Mode 1 Status Flag (v10.2).** Did target deliver to activist after entry? (a) MTP payout ≥40% or TPR ≥80% cumulative over ≥3 FY; (b) ≥5% float retired TTM or ≥10% cumulative since filing; (c) principal accumulation paused (no new ≥1pt 変更報告書 in 6mo, no public letter/proposal/campaign-site in same window). All three must fire concurrently. Fires → NOT REJECT but L3 ceiling cap; co-investment edge = 0; WAC cross-check binding; DPS modifier mandatory; M1-Internal-Carry sub-tag.
**G2 — Threshold Progress Test** with Stall Trigger AND v10.1 Fast Defensive Response sub-rule.
Archetype-specific thresholds:
- Tier R Murakami/Be Brave/Ueshima: initial 5%; 10% (DOE-demand floor); 15% (Mode 2 force); stall window 90 days
- Tier R UGS/SC partnership: initial 5%; 10%; TOB-execution any size; stall window 60 days (faster cycle)
- Tier P Effissimo/SMT: initial 5-8%; 15% (Mode 1); 20% (Mode 2); 25% (Mode 3 anti-MBO veto); stall window 180 days
- Tier P Silchester/Ariake/MIRI: initial 5%; 8-12% (no veto; size signals conviction); stall window 365 days
- Tier E 3D/Oasis: initial 5-7%; letter cadence > stake size; 1+ public letter within 90d, board nominees within 180d; stall window 90 days from initial
- Tier E Dalton+NAVF: initial 5% combined; 10% combined; 15% combined (near-veto ordinary); stall window 180 days
- Tier E Palliser/Kaname: initial 3-5%; public Value Enhancement Plan letter within 120d; AGM proposals within 180d; stall window 120 days
- Tier Q GMO-Usonian/Silchester quality: initial 5%; gate does not apply
Stall Trigger fires (REJECT or DOWNGRADE) only when all three conditions present: stake stalls below threshold for stall window AND target announces defensive action in same window AND no public letter or proposal from principal.
**Fast Defensive Response sub-rule (v10.1):** target announces capital policy upgrade / ToSTNeT-3 block / public TOB / dividend acceleration / buyback / strategic review timed within 30 calendar days of T0 OR within 30 days of any subsequent threshold crossing → fires Concession-Captured warning. Combined verdict per matrix:
| Gate 2 fires | G5 second legs | Verdict |
|---|---|---|
| Stall fires | 0 legs | REJECT |
| Stall fires | 1 weak leg | DOWNGRADE two tiers |
| Stall fires | 2+ strong legs | DOWNGRADE one tier, L3 cap, monitor closely |
| FDR fires | 0 legs | REJECT |
| FDR fires | 1 weak leg | DOWNGRADE two tiers |
| FDR fires | 2+ strong legs | L3 conditional cap with explicit tripwires |
| Both fire | any | Take more conservative |
**G3 — Internal Rotation Penalty (with directionality test).** Compute `delta_fresh_capital = delta_aggregate_stake − delta_from_reshuffle`. <0.5pp + reshuffle present → DOWNGRADE one tier (Piolax Oct 2024 fits: CIT→Reno full transfer 4.68pp + market adds ~0.3pp = 0.32pp fresh, sub-0.5). ≥0.5pp + reshuffle present → no penalty (Sankei REIT Apr 2026: aggregate +2.16pp with reshuffle <2pp = clear fresh deployment). High CR numbers (15+) with new individual vehicle 5%+ → fires regardless of math.
**G4 — Residual Liquidity Test.** Mandatory in any Bull/X-Bull scenario terminating in liquidity event. Compute blended return:
```
acceptance_ratio = min(tender_size_shares / tender_supply, 1.0)
follower_tendered = follower_stake × acceptance_ratio
follower_residual = follower_stake × (1 - acceptance_ratio)
blended_return = (acceptance_ratio × return_tendered) + ((1-acceptance_ratio) × return_residual)
```
Acceptance ratio defaults:
- Self-tender/TOB small-cap (<¥100B) with known activist on register: 45-60%
- Self-tender/TOB mid-cap (¥100-500B): 60-75%
- Self-tender/TOB large-cap (>¥500B): 75-90%
- Third-party MBO at premium: 100%
- Open-market buyback: 0% follower acceptance
Post-event price defaults:
- Self-tender funded buyback: −10 to −25% from tender price
- Third-party MBO succeeded: tender price (delisted)
- Third-party MBO failed: −15 to −40% from pre-bid level
- Open-market buyback: +3 to +8% above pre-announcement
**Trigger:** `blended_return < (return_tendered × 0.6)` → flag setup as TOB-pro-rata trapped. Reject or downgrade two tiers.
**G5 — Second-Leg Requirement.** Taxonomy: SOTP/spin-off; governance overhaul; strategic transaction; cross-shareholding unwind; parent-subsidiary resolution; operational reform; regulatory/TSE governance. Zero candidates with required evidence → REJECT; one weak → L3 maximum with upgrade tripwire; two+ → standard sizing per archetype.
### 5.7 The eleven concealment techniques (C1-C11) — v10.3
(See Section 3.12 above for the full table; severity weights: C1=3, C2=2, C3=1/0, C4=2, C5=1, C6=2, C7=1, C8=1, C9=1, C10=3, C11=2. Bands: 0 clean / 1-2 low-medium / 3-4 material / 5+ severe.)
### 5.8 Position-sizing hard rules
- Single position cap: **12% NAV** (L1 only)
- Per-activist cluster cap: **25% NAV**
- Per-event cluster cap: **50% NAV** (e.g., June AGM cluster)
- Mega-cap activist cluster cap: **6% NAV**
- Mega-cap single position cap: **3% NAV** (>$10B market cap)
- Position count target: **14-18**
- Cash target: **0%** — rotated not accumulated
- PWER entry threshold: **20% absolute** (or 25% annualised for L4)
- New positions must be PWER-accretive against displaced position
- Asymmetry gate: ≥1.5 minimum, ≥2.5 standard sizing, ≥4.0 convex premium permitted
- Harvest review trigger: PWER <15%
- Bear-case CVaR floor: 5th percentile must be no worse than −40% (L1) / −50% (L2) / −60% (L3) of current price; below → downgrade one layer
### 5.9 The Layer Framework
| Layer | Description | Sizing | Target weight | Action bias |
|---|---|---|---|---|
| **L1** | High-conviction binary catalyst <6mo, confirmed activist stake, imminent proposal | 7-12% per position | 50-60% pre-AGM, 20-25% post-AGM | ADD on dips, HOLD at full, TRIM post-resolution |
| **L2** | New activist <6mo OR 3-9mo catalyst horizon | 3-5% | 10-15% | Build through escalation tripwires |
| **L3** | Quality compounder + engaged long-only; 12-24mo | 2-8% | 30-40% | Add on fundamental confirmation, harvest on multiple expansion |
| **L4** | Merger-arb sleeve (long-only mandate; no leverage; no short-hedging) | 1-3% | <10% | Annualised PWER ≥25%; binary days-weeks |
### 5.10 The PWER formula stack (canonical, full math)
```
PWER         = Σᵢ (Pᵢ × Rᵢ)
Rᵢ           = (Targetᵢ − Current)/Current + Carryᵢ
Carryᵢ       = (div_yield + buyback_yield) × (Monthsᵢ/12)
IRRᵢ         = (1 + Rᵢ)^(12/Monthsᵢ) − 1
PW-IRR       = Σᵢ (Pᵢ × IRRᵢ)
Asymmetry    = (P_bull × R_bull + P_xb × R_xb) / |P_bear × R_bear|
Gates:
  Entry:     PWER ≥ 20% absolute (or 20% annualised for dated binary <12mo)
             AND Asymmetry ≥ 1.5
             AND clear ≥2 of the 4 verdict-engine lenses
             AND True-WAC cross-check passes (px ≤ +15% single, ≤ +10% dual or band≥1)
             AND Five Gates clear (v10) AND no Stall / FDR REJECT (v10.1) AND no Gate 1.5 misclassification (v10.2) AND no concealment band 5+ (v10.3)
  Harvest:   PWER < 15% OR Asymmetry < 1.2 OR composite gate FAIL OR ANNUALIZED ≥36mo
  Override:  Anchor reduction filing, velocity trigger (50%+ single month or 2x+ <18mo), regime break, data quarantine, pre-mortem failure (no 5 plausible thesis killers)
```
### 5.11 Default probability anchors by archetype (v9 / v9.1 / pwer-methodology Appendix B)
| Archetype | P(Bear) | P(Base) | P(Bull) | P(Extreme Bull) | Median HPR | Mean HPR | Top-Q | Base mult of WAC |
|---|---|---|---|---|---|---|---|---|
| Effissimo Mode 2 (15-25% band) | 20% | 40% | 25% | 15% | +46% | +63% | ~+110% | 1.46× |
| Effissimo Mode 1 (5-15%) | 15% | 50% | 25% | 10% | +77% | +93% | (top 25%) | 1.77× |
| Effissimo Mode 3 (25%+) | — | — | — | — | +164% | +164% | n=2 | 2.64× |
| 3D (5-15%) | 25% | 40% | 25% | 10% | +26% | +57% | +143% | 1.26× |
| Dalton public-demand (5-15%) | 25% | 40% | 25% | 10% | +15% | +30% | +38% | 1.15× |
| Murakami Stage 1-3 | 25% | 35% | 25% | 15% | — | +20.4% (n=92) | — | — |
| Strategic Capital (5-15%) | 30% | 45% | 20% | 5% | +56% | +65% | +91% | 1.56× |
| Silchester (5-15%) | 25% | 50% | 20% | 5% | +11% | +16% | +42% | 1.11× |
| GMO-Usonian (5-15%) | 25% | 50% | 22% | 3% | +23% | +22% | +37% | 1.23× |
| Ariake (5-15%) | 25% | 50% | 20% | 5% | +49% | +66% | +70% | 1.49× |
| LIM (all) | — | — | — | — | +28% | — | +51% | 1.28× |
| MIRI (5-15%) | — | — | — | — | +22% | +42% | +55% | 1.22× |
| Palliser / AVI engagement | 30% | 40% | 25% | 5% | — | — | — | — |
| L4 Merger arb post-TOB | 15% | 0% | 75% | 10% | — | — | — | — |
### 5.12 V9.1 empirical state distributions (5 buckets)
Effissimo 15-25% band (n=7) — for Ricoh, Teijin, Tamron:
- fail (<+10%): 0.00 (zero observed failures)
- modest (+10-40%): 0.43 (+26.0% within bucket avg)
- solid (+40-80%): 0.29 (+46.7% within)
- strong (+80-150%): 0.14 (+103.8% within)
- home_run (>+150%): 0.14 (+167.5% within)
3D 5-25% band (n=10) — for Square Enix (bimodal distribution):
- fail: 0.30 (+2.4% within)
- modest: 0.40 (+24.5% within)
- solid: 0.00 (none)
- strong: 0.10 (+143.2% within)
- home_run: 0.20 (+158.4% within)
Strategic Capital 5-25% band (n=30) — for Sanyo Denki, Yellow Hat:
- fail: 0.17 (−4.5% within)
- modest: 0.17 (+16.8% within)
- solid: 0.30 (+56.6% within)
- strong: 0.27 (+107.4% within)
- home_run: 0.10 (+207.4% within)
### 5.13 The Distribution-Position Sizing (DPS) Modifier table — v10.2
| Principal current realized HPR bucket | Sizing modifier |
|---|---|
| Below bucket-1 (<+10%) — starter vintage | **1.5× standard layer sizing** (best vintage, full edge) |
| Bucket-2 (+10% to +40%) — modest | **1.0× standard** (median expected, standard edge) |
| Bucket-3 (+40% to +80%) — solid | **0.5× standard, L3 max** (median outcome reached, residual edge only) |
| Bucket-4 (+80% to +150%) — strong | **0.25× standard, L3 starter only, hard 1.5% NAV cap** |
| Bucket-5 (>+150%) — home-run | **Stand down or watch only** (mean-reversion risk dominates) |
### 5.14 The Principal-Follower Divergence Haircut — v10 §3
| Archetype | Mean haircut | Top-decile haircut |
|---|---|---|
| Tier R | −5pp | −10pp |
| Tier P | −2pp | −5pp |
| Tier E | −3pp | −7pp |
| Tier Q | 0pp | −2pp |
Applied to base-rate priors BEFORE PM judgment overlay. PM overlay can override but must document override explicitly in scenario notes.
### 5.15 EDINET filing types & alert priority
| docTypeCode | JP | EN | Trigger |
|---|---|---|---|
| 350 | 大量保有報告書 | Large Shareholding Report — initial | Stake first crosses 5.00% |
| 360 | 大量保有報告書（訂正） | Large Shareholding Amendment | Correction to 350 |
| 370 | 変更報告書 | Change Report | Subsequent ±1pp or joint-holder/purpose/address change |
| 380 | 変更報告書（訂正） | Change Report Amendment | Correction to 370 |
| 180 | 臨時報告書 | Extraordinary Report | AGM voting results, shareholder proposals |
Alert severity: **HIGH** — initial 5% on in-universe; Tier C transition; threshold ≥33.4%; Stage 5 confirmation. **MEDIUM** — stake change >1pp; transition R→E; defender Level 4-5 response. **LOW** — amendment no ratio change; address/name correction; Tier P on non-portfolio.
### 5.16 Filing-stake threshold ladder
| Threshold | Significance | Empirical hit rate |
|---|---|---|
| 5% | Initial filing (anchor) | 100% by definition |
| 10% | Confirmation of accumulation intent; Type R credible-threat floor | ~52% reach |
| 15% | Effissimo Mode 1→2 transition zone; near-veto on ordinary resolutions | ~28% |
| 20% | Forced strategic review territory (Mode 2) | ~14% |
| 33.4% | Special resolution blocking minority (de facto veto) | ~5% |
| 50% | Effective control | <2% |
### 5.17 Liquidity discount heuristic (v9.1)
```
days_to_exit = shares_held / (ADV × 0.25)
discount_pct = min(15, days_to_exit / 30)
realized_value = expected_value × (1 − discount_pct/100)
```
25% of ADV = realistic absorption rate; 1pp discount per 30 days reflects observed Toshiba/UACJ/Kawasaki Kisen exit patterns; 15% cap reflects strategic exit fallback (TOB, secondary, block).
### 5.18 Two-observable-signal rule (PWER §3)
To shift Bull probability +5pp: two Tier-A signals or four Tier-B signals required. Extreme Bull +at all: ≥1 Tier-A specifically suggestive of tender path. Bear-side: single Tier-A acceptable if unambiguously negative.
Tier A signals (each = 1):
- EDINET 大量保有/変更報告書 ≥1pp stake change
- TDNet 適時開示 of buyback, dividend hike, structural disposal, governance reform
- Public letter or campaign material
- AGM voting result with shareholder-proposal support ≥30%
- Cross-shareholder reduction filing on same target
- New activist filing on same name (multi-activist convergence)
- Sell-side rating upgrade citing value-source activist is targeting
Tier B signals (two = one Tier A):
- Earnings beat/miss vs consensus by >5%
- Yahoo Finance Japan board / kabupro chatter inflection
- Bloomberg news flow on activist or company >3 articles in 7 days
- Sector regime data (JPY/USD shock for export-sensitive names)
### 5.19 Hidden-Tech five-gate screen (pre-activist L2)
(1) PBR ≤1.3x AND 5-year return ≥40pp below TOPIX;
(2) disclosed segment in advanced ceramics / semicon materials / AI infra / specialty films / EV-battery / precision motors;
(3) segment ≥25% OP (≥40% = high conviction);
(4) Tier-1 trigger ≤90 days (sell-side upgrade citing segment, CMD, buyback ≥3% float, cross-shareholding unwind);
(5) cost-of-capital mismatch.
Scoring: 4/5 = 3% L2; 5/5 = 4-5%; +activist = L1 5-7%. No WAC gate; floor = legacy business at sector PER.
### 5.20 PAH-A 5-gate pre-activist screen (STOCK v11 May 2026)
(1) PBR ≤1 AND 5-year underperf ≥40pp;
(2) hybrid strategic source tag;
(3) hidden segment ≥25% OP;
(4) ROE ≤8% AND payout ≤30% AND net-cash ≥25% AND no buyback;
(5) catalyst-arrival probability.
5/5 = 2.5% NAV starter; 4/5 = 1.5% NAV starter. Graduates to L1/L2 on Tier 1 5%+ filing. Musashi 7220 canonical (5/5 Dec 2025 → GMO May 2026 +60%).
### 5.21 The Activist-as-Stake-Confirmation Rule (post-Musashi May 2026)
When L4 re-tag fires non-canonical strategic source, activist downgrades from thesis driver to institutional validation of stake. PWER ceiling adjusts:
- Canonical archetype-fit: filer's Bloomberg ACTV mean × 1.5
- Re-tagged with L2+L3 support: sector/structural mean (typically 25-35%)
- Re-tagged WITHOUT L2+L3 support: REJECT stands
Musashi 7220 GMO filing = SUB+TOB re-tag with macro+fundamentals support → BUY at L3 starter at WAC.
### 5.22 The Dual-Lens MoS framework
```
Earn-MoS  = (IV − Px) / IV   where IV = 5-year OP × 0.7 / 0.08
Asset-MoS = (1 − PBR) × 100
```
Both capped −100%. Both measure ACCOUNTING value. Activist edge = gap between accounting and STRATEGIC value neither column sees. Both negative ≠ bad company; cushion lives in strategic source. **Earn-MoS systematically negative on activist targets BY DESIGN — earnings suppression IS thesis.**
### 5.23 Three-stage exit framework
1. **Partial harvest at catalyst resolution (50-60%).** AGM passes, MBO bid announced, capital return committed → harvest majority immediately.
2. **Trail-stop the residual.** Remaining 40-50% held against post-resolution drift; trim on PWER <15% or thesis dilution.
3. **Full exit on activist signal reversal.** Principal files stake reduction → exit fully. **Selling against accumulating activist below cost is most expensive mistake the framework can make** (Shift Inc. = textbook positive case; Exedy = textbook timing of stage-5 exit).
### 5.24 Override conditions (PWER §8)
Five conditions force override or suspension:
1. **Anchor exit signal** — first reduction filing → downgrade one full layer; second reduction → full exit. Murakami Stage 5: all five conditions.
2. **Velocity trigger** — 50%+ in single month or 2x+ in <18mo → trim one full layer minimum (LIM Kitagawa Mar 2026 canonical).
3. **Regime break** — JPY/USD breaching cycle extremes, TSE policy reversal, major Japan banking event, sector shock >30% of book → suspend new initiations 5 trading days; existing positions reviewed.
4. **Data quarantine** — stored PWER inputs conflict with primary EDINET or external price → quarantine (⛔ red); reset probabilities, re-derive. Trigger: stake_confirmation tilt without last_filing.date; calibrated_at_price >5% off verified spot.
5. **Pre-mortem failure** — thesis without ≥5 plausible thesis killers explicitly enumerated and probability-weighted does NOT pass commit.
### 5.25 Refresh discipline rule
- Spot price: ≤2 trading days (daily sweep) / ≤3 trading days (general)
- EDINET scan: ≤7 days
- News scan: ≤3 days (daily sweep) / ≤7 days (general)
- `action_verified_date = today` stamp required before action signal locks
Three sources matching value + same old stamp = ONE cached snapshot, NOT 3 confirmations. JP equities prefer kabutan.jp intraday or Yahoo Finance Japan with today's stamp. Stamp >2 trading days old = STALE, re-search. Tag quoted price with source date.
### 5.26 Single-source-of-truth hierarchy
1. EDINET XBRL (filer's own filing) — supersedes everything
2. Pipeline `current_state.json` — authoritative for in-book stakes
3. Bloomberg ACTV / FLNG — secondary verification
4. kabupro.jp / irbank.net / Yahoo Finance JP — fallback only, stamped with EDINET doc ID
5. Sell-side / news aggregators — colour, never primary signal
---
