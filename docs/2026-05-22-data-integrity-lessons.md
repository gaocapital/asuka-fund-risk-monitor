# Data-Integrity Lessons — 2026-05-22

What an EDINET cross-check of the held book surfaced, and the safeguards put
in place so it does not recur.

## What went wrong

A full audit of all 21 held positions against EDINET `get_ownership_timeline`
found **19 stale or wrong**. Three failure modes:

1. **Partial backfill.** The ownership-history backfill refreshed each
   position's `filing_history` / `accumulation` but not the scalar/prose
   fields — `stake_pct`, `last_filing`, `activist` — so those went stale
   (e.g. 3034 still showed Will Field at 8.69% when EDINET had 18.22% — a
   9.5pp gap; 7752 / 4493 / 5930 had a blank `activist` field despite
   Effissimo 24.77% / SilverCape 9.5% / NAVF 20.55% anchors).
2. **Passive-filer pollution.** `edinet_filings_ingest.py` overwrote a
   position's `last_filing` with whichever 5%-rule filing was newest —
   including passive custodians (Nomura, trust banks) and issuer
   self-filings (臨時報告書) — burying the genuine activist filing.
3. **Name-collision activists.** 3182 and 6914 carried a "GMO-Usonian"
   activist thesis that does not exist in EDINET — a confusion with the
   passive quant house Grantham, Mayo, Van Otterloo ("GMO LLC"). Both
   theses were built on a holder that never filed.

A fourth, related lesson: a project shadow-trade eval treated 4417 as a
"new name" when it was already a held L3-PAH screen — a name must be
checked against the book before it is framed as new.

## Safeguards — prevent / correct / detect

- **Prevent** — `edinet_filings_ingest._is_activist_anchor_filing()` now
  gates the `last_filing` / `filing_history` / `stake_pct` update: only a
  大量保有-family filing from a genuine large-holder (not a passive
  custodian, not an issuer self-filing) may touch the activist record.
  Passive filings still reach the feed.
- **Correct** — the Cowork reasoning layer (`reasoning/cowork-task.md`,
  OWNERSHIP-HISTORY REFRESH) re-pulls EDINET every run and rewrites
  `filing_history`, `accumulation`, `stake_pct`, `last_filing` and
  `activist` — and verifies the named activist actually appears in EDINET.
- **Detect** — `book_hygiene_check.py` runs inside the daily broker sync
  and flags residual inconsistencies (passive `last_filing`, stake vs
  filing_history mismatch, an activist with no filings) in the run log.
- **Guardrail** — `cowork-task.md` NEW-NAME GUARDRAIL: check
  `positions[]` / `watch_list[]` / `exited[]` before framing any ticker
  as a new signal.

## Standing rule

The dashboard's `activist` / `stake_pct` / `last_filing` are only ever as
good as the last EDINET reconciliation. EDINET `get_ownership_timeline` is
the primary source; the pipeline's API-metadata path is a fallback and
cannot recover stakes. Treat any `book_hygiene_check` warning in the daily
log as an open item to resolve that day.
