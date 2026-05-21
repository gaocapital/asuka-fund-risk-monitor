"""
Asuka Fund Risk Monitor - dashboard renderer (Modern Dark, v2).

Presentation layer. Reads dashboard_data.json, computes day-over-day deltas
vs the previous snapshot, and renders a single self-contained dashboard.html:
a pinned top zone (brand, KPIs, Today's Actions hero) over four tabbed
sections (Positions, Risk, Catalysts, Watch).

All data/analytics logic lives in dashboard_core.py. Entry point for the
daily pipeline:  python generate_dashboard.py
"""
from __future__ import annotations

import argparse
from datetime import date, datetime

from dashboard_core import (
    DEFAULT_DATA_PATH, DEFAULT_OUT_PATH, STATE_DIR, PWER_HIGH, PWER_MID,
    load_json, _atomic_write_text, save_state_snapshot, load_previous_state,
    recompute_pwer_at_spot, compute_deltas, compute_portfolio_metrics,
    derive_action, derive_buy_tier, compute_price_freshness,
    wac_delta_pct, html_escape, fmt_num,
)

PWER_FLOOR = 15.0   # per-position PWER floor — risk-view threshold

CSS_STYLE = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--s1:#161b22;--s2:#1c2433;--s3:#12171f;--line:#2a313c;--lsoft:#1c232c;
  --tx:#e6edf3;--mut:#8b949e;--dim:#6e7681;
  --ac:#4d9fff;--pos:#3fb950;--neg:#f85149;--warn:#d6a533;
}
html,body{background:var(--bg);color:var(--tx);
  font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  font-size:13.5px;line-height:1.5;-webkit-font-smoothing:antialiased}
body{max-width:1880px;margin:0 auto;padding:20px 30px 60px}
.n{font-variant-numeric:tabular-nums}
.pos{color:var(--pos)}.neg{color:var(--neg)}.warn{color:var(--warn)}
.mut{color:var(--mut)}.dim{color:var(--dim)}
a{color:var(--ac);text-decoration:none}

/* ===== header ===== */
.topbar{display:flex;justify-content:space-between;align-items:center;
  padding:6px 4px 18px}
.brand{display:flex;align-items:center;gap:12px}
.brand-mark{width:32px;height:32px;border-radius:8px;
  background:linear-gradient(135deg,#4d9fff,#2d6fd6);
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:17px;color:#0b0e13}
.brand-name{font-size:18px;font-weight:800;letter-spacing:.08em}
.brand-tag{font-size:12px;color:var(--mut);border-left:1px solid var(--line);
  padding-left:12px;margin-left:3px}
.topbar-right{display:flex;align-items:center;gap:14px;font-size:12px}
.asof{color:var(--mut)}
.fresh{display:flex;align-items:center;gap:7px;background:var(--s1);
  border:1px solid var(--line);padding:6px 11px;border-radius:7px;color:var(--mut)}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot-ok{background:var(--pos);box-shadow:0 0 6px rgba(63,185,80,.6)}
.dot-warn{background:var(--warn);box-shadow:0 0 6px rgba(214,165,51,.55)}

/* ===== kpi strip ===== */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:14px}
.kpi{background:var(--s1);border:1px solid var(--line);border-radius:10px;
  padding:13px 15px;box-shadow:0 1px 2px rgba(0,0,0,.3)}
.kpi-l{font-size:9.5px;font-weight:700;letter-spacing:.1em;color:var(--mut);
  text-transform:uppercase}
.kpi-v{font-size:26px;font-weight:700;margin-top:6px;letter-spacing:-.01em}
.kpi-s{font-size:10.5px;margin-top:4px;color:var(--dim)}

/* ===== hero ===== */
.hero{background:var(--s2);border:1px solid var(--line);border-radius:12px;
  overflow:hidden;box-shadow:0 8px 26px rgba(0,0,0,.3);margin-bottom:16px}
.hero-head{display:flex;justify-content:space-between;align-items:center;
  padding:13px 18px;border-bottom:1px solid var(--line)}
.hero-title{display:flex;align-items:center;gap:10px;font-size:13px;
  font-weight:800;letter-spacing:.13em}
.hero-title::before{content:"";width:3px;height:15px;background:var(--ac);
  border-radius:2px}
.hero-meta{font-size:11.5px;color:var(--mut)}
.hero-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
  background:var(--line)}
.hcol{background:var(--s2);padding:14px 16px}
.hcol-h{display:flex;align-items:center;gap:8px;font-size:10.5px;font-weight:800;
  letter-spacing:.1em;color:var(--mut);margin-bottom:11px}
.hcol-h .hd{width:9px;height:9px;border-radius:2px}
.hd-add{background:var(--pos)}.hd-red{background:var(--neg)}.hd-flg{background:var(--warn)}
.act{background:var(--s1);border:1px solid var(--line);border-radius:9px;
  padding:10px 12px;margin-bottom:8px}
.act:last-child{margin-bottom:0}
.act-top{display:flex;align-items:center;gap:8px}
.act-tk{font-size:12.5px;font-weight:700}
.act-pw{margin-left:auto;font-size:10.5px;font-weight:700;color:var(--mut)}
.act-why{font-size:11px;color:var(--mut);margin:6px 0}
.act-nums{display:flex;gap:14px;font-size:10px;color:var(--dim)}
.hero-empty{font-size:11.5px;color:var(--dim);font-style:italic;padding:6px 2px}
.flag{display:flex;gap:9px;align-items:flex-start;background:var(--s1);
  border:1px solid var(--line);border-left-width:2px;border-radius:8px;
  padding:9px 11px;margin-bottom:8px;font-size:11px;color:var(--mut)}
.flag:last-child{margin-bottom:0}
.flag-w{border-left-color:var(--warn)}.flag-r{border-left-color:var(--neg)}
.flag-b{border-left-color:var(--ac)}
.flag-i{width:16px;height:16px;border-radius:50%;flex:0 0 16px;display:flex;
  align-items:center;justify-content:center;font-size:10px;font-weight:800;margin-top:1px}
.flag-w .flag-i{background:rgba(214,165,51,.16);color:var(--warn)}
.flag-r .flag-i{background:rgba(248,81,73,.16);color:var(--neg)}
.flag-b .flag-i{background:rgba(77,159,255,.16);color:var(--ac)}
.flag b{color:var(--tx);font-weight:700}

/* ===== badges ===== */
.badge{font-size:9.5px;font-weight:800;padding:3px 7px;border-radius:4px;
  letter-spacing:.04em;white-space:nowrap}
