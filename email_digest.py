"""
email_digest.py — Asuka Fund morning risk digest (email).

Composes a morning-briefing HTML email from dashboard_data.json and — on
--send — delivers it to the GAO operations mailbox via the Gmail API.

Mirrors the GAO sub-ops digest (C:/Users/Owner/sub-ops/src/digest/): a hero
header, a KPI strip, then Priority Actions / Since Yesterday / EDINET Filings
/ Catalysts / Standing Flags sections.

Sending
-------
Uses the Gmail API with the `gmail.send` scope ONLY (send-only; that scope
cannot read mail). It reuses the sub-ops send token (token-send.json) —
the digest is a self-notification to GAO's own ops mailbox, never outbound
mail to a counterparty. The recipient is HARDCODED (RECIPIENT) and is not
configurable, by design.

Usage
-----
  python email_digest.py                 # preview only -> digest_preview.html
  python email_digest.py --open          # preview + open it in a browser
  python email_digest.py --send          # email it to associates@gao-cap.com
  python email_digest.py --send --force  # bypass the once-a-day idempotency guard

Preview is the default and NEVER sends. --send is gated behind a real
gmail.send token; without one it fails loudly rather than sending nothing.

Pure stdlib for the preview path; --send additionally needs google-api-python
-client (already used by broker/fetch_cgsi.py).
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import webbrowser
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dashboard_core import (
    load_json, load_previous_state, recompute_pwer_at_spot, compute_deltas,
    compute_portfolio_metrics, derive_action, derive_buy_tier, html_escape,
    fmt_num,
)
# Reuse the dashboard's rule-based explainers so the digest and the dashboard
# give one consistent rationale for every action and change.
from generate_dashboard import explain_action, _pwer_standing

# Windows consoles default to cp1252 and choke on this script's glyphs. Force
# UTF-8 on the standard streams so a standalone run does not crash mid-output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).parent.resolve()
DATA_PATH = HERE / "dashboard_data.json"
PREVIEW_PATH = HERE / "digest_preview.html"
SEND_LOG_PATH = HERE / "digest_send_log.json"

# Hardcoded recipient — GAO's own operations mailbox, never a counterparty.
RECIPIENT = "associates@gao-cap.com"

# gmail.send is send-only — it physically cannot read mail. The token is
# reused from the sub-ops digest, which already authorised this scope.
GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
SUBOPS_DIR = Path(r"C:\Users\Owner\sub-ops")
SEND_TOKEN = SUBOPS_DIR / "token-send.json"
SEND_CREDS = SUBOPS_DIR / "credentials-send.json"
FALLBACK_CREDS = SUBOPS_DIR / "credentials.json"

JST = timezone(timedelta(hours=9))
PWER_FLOOR = 15.0


class DigestError(Exception):
    """Unrecoverable failure building or sending the digest."""


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _wtd_avg_pwer(positions: list) -> float:
    wsum = pwsum = 0.0
    for p in positions:
        pw, w = p.get("pwer"), p.get("weight") or 0
        if pw is not None:
            wsum += w
            pwsum += w * pw
    return (pwsum / wsum) if wsum else 0.0


def _days_to(date_str) -> "int | None":
    if not date_str:
        return None
    try:
        d = datetime.fromisoformat(str(date_str).split("T")[0]).date()
        return (datetime.now(JST).date() - d).days * -1
    except (ValueError, TypeError):
        return None


def _short_date(date_str) -> str:
    try:
        d = datetime.fromisoformat(str(date_str).split("T")[0]).date()
        return d.strftime("%b %d").replace(" 0", " ")
    except (ValueError, TypeError):
        return str(date_str or "")


# ─────────────────────────────────────────────────────────────────────────────
# Build digest data
# ─────────────────────────────────────────────────────────────────────────────

def build_digest(data: dict, prev: "dict | None") -> dict:
    """Assemble everything the morning digest needs from dashboard_data.json."""
    positions = data.get("positions", []) or []
    watch = data.get("watch_list", []) or []
    filings = data.get("todays_filings", []) or []
    deltas = compute_deltas(data, prev)
    metrics = compute_portfolio_metrics(data)

    by_action: dict[str, list] = {}
    for p in positions:
        by_action.setdefault(derive_action(p), []).append(p)
    deploy = sorted(by_action.get("BUY", []), key=lambda p: -derive_buy_tier(p)[1])
    reduce = (sorted(by_action.get("SELL", []), key=lambda p: (p.get("pwer") or 0))
              + sorted(by_action.get("WEAK_HOLD", []),
                       key=lambda p: (p.get("pwer") or 0)))

    name_of = {p.get("ticker"): p.get("name", "") for p in positions}
    flips = []
    for tk, d in deltas.items():
        if d.get("action_changed"):
            p = next((x for x in positions if x.get("ticker") == tk), None)
            if p:
                flips.append((tk, name_of.get(tk, ""),
                              d.get("prev_action", "?"), derive_action(p)))
    new_filing_tks = [tk for tk, d in deltas.items() if d.get("new_filing")]
    pmoves = sorted(((tk, d["pwer_pp"]) for tk, d in deltas.items()
                     if d.get("pwer_pp") is not None and abs(d["pwer_pp"]) >= 0.5),
                    key=lambda x: -abs(x[1]))
    xmoves = sorted(((tk, d["price_pct"]) for tk, d in deltas.items()
                     if d.get("price_pct") is not None and abs(d["price_pct"]) >= 3),
                    key=lambda x: -abs(x[1]))

    cats = []
    for p in positions:
        dd = _days_to(p.get("catalyst_date"))
        if dd is not None and 0 <= dd <= 7:
            cats.append((dd, p))
    cats.sort(key=lambda x: x[0])

    flags = []
    wpwer = _wtd_avg_pwer(positions)
    if wpwer < PWER_FLOOR:
        flags.append(f"Wtd-Avg PWER {wpwer:.1f}% — below the {PWER_FLOOR:.0f}% floor")
    stubs = [p for p in positions if p.get("needs_enrichment")
             and p.get("enrichment_status") != "draft"]
    if stubs:
        flags.append(f"{len(stubs)} holdings un-enriched — no thesis or PWER yet")
    drafts = [p for p in positions if p.get("enrichment_status") == "draft"]
    if drafts:
        flags.append(f"{len(drafts)} draft thesis(es) awaiting your approval")
    for p in positions:
        if derive_action(p) == "DATA_QUARANTINE":
            flags.append(f"{p.get('name')} — data quarantine")

    return {
        "now": datetime.now(JST),
        "as_of": (data.get("as_of") or "")[:10],
        "positions": positions, "watch": watch, "filings": filings,
        "metrics": metrics, "wtd_pwer": wpwer, "name_of": name_of,
        "deploy": deploy, "reduce": reduce,
        "flips": flips, "new_filing_tks": new_filing_tks,
        "pmoves": pmoves, "xmoves": xmoves, "cats": cats, "flags": flags,
        "n_stub": len(stubs),
    }


def _title(d: dict) -> "tuple[str, str, str]":
    """(title, urgency_marker, hero_class) — built from today's actual state."""
    parts = []
    if d["reduce"]:
        parts.append(f"{len(d['reduce'])} TO REDUCE")
    if d["deploy"]:
        parts.append(f"{len(d['deploy'])} TO DEPLOY")
    if d["flips"]:
        parts.append(f"{len(d['flips'])} VERDICT FLIP{'S' if len(d['flips']) != 1 else ''}")
    if d["new_filing_tks"]:
        n = len(d["new_filing_tks"])
        parts.append(f"{n} NEW FILING{'S' if n != 1 else ''}")
    if not parts:
        parts.append("BOOK STEADY")
    title = "  ·  ".join(parts)
    has_quar = any(derive_action(p) == "DATA_QUARANTINE" for p in d["positions"])
    if d["reduce"] or has_quar:
        return title, "🔴 ", "alert"
    if d["flips"] or d["new_filing_tks"] or d["flags"]:
        return title, "🟡 ", ""
    return title, "🟢 ", "calm"


