"""
PWER Auto-Tilt Rules Engine
============================
Applies systematic probability/return shifts to position pwer_scenarios when
new signals arrive (EDINET filings, TDNet events, fundamental updates).

Design principle:
  - Auto-tilts are SMALL, MECHANICAL, AUDITABLE shifts
  - Each tilt logs a reason + timestamp in pwer_history
  - PM can revert by inspecting history
  - For Hokuetsu-pattern positions: REVERSE the auto-tilt logic
    (activist conviction may be misleading)

Signal types handled:
  EDINET (activist filings):
    - Stake threshold crossing (5/10/15/20/33.4)
    - Material accumulation (Δpp ≥ 0.5)
    - 株主提案 / 臨時報告書 on position
    - Mode change 純投資→重要提案
    - Negative accumulation (activist exiting)

  TDNet (corporate-issuer events):
    - buyback_announcement
    - dividend_increase
    - strategic_review_announcement
    - agm_proposal_response
    - profit_warning / impairment_charge
    - board_nominee_acceptance / rejection
    - agm_voting_result
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Optional
from copy import deepcopy


def _atomic_write_json(path: str, data) -> None:
    """Write JSON atomically via .tmp + os.replace (atomic on NTFS).
    Prevents OneDrive / Defender from exposing partial files to readers.
    """
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

# ============================================================================
# TILT RULES - PROBABILITY SHIFTS (in percentage points)
# ============================================================================
# Format: {bear, base, bull, xbull}
# Sum to 0 (probability conservation)
# Applied multiplicatively to scenario probs, then renormalized

TILT_RULES = {
    # Stake threshold crossings (cumulative impact - more aggressive at higher levels)
    "stake_cross_5":     {"bear": -0.02, "base":  0.00, "bull": +0.01, "xbull": +0.01},
    "stake_cross_10":    {"bear": -0.05, "base": -0.00, "bull": +0.03, "xbull": +0.02},
    "stake_cross_15":    {"bear": -0.08, "base":  0.00, "bull": +0.05, "xbull": +0.03},
    "stake_cross_20":    {"bear": -0.10, "base":  0.00, "bull": +0.05, "xbull": +0.05},
    "stake_cross_33":    {"bear": -0.15, "base":  0.00, "bull": +0.05, "xbull": +0.10},

    # Material accumulation (Δpp magnitude)
    "accum_small":       {"bear": -0.02, "base":  0.00, "bull": +0.01, "xbull": +0.01},  # +0.5-1.0pp
    "accum_medium":      {"bear": -0.03, "base":  0.00, "bull": +0.02, "xbull": +0.01},  # +1.0-2.0pp
    "accum_large":       {"bear": -0.05, "base":  0.00, "bull": +0.03, "xbull": +0.02},  # +2.0pp+

    # Negative accumulation (activist exit signal)
    "exit_signal":       {"bear": +0.05, "base":  0.00, "bull": -0.03, "xbull": -0.02},

    # Filing types (EDINET)
    "shareholder_proposal":   {"bear": -0.03, "base": -0.05, "bull": +0.05, "xbull": +0.03},
    "extraordinary_report":   {"bear": +0.00, "base":  0.00, "bull":  0.00, "xbull":  0.00},  # human review
    "mode_change_serious":    {"bear": -0.05, "base": -0.02, "bull": +0.05, "xbull": +0.02},  # 純投資→重要提案

    # TDNet corporate-issuer signals
    "buyback_announcement":   {"bear": -0.03, "base": +0.02, "bull": +0.03, "xbull": -0.02},  # capital return playing out reduces xbull/bear extremes
    "dividend_increase":      {"bear": -0.03, "base": +0.02, "bull": +0.03, "xbull": -0.02},
    "strategic_review":       {"bear": -0.10, "base": -0.05, "bull": +0.05, "xbull": +0.10},  # binary outcome ahead
    "board_nominee_accepted": {"bear": -0.05, "base": -0.02, "bull": +0.05, "xbull": +0.02},
    "board_nominee_rejected": {"bear": +0.10, "base":  0.00, "bull": -0.07, "xbull": -0.03},
    "profit_warning":         {"bear": +0.10, "base":  0.00, "bull": -0.07, "xbull": -0.03},
    "impairment_charge":      {"bear": +0.05, "base":  0.00, "bull": -0.03, "xbull": -0.02},
    "agm_vote_won":           {"bear": -0.10, "base":  0.00, "bull": +0.05, "xbull": +0.05},
    "agm_vote_lost":          {"bear": +0.10, "base":  0.00, "bull": -0.05, "xbull": -0.05},
}


def is_hokuetsu_pattern(position: dict) -> bool:
    """Detect Hokuetsu-pattern positions where activist conviction is misleading."""
    notes = (position.get("notes") or "").upper()
    activist = (position.get("activist") or "")
    if "HOKUETSU" in notes or "HOKUETSU PATTERN" in notes:
        return True
    # Also flag if explicitly noted as multi-year failed campaign
    if "FAILED CAMPAIGN" in notes or "ACTIVIST EXITING" in notes:
        return True
    return False


def get_applicable_rules(filing: dict, position: dict) -> list[tuple[str, dict, str]]:
    """Determine which tilt rules apply for a given filing on a position.
    Returns list of (rule_name, tilt_dict, reason)."""
    rules = []
    doc_type = filing.get("doc_type", "")
    purpose = filing.get("purpose", "")
    stake_after = filing.get("stake_after") or 0
    stake_before = filing.get("stake_before") or 0
    delta_pp = stake_after - stake_before

    # Threshold crossings
    thresholds = [(5, "stake_cross_5"), (10, "stake_cross_10"), (15, "stake_cross_15"),
                  (20, "stake_cross_20"), (33.4, "stake_cross_33")]
    for level, rule_name in thresholds:
        if stake_before < level <= stake_after:
            rules.append((rule_name, TILT_RULES[rule_name],
                          f"Stake crossed {level}% (was {stake_before:.2f}, now {stake_after:.2f})"))

    # Accumulation magnitude
    if delta_pp >= 2.0:
        rules.append(("accum_large", TILT_RULES["accum_large"],
                      f"Large accumulation +{delta_pp:.2f}pp"))
    elif delta_pp >= 1.0:
        rules.append(("accum_medium", TILT_RULES["accum_medium"],
                      f"Medium accumulation +{delta_pp:.2f}pp"))
    elif delta_pp >= 0.5:
        rules.append(("accum_small", TILT_RULES["accum_small"],
                      f"Small accumulation +{delta_pp:.2f}pp"))
    elif delta_pp <= -0.5:
        rules.append(("exit_signal", TILT_RULES["exit_signal"],
                      f"Activist reduction {delta_pp:.2f}pp"))

    # Filing types
    if "株主提案" in doc_type or filing.get("doc_subtype") == "AGM Proposal Submission":
        rules.append(("shareholder_proposal", TILT_RULES["shareholder_proposal"],
                      "Shareholder proposal filed - catalyst confirmed"))
    if "臨時" in doc_type:
        rules.append(("extraordinary_report", TILT_RULES["extraordinary_report"],
                      "Extraordinary report - human review needed"))
    if purpose == "重要提案" and filing.get("prev_purpose") == "純投資":
        rules.append(("mode_change_serious", TILT_RULES["mode_change_serious"],
                      "Mode change 純投資→重要提案 - escalation signal"))

    # TDNet event types
    event_type = filing.get("event_type", "")
    if event_type and event_type in TILT_RULES:
        reason_map = {
            "buyback_announcement":   "Buyback announced - capital return playbook executing",
            "dividend_increase":      "Dividend increased - shareholder return",
            "strategic_review":       "Strategic review announced - binary outcome ahead",
            "board_nominee_accepted": "Board nominee accepted - governance win",
            "board_nominee_rejected": "Board nominee rejected - campaign setback",
            "profit_warning":         "Profit warning - thesis impaired",
            "impairment_charge":      "Impairment charge - balance sheet hit",
            "agm_vote_won":           "AGM vote won - activist victory",
            "agm_vote_lost":          "AGM vote lost - family/management bloc held",
        }
        rules.append((event_type, TILT_RULES[event_type], reason_map.get(event_type, event_type)))

    return rules


def apply_tilts_to_scenario(scenarios: dict, tilts: list[tuple[str, dict, str]],
                             hokuetsu: bool = False) -> tuple[dict, list[str]]:
    """Apply tilt rules to a pwer_scenarios dict. Returns (new_scenarios, reasons_log).

    For Hokuetsu pattern: REVERSE positive tilts on accumulation (activist conviction may be wrong).
    """
    new_scenarios = deepcopy(scenarios)
    reasons = []

    for rule_name, tilt, reason in tilts:
        # Hokuetsu reversal: if rule would normally signal bullish (bear-, bull+),
        # AND it's a stake_cross/accum rule, REVERSE it
        effective_tilt = tilt
        if hokuetsu and rule_name in ("stake_cross_5", "stake_cross_10", "stake_cross_15",
                                       "stake_cross_20", "stake_cross_33",
                                       "accum_small", "accum_medium", "accum_large"):
            effective_tilt = {k: -v for k, v in tilt.items()}
            reason = f"⚠ HOKUETSU REVERSE: {reason}"

        for label in ["bear", "base", "bull", "xbull"]:
            if label in new_scenarios:
                new_prob = new_scenarios[label]["prob"] + effective_tilt[label]
                new_scenarios[label]["prob"] = max(0.01, min(0.95, new_prob))  # clip

        reasons.append(f"  → {rule_name}: {reason}")

    # Renormalize probabilities to sum to 1.0
    total = sum(new_scenarios[k]["prob"] for k in ["bear", "base", "bull", "xbull"] if k in new_scenarios)
    if total > 0:
        for k in ["bear", "base", "bull", "xbull"]:
            if k in new_scenarios:
                new_scenarios[k]["prob"] = round(new_scenarios[k]["prob"] / total, 3)

    return new_scenarios, reasons


def recompute_pwer(scenarios: dict, current_px: float, wac: float = None) -> tuple[float, float]:
    """Compute (Our PWER from current px, Activist PWER from WAC) given scenarios with anchored targets."""
    our_pwer = 0.0
    activist_pwer = None
    for label in ["bear", "base", "bull", "xbull"]:
        if label in scenarios:
            target = scenarios[label].get("target_jpy")
            prob = scenarios[label].get("prob", 0)
            if target and current_px:
                our_pwer += prob * ((target - current_px) / current_px * 100)
            if target and wac and activist_pwer is None:
                activist_pwer = 0.0
            if target and wac:
                activist_pwer += prob * ((target - wac) / wac * 100)
    return round(our_pwer, 1), (round(activist_pwer, 1) if activist_pwer is not None else None)


def apply_signal_to_position(position: dict, filing: dict, dry_run: bool = False) -> Optional[dict]:
    """Apply auto-tilt to a single position based on a single filing/event.
    Returns the modified position dict (or None if no rules applied).
    Also appends to position['pwer_history'] log."""
    rules = get_applicable_rules(filing, position)
    if not rules:
        return None

    scenarios = position.get("pwer_scenarios")
    if not scenarios:
        return None

    hokuetsu = is_hokuetsu_pattern(position)
    new_scenarios, reasons = apply_tilts_to_scenario(scenarios, rules, hokuetsu=hokuetsu)

    # Refresh return_pct values based on new probabilities (returns themselves are anchored to targets)
    # The targets and return_pct don't change from auto-tilt — only probabilities do.

    # Compute new PWER values
    new_our_pwer, new_activist_pwer = recompute_pwer(new_scenarios, position.get("price"), position.get("wac"))
    old_our_pwer = position.get("pwer")
    old_activist_pwer = position.get("activist_pwer")

    # Build history entry
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "trigger": filing.get("doc_type") or filing.get("event_type", "manual"),
        "filer": filing.get("filer"),
        "rules_applied": [r[0] for r in rules],
        "reasons": reasons,
        "old_pwer": old_our_pwer,
        "new_pwer": new_our_pwer,
        "delta_pp": round(new_our_pwer - (old_our_pwer or 0), 2),
        "hokuetsu_reversed": hokuetsu,
    }

    if not dry_run:
        # Apply changes
        position["pwer_scenarios"] = new_scenarios
        position["pwer_scenarios"]["calculated_at"] = datetime.now().isoformat()
        position["pwer"] = new_our_pwer
        position["activist_pwer"] = new_activist_pwer
        history = position.get("pwer_history") or []
        history.append(history_entry)
        position["pwer_history"] = history[-10:]  # keep last 10 entries

    return history_entry


def apply_signals_batch(data_path: str, signals: list[dict], dry_run: bool = False) -> list[dict]:
    """Apply auto-tilts for a batch of signals. Each signal must include 'ticker'.
    Returns list of history entries (one per signal that triggered rules)."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    history_entries = []
    for signal in signals:
        ticker = signal.get("ticker")
        if not ticker:
            continue
        for pos in data.get("positions", []):
            if pos["ticker"] == ticker:
                entry = apply_signal_to_position(pos, signal, dry_run=dry_run)
                if entry:
                    entry["ticker"] = ticker
                    entry["name"] = pos.get("name")
                    history_entries.append(entry)
                break

    if not dry_run and history_entries:
        _atomic_write_json(data_path, data)

    return history_entries


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dashboard_data.json")
    parser.add_argument("--signals", required=True, help="JSON file with list of signal dicts")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.signals, "r", encoding="utf-8") as f:
        signals = json.load(f)

    entries = apply_signals_batch(args.data, signals, dry_run=args.dry_run)
    print(f"\n{'DRY RUN: ' if args.dry_run else ''}Auto-tilt applied to {len(entries)} positions:\n")
    for e in entries:
        print(f"  {e['ticker']} {e['name']}: {e['old_pwer']:.1f}% → {e['new_pwer']:.1f}% ({e['delta_pp']:+.1f}pp)")
        print(f"    Trigger: {e['trigger']} ({e['filer']})")
        for r in e['reasons']:
            print(f"    {r}")
        if e['hokuetsu_reversed']:
            print(f"    ⚠ HOKUETSU pattern: tilts reversed")


if __name__ == "__main__":
    main()
