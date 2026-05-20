# Activist Tier Classification

Three-tier system used by the conviction scorer. Tier classification lives in `data/activist_universe.yaml`, not in code.

## Tier 1 — Hard activists with track record

Track-record activists with confirmed campaign wins, escalation history, and willingness to use full toolkit (proxy battles, public letters, board nominations, blocking stakes).

**Includes:**
- Effissimo Capital Management (+ SMT Partners)
- 3D Investment Partners
- Dalton Investments (+ NAVF)
- Oasis Management
- Strategic Capital
- LIM Advisors
- Elliott Investment Management
- Murakami group (CIE, CIF, Reno, Aya Nomura, ATRA, etc.)
- Ueshima wolf-pack (DOE5%, Naturali)
- Be Brave (Kazuto Izumida)
- SilverCape Investments
- UGS Asset Management

**Conviction scoring**: base activist score = **7**

**Engagement style**: filing language often includes 重要提案行為 clause from day 1; willing to escalate publicly; multi-vehicle aggregation common.

## Tier 2 — Engagement / quality long-only

Engagement-focused but not hard activists. Typically file with 純投資 (pure investment) language; engagement happens privately. Can run multi-year quiet ratchets.

**Includes:**
- Silchester International Investors
- AVI Japan / Asset Value Investors
- Arcus Investment
- Wil Field Capital

**Conviction scoring**: base activist score = **5**

**Engagement style**: rarely public letters; multi-year hold; engagement letters typical (AVI); patient capital. Annualized PWER cap typically ~10-12% — engagement activists don't force TOB.

**Recent exception**: Silchester's Apr 1 2026 Kansai Paint filing used unusually **activist** language (explicit demands for 増配, buyback, 金庫株消却, capital policy changes). This is atypical for them — when a Tier 2 activist files with Tier 1 language, treat as upgrade signal for that specific position.

## Tier 3 — Patient compounders / fundamental signals

Long-duration compounder investors. Stake size signals "fundamentally cheap" but no near-term forcing function. Re-rating thesis driven by macro tailwind (TSE PBR reform) rather than activist pressure.

**Includes:**
- GMO-Usonian (Drew Edwards)
- Grantham Mayo Van Otterloo
- Ariake Capital
- MIRI Capital Management
- Zennor Asset Management

**Conviction scoring**: base activist score = **3**

**Engagement style**: very rarely confrontational. Filing language is consistently passive. Position-building can take years.

## Escalation bonuses (cumulative, max +5)

Beyond base tier score, the conviction scorer adds bonuses for active campaign indicators in the position's `notes` field:

| Note keyword | Bonus | When to apply |
|---|---:|---|
| "MODE 2" or "ESCALATION" | +3 | Activist crossed from passive accumulation to active pressure |
| "FRESH ACCUMULATION" or "FRESH ENTRY" | +3 | New 5%+ filing within past 30 days |
| "RE-ACCUMULATION PAST PRIOR PEAK" | +5 | Activist exceeded their previous peak stake — high-conviction signal |

These are tagged manually in position notes by the PM (or filing-verifier subagent) when the campaign reaches the relevant stage.

## How to add a new activist

When a new activist appears in the EDINET feed:

1. Verify track record:
   - Number of past Japan campaigns
   - Win rate (board seats won, capital returns extracted, MBOs forced)
   - Escalation history (did they file public letters? proxy contests?)
2. Classify:
   - Track record + willingness to escalate → Tier 1
   - Engagement-only, multi-year hold → Tier 2
   - Patient compounder → Tier 3
3. Add to `data/activist_universe.yaml` with:
   - Canonical name
   - Aliases (for filing-verifier matching)
   - EDINET codes (for filing-verifier subagent)
   - Style description
   - PWER cap (Tier 2-3 only, if applicable)
   - Track record citations

## Murakami special case

The Murakami family operates through a complex web of vehicles. The aliases list in `data/activist_universe.yaml` is critical:

```
- Yoshiaki Murakami (individual)
- Aya Nomura (daughter, individual + Minami Aoyama Real Estate)
- Takateru Murakami (individual + MI2 + MI5)
- ATRA (apex holding company)
- Office Support
- City Index Eleventh (CIE)
- City Index First (CIF)
- Reno
- S-Grant
- Fortis
- C&I
- Rebuild
- Maiko / Hospitality / Holdings
```

For any Murakami-tagged position, the filing-verifier MUST aggregate across all listed vehicles to compute true economic interest. New individual vehicle 5%+ filings in late-stage Murakami campaigns often = internal redistribution, not fresh accumulation.

## ATRA tripwire

ATRA (the apex holding company) usually sits above operating vehicles and does not appear as direct co-filer. When ATRA itself appears in the joint-holder section (alongside Aya Nomura + CIE), it signals high-conviction Murakami deployment — treat as upgrade signal vs CIE/CIF/Reno-only filings.

This tripwire is implemented manually in `notes` for now; a future enhancement will auto-detect ATRA direct-filer events in the EDINET ingest.