# ─────────────────────────────────────────────────────────────────────────────
# Render — HTML
# ─────────────────────────────────────────────────────────────────────────────

_CSS = """
  body{font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;
    max-width:760px;margin:0 auto;padding:0;color:#1a1a1a;line-height:1.45;
    background:#f4f5f7}
  .wrap{padding:0 22px 28px}
  .hero{background:linear-gradient(135deg,#0b1220 0%,#1c2e54 100%);color:#fff;
    padding:22px 26px 18px;border-left:8px solid #4d9fff}
  .hero.alert{background:linear-gradient(135deg,#3a0d0d 0%,#9a2b1c 100%);
    border-left-color:#ffce4d}
  .hero.calm{background:linear-gradient(135deg,#11301f 0%,#2c6b48 100%);
    border-left-color:#7ce0a8}
  .eyebrow{font-size:11px;letter-spacing:.22em;font-weight:700;color:#7fb4ff;
    text-transform:uppercase;margin-bottom:6px}
  .hero.alert .eyebrow{color:#ffce4d}.hero.calm .eyebrow{color:#7ce0a8}
  .hero h1{font-size:25px;font-weight:800;margin:0;letter-spacing:.02em;
    text-transform:uppercase;line-height:1.18}
  .hero .meta{font-size:12px;color:#c5d3ed;margin-top:9px;letter-spacing:.03em}
  h2{font-size:14px;margin:26px 0 9px;padding-bottom:5px;
    border-bottom:1px solid #d6d8dd;color:#444;text-transform:uppercase;
    letter-spacing:.08em}
  .kpis{display:table;width:100%;border-spacing:9px 0;margin:18px 0 4px}
  .kpi{display:table-cell;background:#fff;border:1px solid #e3e4e8;
    border-radius:9px;padding:12px 14px;width:25%;vertical-align:top}
  .kpi .l{font-size:10px;color:#777;text-transform:uppercase;
    letter-spacing:.07em;margin-bottom:5px}
  .kpi .v{font-size:23px;font-weight:700;line-height:1.1}
  .kpi .s{font-size:10.5px;color:#999;margin-top:4px}
  .kpi.warn{background:#fff5f3;border-color:#f3c8bf}.kpi.warn .v{color:#b8341e}
  .kpi.good .v{color:#1f7a3d}
  table{width:100%;border-collapse:collapse;font-size:12.5px;background:#fff;
    border:1px solid #e3e4e8;border-radius:7px;overflow:hidden}
  th{text-align:left;padding:7px 9px;font-size:10px;text-transform:uppercase;
    letter-spacing:.05em;color:#777;background:#f0f1f3;border-bottom:1px solid #d6d8dd}
  td{padding:7px 9px;border-bottom:1px solid #eef0f2;vertical-align:top}
  tr:last-child td{border-bottom:none}
  .tk{font-size:10.5px;font-weight:700;color:#555;background:#f0f1f3;
    border:1px solid #e3e4e8;padding:1px 5px;border-radius:3px}
  .badge{font-size:10px;font-weight:800;padding:2px 7px;border-radius:4px;
    white-space:nowrap}
  .b-buy{background:#e4f5e8;color:#1f7a3d;border:1px solid #b6e0c1}
  .b-sell{background:#fde7e5;color:#c0342480;border:1px solid #f3c8bf;color:#b8341e}
  .b-weak{background:#fdf3df;color:#9a7415;border:1px solid #ecd9a3}
  .b-hi{background:#fde7e5;color:#b8341e;border:1px solid #f3c8bf}
  .b-md{background:#fdf3df;color:#9a7415;border:1px solid #ecd9a3}
  .b-lo{background:#f0f1f3;color:#888;border:1px solid #e3e4e8}
  .pos{color:#1f7a3d;font-weight:700}.neg{color:#b8341e;font-weight:700}
  .mut{color:#888}
  ul.chg{list-style:none;padding:0;margin:0;background:#fff;border:1px solid #e3e4e8;
    border-radius:7px}
  ul.chg li{padding:8px 11px;border-bottom:1px solid #eef0f2;font-size:12.5px}
  ul.chg li:last-child{border-bottom:none}
  .chg-sub{font-size:11px;color:#888;margin-top:3px;line-height:1.45}
  .empty{color:#999;font-style:italic;padding:9px 11px;background:#fff;
    border:1px solid #e3e4e8;border-radius:7px;font-size:12.5px}
  .foot{font-size:10.5px;color:#999;margin-top:30px;padding-top:13px;
    border-top:1px solid #e3e4e8;line-height:1.6}
"""


