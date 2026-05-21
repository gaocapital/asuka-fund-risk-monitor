"""
Fetch the latest CGSI Prime Services Position CSV from Gmail.

Production downloader for the broker-email automation. Authenticates with the
associates@ Gmail token, finds the most recent "(CGSI) Prime Services Report"
email carrying a Position CSV for the target account, and saves it to
broker/inbox/ — ready for apply_cgsi_update.py.

Unattended: no prompts, read-only Gmail scope, no mailbox writes. Exit code 0
on success, non-zero on failure (so a scheduler can detect a failed run).

Usage
-----
  python fetch_cgsi.py                  # account 111681A01 (the active book)
  python fetch_cgsi.py --account 109320
  python fetch_cgsi.py --token PATH     # override the token location
"""
import argparse
import base64
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEFAULT_TOKEN = r"C:\Users\Owner\sub-ops\token.json"
DEFAULT_ACCOUNT = "111681A01"          # the substantive ~21-name Japan book
INBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox")


def _authenticate(token_path: str) -> "Credentials | None":
    """Load the OAuth token, refreshing the access token in-memory if needed.
    The token file itself is never modified."""
    if not os.path.exists(token_path):
        print(f"[error] Gmail token not found: {token_path}", file=sys.stderr)
        return None
    try:
        creds = Credentials.from_authorized_user_file(token_path)
    except (ValueError, KeyError) as e:
        print(f"[error] token file is not a valid OAuth token: {e}", file=sys.stderr)
        return None
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("[error] token is invalid and cannot be refreshed", file=sys.stderr)
            return None
    return creds


def _attachments(payload: dict) -> list:
    """Flatten a Gmail message payload to [(filename, attachmentId, size)]."""
    out = []

    def walk(parts):
        for p in parts or []:
            if p.get("filename"):
                body = p.get("body", {})
                out.append((p["filename"], body.get("attachmentId"),
                            body.get("size", 0)))
            if p.get("parts"):
                walk(p["parts"])

    walk(payload.get("parts", []))
    return out


def fetch_latest_position_csv(account: str = DEFAULT_ACCOUNT,
                              token_path: str = DEFAULT_TOKEN,
                              inbox: str = INBOX) -> "str | None":
    """Find and download the most recent Position CSV for `account`.

    Returns the saved file path, or None on any failure. The subject line
    survives e-mail forwarding (it may gain a 'Fwd:' prefix), so the search
    is by subject and the account is matched on the attachment filename
    `{account}_Position_*.csv` — the definitive marker.
    """
    creds = _authenticate(token_path)
    if creds is None:
        return None

    svc = build("gmail", "v1", credentials=creds)
    res = svc.users().messages().list(
        userId="me", q='subject:"Prime Services Report"', maxResults=40).execute()
    msgs = res.get("messages", [])
    if not msgs:
        print("[error] no 'Prime Services Report' emails in the mailbox",
              file=sys.stderr)
        return None

    marker = f"{account}_Position_"
    # messages().list returns newest-first — the first match is the latest.
    for m in msgs:
        full = svc.users().messages().get(
            userId="me", id=m["id"], format="full").execute()
        for fn, aid, _sz in _attachments(full["payload"]):
            if aid and marker in fn and fn.lower().endswith(".csv"):
                data = svc.users().messages().attachments().get(
                    userId="me", messageId=m["id"], id=aid).execute()
                raw = base64.urlsafe_b64decode(data["data"])
                os.makedirs(inbox, exist_ok=True)
                out = os.path.join(inbox, fn)
                tmp = out + ".part"
                with open(tmp, "wb") as f:
                    f.write(raw)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, out)
                print(f"[ok] {fn}  ({len(raw):,} bytes)  ->  {out}")
                return out

    print(f"[error] searched {len(msgs)} 'Prime Services Report' emails — "
          f"no {account}_Position_*.csv attachment found", file=sys.stderr)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch the latest CGSI Prime Services Position CSV")
    parser.add_argument("--account", default=DEFAULT_ACCOUNT,
                        help="CGSI prime account code (default: 111681A01)")
    parser.add_argument("--token", default=DEFAULT_TOKEN,
                        help="Path to the Gmail OAuth token JSON")
    args = parser.parse_args()

    path = fetch_latest_position_csv(args.account, args.token)
    if not path:
        print(f"[done] FAILED — no CSV fetched for account {args.account}",
              file=sys.stderr)
        return 1
    print(f"[done] account {args.account} — saved {os.path.basename(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