.bg-buy{background:rgba(63,185,80,.15);color:#56c869;border:1px solid rgba(63,185,80,.4)}
.bg-hold{background:rgba(139,148,158,.13);color:#a3acb6;border:1px solid rgba(139,148,158,.32)}
.bg-weak{background:rgba(214,165,51,.14);color:#dcb04a;border:1px solid rgba(214,165,51,.4)}
.bg-sell{background:rgba(248,81,73,.14);color:#ff6b63;border:1px solid rgba(248,81,73,.4)}
.bg-watch{background:rgba(77,159,255,.12);color:#6fb1ff;border:1px solid rgba(77,159,255,.34)}
.bg-stale{background:rgba(214,165,51,.1);color:#c79b34;border:1px solid rgba(214,165,51,.3)}
.bg-quar{background:#7f1d1d;color:#fff;border:1px solid #b91c1c}
.tier{font-size:8.5px;font-weight:800;padding:2px 5px;border-radius:3px;letter-spacing:.03em}
.tier-aaa{background:rgba(63,185,80,.22);color:#56c869;border:1px solid rgba(63,185,80,.55)}
.tier-aa{background:rgba(63,185,80,.12);color:#56c869;border:1px solid rgba(63,185,80,.35)}
.tier-a{background:rgba(77,159,255,.12);color:#6fb1ff;border:1px solid rgba(77,159,255,.35)}
.tier-b{background:rgba(214,165,51,.1);color:#dcb04a;border:1px solid rgba(214,165,51,.3)}

/* ===== tabs ===== */
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);
  position:sticky;top:0;background:var(--bg);z-index:20;padding-top:4px}
.tab{display:flex;align-items:center;gap:8px;padding:12px 18px;font-size:13px;
  color:var(--mut);border-bottom:2px solid transparent;cursor:pointer;
  user-select:none}
.tab:hover{color:var(--tx)}
.tab.on{color:var(--tx);font-weight:600;border-bottom-color:var(--ac)}
.tab-c{font-size:10px;background:var(--s1);border:1px solid var(--line);
  color:var(--mut);padding:1px 7px;border-radius:9px}
.tab.on .tab-c{background:rgba(77,159,255,.14);border-color:rgba(77,159,255,.3);
  color:var(--ac)}
.tabpane{padding-top:18px}
.tabpane[hidden]{display:none}

/* ===== positions tab ===== */
.ptools{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.pchip{font-size:11px;color:var(--mut);background:var(--s1);
  border:1px solid var(--line);padding:6px 12px;border-radius:7px;cursor:pointer;
  user-select:none}
.pchip:hover{color:var(--tx)}
.pchip.on{color:var(--ac);border-color:rgba(77,159,255,.4);background:rgba(77,159,255,.08)}
.psearch{margin-left:auto;font-size:12px;color:var(--tx);background:var(--s1);
  border:1px solid var(--line);padding:7px 12px;border-radius:7px;min-width:230px;
  font-family:inherit}
.psearch::placeholder{color:var(--dim)}
.grid8{display:grid;
  grid-template-columns:minmax(220px,2.4fr) 64px 152px 156px 88px 124px minmax(190px,2fr) 34px;
  align-items:center}
.pthead{padding:9px 12px;border-bottom:1px solid var(--line)}
.pthead>div{font-size:9.5px;font-weight:700;letter-spacing:.09em;color:var(--mut);
  text-transform:uppercase}
.plgroup{display:flex;align-items:baseline;gap:10px;padding:16px 12px 7px}
.pl-t{font-size:10.5px;font-weight:800;letter-spacing:.1em;color:var(--tx)}
.pl-m{font-size:10.5px;color:var(--dim)}
.pl-line{flex:1;height:1px;background:var(--line)}
.prow{padding:11px 12px;border-bottom:1px solid var(--lsoft);cursor:pointer}
.prow:hover{background:#1a212b}
.prow.exp{background:#1a2433;border-bottom-color:var(--line)}
.pc-name{display:flex;align-items:center;gap:10px;min-width:0}
.pc-tk{font-size:11px;font-weight:700;color:var(--mut);background:var(--s1);
  border:1px solid var(--line);padding:2px 6px;border-radius:4px;flex:0 0 auto}
.pc-nm{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.pc-by{font-size:10px;color:var(--dim);margin-top:1px}
.lb{font-size:9px;font-weight:800;padding:2.5px 6px;border-radius:3px;
  letter-spacing:.03em}
.lb-l1{background:rgba(77,159,255,.16);color:#6fb1ff}
.lb-l2{background:rgba(63,185,80,.14);color:#56c869}
.lb-l3{background:rgba(139,148,158,.13);color:#a3acb6}
.lb-lp{background:rgba(214,165,51,.14);color:#dcb04a}
.lb-l4{background:rgba(236,72,153,.14);color:#ec6fb0}
.pc-wv{font-size:13px;font-weight:700}
.pc-sub{font-size:9.5px;margin-top:2px;color:var(--dim)}
.pc-pv{font-size:12.5px;font-weight:600}
.pw{font-size:15px;font-weight:700}
.pw-hi{color:var(--pos)}.pw-mid{color:var(--warn)}.pw-lo{color:var(--neg)}
.pw-na{color:var(--dim);font-size:13px}
.pc-cat{font-size:10.5px;color:var(--mut);line-height:1.35}
.cat-d{display:inline-block;font-size:8.5px;font-weight:700;margin-top:3px;
  padding:1.5px 7px;border-radius:9px;background:rgba(77,159,255,.1);
  color:var(--ac);border:1px solid rgba(77,159,255,.25)}
.cat-d.soon{background:rgba(214,165,51,.12);color:var(--warn);
  border-color:rgba(214,165,51,.3)}
.cat-d.past{background:var(--s1);color:var(--dim);border-color:var(--line)}
.chev{text-align:center;color:var(--dim);font-size:11px}
.enrich{font-size:8.5px;font-weight:800;letter-spacing:.04em;color:var(--warn);
  background:rgba(214,165,51,.12);border:1px solid rgba(214,165,51,.32);
  padding:2px 6px;border-radius:3px}

/* ===== expanded thesis ===== */
.pexp-row[hidden]{display:none}
.pexp{background:var(--s3);border-bottom:1px solid var(--line);padding:18px 22px}
.pexp-grid{display:grid;grid-template-columns:1.05fr 1.4fr;gap:26px}
.pexp-h{font-size:9.5px;font-weight:800;letter-spacing:.11em;color:var(--mut);
  margin-bottom:11px}
.scen{display:flex;flex-direction:column;gap:8px}
.scen-row{display:grid;grid-template-columns:52px 1fr 40px 62px;align-items:center;
  gap:10px}
.scen-l{font-size:10.5px;color:var(--mut);font-weight:600}
.scen-track{height:15px;background:var(--s1);border-radius:3px;overflow:hidden}
.scen-fill{height:100%;border-radius:3px}
.scen-p{font-size:10.5px;color:var(--dim);text-align:right}
.scen-r{font-size:11px;font-weight:700;text-align:right}
.pexp-foot{margin-top:12px;padding-top:10px;border-top:1px solid var(--line);
  font-size:11px;color:var(--mut)}
.pexp-foot b{color:var(--pos);font-size:13px}
.pexp p{font-size:12px;color:var(--mut);margin-bottom:12px;line-height:1.6}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:8px 20px}
.kv-i{display:flex;justify-content:space-between;font-size:11px;
  border-bottom:1px solid var(--lsoft);padding-bottom:6px}
.kv-k{color:var(--dim)}.kv-v{color:var(--tx);font-weight:600}
.pexp-stub{font-size:12px;color:var(--mut);line-height:1.6}

/* ===== risk tab ===== */
.stat4{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:16px}
.stat{background:var(--s1);border:1px solid var(--line);border-radius:10px;
  padding:13px 15px}
.stat-warn{border-left:2px solid var(--warn)}
.stat-neg{border-left:2px solid var(--neg)}
.stat-l{font-size:9.5px;font-weight:700;letter-spacing:.1em;color:var(--mut);
  text-transform:uppercase}
.stat-v{font-size:23px;font-weight:700;margin-top:6px}
.stat-s{font-size:10.5px;margin-top:3px;color:var(--dim)}
.card{background:var(--s1);border:1px solid var(--line);border-radius:12px;
  margin-bottom:16px}
.card-h{display:flex;justify-content:space-between;align-items:baseline;
  padding:13px 16px;border-bottom:1px solid var(--line)}
.card-t{display:flex;align-items:center;gap:9px;font-size:11.5px;font-weight:800;
  letter-spacing:.09em}
.card-t::before{content:"";width:3px;height:13px;background:var(--ac);
  border-radius:2px}
.card-sub{font-size:10.5px;color:var(--dim)}
.card-b{padding:16px}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}

/* scatter / conviction matrix */
.scatter{position:relative;height:380px;padding:10px 12px 34px 50px}
.sc-ylab{position:absolute;left:6px;top:50%;
  transform:rotate(-90deg) translateX(50%);transform-origin:left;
  font-size:9.5px;color:var(--mut);letter-spacing:.09em;white-space:nowrap}
.sc-yt{position:absolute;left:24px;font-size:9.5px;color:var(--dim);
  transform:translateY(-50%)}
.sc-plot{position:relative;height:100%;border-left:1px solid var(--line);
  border-bottom:1px solid var(--line)}
.sc-q{position:absolute;display:flex;padding:9px 11px;font-size:9.5px;
  font-weight:800;letter-spacing:.06em}
.sc-q small{font-weight:600;letter-spacing:.02em;font-size:8.5px;display:block;
  margin-top:2px}
.sc-q-tl{top:0;left:0;width:25%;height:57.1%;background:rgba(248,81,73,.07);
  align-items:flex-start;justify-content:flex-start;color:#c9605b}
.sc-q-tr{top:0;left:25%;right:0;height:57.1%;background:rgba(77,159,255,.06);
  align-items:flex-start;justify-content:flex-end;color:#5f93c9;text-align:right}
.sc-q-bl{bottom:0;left:0;width:25%;height:42.9%;background:rgba(139,148,158,.05);
  align-items:flex-end;justify-content:flex-start;color:var(--dim)}
.sc-q-br{bottom:0;left:25%;right:0;height:42.9%;background:rgba(63,185,80,.07);
  align-items:flex-end;justify-content:flex-end;color:#4f9e5b;text-align:right}
.sc-floor{position:absolute;top:0;bottom:0;left:25%;
  border-left:1px dashed rgba(214,165,51,.55)}
.sc-floor span{position:absolute;top:4px;left:5px;font-size:8.5px;
  color:var(--warn);white-space:nowrap}
.sc-dot{position:absolute;border-radius:50%;transform:translate(-50%,50%);
  border:1.5px solid rgba(13,17,23,.8);box-shadow:0 2px 6px rgba(0,0,0,.45)}
.sc-l1{background:#4d9fff}.sc-l2{background:#3fb950}
.sc-l3{background:#8b949e}.sc-lp{background:#d6a533}.sc-l4{background:#ec6fb0}
.sc-tag{position:absolute;left:50%;bottom:calc(100% + 4px);
  transform:translateX(-50%);font-size:9px;font-weight:700;color:var(--tx);
  background:rgba(13,17,23,.9);padding:1px 6px;border-radius:3px;white-space:nowrap}
.sc-xt{position:absolute;bottom:16px;font-size:9.5px;color:var(--dim);
  transform:translateX(-50%)}
.sc-xlab{position:absolute;bottom:2px;left:50px;right:12px;text-align:center;
  font-size:9.5px;color:var(--mut);letter-spacing:.08em}
.sc-leg{display:flex;gap:16px;padding:0 16px 14px;font-size:10px;color:var(--mut);
  flex-wrap:wrap}
.sc-leg span{display:flex;align-items:center;gap:6px}
.sc-leg i{width:10px;height:10px;border-radius:50%;display:inline-block}

/* donut */
.donut-wrap{display:flex;align-items:center;gap:20px}
.donut{width:136px;height:136px;border-radius:50%;flex:0 0 136px;position:relative}
.donut::after{content:"";position:absolute;inset:33px;background:var(--s1);
  border-radius:50%}
.donut-c{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;z-index:1}
.donut-c b{font-size:18px;font-weight:700}
.donut-c span{font-size:9px;color:var(--dim);letter-spacing:.05em}
.leg{display:flex;flex-direction:column;gap:9px;flex:1}
.leg-i{display:flex;align-items:center;gap:9px;font-size:11.5px}
.leg-d{width:11px;height:11px;border-radius:3px;flex:0 0 11px}
.leg-n{color:var(--mut)}.leg-v{margin-left:auto;font-weight:700}

/* horizontal bars */
.hbars{display:flex;flex-direction:column;gap:10px}
.hbar{display:grid;grid-template-columns:104px 1fr 44px;gap:10px;align-items:center}
.hbar-l{font-size:10.5px;color:var(--mut);text-align:right;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.hbar-tr{height:16px;background:var(--s3);border-radius:3px;overflow:hidden}
.hbar-f{height:100%;border-radius:3px;background:linear-gradient(90deg,#3a7fc4,#4d9fff)}
.hbar-f.amber{background:linear-gradient(90deg,#a8801f,#d6a533)}
.hbar-v{font-size:10.5px;font-weight:700;text-align:right}

/* histogram */
.histo{display:flex;align-items:flex-end;gap:10px;height:170px;padding-top:16px;
  position:relative}
.hb{flex:1;display:flex;flex-direction:column;align-items:center;
  justify-content:flex-end;height:100%;gap:6px}
.hb-bar{width:100%;border-radius:3px 3px 0 0;min-height:3px}
.hb-below{background:linear-gradient(180deg,#d6a533,#9c7720)}
.hb-above{background:linear-gradient(180deg,#3fb950,#2a7d37)}
.hb-na{background:linear-gradient(180deg,#5a626c,#3a4049)}
.hb-c{font-size:12px;font-weight:700}
.hb-l{font-size:8.5px;color:var(--dim);text-align:center}
.histo-floor{position:absolute;top:0;bottom:24px;
  border-left:1px dashed rgba(214,165,51,.6)}
.histo-floor span{position:absolute;top:-3px;left:6px;font-size:8.5px;
  color:var(--warn);white-space:nowrap}

/* ===== interactivity — tooltips & sortable headers ===== */
.charttip{position:fixed;z-index:60;pointer-events:none;max-width:252px;
  background:#0b0e13;border:1px solid var(--line);border-radius:7px;
  padding:8px 11px;font-size:10.5px;line-height:1.55;color:var(--mut);
  box-shadow:0 8px 26px rgba(0,0,0,.6)}
.charttip[hidden]{display:none}
.charttip b{color:var(--tx);font-weight:700;font-size:11px}
.sc-dot{transition:transform .1s ease,box-shadow .1s ease}
.sc-dot:hover{transform:translate(-50%,50%) scale(1.4);border-color:var(--tx);
  box-shadow:0 4px 13px rgba(0,0,0,.75);cursor:pointer;z-index:6}
.hb{cursor:pointer}
.hb-bar{transition:filter .1s ease}
.hb:hover .hb-bar{filter:brightness(1.28)}
.hbar{cursor:pointer}
.hbar-f{transition:filter .1s ease}
.hbar:hover .hbar-f{filter:brightness(1.22)}
.pthead>div.sortable{cursor:pointer;user-select:none;display:flex;
  align-items:center;gap:4px;transition:color .1s ease}
.pthead>div.sortable:hover{color:var(--tx)}
.pthead>div.sort-on{color:var(--ac)}
.sort-ar{font-size:7px;line-height:1}

/* ===== catalysts tab ===== */
.tl{padding:10px 6px 4px}
.tl-months{position:relative;height:18px;margin-bottom:5px}
.tl-months span{position:absolute;font-size:9.5px;font-weight:700;
  color:var(--mut);letter-spacing:.04em}
.tl-track{position:relative;height:9px;background:var(--s3);border-radius:5px;
  margin-bottom:96px}
.tl-grid{position:absolute;top:-5px;bottom:-5px;border-left:1px solid var(--line)}
.tl-today{position:absolute;top:-11px;bottom:-86px;border-left:2px solid var(--ac)}
.tl-today span{position:absolute;top:-16px;left:-17px;font-size:8.5px;
  font-weight:800;color:var(--ac);letter-spacing:.06em}
.tl-ev{position:absolute;top:5px}
.tl-dot{position:absolute;top:1px;left:-5px;width:11px;height:11px;
  border-radius:50%;background:var(--ac);border:2px solid var(--bg)}
.tl-dot.soon{background:var(--warn)}
.tl-pill{position:absolute;top:20px;transform:translateX(-50%);width:148px;
  background:var(--s2);border:1px solid var(--line);border-radius:8px;padding:7px 9px}
.tl-pill.soon{border-color:rgba(214,165,51,.4)}
.tl-d{font-size:9px;font-weight:800;color:var(--ac);letter-spacing:.03em}
.tl-d.soon{color:var(--warn)}
.tl-x{font-size:10.5px;font-weight:700;margin-top:2px}
.tl-w{font-size:9px;color:var(--dim);margin-top:2px;line-height:1.35}
.clist{display:flex;flex-direction:column}
.cl-row{display:grid;grid-template-columns:60px minmax(150px,1.4fr) 2fr 70px;
  gap:13px;align-items:center;padding:11px;border-bottom:1px solid var(--lsoft)}
.cl-row:last-child{border-bottom:none}
.cl-cd{font-size:9.5px;font-weight:800;text-align:center;padding:5px 0;
  border-radius:6px;background:rgba(77,159,255,.1);color:var(--ac);
  border:1px solid rgba(77,159,255,.25)}
.cl-cd.soon{background:rgba(214,165,51,.12);color:var(--warn);
  border-color:rgba(214,165,51,.3)}
.cl-nm{font-size:12.5px;font-weight:600}
.cl-tk{font-size:10px;color:var(--dim)}
.cl-ev{font-size:11px;color:var(--mut)}
.cl-date{font-size:10px;color:var(--dim);text-align:right}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:34px 16px;text-align:center}
.empty-i{width:42px;height:42px;border-radius:11px;background:var(--s3);
  border:1px solid var(--line);display:flex;align-items:center;justify-content:center;
  font-size:20px;color:var(--dim);margin-bottom:11px}
.empty-t{font-size:12.5px;color:var(--mut);font-weight:600}
.empty-s{font-size:10.5px;color:var(--dim);margin-top:5px;line-height:1.5}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:16px}

/* ===== watch tab ===== */
.stat3{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-bottom:16px}
.wtable{width:100%;border-collapse:collapse}
.wtable th{font-size:9.5px;font-weight:700;letter-spacing:.08em;color:var(--mut);
  text-transform:uppercase;text-align:left;padding:10px 12px;
  border-bottom:1px solid var(--line)}
.wtable td{padding:11px 12px;border-bottom:1px solid var(--lsoft);font-size:12px;
  vertical-align:top}
.wtable tr:last-child td{border-bottom:none}
.wt-tk{font-size:10.5px;font-weight:700;color:var(--mut);background:var(--s3);
  border:1px solid var(--line);padding:2px 6px;border-radius:4px}
.wt-nm{font-weight:600}
.chip{font-size:9.5px;font-weight:700;padding:3px 8px;border-radius:10px;
  background:rgba(77,159,255,.1);color:#6fb1ff;border:1px solid rgba(77,159,255,.25);
  white-space:nowrap}
.wt-note{color:var(--mut);font-size:11px}
.dropped{font-size:8.5px;font-weight:800;color:var(--dim);background:var(--s3);
  border:1px solid var(--line);padding:1.5px 6px;border-radius:3px;
  letter-spacing:.03em;margin-right:5px}
.addrow{display:flex;align-items:center;gap:9px;padding:11px 12px;font-size:11px;
  color:var(--ac);background:rgba(77,159,255,.05);border-top:1px solid var(--line)}

/* ===== footer ===== */
footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  font-size:10.5px;color:var(--dim);line-height:1.7}
"""

DASHBOARD_JS = """
(function(){
  function tab(t){
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.tabpane').forEach(x=>{x.hidden=true;});
    t.classList.add('on');
    var pane=document.getElementById(t.dataset.pane);
    if(pane) pane.hidden=false;
  }
  document.querySelectorAll('.tab').forEach(function(t){
    t.addEventListener('click',function(){tab(t);});
  });

  document.querySelectorAll('.prow').forEach(function(r){
    r.addEventListener('click',function(){
      var x=r.nextElementSibling;
      if(x && x.classList.contains('pexp-row')){
        var open=(x.hidden===false);
        x.hidden=open;
        r.classList.toggle('exp',!open);
      }
    });
  });

  var curLayer='all';
  function applyFilter(){
    var box=document.getElementById('psearch');
    var q=(box?box.value:'').toLowerCase().trim();
    document.querySelectorAll('.prow').forEach(function(r){
      var okL=(curLayer==='all')||(r.dataset.layer===curLayer)||
              (curLayer==='enrich' && r.dataset.enrich==='1');
      var okQ=(!q)||((r.dataset.name||'').indexOf(q)>-1);
      var show=okL&&okQ;
      r.hidden=!show;
      var x=r.nextElementSibling;
      if(x && x.classList.contains('pexp-row') && !show){
        x.hidden=true; r.classList.remove('exp');
      }
    });
    document.querySelectorAll('.plgroup').forEach(function(g){
      var lay=g.dataset.layer;
      var vis=document.querySelectorAll('.prow[data-layer="'+lay+'"]:not([hidden])').length;
      g.hidden=(vis===0);
    });
  }
  document.querySelectorAll('.pchip').forEach(function(c){
    c.addEventListener('click',function(){
      document.querySelectorAll('.pchip').forEach(function(x){x.classList.remove('on');});
      c.classList.add('on');
      curLayer=c.dataset.layer;
      applyFilter();
    });
  });
  var sb=document.getElementById('psearch');
  if(sb) sb.addEventListener('input',applyFilter);
})();

/* ---- chart tooltips (conviction matrix, histogram, activist bars) ---- */
(function(){
  var tip=document.createElement('div');
  tip.className='charttip'; tip.hidden=true;
  document.body.appendChild(tip);
  function place(e){
    var off=14, x=e.clientX+off, y=e.clientY+off;
    var w=tip.offsetWidth, h=tip.offsetHeight;
    if(x+w>window.innerWidth-8) x=e.clientX-w-off;
    if(y+h>window.innerHeight-8) y=e.clientY-h-off;
    tip.style.left=(x<8?8:x)+'px';
    tip.style.top=(y<8?8:y)+'px';
  }
  function show(el){
    var lines=(el.getAttribute('data-tip')||'').split('\\n');
    tip.textContent='';
    lines.forEach(function(ln,i){
      if(i) tip.appendChild(document.createElement('br'));
      if(i===0){
        var b=document.createElement('b'); b.textContent=ln; tip.appendChild(b);
      } else {
        tip.appendChild(document.createTextNode(ln));
      }
    });
    tip.hidden=false;
  }
  document.querySelectorAll('[data-tip]').forEach(function(el){
    el.addEventListener('mouseenter',function(){show(el);});
    el.addEventListener('mousemove',place);
    el.addEventListener('mouseleave',function(){tip.hidden=true;});
  });
})();

/* ---- positions-table column sort (sorts within each layer group) ---- */
(function(){
  var heads=document.querySelectorAll('.pthead>div.sortable');
  if(!heads.length) return;
  var state={col:'weight',dir:-1};   // matches the server-side default order

  function defaultDir(col){
    return (col==='name'||col==='action'||col==='catalyst')?1:-1;
  }
  function missing(row,col){
    if(col==='name') return !row.dataset.name;
    var v=row.getAttribute('data-sort-'+col);
    return v===null||v===''||isNaN(parseFloat(v));
  }
  function key(row,col){
    if(col==='name') return row.dataset.name||'';
    return parseFloat(row.getAttribute('data-sort-'+col));
  }
  function sortNow(){
    var table=document.querySelector('.ptable'); if(!table) return;
    var col=state.col, dir=state.dir, pthead=null, segs=[], cur=null;
    Array.prototype.slice.call(table.children).forEach(function(el){
      if(el.classList.contains('pthead')){ pthead=el; }
      else if(el.classList.contains('plgroup')){ cur={head:el,pairs:[]}; segs.push(cur); }
      else if(el.classList.contains('prow') && cur){
        var ex=el.nextElementSibling;
        ex=(ex && ex.classList.contains('pexp-row'))?ex:null;
        cur.pairs.push({row:el,exp:ex});
      }
    });
    segs.forEach(function(seg){
      seg.pairs.sort(function(a,b){
        var am=missing(a.row,col), bm=missing(b.row,col);
        if(am&&bm) return 0;
        if(am) return 1;
        if(bm) return -1;
        var av=key(a.row,col), bv=key(b.row,col);
        if(av<bv) return -dir;
        if(av>bv) return dir;
        return 0;
      });
    });
    if(pthead) table.appendChild(pthead);
    segs.forEach(function(seg){
      table.appendChild(seg.head);
      seg.pairs.forEach(function(pr){
        table.appendChild(pr.row);
        if(pr.exp) table.appendChild(pr.exp);
      });
    });
  }
  function carets(){
    heads.forEach(function(h){
      var on=(h.getAttribute('data-sort')===state.col);
      h.classList.toggle('sort-on',on);
      var ar=h.querySelector('.sort-ar');
      if(ar) ar.textContent=on?(state.dir<0?'▼':'▲'):'';
    });
  }
  heads.forEach(function(h){
    h.addEventListener('click',function(){
      var col=h.getAttribute('data-sort');
      if(state.col===col){ state.dir=-state.dir; }
      else { state.col=col; state.dir=defaultDir(col); }
      sortNow(); carets();
    });
  });
  carets();   // reflect the initial weight-descending order
})();
"""

# ============================================================================
# RENDER HELPERS
# ============================================================================

ACTION_BADGE = {
    "BUY": ("BUY", "bg-buy"),
    "HOLD": ("HOLD", "bg-hold"),
    "WEAK_HOLD": ("WEAK HOLD", "bg-weak"),
    "SELL": ("SELL", "bg-sell"),
    "WATCH": ("WATCH", "bg-watch"),
    "STALE_INPUTS": ("STALE", "bg-stale"),
    "STALE_SCEN": ("STALE SCEN", "bg-stale"),
    "DATA_QUARANTINE": ("QUARANTINE", "bg-quar"),
}
# Action priority for the positions-table column sort — BUYs first, dead names last.
ACTION_SORT_RANK = {
    "BUY": 0, "HOLD": 1, "WEAK_HOLD": 2, "SELL": 3, "WATCH": 4,
    "STALE_INPUTS": 5, "STALE_SCEN": 6, "DATA_QUARANTINE": 7,
}
LAYER_CLS = {"L1": "lb-l1", "L2": "lb-l2", "L3": "lb-l3",
             "L3-PAH": "lb-lp", "L4": "lb-l4"}
LAYER_COLOR = {"L1": "#4d9fff", "L2": "#3fb950", "L3": "#8b949e",
               "L3-PAH": "#d6a533", "L4": "#ec6fb0"}
SCAT_CLS = {"L1": "sc-l1", "L2": "sc-l2", "L3": "sc-l3",
            "L3-PAH": "sc-lp", "L4": "sc-l4"}
LAYER_ORDER = ["L1", "L2", "L3", "L3-PAH", "L4"]
LAYER_TITLE = {
    "L1": "CORE CONVICTION", "L2": "ACTIVE CATALYST",
    "L3": "BUILD / MONITOR", "L3-PAH": "PRE-ACTIVIST SCREEN",
    "L4": "MERGER ARB",
}


def _badge(action: str) -> str:
    label, cls = ACTION_BADGE.get(action, (action, "bg-hold"))
    return f'<span class="badge {cls}">{label}</span>'


def _tip(*lines) -> str:
    """Pack tooltip lines into a data-tip attribute value.

    Each line is HTML-escaped, then lines are joined with the newline entity so
    the whole tooltip rides in one attribute. The shared tooltip handler in
    DASHBOARD_JS reads data-tip, splits on the newline, and renders line 1 bold.
    """
    return "&#10;".join(html_escape(str(ln)) for ln in lines)


def _money(v, sign: bool = False) -> str:
    """Format a JPY amount compactly: 82708350 -> '¥82.7M'."""
    if v is None:
        return "—"
    pre = "+" if (sign and v > 0) else ("−" if v < 0 else "")
    a = abs(v)
    if a >= 1e9:
        body = f"¥{a / 1e9:.2f}B"
    elif a >= 1e6:
        body = f"¥{a / 1e6:.2f}M"
    elif a >= 1e3:
        body = f"¥{a / 1e3:.0f}K"
    else:
        body = f"¥{a:.0f}"
    return pre + body


def _pwer_cls(pwer) -> str:
    if pwer is None:
        return "pw-na"
    if pwer >= PWER_FLOOR:
        return "pw-hi"
    if pwer >= 5:
        return "pw-mid"
    return "pw-lo"


def _days_to(date_str) -> "int | None":
    if not date_str:
        return None
    try:
        d = datetime.fromisoformat(str(date_str).split("T")[0]).date()
        return (d - date.today()).days
    except (ValueError, TypeError):
        return None


def _short_date(date_str) -> str:
    try:
        d = datetime.fromisoformat(str(date_str).split("T")[0]).date()
        return d.strftime("%d %b").lstrip("0")
    except (ValueError, TypeError):
        return str(date_str or "")


def _countdown_chip(date_str) -> str:
    """A catalyst date + countdown chip for the positions table."""
    days = _days_to(date_str)
    if days is None:
        return ""
    if days < 0:
        return f'<span class="cat-d past">{_short_date(date_str)}</span>'
    cls = "cat-d soon" if days <= 30 else "cat-d"
    return f'<span class="{cls}">{_short_date(date_str)} · {days}d</span>'


def _activist_key(s) -> str:
    """Normalise a messy activist string into a short grouping key."""
    s = (s or "").strip()
    if not s:
        return "No activist"
    s = s.split("(")[0].strip()
    parts = s.split()
    if parts and parts[-1].rstrip("%").replace(".", "").isdigit():
        parts = parts[:-1]
    return (" ".join(parts))[:22] or "No activist"


def _action_reason(p: dict, action: str) -> str:
    notes = (p.get("notes") or "").strip()
    first = notes.split(".")[0].strip() if notes else ""
    pwer = p.get("pwer")
    if action == "BUY":
        if first:
            return first[:96]
        return (f"PWER {pwer:.0f}% — clears the entry threshold."
                if pwer is not None else "Thesis intact at the current price.")
    if action == "SELL":
        nu = notes.upper()
        if "PROFIT WARNING" in nu:
            return "Operating-profit warning — thesis impaired."
        if "HOKUETSU" in nu or "FAILED CAMPAIGN" in nu:
            return "Failed-campaign pattern — thesis broken."
        if "ACTIVIST EXITING" in nu:
            return "Anchor activist exiting — co-investment edge gone."
        if pwer is not None and pwer < 5:
            return f"PWER {pwer:.0f}% — below the 5% floor."
        return first[:96] or "Thesis no longer viable at the current price."
    if action == "WEAK_HOLD":
        return (f"PWER {pwer:.0f}% — sub-threshold; trim candidate."
                if pwer is not None else "Sub-threshold conviction — trim candidate.")
    return first[:96]


# ============================================================================
# RENDER — TOP ZONE
# ============================================================================

def render_header(data: dict, positions: list) -> str:
    as_of = data.get("as_of") or ""
    try:
        asof_disp = datetime.fromisoformat(
            as_of.replace("Z", "+00:00")).strftime("%d %b %Y").lstrip("0")
    except (ValueError, TypeError):
        asof_disp = (as_of or "")[:10]

    account = ""
    src = (data.get("metadata") or {}).get("book_source") or ""
    if "account" in src:
        try:
            account = src.split("account", 1)[1].split(",")[0].strip()
        except IndexError:
            account = ""
    acct_str = f" · CGSI {html_escape(account)}" if account else ""

    dates = [p.get("price_date") for p in positions if p.get("price_date")]
    newest = max(dates) if dates else None
    label, cls, days = compute_price_freshness(newest)
    dot = "dot-ok" if (days is not None and days <= 3) else "dot-warn"
    fresh = f"Prices {label}" if newest else "Prices —"

    return f"""
<header class="topbar">
  <div class="brand">
    <div class="brand-mark">A</div>
    <div class="brand-name">ASUKA</div>
    <div class="brand-tag">Fund Risk Monitor</div>
  </div>
  <div class="topbar-right">
    <span class="asof">Book as of {html_escape(asof_disp)}{acct_str}</span>
    <span class="fresh"><span class="dot {dot}"></span>{html_escape(fresh)}</span>
  </div>
</header>"""


def _wtd_avg_pwer(positions: list) -> float:
    wsum = pwsum = 0.0
    for p in positions:
        pw = p.get("pwer")
        w = p.get("weight") or 0
        if pw is not None:
            wsum += w
            pwsum += w * pw
    return (pwsum / wsum) if wsum else 0.0


def _pwer_kpi_cls(v) -> str:
    return "pos" if v >= PWER_FLOOR else ("warn" if v >= 5 else "neg")


def render_kpi_strip(data: dict) -> str:
    """Two PWER measures (per the old dashboard) + Holdings + Cash."""
    positions = data.get("positions", [])
    metrics = compute_portfolio_metrics(data)
    avg_pwer = metrics["avg_pwer"]                 # simple mean, all scored names
    tier_pwer = metrics["tier_weighted_avg_pwer"]  # conviction-tier-weighted (BUYs)
    n = len(positions)
    n_buy = metrics.get("n_buy", 0)
    n_stub = sum(1 for p in positions if p.get("needs_enrichment"))
    stub_sub = f"{n_stub} need enrichment" if n_stub else "all enriched"

    return f"""
<div class="kpis">
  <div class="kpi"><div class="kpi-l">Avg PWER</div>
    <div class="kpi-v n {_pwer_kpi_cls(avg_pwer)}">{avg_pwer:.1f}%</div>
    <div class="kpi-s">simple mean · all {n} names</div></div>
  <div class="kpi"><div class="kpi-l">Tier-Weighted PWER</div>
    <div class="kpi-v n {_pwer_kpi_cls(tier_pwer)}">{tier_pwer:.1f}%</div>
    <div class="kpi-s">conviction-weighted · {n_buy} BUYs · AAA×3 AA×2 A×1 B×½</div></div>
  <div class="kpi"><div class="kpi-l">Holdings</div>
    <div class="kpi-v n">{n}</div>
    <div class="kpi-s">{stub_sub}</div></div>
  <div class="kpi"><div class="kpi-l">Cash</div>
    <div class="kpi-v n">0.0%</div>
    <div class="kpi-s pos">● fully deployed</div></div>
</div>"""


def _act_card(p: dict, action: str) -> str:
    pwer = p.get("pwer")
    pw = f"PWER {pwer:.1f}%" if pwer is not None else "PWER —"
    w = p.get("weight")
    tgt = p.get("weight_target")
    if tgt is not None and w is not None:
        drift = w - tgt
        dcls = "warn" if abs(drift) >= 1 else "dim"
        nums = (f'<span>Wt {w:.2f}% → tgt {tgt:.1f}%</span>'
                f'<span class="{dcls}">{drift:+.2f}pp</span>')
    elif w is not None:
        nums = f'<span>Wt {w:.2f}%</span>'
    else:
        nums = ""
    label, cls = ACTION_BADGE.get(action, (action, "bg-hold"))
    tier_badge = ""
    if action == "BUY":
        tier, _, _ = derive_buy_tier(p)
        if tier and tier != "—":
            tier_badge = f'<span class="tier tier-{tier.lower()}">{tier}</span>'
    return f"""<div class="act">
  <div class="act-top"><span class="badge {cls}">{label}</span>{tier_badge}
    <span class="act-tk">{html_escape(p.get('ticker'))} {html_escape(p.get('name', ''))}</span>
    <span class="act-pw">{pw}</span></div>
  <div class="act-why">{html_escape(_action_reason(p, action))}</div>
  <div class="act-nums">{nums}</div>
</div>"""


def render_hero(positions: list, deltas: dict) -> str:
    by_action: dict[str, list] = {}
    for p in positions:
        by_action.setdefault(derive_action(p), []).append(p)

    deploy = sorted(by_action.get("BUY", []),
                    key=lambda p: -derive_buy_tier(p)[1])
    reduce = (sorted(by_action.get("SELL", []), key=lambda p: (p.get("pwer") or 0))
              + sorted(by_action.get("WEAK_HOLD", []), key=lambda p: (p.get("pwer") or 0)))

    def _col(items, action_of, limit=4):
        if not items:
            return '<div class="hero-empty">Nothing flagged.</div>'
        html = "".join(_act_card(p, action_of(p)) for p in items[:limit])
        if len(items) > limit:
            html += (f'<div class="hero-empty">+{len(items) - limit} more '
                     f'in the Positions tab</div>')
        return html

    deploy_html = _col(deploy, lambda p: "BUY")
    reduce_html = _col(reduce, lambda p: derive_action(p))

    # Flags
    flags = []
    wpwer = _wtd_avg_pwer(positions)
    if wpwer < PWER_FLOOR:
        flags.append(("flag-w", "!", f"<b>Wtd-Avg PWER {wpwer:.1f}%</b> — "
                      f"{PWER_FLOOR - wpwer:.1f}pp below the {PWER_FLOOR:.0f}% floor. "
                      f"Enrich or drop the un-scored stubs to lift it."))
    stubs = [p for p in positions if p.get("needs_enrichment")]
    if stubs:
        names = ", ".join(p.get("name", "").title()[:18] for p in stubs[:3])
        more = f" +{len(stubs) - 3}" if len(stubs) > 3 else ""
        flags.append(("flag-w", str(len(stubs)),
                      f"<b>{len(stubs)} holdings un-enriched</b> — {html_escape(names)}{more}. "
                      f"No thesis or PWER yet."))
    quar = by_action.get("DATA_QUARANTINE", [])
    for p in quar:
        flags.append(("flag-r", "⛔", f"<b>{html_escape(p.get('name'))} "
                      f"({html_escape(p.get('ticker'))})</b> — data quarantine; "
                      f"fields cannot be trusted until re-verified."))
    n_changed = sum(1 for d in deltas.values() if d.get("action_changed"))
    if n_changed:
        flags.append(("flag-b", "Δ", f"<b>{n_changed} verdict "
                      f"{'flip' if n_changed == 1 else 'flips'} overnight</b> — "
                      f"see the action badges in Positions."))
    if not flags:
        flags.append(("flag-b", "✓", "<b>No portfolio-level flags.</b> "
                      "Book is clean on enrichment and data integrity."))
    flags_html = "".join(
        f'<div class="flag {c}"><span class="flag-i">{i}</span><div>{t}</div></div>'
        for c, i, t in flags)

    n_deploy, n_reduce = len(deploy), len(reduce)
    meta = (f"{n_deploy} deploy · {n_reduce} reduce · {len(flags)} "
            f"flag{'s' if len(flags) != 1 else ''} — fully deployed, so adds "
            f"fund from reduces")

    return f"""
<section class="hero">
  <div class="hero-head">
    <div class="hero-title">TODAY'S ACTIONS</div>
    <div class="hero-meta">{meta}</div>
  </div>
  <div class="hero-cols">
    <div class="hcol">
      <div class="hcol-h"><span class="hd hd-add"></span>DEPLOY</div>
      {deploy_html}
    </div>
    <div class="hcol">
      <div class="hcol-h"><span class="hd hd-red"></span>REDUCE</div>
      {reduce_html}
    </div>
    <div class="hcol">
      <div class="hcol-h"><span class="hd hd-flg"></span>FLAGS &amp; CHANGES</div>
      {flags_html}
    </div>
  </div>
</section>"""


# ============================================================================
# RENDER — POSITIONS TAB
# ============================================================================

def render_thesis_expand(p: dict) -> str:
    price = p.get("price")
    w = p.get("weight")
    sc = p.get("pwer_scenarios") or {}
    has_scen = bool(sc) and any(isinstance(sc.get(k), dict)
                                for k in ("bear", "base", "bull", "xbull"))
    if p.get("needs_enrichment") or not has_scen:
        return f"""<div class="pexp"><div class="pexp-stub">
      <b>This holding has no thesis yet.</b> It entered the book from the CGSI
      broker sync and is flagged for enrichment — activist, PWER scenarios and
      hard stops still need to be authored. Current price
      {('¥' + fmt_num(price)) if price else '—'}, portfolio weight
      {(f'{w:.2f}%') if w is not None else '—'}.
    </div></div>"""

    rows = []
    for key, lab in [("bear", "Bear"), ("base", "Base"),
                     ("bull", "Bull"), ("xbull", "X-Bull")]:
        s = sc.get(key) or {}
        prob = s.get("prob")
        if prob is None:
            prob = s.get("probability") or 0
        ret = s.get("return_pct")
        if ret is None:
            ret = 0
        width = min(max(prob * 100 * 2.2, 4), 100)
        if ret < 0:
            col = "#f85149"
        elif ret >= 60:
            col = "#56d364"
        elif ret >= 15:
            col = "#3fb950"
        else:
            col = "#5a8a52"
        rcls = "neg" if ret < 0 else "pos"
        rsign = "+" if ret > 0 else ""
        rows.append(
            f'<div class="scen-row"><span class="scen-l">{lab}</span>'
            f'<div class="scen-track"><div class="scen-fill" '
            f'style="width:{width:.0f}%;background:{col}"></div></div>'
            f'<span class="scen-p">{prob * 100:.0f}%</span>'
            f'<span class="scen-r {rcls}">{rsign}{ret:.1f}%</span></div>')

    pwer = p.get("pwer")
    pwer_txt = f"{pwer:.1f}%" if pwer is not None else "—"
    floor_note = (f"above the {PWER_FLOOR:.0f}% floor" if (pwer or 0) >= PWER_FLOOR
                  else f"below the {PWER_FLOOR:.0f}% floor")

    notes = (p.get("notes") or "").strip() or "No thesis note recorded."
    lf = p.get("last_filing") or {}
    if isinstance(lf, dict) and lf.get("date"):
        filing = f"{_short_date(lf.get('date'))} · {html_escape(lf.get('type', ''))}"
    else:
        filing = "—"
    wac = p.get("wac")
    facts = [
        ("Activist", html_escape((p.get("activist") or "—")[:32])),
        ("Stake", f"{p.get('stake_pct')}%" if p.get("stake_pct") else "—"),
        ("Last filing", filing),
        ("WAC", f"¥{fmt_num(wac)}" if wac else "—"),
        ("Catalyst", html_escape(_short_date(p.get("catalyst_date")))
         if p.get("catalyst_date") else "—"),
        ("Layer", html_escape(p.get("layer", "—"))),
    ]
    kv = "".join(f'<div class="kv-i"><span class="kv-k">{k}</span>'
                 f'<span class="kv-v">{v}</span></div>' for k, v in facts)

    return f"""<div class="pexp"><div class="pexp-grid">
  <div>
    <div class="pexp-h">PWER SCENARIO DISTRIBUTION</div>
    <div class="scen">{''.join(rows)}</div>
    <div class="pexp-foot">Probability-weighted return =
      <b>{pwer_txt}</b> · {floor_note}</div>
  </div>
  <div>
    <div class="pexp-h">THESIS</div>
    <p>{html_escape(notes[:420])}{'…' if len(notes) > 420 else ''}</p>
    <div class="kv">{kv}</div>
  </div>
</div></div>"""


def render_position_row(p: dict, delta: dict) -> str:
    tk = p.get("ticker", "")
    name = p.get("name", "")
    layer = p.get("layer") or "L3"
    enrich = bool(p.get("needs_enrichment"))
    activist = (p.get("activist") or "").strip()
    if enrich:
        by = '<span class="enrich">NEEDS ENRICHMENT</span>'
    elif activist:
        by = html_escape(activist[:40])
    else:
        by = '<span class="dim">—</span>'

    w = p.get("weight")
    tgt = p.get("weight_target")
    if w is not None and tgt is not None:
        drift = w - tgt
        dc = "neg" if abs(drift) >= 4 else ("warn" if abs(drift) >= 1.5 else "dim")
        wsub = f'tgt {tgt:.1f}% · <span class="{dc}">{drift:+.2f}</span>'
    elif w is not None:
        wsub = '<span class="dim">no target</span>'
    else:
        wsub = ""
    wv = f"{w:.2f}%" if w is not None else "—"

    price = p.get("price")
    wac = p.get("wac")
    pv = f"¥{fmt_num(price)}" if price else "—"
    if wac:
        d = wac_delta_pct(price, wac)
        psub = f"WAC ¥{fmt_num(wac)}" + (f" · {d:+.0f}%" if d is not None else "")
    else:
        psub = "WAC —"

    pwer = p.get("pwer")
    pwer_txt = f"{pwer:.1f}%" if pwer is not None else "—"
    pwer_cls = _pwer_cls(pwer)

    action = derive_action(p)
    tier_html = ""
    if action == "BUY":
        tier, _, _ = derive_buy_tier(p)
        if tier and tier != "—":
            tier_html = f' <span class="tier tier-{tier.lower()}">{tier}</span>'
    cat = p.get("catalyst") or ""
    cat_chip = _countdown_chip(p.get("catalyst_date"))
    if cat:
        cat_html = f"{html_escape(cat[:54])}<br>{cat_chip}" if cat_chip \
            else html_escape(cat[:54])
    elif enrich:
        cat_html = '<span class="dim">No thesis — new from CGSI sync</span>'
    else:
        cat_html = '<span class="dim">—</span>'

    # sort keys for the positions-table column sort (JS reads the data-sort-* attrs)
    sv_w = "" if w is None else f"{w}"
    sv_p = "" if price is None else f"{price}"
    sv_pw = "" if pwer is None else f"{pwer}"
    sv_a = ACTION_SORT_RANK.get(action, 9)
    _cd = _days_to(p.get("catalyst_date"))
    sv_c = f"{_cd}" if (_cd is not None and _cd >= 0) else ""

    return f"""
<div class="grid8 prow" data-layer="{html_escape(layer)}" data-enrich="{'1' if enrich else '0'}" data-name="{html_escape((tk + ' ' + name).lower())}" data-sort-weight="{sv_w}" data-sort-price="{sv_p}" data-sort-pwer="{sv_pw}" data-sort-action="{sv_a}" data-sort-catalyst="{sv_c}">
  <div class="pc-name"><span class="pc-tk">{html_escape(tk)}</span>
    <div style="min-width:0"><div class="pc-nm">{html_escape(name)}</div>
      <div class="pc-by">{by}</div></div></div>
  <div><span class="lb {LAYER_CLS.get(layer, 'lb-l3')}">{html_escape('PAH' if layer == 'L3-PAH' else layer)}</span></div>
  <div><div class="pc-wv n">{wv}</div><div class="pc-sub">{wsub}</div></div>
  <div><div class="pc-pv n">{pv}</div><div class="pc-sub">{psub}</div></div>
  <div><span class="pw {pwer_cls} n">{pwer_txt}</span></div>
  <div>{_badge(action)}{tier_html}</div>
  <div class="pc-cat">{cat_html}</div>
  <div class="chev">▸</div>
</div>
<div class="pexp-row" hidden>{render_thesis_expand(p)}</div>"""


def render_tab_positions(positions: list, deltas: dict) -> str:
    n_stub = sum(1 for p in positions if p.get("needs_enrichment"))
    chips = [("all", f"All {len(positions)}"), ("L1", "L1"), ("L2", "L2"),
             ("L3", "L3"), ("enrich", f"Stubs · {n_stub}")]
    chips_html = "".join(
        f'<span class="pchip{" on" if c == "all" else ""}" data-layer="{c}">{html_escape(lbl)}</span>'
        for c, lbl in chips)

    def _th(label, key):
        if key is None:
            return f"<div>{label}</div>"
        return (f'<div class="sortable" data-sort="{key}" title="Sort by {label}">'
                f'{label}<span class="sort-ar"></span></div>')

    head = f"""
<div class="grid8 pthead">
  {_th('Holding', 'name')}{_th('Layer', None)}{_th('Weight', 'weight')}{_th('Price', 'price')}{_th('PWER', 'pwer')}{_th('Action', 'action')}{_th('Catalyst', 'catalyst')}<div></div>
</div>"""

    body = [head]
    for layer in LAYER_ORDER:
        lp = [p for p in positions if (p.get("layer") or "L3") == layer]
        if not lp:
            continue
        lp.sort(key=lambda p: -(p.get("weight") or 0))
        wt = sum(p.get("weight") or 0 for p in lp)
        body.append(
            f'<div class="plgroup" data-layer="{html_escape(layer)}">'
            f'<span class="pl-t">{html_escape(layer)} · {LAYER_TITLE.get(layer, "")}</span>'
            f'<span class="pl-m">{len(lp)} '
            f'{"name" if len(lp) == 1 else "names"} · {wt:.1f}%</span>'
            f'<span class="pl-line"></span></div>')
        body += [render_position_row(p, deltas.get(p.get("ticker"), {})) for p in lp]

    return f"""
<div class="ptools">
  {chips_html}
  <input class="psearch" id="psearch" type="text"
    placeholder="Filter by ticker or name…" autocomplete="off">
</div>
<div class="ptable">{''.join(body)}</div>"""


# ============================================================================
# RENDER — RISK TAB
# ============================================================================

def render_conviction_matrix(positions: list) -> str:
    scored = [p for p in positions if p.get("pwer") is not None]
    top = sorted(scored, key=lambda p: -(p.get("weight") or 0))[:3]
    top_tk = {p.get("ticker") for p in top}
    dots = []
    for p in scored:
        pwer = max(0.0, min(p.get("pwer") or 0, 60.0))
        w = max(0.0, min(p.get("weight") or 0, 14.0))
        left = pwer / 60 * 100
        bottom = w / 14 * 100
        size = 9 + min(p.get("weight") or 0, 13) * 0.95
        scls = SCAT_CLS.get(p.get("layer"), "sc-l3")
        tag = ""
        if p.get("ticker") in top_tk:
            tag = (f'<span class="sc-tag">{html_escape(p.get("ticker"))} '
                   f'{html_escape((p.get("name") or "")[:11])}</span>')
        dlayer = p.get("layer") or "L3"
        dltitle = LAYER_TITLE.get(dlayer, "")
        tip = _tip(
            f"{p.get('ticker', '')} · {p.get('name', '')}",
            dlayer + (f" — {dltitle.title()}" if dltitle else ""),
            f"PWER {p.get('pwer'):.1f}%    ·    Weight {p.get('weight') or 0:.2f}%",
            f"Action — {derive_action(p).replace('_', ' ')}",
        )
        dots.append(
            f'<div class="sc-dot {scls}" data-tip="{tip}" style="left:{left:.1f}%;'
            f'bottom:{bottom:.1f}%;width:{size:.0f}px;height:{size:.0f}px">{tag}</div>')

    return f"""
<div class="card">
  <div class="card-h"><div class="card-t">CONVICTION MATRIX — WEIGHT × PWER</div>
    <div class="card-sub">{len(scored)} scored holdings · un-enriched stubs excluded</div></div>
  <div class="scatter">
    <div class="sc-ylab">PORTFOLIO WEIGHT →</div>
    <div class="sc-yt" style="top:10px">14%</div>
    <div class="sc-yt" style="top:34%">9%</div>
    <div class="sc-yt" style="top:63%">4%</div>
    <div class="sc-yt" style="bottom:34px">0%</div>
    <div class="sc-plot">
      <div class="sc-q sc-q-tl">REDUCE<small>big · low PWER</small></div>
      <div class="sc-q sc-q-tr">CORE<small>big · high PWER</small></div>
      <div class="sc-q sc-q-bl">ENRICH / EXIT<small>small · low PWER</small></div>
      <div class="sc-q sc-q-br">ADD<small>small · high PWER</small></div>
      <div class="sc-floor"><span>15% floor</span></div>
      {''.join(dots)}
    </div>
    <div class="sc-xt" style="left:50px">0%</div>
    <div class="sc-xt" style="left:25%">15%</div>
    <div class="sc-xt" style="left:50%">30%</div>
    <div class="sc-xt" style="left:75%">45%</div>
    <div class="sc-xt" style="left:97%">60%</div>
    <div class="sc-xlab">PROBABILITY-WEIGHTED EXPECTED RETURN (PWER) →</div>
  </div>
  <div class="sc-leg">
    <span><i style="background:#4d9fff"></i>L1 Core</span>
    <span><i style="background:#3fb950"></i>L2 Active catalyst</span>
    <span><i style="background:#8b949e"></i>L3 Build/monitor</span>
    <span><i style="background:#d6a533"></i>L3-PAH pre-activist</span>
    <span style="margin-left:auto">Dot size = portfolio weight</span>
  </div>
</div>"""


def render_layer_donut(positions: list) -> str:
    sums: dict[str, float] = {}
    for p in positions:
        sums[p.get("layer") or "L3"] = sums.get(p.get("layer") or "L3", 0) + (p.get("weight") or 0)
    total = sum(sums.values()) or 1.0
    segs, legend, cum = [], [], 0.0
    for layer in LAYER_ORDER:
        if layer not in sums:
            continue
        pct = sums[layer] / total * 100
        col = LAYER_COLOR.get(layer, "#8b949e")
        segs.append(f"{col} {cum:.2f}% {cum + pct:.2f}%")
        cum += pct
        legend.append(
            f'<div class="leg-i"><span class="leg-d" style="background:{col}"></span>'
            f'<span class="leg-n">{html_escape(layer)}</span>'
            f'<span class="leg-v">{sums[layer]:.1f}%</span></div>')
    grad = ",".join(segs)
    return f"""
<div class="card"><div class="card-h"><div class="card-t">LAYER MIX</div></div>
  <div class="card-b"><div class="donut-wrap">
    <div class="donut" style="background:conic-gradient({grad})">
      <div class="donut-c"><b>{len(positions)}</b><span>HOLDINGS</span></div></div>
    <div class="leg">{''.join(legend)}</div>
  </div></div></div>"""


def render_activist_bars(positions: list) -> str:
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for p in positions:
        k = _activist_key(p.get("activist"))
        sums[k] = sums.get(k, 0) + (p.get("weight") or 0)
        counts[k] = counts.get(k, 0) + 1
    ranked = sorted(sums.items(), key=lambda kv: -kv[1])
    top = ranked[:7]
    rest = ranked[7:]
    rest_count = sum(counts.get(k, 0) for k, _ in rest)
    if rest:
        top.append((f"{len(rest)} others", sum(v for _, v in rest)))
    mx = max((v for _, v in top), default=1.0) or 1.0
    bars = []
    for name, val in top:
        amber = " amber" if name == "No activist" else ""
        if rest and name == f"{len(rest)} others":
            sub = f"{rest_count} positions across {len(rest)} activists"
        else:
            c = counts.get(name, 0)
            sub = f"{c} position{'' if c == 1 else 's'}"
        tip = _tip(name, f"{val:.1f}% of book weight", sub)
        bars.append(
            f'<div class="hbar" data-tip="{tip}">'
            f'<div class="hbar-l">{html_escape(name)}</div>'
            f'<div class="hbar-tr"><div class="hbar-f{amber}" '
            f'style="width:{val / mx * 100:.0f}%"></div></div>'
            f'<div class="hbar-v">{val:.1f}</div></div>')
    return f"""
<div class="card"><div class="card-h">
  <div class="card-t">ACTIVIST CONCENTRATION</div></div>
  <div class="card-b"><div class="hbars">{''.join(bars)}</div></div></div>"""


def render_pwer_histogram(positions: list) -> str:
    buckets = [0, 0, 0, 0, 0, 0]  # <0, 0-15, 15-25, 25-40, 40+, n/a
    members: list[list[str]] = [[], [], [], [], [], []]
    for p in positions:
        pw = p.get("pwer")
        if pw is None:
            idx = 5
        elif pw < 0:
            idx = 0
        elif pw < 15:
            idx = 1
        elif pw < 25:
            idx = 2
        elif pw < 40:
            idx = 3
        else:
            idx = 4
        buckets[idx] += 1
        members[idx].append(p.get("ticker") or "?")
    mx = max(buckets) or 1
    cls = ["hb-below", "hb-below", "hb-above", "hb-above", "hb-above", "hb-na"]
    labels = ["&lt;0%", "0–15", "15–25", "25–40", "40%+", "n/a"]
    tip_range = ["PWER below 0%", "PWER 0–15%", "PWER 15–25%",
                 "PWER 25–40%", "PWER 40% and above", "PWER not scored"]
    bars = []
    for i, c in enumerate(buckets):
        cnum = f'<div class="hb-c{" dim" if i == 5 else ""}">{c}</div>'
        tk_list = ", ".join(members[i]) if members[i] else "—"
        tip = _tip(tip_range[i], f"{c} holding{'' if c == 1 else 's'}", tk_list)
        bars.append(
            f'<div class="hb" data-tip="{tip}">{cnum}'
            f'<div class="hb-bar {cls[i]}" style="height:{c / mx * 100:.0f}%"></div>'
            f'<div class="hb-l">{labels[i]}</div></div>')
    return f"""
<div class="card"><div class="card-h">
  <div class="card-t">PWER DISTRIBUTION</div></div>
  <div class="card-b"><div class="histo">
    <div class="histo-floor" style="left:calc(33.3% - 4px)"><span>15% floor</span></div>
    {''.join(bars)}
  </div></div></div>"""


def render_tab_risk(positions: list) -> str:
    weights = sorted((p.get("weight") or 0 for p in positions), reverse=True)
    top5 = sum(weights[:5])
    n = len(positions) or 1
    scored = [p for p in positions if p.get("pwer") is not None]
    below = [p for p in scored if (p.get("pwer") or 0) < PWER_FLOOR]
    below_wt = sum(p.get("weight") or 0 for p in below)
    stubs = [p for p in positions if p.get("needs_enrichment")]
    stub_wt = sum(p.get("weight") or 0 for p in stubs)
    hhi = sum((p.get("weight") or 0) ** 2 for p in positions)
    eff_n = (10000 / hhi) if hhi else 0
    largest = max(positions, key=lambda p: p.get("weight") or 0, default=None)
    largest_str = (f"{largest.get('name', '')[:16]} {largest.get('weight', 0):.1f}%"
                   if largest else "—")

    stats = f"""
<div class="stat4">
  <div class="stat"><div class="stat-l">Top-5 Concentration</div>
    <div class="stat-v n">{top5:.1f}%</div>
    <div class="stat-s">Largest: {html_escape(largest_str)}</div></div>
  <div class="stat stat-neg"><div class="stat-l">Below 15% PWER Floor</div>
    <div class="stat-v n warn">{below_wt:.0f}%</div>
    <div class="stat-s">{len(below)} scored names under the floor</div></div>
  <div class="stat stat-warn"><div class="stat-l">Un-enriched Exposure</div>
    <div class="stat-v n warn">{stub_wt:.0f}%</div>
    <div class="stat-s">{len(stubs)} names — no thesis or PWER</div></div>
  <div class="stat"><div class="stat-l">Effective Positions</div>
    <div class="stat-v n">{eff_n:.1f}</div>
    <div class="stat-s">of {n} held · HHI {hhi:.0f}</div></div>
</div>"""

    return f"""{stats}
{render_conviction_matrix(positions)}
<div class="row3">
  {render_layer_donut(positions)}
  {render_activist_bars(positions)}
  {render_pwer_histogram(positions)}
</div>"""


# ============================================================================
# RENDER — CATALYSTS TAB
# ============================================================================

def _future_catalysts(positions: list) -> list:
    out = []
    for p in positions:
        days = _days_to(p.get("catalyst_date"))
        if days is not None and days >= 0:
            out.append((days, p))
    out.sort(key=lambda x: x[0])
    return out


def render_catalyst_timeline(positions: list) -> str:
    fut = _future_catalysts(positions)
    if not fut:
        return """
<div class="card"><div class="card-h"><div class="card-t">CATALYST TIMELINE</div></div>
  <div class="card-b"><div class="empty"><div class="empty-i">◷</div>
    <div class="empty-t">No upcoming catalysts on the book</div>
    <div class="empty-s">No position carries a future catalyst date.</div>
  </div></div></div>"""

    span = max(max(d for d, _ in fut) + 16, 60)
    today = date.today()

    # month gridlines
    months = []
    y, m = today.year, today.month
    for _ in range(8):
        m += 1
        if m > 12:
            m = 1
            y += 1
        try:
            mdate = date(y, m, 1)
        except ValueError:
            break
        off = (mdate - today).days
        if off <= 0 or off > span:
            continue
        months.append((off / span * 100, mdate.strftime("%b")))

    grid = "".join(f'<div class="tl-grid" style="left:{o:.1f}%"></div>'
                   for o, _ in months)
    mlabels = ('<span style="left:0%">' + today.strftime("%b") + '</span>'
               + "".join(f'<span style="left:{o:.1f}%">{lbl}</span>'
                         for o, lbl in months))

    # group catalysts within 7 days
    groups: list[list] = []
    for days, p in fut:
        if groups and days - groups[-1][0][0] <= 7:
            groups[-1].append((days, p))
        else:
            groups.append([(days, p)])

    evs = []
    for g in groups:
        d0 = g[0][0]
        off = d0 / span * 100
        soon = " soon" if d0 <= 30 else ""
        names = " · ".join(f"{html_escape(p.get('ticker'))}" for _, p in g)
        if len(g) == 1:
            p = g[0][1]
            title = html_escape((p.get("name") or "")[:20])
            dd = _short_date(p.get("catalyst_date")).upper()
        else:
            title = f"Catalyst cluster — {len(g)}"
            dd = (_short_date(g[0][1].get("catalyst_date"))
                  + " – " + _short_date(g[-1][1].get("catalyst_date"))).upper()
        evs.append(f"""<div class="tl-ev" style="left:{off:.1f}%">
  <div class="tl-dot{soon}"></div>
  <div class="tl-pill{soon}">
    <div class="tl-d{soon}">{dd}</div>
    <div class="tl-x">{title}</div>
    <div class="tl-w">{names}</div>
  </div></div>""")

    return f"""
<div class="card">
  <div class="card-h"><div class="card-t">CATALYST TIMELINE</div>
    <div class="card-sub">next {span} days · binary events from position catalyst dates</div></div>
  <div class="card-b"><div class="tl">
    <div class="tl-months">{mlabels}</div>
    <div class="tl-track">
      {grid}
      <div class="tl-today" style="left:0%"><span>TODAY</span></div>
      {''.join(evs)}
    </div>
  </div></div>
</div>"""


def render_tab_catalysts(positions: list, data: dict) -> str:
    fut = _future_catalysts(positions)
    next_d = fut[0][0] if fut else None
    in8wk = sum(1 for d, _ in fut if d <= 56)
    filings = data.get("todays_filings", []) or []

    stats = f"""
<div class="stat4">
  <div class="stat"><div class="stat-l">Next Catalyst</div>
    <div class="stat-v n">{(str(next_d) + ' days') if next_d is not None else '—'}</div>
    <div class="stat-s">{html_escape(_short_date(fut[0][1].get('catalyst_date'))) if fut else 'none scheduled'}</div></div>
  <div class="stat"><div class="stat-l">Events, Next 8 Weeks</div>
    <div class="stat-v n">{in8wk}</div>
    <div class="stat-s">binary catalyst events</div></div>
  <div class="stat"><div class="stat-l">Upcoming Total</div>
    <div class="stat-v n">{len(fut)}</div>
    <div class="stat-s">positions with a future catalyst</div></div>
  <div class="stat"><div class="stat-l">Filings Today</div>
    <div class="stat-v n">{len(filings)}</div>
    <div class="stat-s">EDINET / TDnet scan</div></div>
</div>"""

    rows = []
    for days, p in fut:
        soon = " soon" if days <= 30 else ""
        rows.append(f"""
<div class="cl-row">
  <div class="cl-cd{soon}">{days}d</div>
  <div><div class="cl-nm">{html_escape(p.get('name', ''))}</div>
    <div class="cl-tk">{html_escape(p.get('ticker'))} · {html_escape(p.get('layer', ''))}</div></div>
  <div class="cl-ev">{html_escape((p.get('catalyst') or '')[:80])}</div>
  <div class="cl-date">{html_escape(_short_date(p.get('catalyst_date')))}</div>
</div>""")
    upcoming = ("".join(rows) if rows
                else '<div class="empty"><div class="empty-t">No upcoming catalysts</div></div>')

    if filings:
        frows = []
        for f in filings[:8]:
            frows.append(f"""
<div class="cl-row">
  <div class="cl-cd">NEW</div>
  <div><div class="cl-nm">{html_escape(f.get('name', ''))}</div>
    <div class="cl-tk">{html_escape(f.get('ticker', ''))}</div></div>
  <div class="cl-ev">{html_escape((f.get('doc_type') or '') + ' · ' + (f.get('filer') or ''))}</div>
  <div class="cl-date">{html_escape(str(f.get('received_at', ''))[:10])}</div>
</div>""")
        filings_body = '<div class="clist">' + "".join(frows) + "</div>"
    else:
        filings_body = """
<div class="empty"><div class="empty-i">▤</div>
  <div class="empty-t">No new filings today</div>
  <div class="empty-s">EDINET + TDnet monitored for 大量保有報告 / 変更報告書<br>
  across all held positions.</div></div>"""

    return f"""{stats}
{render_catalyst_timeline(positions)}
<div class="row2">
  <div class="card">
    <div class="card-h"><div class="card-t">UPCOMING CATALYSTS</div>
      <div class="card-sub">{len(fut)} events</div></div>
    <div class="clist">{upcoming}</div>
  </div>
  <div class="card">
    <div class="card-h"><div class="card-t">FILINGS FEED</div>
      <div class="card-sub">EDINET · TDnet</div></div>
    {filings_body}
  </div>
</div>"""


# ============================================================================
# RENDER — WATCH TAB
# ============================================================================

def render_tab_watch(data: dict) -> str:
    watch = data.get("watch_list", []) or []
    exited = data.get("exited", []) or []

    spons: dict[str, int] = {}
    for w in watch:
        k = _activist_key(w.get("activist"))
        spons[k] = spons.get(k, 0) + 1
    top_sponsor = max(spons.items(), key=lambda kv: kv[1], default=("—", 0))

    stats = f"""
<div class="stat3">
  <div class="stat"><div class="stat-l">PM Watchlist</div>
    <div class="stat-v n">{len(watch)} <span style="font-size:12px;color:var(--dim)">names</span></div>
    <div class="stat-s">PM-curated, not held</div></div>
  <div class="stat"><div class="stat-l">Recently Exited</div>
    <div class="stat-v n">{len(exited)} <span style="font-size:12px;color:var(--dim)">names</span></div>
    <div class="stat-s">book rotation history</div></div>
  <div class="stat"><div class="stat-l">Most-Watched Sponsor</div>
    <div class="stat-v" style="font-size:16px">{html_escape(top_sponsor[0])}</div>
    <div class="stat-s">{top_sponsor[1]} watchlist names</div></div>
</div>"""

    wrows = []
    for w in watch:
        note = (w.get("notes") or w.get("trigger") or "").strip()
        dropped = ""
        if "DROPPED FROM BOOK" in note.upper() or "dropped from book" in note.lower():
            dropped = '<span class="dropped">DROPPED FROM BOOK</span>'
            note = note.split("—")[-1].strip() if "—" in note else note
        act = (w.get("activist") or "").strip()
        chip = f'<span class="chip">{html_escape(act[:24])}</span>' if act else '<span class="dim">—</span>'
        wrows.append(f"""
<tr><td><span class="wt-tk">{html_escape(w.get('ticker', ''))}</span></td>
  <td class="wt-nm">{html_escape(w.get('name', ''))}</td>
  <td>{chip}</td>
  <td class="wt-note">{dropped}{html_escape(note[:90])}</td></tr>""")
    watch_body = ("".join(wrows) if wrows
                  else '<tr><td colspan="4" class="wt-note">Watchlist is empty.</td></tr>')

    erows = []
    for e in exited:
        erows.append(f"""
<tr><td><span class="wt-tk">{html_escape(e.get('ticker', ''))}</span></td>
  <td class="wt-nm">{html_escape(e.get('name', ''))}</td>
  <td class="wt-note">{html_escape(_short_date(e.get('exit_date')))}</td>
  <td class="wt-note">{html_escape((e.get('reason') or '')[:90])}</td></tr>""")
    exited_body = ("".join(erows) if erows
                   else '<tr><td colspan="4" class="wt-note">No exits recorded.</td></tr>')

    return f"""{stats}
<div class="card">
  <div class="card-h"><div class="card-t">PM WATCHLIST</div>
    <div class="card-sub">source: pm_watchlist.csv — PM-editable</div></div>
  <table class="wtable">
    <thead><tr><th>Ticker</th><th>Name</th><th>Activist sponsor</th>
      <th>Trigger / note</th></tr></thead>
    <tbody>{watch_body}</tbody>
  </table>
  <div class="addrow">+ &nbsp;<b>Add a name</b> &nbsp;— append a row to
    pm_watchlist.csv; it appears here on the next broker sync.</div>
</div>
<div class="card">
  <div class="card-h"><div class="card-t">RECENTLY EXITED</div>
    <div class="card-sub">{len(exited)} names</div></div>
  <table class="wtable">
    <thead><tr><th>Ticker</th><th>Name</th><th>Exit date</th>
      <th>Reason</th></tr></thead>
    <tbody>{exited_body}</tbody>
  </table>
</div>"""


# ============================================================================
# DASHBOARD ASSEMBLY
# ============================================================================

def render_dashboard(data: dict, positions: list, deltas: dict) -> str:
    watch = data.get("watch_list", []) or []
    n_future = len(_future_catalysts(positions))
    gen = datetime.now().strftime("%d %b %Y %H:%M").lstrip("0")
    as_of = (data.get("as_of") or "")[:10]
    sources = " · ".join((data.get("metadata") or {}).get("data_sources", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Asuka Fund Risk Monitor</title>
<style>{CSS_STYLE}</style>
</head>
<body>
{render_header(data, positions)}
{render_kpi_strip(data)}
{render_hero(positions, deltas)}
<nav class="tabs">
  <div class="tab on" data-pane="tab-positions">Positions <span class="tab-c">{len(positions)}</span></div>
  <div class="tab" data-pane="tab-risk">Risk</div>
  <div class="tab" data-pane="tab-catalysts">Catalysts <span class="tab-c">{n_future}</span></div>
  <div class="tab" data-pane="tab-watch">Watch <span class="tab-c">{len(watch)}</span></div>
</nav>
<main>
  <section class="tabpane" id="tab-positions">{render_tab_positions(positions, deltas)}</section>
  <section class="tabpane" id="tab-risk" hidden>{render_tab_risk(positions)}</section>
  <section class="tabpane" id="tab-catalysts" hidden>{render_tab_catalysts(positions, data)}</section>
  <section class="tabpane" id="tab-watch" hidden>{render_tab_watch(data)}</section>
</main>
<footer>
  Asuka Fund Risk Monitor · rendered {gen} · {len(positions)} holdings ·
  book as of {html_escape(as_of)}{' · ' + html_escape(sources) if sources else ''}<br>
  PWER recomputed at live spot · deltas vs the previous snapshot ·
  Wtd-Avg PWER floor 25%.
</footer>
<script>{DASHBOARD_JS}</script>
</body>
</html>"""


def generate(data_path: str, output_path: str, state_dir: str = STATE_DIR) -> dict:
    data = load_json(data_path)
    prev = load_previous_state(state_dir)

    n_recomputed = 0
    for p in data.get("positions", []):
        before = p.get("pwer")
        recompute_pwer_at_spot(p)
        if before != p.get("pwer"):
            n_recomputed += 1
    if n_recomputed:
        print(f"  · PWER recomputed at live spot for {n_recomputed} positions")

    deltas = compute_deltas(data, prev)
    positions = data.get("positions", [])
    html_out = render_dashboard(data, positions, deltas)
    _atomic_write_text(output_path, html_out)
    snapshot = save_state_snapshot(data, state_dir)

    metrics = compute_portfolio_metrics(data)
    return {
        "output": output_path,
        "snapshot": snapshot,
        "positions": len(positions),
        "deltas_computed": len(deltas),
        "avg_pwer": metrics["avg_pwer"],
        "wtd_pwer": round(_wtd_avg_pwer(positions), 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the Asuka Fund Risk Monitor dashboard")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH,
                        help="Path to dashboard_data.json")
    parser.add_argument("--out", default=DEFAULT_OUT_PATH,
                        help="Output HTML path")
    parser.add_argument("--state-dir", default=STATE_DIR,
                        help="State snapshot directory")
    args = parser.parse_args()

    result = generate(args.data, args.out, args.state_dir)
    print(f"Dashboard generated: {result['output']}")
    print(f"  Positions: {result['positions']}  ·  "
          f"Wtd-Avg PWER: {result['wtd_pwer']:.1f}%  ·  "
          f"Deltas: {result['deltas_computed']}")
    print(f"  State snapshot: {result['snapshot']}")


if __name__ == "__main__":
    main()