def _kpi(label: str, value: str, sub: str, cls: str = "") -> str:
    return (f'<div class="kpi {cls}"><div class="l">{label}</div>'
            f'<div class="v">{value}</div><div class="s">{sub}</div></div>')


def _action_table(rows: list, action_of) -> str:
    if not rows:
        return '<div class="empty">Nothing flagged.</div>'
    out = ['<table><tr><th>Action</th><th>Holding</th><th>PWER</th>'
           '<th>Weight</th><th>Why</th></tr>']
    for p in rows:
        a = action_of(p)
        bcls = {"BUY": "b-buy", "SELL": "b-sell",
                "WEAK_HOLD": "b-weak"}.get(a, "b-lo")
        alabel = {"BUY": "BUY", "SELL": "SELL", "WEAK_HOLD": "WEAK HOLD"}.get(a, a)
        tier = ""
        if a == "BUY":
            t, _, _ = derive_buy_tier(p)
            if t and t != "—":
                tier = f" {html_escape(t)}"
        pwer = p.get("pwer")
        pw = f"{pwer:.1f}%" if pwer is not None else "—"
        w = p.get("weight")
        wt = f"{w:.2f}%" if w is not None else "—"
        out.append(
            f'<tr><td><span class="badge {bcls}">{alabel}{tier}</span></td>'
            f'<td><span class="tk">{html_escape(p.get("ticker", ""))}</span> '
            f'{html_escape(p.get("name", ""))}</td>'
            f'<td>{pw}</td><td>{wt}</td>'
            f'<td>{html_escape(explain_action(p, a))}</td></tr>')
    out.append("</table>")
    return "".join(out)


