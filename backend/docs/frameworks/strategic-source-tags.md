# Strategic Source Taxonomy · 9-tag classification

Each activist target gets ONE primary tag = the value source the activist will extract. The tag tells you what the activist sees that neither Earn-MoS nor Asset-MoS captures.

## The 9 tags

| Tag | Color | Meaning | Typical activist | Bull case shape |
|---|---|---|---|---|
| `IP` | purple | Hidden intangible / off-book IP | Effissimo, AVI | Re-rating from peer multiples on disclosed IP |
| `RE` | brown | Real estate fair value vs book | Strategic Capital, LIM | Property appraisal-based unlock |
| `SOTP` | cyan | Conglomerate breakup / parts unlock | Effissimo, 3D, Elliott | Sum-of-parts vs current discount |
| `CASH` | yellow | Dormant capital → buyback / dividend | Be Brave, Ueshima, Strategic Capital | Cap returned, multiple re-rates |
| `FWD` | gold | Forward growth NPV (trailing PE wrong tool) | Arcus, Wil Field, SilverCape | DCF-driven, longer horizon |
| `TOB` | indigo | Parent-sub take-private optionality | Murakami, Oasis | Bimodal: TOB premium or status quo |
| `GOV` | blue | Governance / ROE math reform | Dalton, AVI, UGS | Modest reset to ROE > 8%, PBR > 1.0x |
| `SUB` | green | Sub-book PBR < 1x asset unlock | Effissimo, Silchester, Murakami | Re-rate to 1.0x book |
| `CYC` | gray | Cyclical (caveat — not classic activist) | Generic | Cycle floor → mid-cycle multiple |
| `ARB` | gold-border | L4 merger-arb (separate sleeve math) | Various | Deal close at announced terms |

## Why this matters

When both Earn-MoS and Asset-MoS are negative, the strategic-source tag tells you what the activist sees that neither accounting lens captures.

Earn-MoS = `(IV − Px) / IV` where IV = 5yr OP × 0.7 / 0.08
Asset-MoS = `(1 − PBR) × 100`

Both measure **accounting value**. Activist edge = gap between accounting value and **strategic value** that neither column sees. The strategic-source tag tells you what kind of strategic value the activist is targeting.

Earn-MoS is systematically negative on activist targets BY DESIGN — earnings suppression IS the thesis. So a deeply-negative Earn-MoS isn't a sell signal; it's the entry condition for the activist to extract value.

## How to assign tags

For each new activist target:

1. **What is the activist demanding?**
   - "Increase dividend / buyback" → CASH
   - "Spin off the [X] business" → SOTP
   - "Adopt ROE 8% target / DOE 5%" → GOV
   - "Sell parent's stake / parent should TOB the sub" → TOB
   - "Mark up real estate to fair value" → RE
   - "Unlock IP licensing revenue" → IP

2. **What's the company's structural setup?**
   - PBR < 1.0x with no obvious operating fix → SUB
   - Multi-segment with hidden gem → SOTP
   - Parent-sub with controlling stake mismatch → TOB
   - Trailing PE high but forward growth strong → FWD

3. **Cyclical? CYC, with caveat.**
   - Shipping (9104, 9110, 9115), commodities — these aren't classic activist targets even when an activist is on the register. Treat with caution.

## Bull case shape by tag

The bull case scenario (and target price) should follow the tag:

- `CASH`: bull = "all dormant capital returned, multiple holds" → typical +30-50% from current
- `SOTP`: bull = "non-core spun out at peer multiple" → sum-of-parts gap, often +50-100%
- `TOB`: bull = "TOB at 30-40% premium" → bimodal, narrow base case
- `GOV`: bull = "ROE 8%+ achieved, PBR re-rates to 1.0x" → modest, +20-40%
- `SUB`: bull = "PBR re-rates from 0.6x to 1.0x" → arithmetic from PBR delta
- `FWD`: bull = "forward NPV materializes as growth compounds" → patient, +40-80% over 2-3yr
- `IP`: bull = "IP value disclosed and monetized" → can be very large
- `RE`: bull = "real estate at fair value" → property appraisal-driven

The tag also constrains how aggressive your bull case can be. CASH bulls are capped at "all cash returned" — you can't reasonably argue more upside than that comes from the cash bucket. SOTP bulls are capped at the sum-of-parts gap.

## Strategic-source vs sector

Don't confuse:
- **Sector** (e.g., "industrials", "consumer goods") — descriptive
- **Strategic source** — prescriptive (what catalyst is being extracted)

Two industrials companies can have completely different strategic sources: one might be SOTP (multi-segment), the other CASH (cash-rich monoline).

## Tagging in `data/positions.json`

```json
{
  "ticker": "4613",
  "strategic_source": "SUB",
  ...
}
```

Single tag only. If multiple apply, pick the dominant one and note the secondary in `notes`.
