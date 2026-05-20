"""
Probe the CGSI broker-email path via the associates@ Gmail token.

Read-only test: confirms the token authenticates, which account it serves,
and what "(CGSI) Prime Services Report" emails + attachments are reachable.
Downloads the most recent *_Position_*.csv as end-to-end proof. No mailbox
writes; the token file is not modified (refresh happens in-memory only).
"""
import os
import sys
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = r"C:\Users\Owner\sub-ops\token.json"
INBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox")
os.makedirs(INBOX, exist_ok=True)


def main() -> int:
    creds = Credentials.from_authorized_user_file(TOKEN)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("[auth] access token had expired — refreshed in-memory via refresh_token OK")
        else:
            print("[auth] FAILED — token is invalid and cannot be refreshed")
            return 1
    print(f"[auth] scopes: {creds.scopes}")

    svc = build("gmail", "v1", credentials=creds)
    prof = svc.users().getProfile(userId="me").execute()
    print(f"[auth] token serves account: {prof['emailAddress']}  (total messages: {prof.get('messagesTotal')})")

    q = 'subject:"Prime Services Report"'
    res = svc.users().messages().list(userId="me", q=q, maxResults=25).execute()
    msgs = res.get("messages", [])
    print(f"\n[search] {q}  ->  {len(msgs)} message(s)")

    position_csvs = []
    for m in msgs:
        full = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
        hdrs = {h["name"].lower(): h["value"] for h in full["payload"].get("headers", [])}
        atts = []

        def walk(parts):
            for p in parts:
                if p.get("filename"):
                    atts.append((p["filename"], p["body"].get("attachmentId"), p["body"].get("size", 0)))
                if p.get("parts"):
                    walk(p["parts"])

        walk(full["payload"].get("parts", []) or [])
        print(f"  - {hdrs.get('date', '?')[:31]} | {hdrs.get('from', '?')[:42]} | {hdrs.get('subject', '?')[:52]}")
        for fn, aid, sz in atts:
            is_pos = "_Position_" in fn and fn.lower().endswith(".csv")
            print(f"      attachment: {fn}  ({sz} bytes){'   <-- POSITION CSV' if is_pos else ''}")
            if is_pos:
                position_csvs.append((m["id"], fn, aid))

    if position_csvs:
        mid, fn, aid = position_csvs[0]
        data = svc.users().messages().attachments().get(userId="me", messageId=mid, id=aid).execute()
        raw = base64.urlsafe_b64decode(data["data"])
        out = os.path.join(INBOX, fn)
        with open(out, "wb") as f:
            f.write(raw)
        print(f"\n[download] {fn}  ->  {out}  ({len(raw):,} bytes)")
        print("[download] header + first row:")
        for line in raw.decode("utf-8", "replace").splitlines()[:2]:
            print("   ", line[:150])
        print("\n[result] PASS — token works, account reachable, Position CSV fetched end-to-end.")
    else:
        print("\n[result] Token works, but no '*_Position_*.csv' attachment in the matched emails.")
        print("         (If 0 messages: associates@ has no CGSI mail yet — forward one to test today.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