def _changes_list(d: dict) -> str:
    by_tk = {p.get("ticker"): p for p in d["positions"]}
    items = []
    for tk, nm, prev, now in d["flips"]:
        p = by_tk.get(tk)
        sub = (f'<div class="chg-sub">{html_escape(explain_action(p, now))}</div>'
               if p else "")
        items.append(f'<b>{html_escape(tk)} {html_escape(nm[:24])}</b> — '
                     f'verdict {html_escape(prev)} → {html_escape(now)}{sub}')
    if d["new_filing_tks"]:
        items.append(f'<b>{len(d["new_filing_tks"])} new EDINET filing(s)</b> — '
                     f'{html_escape(", ".join(d["new_filing_tks"]))}'
                     f'<div class="chg-sub">A filing on an anchor activist '
                     f'confirms or breaks the accumulation thesis — decode it '
                     f'in the dashboard Filings tab.</div>')
    for tk, pp in d["pmoves"][:5]:
        p = by_tk.get(tk)
        cls = "pos" if pp > 0 else "neg"
        sub = (f'<div class="chg-sub">{html_escape(_pwer_standing(p.get("pwer")))}'
               f' — thesis {"strengthening" if pp > 0 else "softening"} at spot.'
               f'</div>' if p else "")
        items.append(f'<b>{html_escape(tk)} {html_escape(d["name_of"].get(tk, "")[:24])}</b>'
                     f' — PWER <span class="{cls}">{pp:+.1f}pp</span> at spot{sub}')
    for tk, pc in d["xmoves"][:5]:
        p = by_tk.get(tk)
        cls = "pos" if pc > 0 else "neg"
        sub = (f'<div class="chg-sub">{html_escape(_pwer_standing(p.get("pwer")))}'
               f' after the re-rate.</div>' if p else "")
        items.append(f'<b>{html_escape(tk)} {html_escape(d["name_of"].get(tk, "")[:24])}</b>'
                     f' — price <span class="{cls}">{pc:+.1f}%</span>{sub}')
    if not items:
        return '<div class="empty">No changes since the last snapshot.</div>'
    return '<ul class="chg"><li>' + "</li><li>".join(items) + "</li></ul>"


