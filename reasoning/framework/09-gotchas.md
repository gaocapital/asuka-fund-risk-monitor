<!-- Asuka v8-v11 framework reference - migration handoff Section 10 - populated 2026-05-21, verbatim. -->

## SECTION 10 — IMPLICIT KNOWLEDGE & GOTCHAS
**⚠ INFERRED CONTENT — NOT FORMAL SPEC.** This section reconstructs implicit operating preferences from the embedded `(memory)`, `CORRECTION`, and `memory rule` annotations across the knowledge base, plus what is implied between the lines of custom instructions. Where I genuinely cannot recover something without the lost chat history, it is flagged as a known gap.
### 10.1 Tone & format preferences (inferred from output patterns)
- **No hedging, no disclaimers, no "consult a financial advisor."** Yongjie operates the fund himself; he is the audience. Treat him as a peer PM, not a retail user. The standing instruction "institutional PM standard — no hedging, direct conviction calls" is binding even on borderline positions.
- **Verdicts always come first.** The first line of any position memo should be the action (BUY/HOLD/TRIM/EXIT/WATCH) and the layer assignment, then the rationale. Yongjie scans for the verdict; the analysis is justification, not preamble.
- **Tables over prose for quantitative content.** Scenario tables, gate tables, freshness sweeps — always in markdown tables. Avoid burying numbers in sentences.
- **Use ¥ symbol, not JPY.** Always with the ticker code in `NNNN JP Equity` or `NNNN.T` format on first reference; bare ticker after.
- **Bullet structure for diagnostics, prose for synthesis.** The sweep memo top-of-page summary is prose; the per-position diagnostic blocks are structured. Mixing the two confuses the read.
- **Explicit "do not skip" headers when refusing to refresh stale data.** `⚠ NEEDS REFRESH`, `STALE_INPUTS`, `DATA_QUARANTINE` — Yongjie wants these surfaced loudly, not hidden in footnotes. The discipline is *honest about what is not known*, not pretend-precision.
- **Catalysts are dated, not "near-term."** Always cite the actual date and the IR-calendar source. "May 12 earnings" not "upcoming earnings." Memory rule #21 is taken seriously.
- **Japanese terminology where it matters.** 大量保有報告書, 変更報告書, 共同保有者, 純投資, 重要提案行為等, 適時開示, 立会外取引, 招集通知, 有価証券報告書, 決算短信 — these terms have specific meanings and the English glosses can drift. Use the Japanese in headers and on first reference, then the English in body.
- **Acronyms expected on first use:** PWER, WAC, ADV, AGM, MTP/MTMP, DOE, ROE, PBR, ROIC, SOTP, MBO, TOB, FYE, NAV, EDINET, TDNet. After that, bare.
### 10.2 Decision-making cadence (inferred from how rebalances actually happened)
- **Rebalances are event-driven, not periodic.** Yongjie does not run a Monday-morning rebalance regardless of news. He rebalances when (a) a new EDINET filing materially changes a position; (b) a price gap creates a forward-PWER reset; (c) an AGM / earnings binary resolves. Monthly check-ins are checks, not prompts.
- **Capital deployment is "trim-to-fund," explicit and named.** "Trim Alfresa 2% → 0% and Daito Trust 2% → 1% → fund Yellow Hat 3%." Always name the source of capital. Do not leave a rebalance as "free up capital somewhere."
- **Re-underwrite, don't re-confirm.** When a position is up materially (e.g. Ricoh +34%, Sanyo Denki +57% above WAC), Yongjie wants a fresh PWER table built from current price, not a confirmation that "the thesis still works." Forward PWER compression is the decision input.
- **He will reject your sizing if you ignore liquidity.** Inui Global Logistics ¥159M ADV → 1.5% max regardless of PWER. Miyoshi Oil & Fat micro-cap → 1.5% hold even with 20% PWER. Liquidity cap binds before PWER.
- **He will correct you on primary-source facts immediately.** EDINET filing details, activist WAC, share counts, AGM dates — if you cite an aggregator and he has the EDINET XBRL, you are wrong, no matter what. Treat his corrections as superseding your prior conclusion in full; do not argue.
- **He values "what changed" over "what is."** A daily sweep that re-states yesterday's read with no delta is useless. Lead with the increment — new filings, price moves, news, verdict changes.
### 10.3 Pet peeves and likely-to-trip-up-a-newcomer items
- **Do not call Tier 2 long-only investors "activists" without qualification.** Silchester, Ariake, MIRI, GMO, Zennor, Kaname are *engaged* but not hard activists. Conflating styles produces wrong PWER inputs. Filer-roster taxonomy matters.
- **Do not assume June AGM for every position.** Memory rule #21 + 4404 Miyoshi Oil & Fat correction = explicit. FYE varies; AGM follows FYE + ~3 months. Money Forward (FYE Nov 30) AGM Jan–Feb. Verify per name.
- **Do not treat "純投資" as passive.** Memory rule #1. Every framework file repeats this and Yongjie will catch any drift back into "the activist filed pure-investment, so it's a watch-only situation."
- **Do not aggregate Murakami without reading the joint-holder section.** Memory rule #10. New vehicle 5%+ filings late in a campaign are often internal redistribution. The Exedy CR No. 24 lesson is canonical and treated as a teaching case.
- **Do not skip the True-WAC step.** Memory rule v10.3 Standing Rule #2. Every memo. Every refresh. The mandatory concealment scan is mandatory.
- **Do not confuse Tier R Mode 1 with M1-Internal-Carry sleeve assignment.** v10.2 §4 diagnostic: is there a named external counterparty? If yes (Sankei REIT, Aichi Steel, board contest at Sanyo Denki) = M1-External-Binary, L4 ARB sleeve, days-to-weeks. If no (Yellow Hat, Bunka Shutter watch) = M1-Internal-Carry, L3 patient sleeve. Misclassifying drives wrong sleeve, wrong sizing, wrong hold horizon.
- **Do not run a sweep without verifying date stamps.** Memory rule #24 (price freshness) + #25 (PBR freshness) + #29 (daily freshness sweep). Stale data treated as wrong data.
- **Do not write artifacts (HTML, code) when the request is for a memo or analysis.** The pipeline outputs HTML; Yongjie reads the markdown. Memo content goes in markdown / inline; production artifacts go in the file system explicitly.
- **Do not narrate process; deliver conclusions.** "Let me think about this" / "I'll need to consider…" is friction. Get to the verdict.
- **Do not auto-translate Japanese terms when the Japanese is the primary terminology.** `重要提案行為等` is more precise than "important proposal actions"; use the Japanese where it carries the meaning.
- **Do not invent precision.** If PWER is "approximately 25–30%," say so. If a fact is `INFERENCE` not `CONFIRMED`, label it. Memory rule #27.
### 10.4 Decision shortcuts Yongjie uses (inferred)
- **If a position is named in the v8 portfolio reference (Section 4 of custom instructions) but not in `position-book-current.md` recent reviews**, it likely needs `⚠ NEEDS REFRESH`. The v8 portfolio is a starting reference, not the live book.
- **If a filer is in Tier 1 but the position is at L3**, the constraint is likely WAC inversion or sub-20% PWER. Check both before recommending an upgrade.
- **If a filer is in Tier 2 (Silchester, Ariake, MIRI, GMO, Zennor) and the position is at L1**, the position is probably an outlier and should be checked — Tier 2 generally maps to L3 patient sleeve.
- **If a position has been held >18 months with no filing event**, evaluate Hokuetsu-pattern lock (memory rule #14 sister-pattern).
- **The 25% per-activist cap is the binding constraint for the Effissimo cluster.** Currently Ricoh 8 + Teijin 5.5 + Tamron 3.5 = 17%. Adding a fourth Effissimo name (e.g. Ines Holdings 9742) tightens room aggressively.
### 10.5 Output structure for non-sweep deliverables
(Inferred from the custom-instructions Section 7 outline + observed deliverables.)
**New activist signal memo — eight-block sequence:** Setup → Shareholder Structure → Playbook → Fundamentals → Catalyst Path → PWER Table → Bear Case → Portfolio Recommendation. This is the standard for any new in-universe filer; deliver in this order, every time.
**Portfolio update memo — four-block sequence:** What's added → What's trimmed → Reallocation rationale → Post-change Wtd-Avg PWER + position count + cash buffer. Confirm 14–18 position count and 100% deployed (or stated buffer) at the end.
**Deep dive (multi-day research workup) — uses the `fundamental-deep-dive` skill** when the request signals max depth ("comprehensive analysis," "institutional-grade research," "bull-base-bear with contrarian view"). For routine activist-filing screens, use `shadow-trade-disclosure` skill instead. For multi-position rebalances, use `asuka-basket-construction`. For single-position questions, `asuka-position-sizing`. Skill selection matters; running the wrong skill produces too-shallow or too-deep output.
### 10.6 Things I cannot reconstruct without the lost chat history — known gaps for the successor to raise with Yongjie
Be explicit with Yongjie when first sitting down with him; these are the items where I have indirect evidence but no canonical specification, and getting them wrong is high-cost:
1. **Exact current weights for several L2/L3 positions.** `position-book-current.md` carries `⚠ NEEDS REFRESH` on Kobayashi Pharma (4967), en Japan (4849), Kakaku.com (2371), Tsurumi Mfg (6351), Ezaki Glico (2206), Tosei (8923). The Asuka_v3_state.md May 3 reference gives weights for some but not all. **Ask Yongjie for current weights and last-trade dates on the `NEEDS REFRESH` items before sizing anything.**
2. **The current Wtd-Avg PWER target.** The custom instructions say ≥25%; the v3 state May 3 shows 21.5%; recent dashboard reads show 27%. The actual target may have moved with v11 deployment.
3. **The cash buffer policy.** Custom instructions say "100% deployed"; v11 recent updates allow 5–10% cash buffer for transitions. Confirm which is binding for daily sweeps.
4. **Exact bucket boundaries for the DPS modifier across all filers.** Yellow Hat case used SC bucket-3 +40% to +80%; the boundaries for Effissimo, Murakami, Be Brave, Oasis, 3D, Dalton are referenced in v9.1 but the live values may have been refreshed since.
5. **Whether the L4 ARB sleeve mandate has expanded beyond Sankei REIT.** v10.2 named Sankei REIT as the canonical case and noted Aichi Steel retro as "would have been L4." No active L4 ARB positions beyond Sankei REIT are confirmed in `position-book-current.md`.
6. **The state of the dashboard_data.json schema.** The HTML mockup (`Asuka_Active_Book_Daily_Risk_v1.html`) shows fields (MoS-IV, capture, tier-AAA/AA/A/B/C grade) that may have been added after the v3 state file was generated. The successor will need a current JSON schema from Yongjie.
7. **The Bloomberg ACTV refresh cadence and how stale the empirical HPR distributions are.** v9.1 set annual refresh; current readings cited NSD_1 May 11 2026. The next refresh due date and the procedure (`Bloomberg Activist Pull` directory contents) should be confirmed.
8. **The exact list of "current open trades" / pending orders.** Daily sweep mentions limit orders (e.g. meito ¥2,600–2,750 zone) but the live order book is not in any file I can see. Ask Yongjie for the open-orders file or workflow.
9. **Whether `Asuka_Fund_Portfolio.xlsx` is the authoritative weights file.** Multiple data sources (v3 state markdown, position book, dashboard HTML, Asuka_Fund_Portfolio.xlsx) carry portfolio weights. If they conflict, which wins? Likely the xlsx is the trade-book authority but this needs confirmation.
10. **Process for refreshing the `recent_updates` memory list.** Memory rules #25 through #30 were added in May 2026; the cadence for adding new memory rules (and the numbering authority) is implicit. Probably: when a correction holds across two refreshes, promote to memory rule with next sequential number.
11. **The specific Cowork morning-brief format.** `edinet-monitoring-protocol.md §6` references Cowork reading `dashboard_latest.html` at 09:15 SGT. The morning-brief template (what Cowork narrates back) is not in any file I have seen.
12. **Whether the Tsurumi Mfg (6351) position is still open.** Custom instructions list it at L1 11%; position book says `⚠ NEEDS CONFIRMATION — may be stale or trimmed`. Asuka_v3_state.md does not list it. This is the largest currently-ambiguous holding by potential weight.
### 10.7 The "if in doubt" defaults
When in doubt, default to:
- Smaller size (you can add; you cannot un-add cleanly into thin liquidity).
- Read the joint-holder section before treating any individual filer as the full economic interest.
- Pull EDINET XBRL before quoting any stake or WAC number.
- Stamp every price quote with source-date.
- Cite the IR calendar primary for any binary-event date.
- Flag `STALE_INPUTS` loudly rather than estimate quietly.
- Treat memory rules #1–#30 as binding even when a fresh observation seems to contradict them. New rules require explicit promotion, not silent override.
---