def _filings_table(filings: list) -> str:
    if not filings:
        return '<div class="empty">No EDINET filings in the scan window.</div>'
    rank = {"HIGH": 0, "MED": 1, "LOW": 2}
    ordered = sorted(filings, key=lambda f: str(f.get("received_at", "")),
                     reverse=True)
    ordered = sorted(ordered, key=lambda f: rank.get(f.get("alert_priority", "LOW"), 3))
    out = ['<table><tr><th>Priority</th><th>Holding</th><th>Filing</th>'
           '<th>Filer</th><th>Date</th></tr>']
    for f in ordered[:14]:
        pr = f.get("alert_priority", "LOW")
        bcls = {"HIGH": "b-hi", "MED": "b-md"}.get(pr, "b-lo")
        out.append(
            f'<tr><td><span class="badge {bcls}">{html_escape(pr)}</span></td>'
            f'<td><span class="tk">{html_escape(f.get("ticker", ""))}</span> '
            f'{html_escape((f.get("name") or "")[:22])}</td>'
            f'<td>{html_escape(f.get("doc_type", ""))}</td>'
            f'<td class="mut">{html_escape((f.get("filer") or "—")[:30])}</td>'
            f'<td class="mut">{html_escape(str(f.get("received_at", ""))[:10])}</td></tr>')
    out.append("</table>")
    return "".join(out)


def _catalyst_table(cats: list) -> str:
    if not cats:
        return '<div class="empty">No catalysts inside the next 7 days.</div>'
    out = ['<table><tr><th>In</th><th>Holding</th><th>Catalyst</th><th>Date</th></tr>']
    for days, p in cats:
        out.append(
            f'<tr><td><b>{days}d</b></td>'
            f'<td><span class="tk">{html_escape(p.get("ticker", ""))}</span> '
            f'{html_escape(p.get("name", ""))}</td>'
            f'<td class="mut">{html_escape((p.get("catalyst") or "—")[:60])}</td>'
            f'<td class="mut">{html_escape(_short_date(p.get("catalyst_date")))}</td></tr>')
    out.append("</table>")
    return "".join(out)


def render_html(d: dict) -> str:
    title, marker, hero_cls = _title(d)
    m = d["metrics"]
    wp = d["wtd_pwer"]
    wp_cls = "good" if wp >= PWER_FLOOR else "warn"
    n = len(d["positions"])
    stub_s = f"{d['n_stub']} need enrichment" if d["n_stub"] else "all enriched"
    kpis = (
        _kpi("Wtd-Avg PWER", f"{wp:.1f}%", f"floor {PWER_FLOOR:.0f}%", wp_cls)
        + _kpi("Holdings", str(n), stub_s)
        + _kpi("BUYs", str(len(d["deploy"])), f"{len(d['reduce'])} to reduce")
        + _kpi("EDINET Filings", str(len(d["filings"])), "in the scan window")
    )
    flags_html = ('<ul class="chg"><li>'
                  + "</li><li>".join(html_escape(f) for f in d["flags"])
                  + "</li></ul>") if d["flags"] else \
        '<div class="empty">No standing flags — book is clean.</div>'
    actions = (_action_table(d["deploy"], lambda p: "BUY")
               + _action_table(d["reduce"], derive_action)) \
        if (d["deploy"] or d["reduce"]) else \
        '<div class="empty">No deploy or reduce actions today.</div>'
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Asuka Fund — Daily Risk Digest</title>
<style>{_CSS}</style></head><body>
<div class="hero {hero_cls}">
  <div class="eyebrow">🌅 Asuka Fund · Daily Risk Digest</div>
  <h1>{marker}{html_escape(title)}</h1>
  <div class="meta">{d['now'].strftime('%A %B %d, %Y · %H:%M JST')}
    &nbsp;·&nbsp; book as of {html_escape(d['as_of'])}</div>
</div>
<div class="wrap">
<div class="kpis">{kpis}</div>
<h2>Priority Actions</h2>
{actions}
<h2>Since Yesterday</h2>
{_changes_list(d)}
<h2>EDINET Filings</h2>
{_filings_table(d['filings'])}
<h2>Catalysts — Next 7 Days</h2>
{_catalyst_table(d['cats'])}
<h2>Standing Flags</h2>
{flags_html}
<div class="foot">
  Asuka Fund Risk Monitor · generated {d['now'].strftime('%Y-%m-%d %H:%M JST')}
  · PWER recomputed at live spot · deltas vs the previous snapshot.<br>
  Automated morning digest — internal GAO operations notification.
</div>
</div></body></html>"""


def render_text(d: dict) -> str:
    title, _, _ = _title(d)
    lines = [f"ASUKA FUND — DAILY RISK DIGEST — {d['now'].strftime('%a %b %d %Y')}",
             title, "",
             f"  Wtd-Avg PWER : {d['wtd_pwer']:.1f}%",
             f"  Holdings     : {len(d['positions'])}",
             f"  BUYs         : {len(d['deploy'])}   Reduce: {len(d['reduce'])}",
             f"  EDINET filings: {len(d['filings'])}", ""]
    if d["flips"]:
        lines.append("VERDICT FLIPS:")
        for tk, nm, prev, now in d["flips"]:
            lines.append(f"  {tk} {nm[:24]} — {prev} -> {now}")
    if d["flags"]:
        lines.append("STANDING FLAGS:")
        lines += [f"  - {f}" for f in d["flags"]]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Send (Gmail API, gmail.send scope)
# ─────────────────────────────────────────────────────────────────────────────

def _build_service():
    """Build a Gmail API service authorised for gmail.send only, using the
    sub-ops send token. Never runs an interactive OAuth flow — this script is
    unattended; a missing/invalid token fails loudly instead."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as e:
        raise DigestError(f"google-api-python-client not available: {e}")
    if not SEND_TOKEN.exists():
        raise DigestError(
            f"No gmail.send token at {SEND_TOKEN}. The sub-ops digest creates "
            f"it on its first authorised --send run. Authorise sending there "
            f"once (or place a gmail.send-scoped token at that path), then retry.")
    creds = Credentials.from_authorized_user_file(str(SEND_TOKEN),
                                                  [GMAIL_SEND_SCOPE])
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise DigestError("gmail.send token is invalid and cannot be "
                              "refreshed — re-authorise via the sub-ops digest.")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _send(subject: str, html: str) -> str:
    """Send the digest HTML to RECIPIENT. Returns the Gmail message id."""
    service = _build_service()
    msg = MIMEMultipart("alternative")
    msg["To"] = msg["From"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    try:
        sent = service.users().messages().send(
            userId="me", body={"raw": raw}).execute()
    except Exception as e:
        raise DigestError(f"Gmail send failed: {e}") from e
    return sent.get("id", "")


def _already_sent_today() -> bool:
    if not SEND_LOG_PATH.exists():
        return False
    try:
        log = json.loads(SEND_LOG_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return False
    return log.get("last_sent_date") == datetime.now(JST).strftime("%Y-%m-%d")


def _record_send(subject: str, msg_id: str) -> None:
    log = {"sends": []}
    if SEND_LOG_PATH.exists():
        try:
            log = json.loads(SEND_LOG_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log["last_sent_date"] = today
    log.setdefault("sends", []).append(
        {"date": today, "sent_at": datetime.now(JST).isoformat(),
         "subject": subject, "message_id": msg_id, "recipient": RECIPIENT})
    log["sends"] = log["sends"][-60:]
    SEND_LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2),
                             encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Asuka Fund morning email digest")
    parser.add_argument("--data", default=str(DATA_PATH))
    parser.add_argument("--send", action="store_true",
                        help="Email the digest to associates@gao-cap.com")
    parser.add_argument("--force", action="store_true",
                        help="Bypass the once-a-day idempotency guard on --send")
    parser.add_argument("--open", dest="do_open", action="store_true",
                        help="Open the rendered preview in a browser")
    args = parser.parse_args()

    data = load_json(args.data)
    for p in data.get("positions", []):
        recompute_pwer_at_spot(p)
    prev = load_previous_state()
    d = build_digest(data, prev)
    html = render_html(d)
    title, _, _ = _title(d)
    subject = f"Asuka Fund — Daily Risk Digest — {d['now'].strftime('%b %d')} — {title}"

    if not args.send:
        PREVIEW_PATH.write_text(html, encoding="utf-8")
        print(f"✓ Preview written: {PREVIEW_PATH}")
        print(f"  Subject would be: {subject}")
        print(f"  Recipient (on --send): {RECIPIENT}")
        print()
        print(render_text(d))
        if args.do_open:
            webbrowser.open(PREVIEW_PATH.as_uri())
        return 0

    if _already_sent_today() and not args.force:
        print("· digest already sent today — skipping (use --force to override)")
        return 0
    try:
        msg_id = _send(subject, html)
    except DigestError as e:
        print(f"✗ digest send failed: {e}", file=sys.stderr)
        return 1
    _record_send(subject, msg_id)
    print(f"✓ Digest sent to {RECIPIENT}  (message {msg_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
