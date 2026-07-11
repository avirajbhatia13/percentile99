#!/usr/bin/env python3
"""v6: multi-page app — onboarding, plan modes, nested sheet, tagged PYQs, redesign."""
import json, re, html as _html

plan = json.load(open("plan_data.json"))
bank = json.load(open("bank.json"))
papers_raw = json.load(open("papers.json"))
qids = [l.split("|") for l in open("qids.txt").read().strip().split("\n")]
dids = [l.split("|") for l in open("dids.txt").read().strip().split("\n")]
def ms(s):
    p = s.split(":"); return int(p[0])*60+int(p[1])

subs, sub_idx, VQ, VD = [], {}, [], []
def add_video(prefix, v):
    key = (prefix, v["main"], v["sub"])
    if key not in sub_idx:
        sub_idx[key] = len(subs); subs.append([v["main"], v["sub"]])
    (VQ if prefix == "Q" else VD).append([v["name"], v["secs"], sub_idx[key]])
for day in plan["calendar"]:
    if "morning" in day:
        for v in day["morning"]["videos"]: add_video("Q", v)
    if "evening" in day:
        pref = "L" if day["evening"]["track"] == "LRDI" else "Q"
        for v in day["evening"]["videos"]: add_video(pref, v)
assert len(qids) == len(VQ) == 384 and len(dids) == len(VD) == 85
for i, (vid_id, secs) in enumerate(qids):
    assert int(secs) == VQ[i][1]; VQ[i].append(vid_id)
for i, (vid_id, dur) in enumerate(dids):
    assert ms(dur) == VD[i][1]; VD[i].append(vid_id)

# ---------- PYQ topic tagging (keyword heuristics, first match wins) ----------
QA_TAGS = [
 ("Remainders", ["remainder"]), ("HCF & LCM", ["hcf", "lcm", "highest common", "least common multiple"]),
 ("Base Systems", ["base 2", "base 3", "base 5", "base 6", "base 7", "base 8", "base 9", "in base"]),
 ("Factors", ["factor", "divisor"]),
 ("Logarithms", ["log"]), ("Probability", ["probability", "dice", "drawn at random"]),
 ("Permutations & Combinations", ["number of ways", "how many ways", "permutation", "combination", "arrangements", "number of arrangements"]),
 ("SI & CI", ["interest", "compounded"]),
 ("Profit & Loss", ["profit", "loss", "discount", "selling price", "cost price", "marked price", "markup", "retail price"]),
 ("Alligation & Mixture", ["mixture", "alloy", "dilute", "solution containing", "milk and water"]),
 ("Averages", ["average", "mean of"]),
 ("Percentages", ["percent", "per cent"]),
 ("Time & Work", ["complete the work", "work alone", "working together", "pipe", "fill the tank", "empty the tank", "days to finish", "job in"]),
 ("TSD – Boats & Streams", ["boat", "stream", "upstream", "downstream", "river"]),
 ("Circular Tracks", ["circular track"]),
 ("TSD – Linear Races", ["race"]),
 ("Clocks", ["o'clock", "minute hand", "hour hand"]),
 ("Time Speed Distance", ["speed", "km/hr", "kmph", "km per hour", "train", "distance", "walks", "cycles at", "travels"]),
 ("Triangles", ["triangle", "equilateral", "isosceles"]),
 ("Circles", ["circle", "chord", "radius", "tangent", "circumference", "semicircle"]),
 ("Quadrilaterals", ["rectangle", "square abcd", "parallelogram", "trapezium", "rhombus", "quadrilateral"]),
 ("Mensuration", ["volume", "cylinder", "cone", "sphere", "cube", "cuboid", "surface area"]),
 ("Coordinate/Graphs", []),
 ("Quadratic Equations", ["quadratic", "roots of the equation", "real roots"]),
 ("Inequalities", ["inequalit", "minimum possible value", "maximum possible value", "least value", "greatest value"]),
 ("Functions", ["f(x", "f (x", "function f", "g(x"]),
 ("Arithmetic Progression", ["arithmetic progression", "arithmetic sequence"]),
 ("Geometric Progression", ["geometric progression", "infinite geometric"]),
 ("Sequence & Series", ["sequence", "series", "sum of the first"]),
 ("Simple Equations", ["equation", "satisfying", "= 0"]),
 ("Numbers Basics", ["integer", "natural number", "digit", "odd number", "even number", "real number"]),
]
DILR_TAGS = [
 ("Venn Diagrams", ["venn", "exactly one of", "none of the three", "all three", "at least one of the three"]),
 ("Games & Tournaments", ["tournament", "match", "played", "team", "player", "round", "wins", "points table", "game"]),
 ("Pie Charts", ["pie chart", "pie-chart"]),
 ("Routes & Networks", ["route", "network", "path", "road", "junction", "city a", "flight"]),
 ("Calendars", ["calendar", "day of the week"]),
 ("Cubes", ["cube"]),
 ("Number Series", ["series"]),
 ("Arrangements (Linear & Circular)", ["seated", "sitting", "arrangement", "sit around", "row of"]),
 ("Maxima-Minima & Chocolate Distribution", ["maximum possible", "minimum possible", "distributed"]),
 ("Tables", ["table below", "following table", "tabular"]),
]
VALID_SUBS = {s for _, s in subs}
def tag(text, table):
    t = text.lower()
    for sub, kws in table:
        if sub not in VALID_SUBS: continue
        for k in kws:
            if k in t: return sub
    return None

def esc(s): return _html.escape(s or "").replace("\n", "<br>")
MOCKS, tagged_q, tagged_d = [], 0, 0
for p in papers_raw:
    ctxs, cmap, secs = [], {}, []
    for s in p["sections"]:
        qs, skip = [], 0
        for q in s["qs"]:
            if q.get("img"): skip += 1; continue
            item = {"n": q["n"], "type": q["type"], "q": esc(q["q"]), "ans": q["ans"], "sol": esc(q.get("sol",""))}
            if q["type"] == "mcq": item["opts"] = [esc(o) for o in q["opts"][:4]]
            c = q.get("ctx")
            if c:
                if c not in cmap: cmap[c] = len(ctxs); ctxs.append(esc(c))
                item["c"] = cmap[c]
            if s["name"] == "QA":
                sb = tag(q["q"], QA_TAGS)
                if sb: item["sub"] = sb; tagged_q += 1
            elif s["name"] == "DILR":
                sb = tag((q.get("ctx","") + " " + q["q"]), DILR_TAGS)
                if sb: item["sub"] = sb; tagged_d += 1
            qs.append(item)
        secs.append({"name": s["name"], "qs": qs, "skip": skip})
    MOCKS.append({"id": p["id"], "name": p["name"].replace("Actual ",""), "year": p["year"],
                  "secMin": p["secMin"], "ctxs": ctxs, "sections": secs})
usable = sum(len(s["qs"]) for m in MOCKS for s in m["sections"])
print(f"mocks: {len(MOCKS)} papers, {usable} usable Qs · tagged QA {tagged_q}, DILR {tagged_d}")

DATA = json.dumps({"subs": subs, "vq": VQ, "vd": VD,
    "qsecs": plan["quant"]["secs"], "dsecs": plan["dilr"]["secs"]}, separators=(",", ":"))
BANK = json.dumps(bank, separators=(",", ":"), ensure_ascii=False)
MOCKS_J = json.dumps(MOCKS, separators=(",", ":"), ensure_ascii=False)

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Percentile99 · CAT Prep OS</title>
<style>
:root{
  color-scheme: light;
  --bg:#f1f3f9; --ink:#101528; --mut:#5c6a86; --faint:#94a1ba;
  --card:#ffffff; --card2:#f7f9fd; --line:#e4e8f1; --line2:#eef1f8;
  --b1:#4f46e5; --b2:#9333ea; --brand:linear-gradient(135deg,#4f46e5,#9333ea 60%,#db2777);
  --qa:#4f46e5; --qa-soft:#eceafd; --lr:#d97706; --lr-soft:#fdf1dd;
  --ok:#0ea86c; --ok-soft:#e2f7ec; --bad:#dc2626; --bad-soft:#feecec;
  --mark:#7c3aed; --star:#f59e0b; --yt:#e02f2f;
  --hm0:#e6eaf3; --hm1:#c1e7d2; --hm2:#77caa0; --hm3:#2d9868; --hm4:#14532d;
  --ring-track:#e6eaf3; --head-bg:rgba(241,243,249,.75);
  --shadow:0 1px 2px rgba(16,21,40,.04),0 10px 30px -14px rgba(16,21,40,.14);
  --shadow-lg:0 6px 18px -4px rgba(79,70,229,.16),0 22px 48px -18px rgba(79,70,229,.28);
  --glow1:rgba(79,70,229,.14); --glow2:rgba(219,39,119,.10);
}
[data-theme="dark"]{
  color-scheme: dark;
  --bg:#090d1a; --ink:#e9edf6; --mut:#93a1bd; --faint:#5b6981;
  --card:#111828; --card2:#0d1422; --line:#213049; --line2:#182337;
  --qa:#818cf8; --qa-soft:#1e2350; --lr:#f0a83a; --lr-soft:#3a2c12;
  --ok:#34d399; --ok-soft:#0c3527; --bad:#f87171; --bad-soft:#3a1515;
  --mark:#a78bfa; --star:#fbbf24; --yt:#ff5c5c;
  --hm0:#1b2437; --hm1:#12472e; --hm2:#177347; --hm3:#22a266; --hm4:#4ade97;
  --ring-track:#1b2437; --head-bg:rgba(9,13,26,.75);
  --shadow:0 1px 2px rgba(0,0,0,.5),0 10px 30px -14px rgba(0,0,0,.55);
  --shadow-lg:0 6px 20px -4px rgba(0,0,0,.5),0 22px 48px -18px rgba(129,140,248,.35);
  --glow1:rgba(99,102,241,.16); --glow2:rgba(219,39,119,.10);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;padding-bottom:60px;
  background-image:radial-gradient(800px 400px at 12% -4%,var(--glow1),transparent 60%),
                   radial-gradient(700px 380px at 95% 4%,var(--glow2),transparent 60%);
  background-attachment:fixed}
.wrap{max-width:940px;margin:0 auto;padding:0 18px}
/* nav */
.top{position:sticky;top:0;z-index:30;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  background:var(--head-bg);border-bottom:1px solid var(--line2)}
.topin{max-width:940px;margin:0 auto;padding:10px 18px;display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;border-radius:11px;background:var(--brand);display:grid;place-items:center;
  color:#fff;font-weight:800;font-size:13px;flex:none;box-shadow:0 4px 14px -4px rgba(147,51,234,.5)}
.brand{font-weight:800;font-size:15px;letter-spacing:-.2px;white-space:nowrap}
.brand small{display:block;font-size:10px;color:var(--mut);font-weight:600;letter-spacing:.4px}
.nav{display:flex;gap:4px;margin-left:12px;background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:3px;box-shadow:var(--shadow)}
.nav button{border:0;background:transparent;padding:7px 14px;border-radius:9px;font:600 12.5px inherit;
  color:var(--mut);cursor:pointer;transition:.15s;white-space:nowrap}
.nav button.act{background:var(--brand);color:#fff;box-shadow:0 3px 10px -3px rgba(147,51,234,.5)}
.iconbtn{width:36px;height:36px;border-radius:11px;border:1px solid var(--line);background:var(--card);
  cursor:pointer;font-size:15px;display:grid;place-items:center;transition:transform .15s;flex:none}
.iconbtn:hover{transform:translateY(-1px)}
.avatar{width:36px;height:36px;border-radius:50%;background:var(--brand);color:#fff;display:grid;
  place-items:center;font-weight:800;font-size:14px;flex:none;cursor:pointer}
/* pages */
.page{display:none;animation:pgin .25s ease-out}
.page.act{display:block}
@keyframes pgin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
h2.ph{font-size:19px;margin:20px 0 4px;letter-spacing:-.3px}
.psub{color:var(--mut);font-size:12.5px;margin-bottom:14px}
/* hero */
.hero{display:grid;grid-template-columns:auto 1fr;gap:18px;align-items:center;background:var(--card);
  border:1px solid var(--line);border-radius:20px;padding:20px 22px;margin:16px 0 14px;box-shadow:var(--shadow)}
.ring{position:relative;width:112px;height:112px;flex:none}
.ring svg{transform:rotate(-90deg)}
.ring .pct{position:absolute;inset:0;display:grid;place-items:center;text-align:center}
.ring .pct b{font-size:22px;display:block;line-height:1}
.ring .pct span{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
.hstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(108px,1fr));gap:10px}
.hs{background:var(--card2);border:1px solid var(--line2);border-radius:13px;padding:10px 12px}
.hs b{font-size:17px;display:block}
.hs span{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}
.tbars{grid-column:1/-1;display:grid;gap:9px;margin-top:2px}
.bar .lbl{display:flex;justify-content:space-between;font-size:11.5px;color:var(--mut);margin-bottom:4px}
.bar .lbl b{color:var(--ink);font-weight:600}
.track{height:7px;background:var(--ring-track);border-radius:5px;overflow:hidden}
.fill{height:100%;border-radius:5px;transition:width .5s cubic-bezier(.2,.8,.2,1)}
/* heatmap */
.hmcard{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:14px 18px;margin-bottom:14px;box-shadow:var(--shadow)}
.hmtop{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}
.hmtop b{font-size:13px}.hmtop span{font-size:11.5px;color:var(--mut)}
.hmscroll{overflow-x:auto;padding-bottom:4px}
.hmgrid{display:flex;gap:3px}.hmcol{display:flex;flex-direction:column;gap:3px}
.hmcell{width:11px;height:11px;border-radius:3px;background:var(--hm0)}
.hmcell.l1{background:var(--hm1)}.hmcell.l2{background:var(--hm2)}.hmcell.l3{background:var(--hm3)}.hmcell.l4{background:var(--hm4)}
.hmcell.today{outline:2px solid var(--qa);outline-offset:-1px}
.hmmonths{display:flex;gap:3px;margin-bottom:4px;font-size:9.5px;color:var(--faint)}
.hmmonths span{width:11px;flex:none;white-space:nowrap}
.hmlegend{display:flex;align-items:center;gap:4px;font-size:10px;color:var(--faint);margin-top:8px;justify-content:flex-end}
.pl{width:12px;height:12px;border-radius:4px;display:inline-block;flex:none}
/* controls */
.ctrl{display:flex;gap:8px;align-items:center;margin:14px 0 12px;flex-wrap:wrap}
.seg{display:inline-flex;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:3px;box-shadow:var(--shadow);flex-wrap:wrap}
.seg button{border:0;background:transparent;padding:7px 13px;border-radius:9px;font:600 12.5px inherit;color:var(--mut);cursor:pointer;transition:.15s}
.seg button.act{background:var(--ink);color:var(--card)}
.pill{border:1px solid var(--line);background:var(--card);color:var(--mut);border-radius:12px;padding:8px 14px;
  font:600 12.5px inherit;cursor:pointer;box-shadow:var(--shadow);transition:transform .15s}
.pill:hover{transform:translateY(-1px);color:var(--ink)}
.pill.primary{background:var(--brand);border:none;color:#fff}
.pill.go{background:var(--ok);border-color:var(--ok);color:#fff}
/* cards & days */
.pcard{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);padding:18px 20px;margin-bottom:12px}
.pcard h3{margin:0 0 10px;font-size:13.5px}
.pcard .hint{font-size:11.5px;color:var(--mut);margin:6px 0;line-height:1.6}
.day{background:var(--card);border:1px solid var(--line);border-radius:16px;margin-bottom:9px;overflow:hidden;box-shadow:var(--shadow);position:relative;transition:box-shadow .2s}
.day::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px}
.day.done::before{background:var(--ok)}.day.next::before{background:var(--qa)}
.day.done .dn,.day.done .dd{color:var(--faint)}
.day.next{box-shadow:var(--shadow-lg)}
.dhead{display:flex;align-items:center;gap:11px;padding:12px 16px;cursor:pointer;user-select:none}
.dhead:hover{background:var(--card2)}
.dnum{width:40px;height:40px;border-radius:12px;background:var(--card2);border:1px solid var(--line2);display:grid;place-items:center;flex:none;font-weight:800;font-size:13px}
.day.done .dnum{background:var(--ok-soft);border-color:transparent;color:var(--ok)}
.day.next .dnum{background:var(--qa-soft);border-color:transparent;color:var(--qa)}
.dn{font-weight:700;font-size:13.5px}.dd{font-size:11.5px;color:var(--mut)}
.chip{font-size:9.5px;font-weight:800;padding:3px 8px;border-radius:99px;letter-spacing:.5px}
.chip.up{background:var(--qa-soft);color:var(--qa)}.chip.wk{background:var(--lr-soft);color:var(--lr)}
.chip.pyq{background:var(--ok-soft);color:var(--ok);cursor:pointer;border:none;font-family:inherit}
.chip.pyq:hover{filter:brightness(1.08)}
.dright{margin-left:auto;display:flex;align-items:center;gap:10px;flex:none}
.dprog{font-size:11.5px;color:var(--mut);font-variant-numeric:tabular-nums}
.donetick{color:var(--ok)}
.caret{color:var(--faint);transition:transform .2s;font-size:11px}
.day.open .caret,.mtop.open>.mhead .caret,.sub.open>.subhead .caret{transform:rotate(180deg)}
.dbody{display:none;border-top:1px solid var(--line2);padding:4px 16px 12px}
.day.open .dbody{display:block;animation:pgin .18s ease-out}
.slot{margin:10px 0 4px}
.slothead{display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap}
.badge{font-size:10px;font-weight:800;padding:3.5px 9px;border-radius:8px;letter-spacing:.5px;flex:none}
.badge.q{background:var(--qa-soft);color:var(--qa)}.badge.l{background:var(--lr-soft);color:var(--lr)}
.slothead .topic{font-size:12.5px;font-weight:600}
.slothead .dur{font-size:11.5px;color:var(--mut);margin-left:auto;font-variant-numeric:tabular-nums}
.vid{display:flex;align-items:center;gap:8px;padding:5px 6px;border-radius:10px;transition:background .12s}
.vid:hover{background:var(--card2)}
.vid input{width:17px;height:17px;accent-color:var(--ok);cursor:pointer;flex:none}
.vid .nm{flex:1;font-size:13px;min-width:0}
.vid .du{color:var(--faint);font-size:11.5px;font-variant-numeric:tabular-nums;flex:none}
.vid.ck .nm{text-decoration:line-through;color:var(--faint)}
.act3{display:flex;gap:2px;flex:none}
.abtn{width:26px;height:26px;border:none;background:transparent;border-radius:8px;cursor:pointer;display:grid;place-items:center;font-size:13px;color:var(--faint);text-decoration:none;transition:.12s}
.abtn:hover{background:var(--line2);transform:scale(1.12)}
.abtn.yt{color:var(--yt)}.abtn.star.on{color:var(--star)}.abtn.note.on{color:var(--qa)}
.notebox{display:none;margin:2px 0 6px 42px}
.notebox.open{display:block}
.notebox textarea{width:100%;min-height:52px;border:1px solid var(--line);border-radius:10px;background:var(--card2);color:var(--ink);font:12.5px/1.45 inherit;padding:8px 10px;resize:vertical}
.dayact{display:flex;gap:8px;margin-top:10px}
.dayact button{font:600 11.5px inherit;border:1px solid var(--line);background:var(--card2);color:var(--mut);border-radius:9px;padding:6px 12px;cursor:pointer}
.dayact button:hover{color:var(--ok);border-color:var(--ok)}
/* study nested */
.sec2{background:var(--card);border:1px solid var(--line);border-radius:20px;margin-bottom:14px;box-shadow:var(--shadow);overflow:hidden}
.sec2>.shead{display:flex;align-items:center;gap:14px;padding:16px 20px;cursor:pointer}
.sec2>.shead:hover{background:var(--card2)}
.sico{width:44px;height:44px;border-radius:13px;display:grid;place-items:center;font-size:19px;flex:none}
.sname{font-weight:800;font-size:15px}.ssub{font-size:11.5px;color:var(--mut)}
.sbody{display:none;padding:6px 14px 14px;border-top:1px solid var(--line2)}
.sec2.open .sbody{display:block}
.mtop{background:var(--card2);border:1px solid var(--line2);border-radius:14px;margin:8px 0;overflow:hidden}
.mhead{display:flex;align-items:center;gap:11px;padding:12px 14px;cursor:pointer;user-select:none}
.mhead:hover{background:var(--line2)}
.mico{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;font-size:15px;flex:none;background:var(--card)}
.mname{font-weight:700;font-size:13px}.msub{font-size:11px;color:var(--mut)}
.mright{margin-left:auto;display:flex;align-items:center;gap:10px}
.mpct{font-size:12px;font-weight:700;color:var(--ok);font-variant-numeric:tabular-nums}
.mbody{display:none;border-top:1px solid var(--line2);padding:2px 10px 10px}
.mtop.open>.mbody{display:block}
.sub{border:1px solid var(--line2);border-radius:11px;margin:7px 0;background:var(--card);overflow:hidden}
.subhead{display:flex;align-items:center;gap:8px;padding:9px 12px;cursor:pointer;flex-wrap:wrap}
.subhead:hover{background:var(--card2)}
.subhead .sname2{font-weight:700;font-size:12.5px}
.subhead .scount{font-size:11px;color:var(--mut);font-variant-numeric:tabular-nums}
.subbody{display:none;padding:2px 10px 8px;border-top:1px solid var(--line2)}
.sub.open .subbody{display:block}
.mini{width:74px;height:6px;background:var(--ring-track);border-radius:4px;overflow:hidden;flex:none;margin-left:auto}
.mini i{display:block;height:100%;background:var(--ok);border-radius:4px;transition:width .4s}
.rev{background:var(--card);border:1px solid var(--line);border-radius:16px;margin-bottom:9px;box-shadow:var(--shadow);overflow:hidden}
.rev .rhead{padding:11px 16px;font-weight:700;font-size:13px;border-bottom:1px solid var(--line2)}
.rev .body{padding:4px 12px 8px}
.empty{text-align:center;color:var(--mut);padding:44px 0}
/* practice */
.tgroup{margin:10px 0}
.tgroup .glab{font-size:11px;font-weight:800;color:var(--mut);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.tchips{display:flex;gap:6px;flex-wrap:wrap}
.tchip{border:1px solid var(--line);background:var(--card2);color:var(--mut);border-radius:99px;padding:5px 12px;font:600 12px inherit;cursor:pointer;transition:.12s}
.tchip.on{background:var(--qa);border-color:var(--qa);color:#fff}
.tchip .n{opacity:.7;font-size:10.5px}
textarea.imp{width:100%;min-height:90px;border:1px solid var(--line);border-radius:10px;background:var(--card2);color:var(--ink);font:11.5px/1.5 ui-monospace,monospace;padding:8px 10px}
.histrow{display:flex;gap:12px;align-items:center;padding:8px 4px;border-top:1px solid var(--line2);font-size:12.5px;flex-wrap:wrap}
.histrow:first-child{border-top:none}
.histrow .sc{font-weight:800;min-width:54px}
.histrow .mu{color:var(--mut);font-size:11.5px}
/* profile */
.frow{display:flex;align-items:center;gap:12px;margin:10px 0;flex-wrap:wrap}
.frow label{font-size:12.5px;color:var(--mut);font-weight:600;min-width:160px}
.frow input[type=text],.frow input[type=email],.frow input[type=number],.frow input[type=date]{
  border:1px solid var(--line);background:var(--card2);color:var(--ink);border-radius:10px;padding:8px 12px;font:inherit;font-size:13px;flex:1;min-width:160px}
.frow input[type=range]{flex:1;min-width:140px;accent-color:var(--qa)}
.frow .val{font-weight:700;font-size:12.5px;min-width:60px}
.preview{margin-top:10px;padding:11px 13px;background:var(--qa-soft);border-radius:12px;font-size:12.5px;font-weight:600}
.planopt{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:10px 0}
.pop{border:1.5px solid var(--line);border-radius:14px;padding:13px 14px;cursor:pointer;transition:.15s;background:var(--card2)}
.pop:hover{border-color:var(--qa)}
.pop.on{border-color:var(--qa);background:var(--qa-soft);box-shadow:var(--shadow-lg)}
.pop b{display:block;font-size:13px;margin-bottom:3px}
.pop span{font-size:11px;color:var(--mut);line-height:1.5;display:block}
/* onboarding */
#onb{position:fixed;inset:0;z-index:200;background:var(--bg);display:none;overflow-y:auto;
  background-image:radial-gradient(800px 500px at 20% 0%,var(--glow1),transparent 60%),radial-gradient(700px 400px at 90% 10%,var(--glow2),transparent 60%)}
#onb.on{display:block}
.onbwrap{max-width:520px;margin:7vh auto;padding:0 18px}
.onbcard{background:var(--card);border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow-lg);padding:30px 30px}
.onblogo{width:56px;height:56px;border-radius:16px;background:var(--brand);display:grid;place-items:center;color:#fff;font-weight:800;font-size:20px;margin:0 auto 14px;box-shadow:0 8px 24px -6px rgba(147,51,234,.5)}
.onbcard h1{font-size:22px;text-align:center;margin:0 0 6px;letter-spacing:-.4px}
.onbcard .sub{color:var(--mut);text-align:center;font-size:13px;margin-bottom:22px;line-height:1.6}
.gbtn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:12px;border-radius:13px;
  border:1px solid var(--line);background:var(--card2);font:600 14px inherit;color:var(--ink);cursor:pointer;transition:.15s}
.gbtn:hover{transform:translateY(-1px);box-shadow:var(--shadow)}
.gsvg{width:18px;height:18px;flex:none}
.steps{display:flex;gap:6px;justify-content:center;margin-bottom:18px}
.stepdot{width:26px;height:4px;border-radius:3px;background:var(--line)}
.stepdot.on{background:var(--brand)}
.onbnote{font-size:11px;color:var(--faint);text-align:center;margin-top:14px;line-height:1.6}
/* test overlay (unchanged core) */
#tover{position:fixed;inset:0;z-index:100;background:var(--bg);display:none;flex-direction:column}
#tover.on{display:flex}
.tbar{display:flex;align-items:center;gap:10px;padding:10px 16px;background:var(--card);border-bottom:1px solid var(--line);flex:none;flex-wrap:wrap}
.tbar .ttl{font-weight:800;font-size:13.5px}
.timer{font-variant-numeric:tabular-nums;font-weight:800;font-size:16px;padding:5px 12px;border-radius:10px;background:var(--qa-soft);color:var(--qa)}
.timer.low{background:var(--bad-soft);color:var(--bad);animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.6}}
.tmain{flex:1;display:flex;min-height:0}
.qpanel{flex:1;overflow-y:auto;padding:20px 24px}
.qhead{display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.qnum{font-weight:800;font-size:14px}
.qtag{font-size:10.5px;font-weight:700;padding:3px 9px;border-radius:99px;background:var(--qa-soft);color:var(--qa)}
.qtype{font-size:10.5px;color:var(--mut)}
.qtext{font-size:15px;line-height:1.65;margin-bottom:18px}
.ctxbox{max-height:40vh;overflow-y:auto;background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:14px 16px;font-size:13px;line-height:1.6;margin-bottom:14px}
.opt{display:flex;gap:10px;align-items:flex-start;border:1.5px solid var(--line);border-radius:12px;padding:11px 14px;margin-bottom:8px;cursor:pointer;transition:.12s;font-size:14px}
.opt:hover{border-color:var(--qa)}
.opt.sel{border-color:var(--qa);background:var(--qa-soft)}
.opt .ol{font-weight:800;color:var(--mut);flex:none}
.titain{border:1.5px solid var(--line);border-radius:12px;background:var(--card);color:var(--ink);padding:11px 14px;font:15px inherit;width:220px}
.palette{width:212px;flex:none;border-left:1px solid var(--line);background:var(--card);padding:14px;overflow-y:auto}
.palette h4{margin:0 0 10px;font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}
.pgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}
.pbtn{aspect-ratio:1;border-radius:10px;border:1px solid var(--line);background:var(--card2);color:var(--mut);font-weight:700;font-size:12px;cursor:pointer}
.pbtn.cur{outline:2.5px solid var(--qa);outline-offset:1px}
.pbtn.ans{background:var(--ok);border-color:var(--ok);color:#fff}
.pbtn.seen{background:var(--bad-soft);border-color:var(--bad);color:var(--bad)}
.pbtn.mk{background:var(--mark);border-color:var(--mark);color:#fff}
.pbtn.mkans{background:var(--mark);border-color:var(--ok);color:#fff;box-shadow:inset 0 -4px 0 var(--ok)}
.plegend{margin-top:12px;font-size:10.5px;color:var(--mut);display:grid;gap:5px}
.plegend span{display:flex;align-items:center;gap:6px}
.tfoot{display:flex;gap:8px;padding:10px 16px;background:var(--card);border-top:1px solid var(--line);flex:none;flex-wrap:wrap}
.tfoot .sp{flex:1}
#calc{position:fixed;right:240px;bottom:70px;z-index:120;width:210px;background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow-lg);display:none;overflow:hidden}
#calc.on{display:block}
#calc .chead{padding:8px 12px;font-size:11px;font-weight:800;color:var(--mut);display:flex;justify-content:space-between;background:var(--card2)}
#calc .cdisp{padding:8px 12px;text-align:right;font:600 20px ui-monospace,monospace;min-height:38px;word-break:break-all}
#calc .cgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line2)}
#calc button{border:none;background:var(--card);padding:11px 0;font:600 14px inherit;color:var(--ink);cursor:pointer}
#calc button:hover{background:var(--card2)}
#calc button.op{color:var(--qa);font-weight:800}
#calc button.eq{background:var(--qa);color:#fff}
.sumgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;margin-bottom:12px}
.secsum{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:10px 0}
.ares{border:1px solid var(--line);border-radius:13px;margin-bottom:8px;overflow:hidden}
.arhead{display:flex;gap:10px;align-items:center;padding:10px 14px;cursor:pointer;font-size:13px}
.arhead:hover{background:var(--card2)}
.arhead .ic{font-weight:900;flex:none;width:20px;text-align:center}
.ok2{color:var(--ok)}.bad2{color:var(--bad)}.skip2{color:var(--faint)}
.arhead .tt{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.arhead .tm{font-variant-numeric:tabular-nums;color:var(--mut);font-size:12px;flex:none}
.arbody{display:none;border-top:1px solid var(--line2);padding:12px 16px;font-size:13.5px}
.ares.open .arbody{display:block}
.arbody .sol{background:var(--ok-soft);border-radius:11px;padding:10px 12px;margin-top:8px}
.foot{color:var(--faint);font-size:11.5px;margin-top:20px;text-align:center;line-height:1.7}
#copybox{width:100%;min-height:96px;margin:8px 0;font:12px ui-monospace,monospace;display:none;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:11px;padding:10px}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--ink);color:var(--card);padding:10px 20px;border-radius:13px;font:600 13px inherit;transition:transform .3s;z-index:300}
.toast.show{transform:translateX(-50%) translateY(0)}
@media(max-width:680px){.hero{grid-template-columns:1fr}.ring{margin:0 auto}.palette{width:150px}.pgrid{grid-template-columns:repeat(3,1fr)}#calc{right:160px}.brand small{display:none}.nav{margin-left:4px}.nav button{padding:7px 9px;font-size:11.5px}}
</style>
</head>
<body>
<div class="top"><div class="topin">
  <div class="logo">99</div>
  <div class="brand">Percentile99<small>CAT PREP OS</small></div>
  <div class="nav" id="nav">
    <button data-p="home" class="act">🏠 Home</button>
    <button data-p="study">📚 Study</button>
    <button data-p="practice">🎯 Practice</button>
    <button data-p="profile">👤 Profile</button>
  </div>
  <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <button class="iconbtn" id="theme" title="Toggle dark mode">🌙</button>
    <div class="avatar" id="avatar" title="Profile">?</div>
  </div>
</div></div>

<div class="wrap">
<!-- ============ HOME ============ -->
<div class="page act" id="pg-home">
  <h2 class="ph" id="greet">Welcome</h2>
  <div class="psub" id="headtag"></div>
  <div class="hero">
    <div class="ring">
      <svg width="112" height="112" viewBox="0 0 112 112">
        <circle cx="56" cy="56" r="49" fill="none" stroke="var(--ring-track)" stroke-width="9"/>
        <circle id="ringfill" cx="56" cy="56" r="49" fill="none" stroke="url(#rg)" stroke-width="9"
          stroke-linecap="round" stroke-dasharray="307.9" stroke-dashoffset="307.9" style="transition:stroke-dashoffset .7s cubic-bezier(.2,.8,.2,1)"/>
        <defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#4f46e5"/><stop offset="1" stop-color="#db2777"/></linearGradient></defs>
      </svg>
      <div class="pct"><div><b id="pctnum">0%</b><span>complete</span></div></div>
    </div>
    <div class="hstats" id="hstats"></div>
    <div class="tbars" id="tbars"></div>
  </div>
  <div class="hmcard">
    <div class="hmtop"><b>📆 Activity heatmap</b><span id="hmsum"></span></div>
    <div class="hmscroll"><div id="hmwrap"></div></div>
    <div class="hmlegend">Less <span class="pl" style="background:var(--hm0)"></span><span class="pl" style="background:var(--hm1)"></span><span class="pl" style="background:var(--hm2)"></span><span class="pl" style="background:var(--hm3)"></span><span class="pl" style="background:var(--hm4)"></span> More</div>
  </div>
  <div class="ctrl">
    <div class="seg" id="modeseg">
      <button data-pm="daily">📅 Daily</button>
      <button data-pm="weekly">🗓️ Weekly</button>
      <button data-pm="topic">🧱 Topic-wise</button>
    </div>
    <div class="seg" id="filter">
      <button class="act" data-f="all">All</button>
      <button data-f="todo">Remaining</button>
      <button data-f="done">Done</button>
    </div>
    <button class="pill primary" id="jump">Jump to next ↓</button>
    <button class="pill" id="copy">📋 Copy update</button>
  </div>
  <textarea id="copybox" readonly></textarea>
  <div id="plan"></div>
</div>

<!-- ============ STUDY ============ -->
<div class="page" id="pg-study">
  <h2 class="ph">Study Sheet</h2>
  <div class="psub">Everything, topic by topic — expand a section → topic → lectures. ▶ opens the exact video · ⭐ queues revision · 🎯 chips launch topic PYQs.</div>
  <div class="seg" id="studyseg" style="margin-bottom:12px">
    <button class="act" data-s="sheet">📋 Sheet</button>
    <button data-s="rev">⭐ Revision</button>
  </div>
  <div id="sheet"></div>
  <div id="rev" style="display:none"></div>
</div>

<!-- ============ PRACTICE ============ -->
<div class="page" id="pg-practice">
  <h2 class="ph">Practice Arena</h2>
  <div class="psub">Real CAT paper mocks, topic-wise PYQ drills, and every attempt analysed to the second.</div>
  <div id="practice"></div>
</div>

<!-- ============ PROFILE ============ -->
<div class="page" id="pg-profile">
  <h2 class="ph">Profile & Settings</h2>
  <div class="psub">Your details and plan preferences — every change re-plans the whole calendar instantly.</div>
  <div class="pcard"><h3>👤 Your details</h3>
    <div class="frow"><label>Name</label><input type="text" id="pf-name" placeholder="Your name"></div>
    <div class="frow"><label>Email</label><input type="email" id="pf-email" placeholder="you@gmail.com"></div>
    <div class="frow"><label>Target exam</label><input type="text" id="pf-target" placeholder="CAT 2026"></div>
    <div class="frow"><label>Study hours available / week</label><input type="number" id="pf-hrs" min="5" max="80" style="max-width:110px"> <span class="val">hrs</span></div>
  </div>
  <div class="pcard"><h3>🗺️ Plan type</h3>
    <div class="planopt" id="pf-mode">
      <div class="pop" data-pm="daily"><b>📅 Daily plan</b><span>Exact lectures for every single day. Best for routine-driven prep.</span></div>
      <div class="pop" data-pm="weekly"><b>🗓️ Weekly plan</b><span>A set of topics per week — flexible about which day you do what.</span></div>
      <div class="pop" data-pm="topic"><b>🧱 Topic-wise</b><span>No dates — just work through the sheet in order, at your pace.</span></div>
    </div>
  </div>
  <div class="pcard"><h3>⚡ Pace</h3>
    <div class="planopt" id="pf-pace">
      <div class="pop" data-pace="55"><b>🐢 Relaxed</b><span>~55 min video per slot</span></div>
      <div class="pop" data-pace="75"><b>🚶 Standard</b><span>~75 min per slot (commuter default)</span></div>
      <div class="pop" data-pace="100"><b>🚀 Fast</b><span>~100 min per slot</span></div>
    </div>
    <div class="frow"><label>Fine-tune (min / slot)</label><input type="range" id="cfg-min" min="45" max="120" step="5"><span class="val" id="cfg-min-val"></span></div>
    <div class="frow"><label>Slots per day</label>
      <div class="seg"><button data-mode="2">2 — AM + PM (commuter)</button><button data-mode="1">1 — single session</button></div></div>
    <div class="frow"><label>Start date</label><input type="date" id="cfg-start"></div>
    <div class="preview" id="preview"></div>
  </div>
  <div class="pcard"><h3>🗄️ Data</h3>
    <div class="frow">
      <button class="pill" id="cfg-reset">Reset plan to defaults</button>
      <button class="pill" id="wipe" style="color:var(--bad)">Erase ALL progress on this device</button>
    </div>
    <div class="hint">Everything is stored locally on this device. Google sign-in & cloud sync arrive when this ships as a hosted website.</div>
  </div>
</div>
</div>

<div class="foot wrap">Built from the official Rodha playlists (469 lectures · 147.9 h) + 5 real CAT papers (391 PYQs).</div>

<!-- onboarding -->
<div id="onb"><div class="onbwrap"><div class="onbcard">
  <div class="onblogo">99</div>
  <div class="steps"><div class="stepdot on" id="sd1"></div><div class="stepdot" id="sd2"></div><div class="stepdot" id="sd3"></div></div>
  <div id="onbstep"></div>
</div></div></div>

<!-- test overlay -->
<div id="tover">
  <div class="tbar">
    <span class="ttl">🎯 CAT Practice Test</span>
    <span class="timer" id="timer">--:--</span>
    <span style="flex:1"></span>
    <button class="pill" id="calcbtn">🧮 Calculator</button>
    <button class="pill" id="fsbtn">⛶ Fullscreen</button>
    <button class="pill" id="subbtn" style="background:var(--bad);border-color:var(--bad);color:#fff">Submit Test</button>
  </div>
  <div class="tmain">
    <div class="qpanel" id="qpanel"></div>
    <div class="palette">
      <h4>Question Palette</h4>
      <div class="pgrid" id="pgrid"></div>
      <div class="plegend">
        <span><span class="pl" style="background:var(--ok)"></span>Answered</span>
        <span><span class="pl" style="background:var(--bad-soft);border:1px solid var(--bad)"></span>Visited, unanswered</span>
        <span><span class="pl" style="background:var(--mark)"></span>Marked for review</span>
        <span><span class="pl" style="background:var(--card2);border:1px solid var(--line)"></span>Not visited</span>
      </div>
    </div>
  </div>
  <div class="tfoot">
    <button class="pill" id="clearbtn">Clear Response</button>
    <button class="pill" id="markbtn" style="color:var(--mark)">Mark for Review &amp; Next</button>
    <span class="sp"></span>
    <button class="pill" id="prevbtn">← Previous</button>
    <button class="pill primary" id="nextbtn">Save &amp; Next →</button>
  </div>
</div>

<div id="calc">
  <div class="chead"><span>CALCULATOR</span><button style="border:none;background:none;cursor:pointer;color:var(--mut)" id="calcx">✕</button></div>
  <div class="cdisp" id="cdisp">0</div>
  <div class="cgrid">
    <button data-c="C">C</button><button data-c="⌫">⌫</button><button data-c="%" class="op">%</button><button data-c="÷" class="op">÷</button>
    <button data-c="7">7</button><button data-c="8">8</button><button data-c="9">9</button><button data-c="×" class="op">×</button>
    <button data-c="4">4</button><button data-c="5">5</button><button data-c="6">6</button><button data-c="−" class="op">−</button>
    <button data-c="1">1</button><button data-c="2">2</button><button data-c="3">3</button><button data-c="+" class="op">+</button>
    <button data-c="±">±</button><button data-c="0">0</button><button data-c=".">.</button><button data-c="=" class="eq">=</button>
    <button data-c="√">√</button><button data-c="x²">x²</button><button data-c="1/x">1/x</button><button data-c="00">00</button>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const DATA = __DATA__;
const BANK0 = __BANK__;
const MOCKS = __MOCKS__;
const LIST = {Q:"PLG4bwc5fquzgfMh4YFDnv7fttM0RIKiUQ", L:"PLG4bwc5fquzhDp8eqRym2Ma1ut10YF0Ea"};
const KEY="cat26_rodha_v1", TKEY="cat26_theme", CKEY="cat26_cfg", NKEY="cat26_notes", RKEY="cat26_rev",
      HKEY="cat26_tests", PKEY="cat26_pyqs", FKEY="cat26_profile";
const DEF = {slotMin:75, mode:2, start:"2026-07-13"};
const load=(k,f)=>{try{return JSON.parse(localStorage.getItem(k))||f}catch(e){return f}};
let done=load(KEY,{}), notes=load(NKEY,{}), stars=load(RKEY,{}), cfg={...DEF,...load(CKEY,{})},
    hist=load(HKEY,[]), imported=load(PKEY,[]), prof=load(FKEY,{});
prof.planMode=prof.planMode||"daily";
let filter="all"; const openNotes=new Set();
const save=()=>localStorage.setItem(KEY,JSON.stringify(done));
const saveN=()=>localStorage.setItem(NKEY,JSON.stringify(notes));
const saveR=()=>localStorage.setItem(RKEY,JSON.stringify(stars));
const saveC=()=>localStorage.setItem(CKEY,JSON.stringify(cfg));
const saveH=()=>localStorage.setItem(HKEY,JSON.stringify(hist));
const saveP=()=>localStorage.setItem(PKEY,JSON.stringify(imported));
const saveF=()=>localStorage.setItem(FKEY,JSON.stringify(prof));
const fmt=s=>{const h=Math.floor(s/3600),m=Math.round(s%3600/60);return h?h+"h "+m+"m":m+" min"};
const fmtv=s=>Math.floor(s/60)+":"+String(s%60).padStart(2,"0");
const today=()=>new Date().toISOString().slice(0,10);
const vid=(t,i)=>t+i;
const V=t=>t==="Q"?DATA.vq:DATA.vd;
const yt=(t,i)=>`https://www.youtube.com/watch?v=${V(t)[i][3]}&list=${LIST[t]}`;
const SUBMAIN=Object.fromEntries(DATA.subs.map(([m,s])=>[s,m]));
const MPOOL=MOCKS.flatMap((m,mi)=>m.sections.flatMap(sec=>sec.qs.filter(q=>q.sub).map(q=>({...q,_m:mi,topic:SUBMAIN[q.sub]||sec.name,sec:sec.name,src:m.name}))));
const allQ=()=>BANK0.concat(imported,MPOOL);
const ctxOf=q=>q.c===undefined?null:(q._m!==undefined?MOCKS[q._m].ctxs[q.c]:(PT.mock?PT.mock.ctxs[q.c]:null));

/* theme */
const setTheme=t=>{document.documentElement.dataset.theme=t;localStorage.setItem(TKEY,t);
  document.getElementById("theme").textContent=t==="dark"?"☀️":"🌙"};
setTheme(localStorage.getItem(TKEY)||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"));
document.getElementById("theme").onclick=()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark");

/* router */
function go(p){
  document.querySelectorAll(".page").forEach(x=>x.classList.remove("act"));
  document.getElementById("pg-"+p).classList.add("act");
  document.querySelectorAll("#nav button").forEach(b=>b.classList.toggle("act",b.dataset.p===p));
  window.scrollTo({top:0});
}
document.querySelectorAll("#nav button").forEach(b=>b.onclick=()=>go(b.dataset.p));
document.getElementById("avatar").onclick=()=>go("profile");

/* scheduler */
function pack(tr,cap){const arr=V(tr),slots=[];let cur=[],s=0;
  arr.forEach((v,i)=>{if(cur.length&&s+v[1]>cap){slots.push(cur);cur=[];s=0}cur.push(i);s+=v[1]});
  if(cur.length)slots.push(cur);return slots}
let DAYS=[];
function computeDays(){
  const cap=cfg.slotMin*60, qs=pack("Q",cap), ls=pack("L",cap);
  const days=[];let qi=0,li=0,d=0;
  if(cfg.mode===2){
    while(qi<qs.length||li<ls.length){const slots=[];
      if(qi<qs.length)slots.push({tr:"Q",lab:"AM · QUANT",idx:qs[qi++]});
      if(li<ls.length)slots.push({tr:"L",lab:"PM · LRDI",idx:ls[li++]});
      else if(qi<qs.length)slots.push({tr:"Q",lab:"PM · QUANT",idx:qs[qi++]});
      days.push({d:++d,slots})}
  }else{
    let turnQ=true;
    while(qi<qs.length||li<ls.length){let slot;
      if(turnQ&&qi<qs.length)slot={tr:"Q",lab:"QUANT",idx:qs[qi++]};
      else if(li<ls.length)slot={tr:"L",lab:"LRDI",idx:ls[li++]};
      else slot={tr:"Q",lab:"QUANT",idx:qs[qi++]};
      turnQ=!turnQ;days.push({d:++d,slots:[slot]})}
  }
  const start=new Date(cfg.start+"T00:00:00");
  days.forEach(x=>{const dt=new Date(start);dt.setDate(dt.getDate()+x.d-1);x.dt=dt});
  DAYS=days;
  const fin=days[days.length-1].dt;
  document.getElementById("headtag").textContent=
    `469 lectures · ${days.length} plan days · finish ${fin.toLocaleDateString("en-IN",{day:"numeric",month:"short"})} · ${allQ().length} PYQs in the bank`;
  document.getElementById("preview").textContent=
    `→ ${days.length} days · finishes ${fin.toLocaleDateString("en-IN",{weekday:"short",day:"numeric",month:"short",year:"numeric"})} at ${cfg.slotMin} min × ${cfg.mode} slot${cfg.mode>1?"s":""}/day`;
}
function dayStatus(day){let t=0,n=0;
  for(const sl of day.slots)for(const i of sl.idx){t++;if(done[vid(sl.tr,i)])n++}
  return[n,t]}
function firstOpenDay(){for(const d of DAYS){const[n,t]=dayStatus(d);if(n<t)return d.d}return null}

/* heatmap */
function heatmap(){
  const act={};
  for(const k in done){const v=done[k];if(typeof v==="string")act[v]=(act[v]||0)+1}
  hist.forEach(s=>{if(s.date)act[s.date]=(act[s.date]||0)+(s.n||0)});
  let start=new Date(cfg.start+"T00:00:00");const now=new Date();
  if(now<start)start=new Date(now);
  const keys=Object.keys(act).sort();
  if(keys.length&&new Date(keys[0]+"T00:00:00")<start)start=new Date(keys[0]+"T00:00:00");
  let end=new Date("2026-11-29T00:00:00");if(now>end)end=now;
  start.setDate(start.getDate()-start.getDay());
  const days=Math.floor((end-start)/864e5)+1, weeks=Math.ceil(days/7);
  const lvl=n=>n>=8?4:n>=5?3:n>=3?2:n>=1?1:0;
  const tstr=today();
  let months='<div class="hmmonths">',cols='<div class="hmgrid">',lastM=-1,total=0,active=0;
  for(let w=0;w<weeks;w++){
    const d0=new Date(start);d0.setDate(d0.getDate()+w*7);
    months+=`<span>${d0.getMonth()!==lastM?d0.toLocaleDateString("en-IN",{month:"short"}):""}</span>`;
    lastM=d0.getMonth();
    let col='<div class="hmcol">';
    for(let i=0;i<7;i++){
      const d=new Date(start);d.setDate(d.getDate()+w*7+i);
      if(d>end){col+='<span class="hmcell" style="visibility:hidden"></span>';continue}
      const ds=d.toISOString().slice(0,10),n=act[ds]||0;
      if(n){total+=n;active++}
      col+=`<span class="hmcell l${lvl(n)}${ds===tstr?' today':''}" title="${n} item${n===1?'':'s'} · ${d.toLocaleDateString('en-IN',{day:'numeric',month:'short'})}"></span>`;
    }
    cols+=col+'</div>';
  }
  document.getElementById("hmwrap").innerHTML=months+'</div>'+cols+'</div>';
  document.getElementById("hmsum").textContent=`${total} items across ${active} active days`;
}

/* shared lecture row */
const row=(tr,i)=>{const v=V(tr)[i],id=vid(tr,i),nk=notes[id];
  return`<div class="vid ${done[id]?'ck':''}">
    <input type="checkbox" data-id="${id}" ${done[id]?'checked':''}>
    <span class="nm">${v[0]}</span><span class="du">${fmtv(v[1])}</span>
    <span class="act3">
      <a class="abtn yt" href="${yt(tr,i)}" target="_blank" rel="noopener" title="Watch on YouTube">▶</a>
      <button class="abtn star ${stars[id]?'on':''}" data-star="${id}" title="Mark for revision">${stars[id]?'★':'☆'}</button>
      <button class="abtn note ${nk?'on':''}" data-notebtn="${id}" title="Notes">✎</button>
    </span></div>
    <div class="notebox ${openNotes.has(id)?'open':''}" id="nb-${id}">
      <textarea data-note="${id}" placeholder="Your notes / remarks…">${nk?nk.replace(/</g,"&lt;"):""}</textarea></div>`};
function pyqCount(f){return allQ().filter(f).length}

/* ---------- render ---------- */
function render(){
  computeDays();heatmap();
  document.getElementById("greet").textContent=prof.name?`Hi ${prof.name.split(" ")[0]} 👋`:"Welcome";
  document.getElementById("avatar").textContent=prof.name?prof.name[0].toUpperCase():"?";
  let qd=0,qs=0,ld=0,ls=0,starN=0;
  DATA.vq.forEach((v,i)=>{if(done[vid("Q",i)]){qd++;qs+=v[1]}if(stars[vid("Q",i)])starN++});
  DATA.vd.forEach((v,i)=>{if(done[vid("L",i)]){ld++;ls+=v[1]}if(stars[vid("L",i)])starN++});
  const next=firstOpenDay();
  let daysDone=0;for(const d of DAYS){const[a,b]=dayStatus(d);if(a===b)daysDone++}
  const frac=(qs+ls)/(DATA.qsecs+DATA.dsecs);
  document.getElementById("ringfill").style.strokeDashoffset=(307.9*(1-frac)).toFixed(1);
  document.getElementById("pctnum").textContent=Math.round(frac*100)+"%";
  const dleft=Math.max(0,Math.ceil((new Date("2026-11-29")-new Date())/864e5));
  document.getElementById("hstats").innerHTML=
    `<div class="hs"><b>${daysDone}<span style="font-size:12px;color:var(--mut)"> / ${DAYS.length}</span></b><span>days done</span></div>`+
    `<div class="hs"><b>${qd+ld}<span style="font-size:12px;color:var(--mut)"> / 469</span></b><span>lectures</span></div>`+
    `<div class="hs"><b>${starN}</b><span>⭐ revision</span></div>`+
    `<div class="hs"><b>${dleft}</b><span>days to CAT</span></div>`;
  const bar=(l,sub,f,c)=>`<div class="bar"><div class="lbl"><span><b>${l}</b> ${sub}</span><span>${Math.round(f*100)}%</span></div><div class="track"><div class="fill" style="width:${(f*100).toFixed(1)}%;background:${c}"></div></div></div>`;
  document.getElementById("tbars").innerHTML=
    bar("Quant",`· ${qd}/384`,qs/DATA.qsecs,"var(--qa)")+bar("LRDI",`· ${ld}/85`,ls/DATA.dsecs,"var(--lr)");
  document.querySelectorAll("#modeseg button").forEach(b=>b.classList.toggle("act",b.dataset.pm===prof.planMode));
  document.getElementById("filter").style.display=prof.planMode==="daily"?"inline-flex":"none";
  document.getElementById("jump").style.display=prof.planMode!=="topic"?"":"none";
  renderPlan(next);
  renderStudy();
  renderPracticeHome();
  bind();
}
function renderPlan(next){
  const el=document.getElementById("plan");
  if(prof.planMode==="topic"){
    // next 2 incomplete sub-topics
    const seen=new Set();const upnext=[];
    ["Q","L"].forEach(t=>V(t).forEach((v,i)=>{
      const s=DATA.subs[v[2]][1];if(seen.has(s))return;
      if(!done[vid(t,i)]){seen.add(s);
        if(upnext.length<2){const items=[];V(t).forEach((v2,j)=>{if(DATA.subs[v2[2]][1]===s)items.push([t,j])});
          upnext.push({s,main:DATA.subs[v[2]][0],items})}}
    }));
    el.innerHTML=`<div class="pcard"><h3>🧱 Topic-wise mode</h3>
      <div class="hint">No dates, no pressure — work down the sheet in order. Here's what's next:</div>
      ${upnext.map(u=>`<div class="slothead" style="margin-top:10px"><span class="badge q">${u.main}</span><span class="topic">${u.s}</span></div>`+
        u.items.map(([t,i])=>row(t,i)).join("")).join("")}
      <div class="dayact"><button class="pill primary" onclick="go('study')" style="margin-top:8px">Open the full sheet →</button></div></div>`;
    return;
  }
  if(prof.planMode==="weekly"){
    let html="";
    for(let w=0;w<Math.ceil(DAYS.length/7);w++){
      const wd=DAYS.slice(w*7,w*7+7);
      let t=0,n=0,secs=0;const subsSeen=[];
      wd.forEach(day=>{const[a,b]=dayStatus(day);n+=a;t+=b;
        day.slots.forEach(sl=>sl.idx.forEach(i=>{secs+=V(sl.tr)[i][1];
          const s=DATA.subs[V(sl.tr)[i][2]][1];
          if(!subsSeen.some(x=>x.s===s))subsSeen.push({s,tr:sl.tr,items:[]});
          subsSeen.find(x=>x.s===s).items.push([sl.tr,i])}))});
      const isDone=n===t, isNext=!isDone&&!html.includes("next");
      const d1=wd[0].dt,d2=wd[wd.length-1].dt;
      const rng=d1.toLocaleDateString("en-IN",{day:"numeric",month:"short"})+" – "+d2.toLocaleDateString("en-IN",{day:"numeric",month:"short"});
      html+=`<div class="day ${isDone?'done':''} ${isNext?'next':''}" id="week${w+1}">
        <div class="dhead" data-d="w${w}"><div class="dnum">${isDone?"✓":"W"+(w+1)}</div>
        <div><div class="dn">Week ${w+1}</div><div class="dd">${rng} · ${fmt(secs)} video</div></div>
        ${isNext?'<span class="chip up">THIS WEEK</span>':''}
        <div class="dright"><span class="dprog">${isDone?'<span class="donetick">done ✓</span>':n+" / "+t}</span><span class="caret">▼</span></div></div>
        <div class="dbody">${subsSeen.map(x=>`<div class="slothead" style="margin-top:8px"><span class="badge ${x.tr==="Q"?"q":"l"}">${x.tr==="Q"?"QA":"LRDI"}</span><span class="topic">${x.s}</span></div>`+x.items.map(([t2,i])=>row(t2,i)).join("")).join("")}</div></div>`;
    }
    el.innerHTML=html;
    return;
  }
  // daily
  el.innerHTML=DAYS.map(day=>{
    const[n,t]=dayStatus(day),isDone=n===t,isNext=day.d===next;
    if(filter==="todo"&&isDone)return"";
    if(filter==="done"&&!isDone)return"";
    const wk=[0,6].includes(day.dt.getDay());
    const ds=day.dt.toLocaleDateString("en-IN",{weekday:"short",day:"numeric",month:"short"});
    let body="";
    for(const sl of day.slots){
      let secs=0;sl.idx.forEach(i=>secs+=V(sl.tr)[i][1]);
      const names=[...new Set(sl.idx.map(i=>DATA.subs[V(sl.tr)[i][2]][1]))].join(" → ");
      body+=`<div class="slot"><div class="slothead"><span class="badge ${sl.tr==="Q"?"q":"l"}">${sl.lab}</span><span class="topic">${names}</span><span class="dur">${fmt(secs)}</span></div>${sl.idx.map(i=>row(sl.tr,i)).join("")}</div>`}
    body+=`<div class="dayact"><button data-all="${day.d}">${isDone?"Un-mark day":"✓ Mark whole day done"}</button></div>`;
    return`<div class="day ${isDone?'done':''} ${isNext?'next open':''}" id="day${day.d}">
      <div class="dhead" data-d="${day.d}">
        <div class="dnum">${isDone?"✓":day.d}</div>
        <div><div class="dn">Day ${day.d}</div><div class="dd">${ds}</div></div>
        ${isNext?'<span class="chip up">UP NEXT</span>':''}${wk?'<span class="chip wk">WEEKEND</span>':''}
        <div class="dright"><span class="dprog">${isDone?'<span class="donetick">done ✓</span>':n+" / "+t}</span><span class="caret">▼</span></div>
      </div><div class="dbody">${body}</div></div>`}).join("")||`<div class="empty">Nothing here 🎉</div>`;
}
function renderStudy(){
  const build=(tr,label,icon,cls,total,secsTotal)=>{
    const mains=new Map();
    V(tr).forEach((v,i)=>{const[m,s]=DATA.subs[v[2]];
      if(!mains.has(m))mains.set(m,{subs:new Map(),c:0,dc:0,s:0});
      const M=mains.get(m);M.c++;M.s+=v[1];
      if(!M.subs.has(s))M.subs.set(s,{items:[],dc:0,secs:0});
      const S=M.subs.get(s);S.items.push(i);S.secs+=v[1];
      if(done[vid(tr,i)]){M.dc++;S.dc++}});
    const ico={"Number System":"🔢","Geometry":"📐","Arithmetic":"➗","Algebra":"𝑥","Modern Math":"🎲","Practice & Revision":"🔁","LR Foundations":"🧩","Puzzles":"🧠","Logic Sets":"⚖️","Data Interpretation":"📊","Advanced Practice":"🔥"};
    let dcTot=0;mains.forEach(M=>dcTot+=M.dc);
    let inner="";let mi=0;
    for(const[m,M]of mains){
      let subsHtml="";let si=0;
      for(const[s,S]of M.subs){
        const pq=pyqCount(q=>q.sub===s);
        const full=S.dc===S.items.length;
        subsHtml+=`<div class="sub" id="sub-${tr}-${mi}-${si}"><div class="subhead">
          <span class="caret">▼</span><span class="sname2">${s}</span>
          <span class="scount">${S.dc}/${S.items.length} · ${fmt(S.secs)}</span>
          ${pq?`<button class="chip pyq" data-pyq="${s.replace(/"/g,'&quot;')}">${full?'✓ ':''}🎯 ${pq} PYQs</button>`:''}
          <span class="mini"><i style="width:${(S.dc/S.items.length*100).toFixed(0)}%"></i></span></div>
          <div class="subbody">${S.items.map(i=>row(tr,i)).join("")}</div></div>`;
        si++;
      }
      const tq=pyqCount(q=>q.topic===m);
      inner+=`<div class="mtop" id="m-${tr}-${mi}"><div class="mhead">
        <div class="mico">${ico[m]||"📚"}</div>
        <div><div class="mname">${m}</div><div class="msub">${M.c} lectures · ${fmt(M.s)}${tq?` · 🎯 ${tq} PYQs`:''}</div></div>
        <div class="mright"><span class="mpct">${Math.round(M.dc/M.c*100)}%</span><span class="caret">▼</span></div></div>
        <div class="mbody">${subsHtml}</div></div>`;
      mi++;
    }
    return`<div class="sec2 open" id="sec-${tr}"><div class="shead">
      <div class="sico ${cls}" style="background:${tr==="Q"?"var(--qa-soft)":"var(--lr-soft)"}">${icon}</div>
      <div><div class="sname">${label}</div><div class="ssub">${total} lectures · ${fmt(secsTotal)} · ${dcTot} done</div></div>
      <div class="mright"><span class="mpct">${Math.round(dcTot/total*100)}%</span><span class="caret">▼</span></div></div>
      <div class="sbody">${inner}</div></div>`;
  };
  document.getElementById("sheet").innerHTML=
    build("Q","Quantitative Aptitude","➗","q",384,DATA.qsecs)+
    build("L","LRDI — Logical Reasoning & DI","🧩","l",85,DATA.dsecs);
  const groups={};
  ["Q","L"].forEach(t=>V(t).forEach((v,i)=>{const id=vid(t,i);if(!stars[id])return;
    const[m]=DATA.subs[v[2]],k=(t==="Q"?"QA · ":"LRDI · ")+m;
    (groups[k]=groups[k]||[]).push([t,i])}));
  document.getElementById("rev").innerHTML=Object.entries(groups).map(([k,arr])=>
    `<div class="rev"><div class="rhead">⭐ ${k} <span style="color:var(--mut);font-weight:400;font-size:11.5px">· ${arr.length} marked</span></div>
     <div class="body">${arr.map(([t,i])=>row(t,i)).join("")}</div></div>`).join("")||
    `<div class="empty">Nothing starred yet.<br>Hit ☆ on any lecture to queue it for revision.</div>`;
}

/* ---------- PRACTICE ---------- */
let sel=new Set(), selCount=10, selPace=120;
let PT={view:"home"};
function renderPracticeHome(){
  if(PT.view!=="home")return;
  const bank=allQ();
  const groups={};
  bank.forEach(q=>{if(!q.sub)return;const k=(q.sec||"QA")+" · "+(q.topic||"");(groups[k]=groups[k]||{})[q.sub]=(groups[k][q.sub]||0)+1});
  const pool=bank.filter(q=>sel.has(q.sub)).length;
  const chips=Object.entries(groups).map(([g,subsMap])=>
    `<div class="tgroup"><div class="glab">${g}</div><div class="tchips">${
      Object.entries(subsMap).map(([s,n])=>
        `<button class="tchip ${sel.has(s)?'on':''}" data-tsel="${s.replace(/"/g,'&quot;')}">${s} <span class="n">· ${n}</span></button>`).join("")
    }</div></div>`).join("");
  const histHtml=hist.slice().reverse().slice(0,8).map(s=>
    `<div class="histrow"><span class="sc" style="color:${s.score>=0?'var(--ok)':'var(--bad)'}">${s.score>0?'+':''}${s.score}</span>
     <span>${s.correct}✓ ${s.wrong}✗ ${s.skip}−</span><span class="mu">${s.n} Qs · ${fmtv(s.secs)} · ${s.date}</span>
     <span class="mu" style="margin-left:auto">${s.topics||""}</span></div>`).join("");
  const mockCard=`<div class="pcard"><h3>🏆 Full-Paper Mocks — actual CAT papers</h3>
    <div class="hint">Section-locked (VARC → DILR → QA), per-section timer, no going back — exactly like exam day.</div>
    ${MOCKS.map((m,i)=>{const sk=m.sections.reduce((a,s)=>a+s.skip,0);
      const att=hist.filter(h=>h.kind==="mock"&&h.paper===m.name).length;
      return `<div class="histrow"><b style="min-width:140px">${m.name}</b>
      <span class="mu">${m.sections.map(s=>s.name+" "+s.qs.length).join(" · ")} · ${m.secMin} min/section${sk?` · ${sk} Qs excluded (figures lost in source PDF)`:''}${att?` · attempted ${att}×`:''}</span>
      <button class="pill go" style="margin-left:auto;flex:none" data-mock="${i}">▶ Start</button></div>`}).join("")}
  </div>`;
  document.getElementById("practice").innerHTML=mockCard+`
  <div class="pcard"><h3>🎯 Topic drill — timed PYQ set</h3>
    <div class="hint">Pick topics (the Study sheet shows 🎯 chips on each), choose length, get the CAT interface with palette, calculator and per-question analysis. Real CAT PYQs are auto-tagged into topics.</div>
    <div class="frow"><label>Number of questions</label>
      <div class="seg">${[5,10,15,20].map(n=>`<button data-qn="${n}" class="${selCount===n?'act':''}">${n}</button>`).join("")}</div></div>
    <div class="frow"><label>Pace</label>
      <div class="seg">${[[120,"CAT · 2 min/Q"],[90,"Sprint · 1.5 min/Q"],[0,"Untimed"]].map(([v,l])=>`<button data-pace="${v}" class="${selPace===v?'act':''}">${l}</button>`).join("")}</div></div>
    ${chips}
    <div class="frow" style="margin-top:14px">
      <button class="pill go" id="startbtn" ${pool===0?"disabled style='opacity:.5'":""}>▶ Start test (${Math.min(selCount,pool)} of ${pool} available)</button>
      <button class="pill" id="selall">Select all topics</button>
      <button class="pill" id="selnone">Clear</button>
    </div>
  </div>
  <div class="pcard"><h3>📜 Attempt history</h3>${histHtml||'<div class="hint">No attempts yet — your tests and mocks will appear here and on the heatmap.</div>'}</div>
  <div class="pcard"><h3>📥 Import more PYQ sets</h3>
    <div class="hint">Loaded: <b>${BANK0.length} practice + ${MPOOL.length} real CAT PYQs (auto-tagged)</b> + <b>${imported.length} imported</b>. Paste a JSON array —
    <code>{"id","sec","topic","sub","type":"mcq|tita","q","opts":[…],"ans","sol","year","src"}</code>. Give Claude any paper in chat to convert.</div>
    <textarea class="imp" id="impbox" placeholder='[{"id":"c24-q1","sec":"QA","topic":"Arithmetic","sub":"Percentages","type":"mcq","q":"…","opts":["a","b","c","d"],"ans":0,"sol":"…","year":2024,"src":"CAT 2024 Slot 1"}]'></textarea>
    <div class="frow" style="margin-top:8px">
      <button class="pill primary" id="impbtn">Import</button>
      ${imported.length?'<button class="pill" id="impclear">Remove imported ('+imported.length+')</button>':''}
    </div>
  </div>`;
  bindPractice();
}
function bindPractice(){
  document.querySelectorAll("[data-mock]").forEach(b=>b.onclick=()=>startMock(+b.dataset.mock));
  document.querySelectorAll("[data-tsel]").forEach(b=>b.onclick=()=>{
    const s=b.dataset.tsel;sel.has(s)?sel.delete(s):sel.add(s);renderPracticeHome()});
  document.querySelectorAll("[data-qn]").forEach(b=>b.onclick=()=>{selCount=+b.dataset.qn;renderPracticeHome()});
  document.querySelectorAll("[data-pace]").forEach(b=>b.onclick=()=>{selPace=+b.dataset.pace;renderPracticeHome()});
  const sa=document.getElementById("selall");if(sa)sa.onclick=()=>{allQ().forEach(q=>q.sub&&sel.add(q.sub));renderPracticeHome()};
  const sn=document.getElementById("selnone");if(sn)sn.onclick=()=>{sel.clear();renderPracticeHome()};
  const st=document.getElementById("startbtn");if(st)st.onclick=startTest;
  const ib=document.getElementById("impbtn");if(ib)ib.onclick=()=>{
    try{const arr=JSON.parse(document.getElementById("impbox").value);
      if(!Array.isArray(arr))throw 0;
      const ok=arr.filter(q=>q.id&&q.q&&q.sub&&q.type&&(q.type==="tita"||Array.isArray(q.opts)));
      const ids=new Set(allQ().map(q=>q.id));
      const fresh=ok.filter(q=>!ids.has(q.id));
      imported=imported.concat(fresh);saveP();renderPracticeHome();
      toast(`Imported ${fresh.length} questions`);
    }catch(e){toast("Invalid JSON — check the format")}};
  const ic=document.getElementById("impclear");if(ic)ic.onclick=()=>{imported=[];saveP();renderPracticeHome();toast("Imported questions removed")};
}

/* test engine */
function startTest(){
  const pool=allQ().filter(q=>sel.has(q.sub));
  if(!pool.length)return;
  const qs=pool.slice().sort(()=>Math.random()-0.5).slice(0,selCount);
  PT={view:"test",kind:"practice",qs,cur:0,ans:{},marked:{},visited:{},times:qs.map(()=>0),
      pace:selPace,remain:selPace?selPace*qs.length:0,elapsed:0,timer:null};
  document.getElementById("tover").classList.add("on");
  document.getElementById("subbtn").textContent="Submit Test";
  document.querySelector("#tover .ttl").textContent="🎯 Topic Drill";
  PT.timer=setInterval(tick,1000);
  showQ(0);
}
function startMock(mi){
  const m=MOCKS[mi];
  PT={view:"test",kind:"mock",mock:m,si:-1,results:[],elapsed:0,timer:null,pace:1};
  document.getElementById("tover").classList.add("on");
  document.getElementById("subbtn").textContent="End Section";
  PT.timer=setInterval(tick,1000);
  loadSection(0);
  toast(`${m.name} — ${m.sections[0].name} begins. ${m.secMin} minutes.`);
}
function loadSection(si){
  const sec=PT.mock.sections[si];
  PT.si=si;PT.qs=sec.qs;PT.cur=0;PT.ans={};PT.marked={};PT.visited={};
  PT.times=sec.qs.map(()=>0);PT.remain=PT.mock.secMin*60;
  document.querySelector("#tover .ttl").textContent=`🏆 ${PT.mock.name} — ${sec.name} (${si+1}/${PT.mock.sections.length})`;
  showQ(0);
}
function gradeCurrent(){
  let score=0,correct=0,wrong=0,skip=0;
  const rows=PT.qs.map((q,i)=>{
    const a=PT.ans[i],att=a!==undefined,ok=eqAns(q,a);
    if(!att)skip++;else if(ok){correct++;score+=3}else{wrong++;if(q.type==="mcq")score-=1}
    return{q,i,a,att,ok,t:PT.times[i]}});
  return{rows,score,correct,wrong,skip};
}
function endSection(){
  const g=gradeCurrent();
  g.name=PT.mock.sections[PT.si].name;g.skipQ=PT.mock.sections[PT.si].skip;
  PT.results.push(g);
  if(PT.si+1<PT.mock.sections.length){
    loadSection(PT.si+1);
    toast(`Section locked. ${PT.mock.sections[PT.si].name} begins — ${PT.mock.secMin} min.`);
  }else finishMock();
}
function tick(){
  PT.times[PT.cur]++;PT.elapsed++;
  if(PT.pace){PT.remain--;
    if(PT.remain<=0)return PT.kind==="mock"?endSection():submitTest();
    const el=document.getElementById("timer");
    el.textContent=fmtv(PT.remain);el.classList.toggle("low",PT.remain<=60);
  }else document.getElementById("timer").textContent=fmtv(PT.elapsed);
}
function showQ(i){
  PT.cur=i;PT.visited[i]=true;
  const q=PT.qs[i];
  const tag=PT.kind==="mock"?PT.mock.sections[PT.si].name:`${q.topic||""} · ${q.sub||""}`;
  let inner=`<div class="qhead"><span class="qnum">Question ${i+1} of ${PT.qs.length}</span>
    <span class="qtag">${tag}</span>
    <span class="qtype">${q.type==="mcq"?"MCQ · +3 / −1":"TITA · +3 / no negative"}${q.src?` · ${q.src}`:""}</span></div>`;
  const cx=PT.kind==="mock"?(q.c!==undefined?PT.mock.ctxs[q.c]:null):ctxOf(q);
  if(cx)inner+=`<div class="ctxbox">${cx}</div>`;
  inner+=`<div class="qtext">${q.q}</div>`;
  if(q.type==="mcq"){
    inner+=q.opts.map((o,k)=>`<div class="opt ${PT.ans[i]===k?'sel':''}" data-opt="${k}"><span class="ol">${"ABCD"[k]})</span><span>${o}</span></div>`).join("");
  }else{
    inner+=`<input class="titain" id="titain" placeholder="Type your answer" value="${PT.ans[i]!==undefined?String(PT.ans[i]).replace(/"/g,'&quot;'):''}">`;
  }
  document.getElementById("qpanel").innerHTML=inner;
  document.querySelectorAll("[data-opt]").forEach(o=>o.onclick=()=>{PT.ans[PT.cur]=+o.dataset.opt;showQ(PT.cur)});
  const ti=document.getElementById("titain");
  if(ti)ti.oninput=()=>{const v=ti.value.trim();if(v)PT.ans[PT.cur]=v;else delete PT.ans[PT.cur];palette()};
  document.getElementById("timer").textContent=fmtv(PT.pace?PT.remain:PT.elapsed);
  palette();
}
function palette(){
  document.getElementById("pgrid").innerHTML=PT.qs.map((q,i)=>{
    const a=PT.ans[i]!==undefined,m=PT.marked[i],v=PT.visited[i];
    let cls=m?(a?"mkans":"mk"):a?"ans":v?"seen":"";
    return`<button class="pbtn ${cls} ${i===PT.cur?'cur':''}" data-goto="${i}">${i+1}</button>`}).join("");
  document.querySelectorAll("[data-goto]").forEach(b=>b.onclick=()=>showQ(+b.dataset.goto));
}
document.getElementById("nextbtn").onclick=()=>showQ(Math.min(PT.cur+1,PT.qs.length-1));
document.getElementById("prevbtn").onclick=()=>showQ(Math.max(PT.cur-1,0));
document.getElementById("clearbtn").onclick=()=>{delete PT.ans[PT.cur];showQ(PT.cur)};
document.getElementById("markbtn").onclick=()=>{PT.marked[PT.cur]=!PT.marked[PT.cur];showQ(Math.min(PT.cur+1,PT.qs.length-1))};
document.getElementById("subbtn").onclick=()=>{
  if(PT.kind==="mock"){
    if(confirm(PT.si+1<PT.mock.sections.length?"End this section early? You cannot come back (just like the real CAT).":"End the final section and submit the mock?"))endSection();
  }else if(confirm("Submit the test?"))submitTest()};
document.getElementById("fsbtn").onclick=()=>{
  const el=document.getElementById("tover");
  if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
  else if(el.requestFullscreen)el.requestFullscreen().catch(()=>toast("Fullscreen blocked — the test already fills the window"));
  else toast("Fullscreen not available here")};
function eqAns(q,a){
  if(a===undefined)return false;
  if(q.type==="mcq")return a===q.ans;
  const x=String(a).trim().toLowerCase(),y=String(q.ans).trim().toLowerCase();
  const nx=parseFloat(x),ny=parseFloat(y);
  if(!isNaN(nx)&&!isNaN(ny))return Math.abs(nx-ny)<1e-6;
  return x===y;
}
function closeTest(){
  clearInterval(PT.timer);
  document.getElementById("tover").classList.remove("on");
  if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
  document.getElementById("calc").classList.remove("on");
}
function qrowHtml(r,cx){
  const ua=r.att?(r.q.type==="mcq"?"ABCD"[r.a]+") "+r.q.opts[r.a]:r.a):"—";
  const ca=r.q.type==="mcq"?"ABCD"[r.q.ans]+") "+r.q.opts[r.q.ans]:r.q.ans;
  return`<div class="ares"><div class="arhead" data-ar>
    <span class="ic ${r.ok?'ok2':r.att?'bad2':'skip2'}">${r.ok?"✓":r.att?"✗":"−"}</span>
    <span class="tt">${r.q.sub?r.q.sub+" — ":""}${r.q.q.replace(/<[^>]+>/g," ").slice(0,70)}…</span>
    <span class="tm">${fmtv(r.t)}</span><span class="caret">▼</span></div>
  <div class="arbody">${cx?`<div class="ctxbox">${cx}</div>`:""}<div>${r.q.q}</div>
    ${r.q.type==="mcq"?r.q.opts.map((o,k)=>`<div style="padding:3px 0;color:${k===r.q.ans?'var(--ok)':k===r.a?'var(--bad)':'inherit'}">${"ABCD"[k]}) ${o}${k===r.q.ans?" ✓":k===r.a?" (your answer)":""}</div>`).join(""):
    `<div style="margin-top:6px">Your answer: <b>${ua}</b> · Correct: <b class="ok2">${ca}</b></div>`}
    ${r.q.sol?`<div class="sol"><b>Solution:</b> ${r.q.sol}</div>`:`<div class="sol"><b>Official answer:</b> ${ca}</div>`}
    <div style="margin-top:6px;font-size:11.5px;color:var(--mut)">Time: ${fmtv(r.t)} · ${r.q.src||"Practice set"}</div>
  </div></div>`;
}
function submitTest(){
  closeTest();
  const g=gradeCurrent();
  const topics={};
  g.rows.forEach(r=>{const k=r.q.sub||"—";topics[k]=topics[k]||{c:0,w:0,s:0,t:0};
    topics[k].t+=r.t;if(!r.att)topics[k].s++;else r.ok?topics[k].c++:topics[k].w++});
  hist.push({date:today(),n:PT.qs.length,score:g.score,correct:g.correct,wrong:g.wrong,skip:g.skip,
    secs:PT.elapsed,topics:[...new Set(PT.qs.map(q=>q.sub))].slice(0,3).join(", ")});
  saveH();
  PT.view="result";
  const acc=g.correct+g.wrong?Math.round(g.correct/(g.correct+g.wrong)*100):0;
  document.getElementById("practice").innerHTML=`
  <div class="pcard"><h3>📊 Test Analysis — ${today()}</h3>
    <div class="sumgrid">
      <div class="hs"><b style="color:${g.score>=0?'var(--ok)':'var(--bad)'}">${g.score>0?'+':''}${g.score}</b><span>score (max ${PT.qs.length*3})</span></div>
      <div class="hs"><b>${g.correct} / ${PT.qs.length}</b><span>correct</span></div>
      <div class="hs"><b>${acc}%</b><span>accuracy</span></div>
      <div class="hs"><b>${g.wrong}</b><span>wrong</span></div>
      <div class="hs"><b>${g.skip}</b><span>skipped</span></div>
      <div class="hs"><b>${fmtv(PT.elapsed)}</b><span>total time</span></div>
      <div class="hs"><b>${fmtv(Math.round(PT.elapsed/PT.qs.length))}</b><span>avg / question</span></div>
    </div>
    <h3 style="margin-top:14px">Topic-wise</h3>
    ${Object.entries(topics).map(([k,x])=>`<div class="histrow"><span style="flex:1">${k}</span>
      <span class="ok2">${x.c}✓</span><span class="bad2">${x.w}✗</span><span class="skip2">${x.s}−</span>
      <span class="mu">${fmtv(x.t)}</span></div>`).join("")}
  </div>
  <div class="pcard"><h3>Question-by-question (tap for solution)</h3>
    ${g.rows.map(r=>qrowHtml(r,ctxOf(r.q))).join("")}
    <div class="frow" style="margin-top:12px"><button class="pill primary" id="again">↺ New test</button></div>
  </div>`;
  document.querySelectorAll("[data-ar]").forEach(h=>h.onclick=()=>h.parentElement.classList.toggle("open"));
  document.getElementById("again").onclick=()=>{PT={view:"home"};render()};
  heatmap();go("practice");
}
function finishMock(){
  closeTest();
  const R=PT.results,m=PT.mock;
  const tot={score:0,correct:0,wrong:0,skip:0,n:0};
  R.forEach(g=>{tot.score+=g.score;tot.correct+=g.correct;tot.wrong+=g.wrong;tot.skip+=g.skip;tot.n+=g.rows.length});
  hist.push({kind:"mock",paper:m.name,date:today(),n:tot.n,score:tot.score,
    correct:tot.correct,wrong:tot.wrong,skip:tot.skip,secs:PT.elapsed,topics:"🏆 "+m.name});
  saveH();
  PT.view="result";
  document.getElementById("practice").innerHTML=`
  <div class="pcard"><h3>🏆 Mock Analysis — ${m.name}</h3>
    <div class="sumgrid">
      <div class="hs"><b style="color:${tot.score>=0?'var(--ok)':'var(--bad)'}">${tot.score}</b><span>total (max ${tot.n*3})</span></div>
      <div class="hs"><b>${tot.correct}✓ ${tot.wrong}✗ ${tot.skip}−</b><span>C / W / skipped</span></div>
      <div class="hs"><b>${tot.correct+tot.wrong?Math.round(tot.correct/(tot.correct+tot.wrong)*100):0}%</b><span>accuracy</span></div>
      <div class="hs"><b>${fmtv(PT.elapsed)}</b><span>total time</span></div>
    </div>
    <div class="secsum">${R.map(g=>`<div class="hs"><b>${g.name}: ${g.score}</b>
      <span>${g.correct}✓ ${g.wrong}✗ ${g.skip}−${g.skipQ?` · ${g.skipQ} Q excluded`:""}</span></div>`).join("")}</div>
    <div class="hint">${m.year===2020?"Reference: in CAT 2020 ~100/228 raw ≈ 99th percentile, ~76 ≈ 95th, ~62 ≈ 90th (approximate).":""}
    ${m.year===2017?"Reference: CAT 2017 was a 300-mark paper; ~170+ raw ≈ 99th percentile territory (approximate).":""}</div>
  </div>
  ${R.map(g=>`<div class="pcard"><h3>${g.name} — question by question</h3>${g.rows.map(r=>qrowHtml(r,r.q.c!==undefined?m.ctxs[r.q.c]:null)).join("")}</div>`).join("")}
  <div class="pcard"><button class="pill primary" id="again">↺ Back to Practice</button></div>`;
  document.querySelectorAll("[data-ar]").forEach(h=>h.onclick=()=>h.parentElement.classList.toggle("open"));
  document.getElementById("again").onclick=()=>{PT={view:"home"};render()};
  heatmap();go("practice");window.scrollTo({top:0});
}

/* calculator */
let cal={disp:"0",acc:null,op:null,fresh:true};
function calShow(){document.getElementById("cdisp").textContent=cal.disp}
function calDo(op,a,b){switch(op){case"+":return a+b;case"−":return a-b;case"×":return a*b;case"÷":return b===0?NaN:a/b}return b}
document.getElementById("calcbtn").onclick=()=>document.getElementById("calc").classList.toggle("on");
document.getElementById("calcx").onclick=()=>document.getElementById("calc").classList.remove("on");
document.querySelectorAll("#calc [data-c]").forEach(b=>b.onclick=()=>{
  const c=b.dataset.c,d=parseFloat(cal.disp);
  const round=x=>{const r=Math.round(x*1e10)/1e10;return String(isFinite(r)?r:"Error")};
  if(/^\d+$/.test(c)){cal.disp=cal.fresh||cal.disp==="0"?c:cal.disp+c;cal.fresh=false}
  else if(c==="."){if(cal.fresh){cal.disp="0.";cal.fresh=false}else if(!cal.disp.includes("."))cal.disp+="."}
  else if(c==="C"){cal={disp:"0",acc:null,op:null,fresh:true}}
  else if(c==="⌫"){cal.disp=cal.disp.length>1?cal.disp.slice(0,-1):"0"}
  else if(c==="±"){cal.disp=round(-d)}
  else if(c==="√"){cal.disp=round(Math.sqrt(d));cal.fresh=true}
  else if(c==="x²"){cal.disp=round(d*d);cal.fresh=true}
  else if(c==="1/x"){cal.disp=round(1/d);cal.fresh=true}
  else if(c==="%"){cal.disp=round(cal.acc!==null?cal.acc*d/100:d/100)}
  else if(c==="="){if(cal.op&&cal.acc!==null){cal.disp=round(calDo(cal.op,cal.acc,d));cal.acc=null;cal.op=null;cal.fresh=true}}
  else{if(cal.op&&cal.acc!==null&&!cal.fresh)cal.disp=round(calDo(cal.op,cal.acc,d));
    cal.acc=parseFloat(cal.disp);cal.op=c;cal.fresh=true}
  calShow()});

/* bindings */
function keepOpen(fn){const o=[...document.querySelectorAll('.day.open,.mtop.open,.sub.open,.sec2.open')].map(x=>x.id);fn();
  o.forEach(id=>{const e=document.getElementById(id);if(e)e.classList.add('open')})}
function bind(){
  document.querySelectorAll('.vid input').forEach(cb=>cb.onchange=e=>{
    if(e.target.checked)done[e.target.dataset.id]=today();else delete done[e.target.dataset.id];
    save();keepOpen(render)});
  document.querySelectorAll('[data-star]').forEach(b=>b.onclick=()=>{
    const id=b.dataset.star;if(stars[id])delete stars[id];else stars[id]=true;
    saveR();keepOpen(render)});
  document.querySelectorAll('[data-notebtn]').forEach(b=>b.onclick=()=>{
    const id=b.dataset.notebtn;
    document.querySelectorAll(`#nb-${CSS.escape(id)}`).forEach(nb=>{
      if(openNotes.has(id)){openNotes.delete(id);nb.classList.remove("open")}
      else{openNotes.add(id);nb.classList.add("open");nb.querySelector("textarea").focus()}})});
  document.querySelectorAll('[data-note]').forEach(t=>t.oninput=()=>{
    const id=t.dataset.note;if(t.value.trim())notes[id]=t.value;else delete notes[id];saveN();
    document.querySelectorAll(`[data-notebtn="${id}"]`).forEach(b=>b.classList.toggle("on",!!notes[id]))});
  document.querySelectorAll('[data-all]').forEach(b=>b.onclick=()=>{
    const day=DAYS.find(x=>x.d==b.dataset.all);const[n,t]=dayStatus(day);const mark=n<t;
    for(const sl of day.slots)for(const i of sl.idx){if(mark)done[vid(sl.tr,i)]=today();else delete done[vid(sl.tr,i)]}
    save();keepOpen(render);toast(mark?`Day ${day.d} complete 🎉`:`Day ${day.d} reset`)});
  document.querySelectorAll('.dhead').forEach(h=>h.onclick=e=>{
    if(e.target.tagName==="INPUT")return;h.parentElement.classList.toggle('open')});
  document.querySelectorAll('.mhead').forEach(h=>h.onclick=()=>h.parentElement.classList.toggle('open'));
  document.querySelectorAll('.subhead').forEach(h=>h.onclick=e=>{
    if(e.target.dataset.pyq!==undefined)return;h.parentElement.classList.toggle('open')});
  document.querySelectorAll('.sec2>.shead').forEach(h=>h.onclick=()=>h.parentElement.classList.toggle('open'));
  document.querySelectorAll('[data-pyq]').forEach(b=>b.onclick=e=>{
    e.stopPropagation();sel=new Set([b.dataset.pyq]);PT={view:"home"};
    renderPracticeHome();go("practice");toast("Topic loaded — start your drill")});
  document.querySelectorAll("#modeseg button").forEach(b=>b.onclick=()=>{
    prof.planMode=b.dataset.pm;saveF();render()});
}
document.getElementById("filter").querySelectorAll("button").forEach(b=>b.onclick=()=>{
  document.getElementById("filter").querySelectorAll("button").forEach(x=>x.classList.remove("act"));b.classList.add("act");
  filter=b.dataset.f;render()});
document.getElementById("jump").onclick=()=>{
  if(prof.planMode==="weekly"){
    const el=document.querySelector(".day.next");if(el){el.classList.add("open");el.scrollIntoView({behavior:"smooth",block:"center"})}
    return}
  const n=firstOpenDay();
  if(!n)return toast("All done — syllabus complete! 🏆");
  const el=document.getElementById("day"+n);if(el){el.classList.add("open");el.scrollIntoView({behavior:"smooth",block:"center"})}};
document.getElementById("studyseg").querySelectorAll("button").forEach(b=>b.onclick=()=>{
  document.getElementById("studyseg").querySelectorAll("button").forEach(x=>x.classList.remove("act"));b.classList.add("act");
  document.getElementById("sheet").style.display=b.dataset.s==="sheet"?"":"none";
  document.getElementById("rev").style.display=b.dataset.s==="rev"?"":"none"});

/* profile page */
function syncProfile(){
  document.getElementById("pf-name").value=prof.name||"";
  document.getElementById("pf-email").value=prof.email||"";
  document.getElementById("pf-target").value=prof.target||"CAT 2026";
  document.getElementById("pf-hrs").value=prof.hrsWeek||30;
  document.getElementById("cfg-min").value=cfg.slotMin;
  document.getElementById("cfg-min-val").textContent=cfg.slotMin+" min";
  document.getElementById("cfg-start").value=cfg.start;
  document.querySelectorAll("#pg-profile [data-mode]").forEach(b=>b.classList.toggle("act",+b.dataset.mode===cfg.mode));
  document.querySelectorAll("#pf-mode .pop").forEach(p=>p.classList.toggle("on",p.dataset.pm===prof.planMode));
  document.querySelectorAll("#pf-pace .pop").forEach(p=>p.classList.toggle("on",+p.dataset.pace===cfg.slotMin));
}
["pf-name","pf-email","pf-target","pf-hrs"].forEach(id=>{
  document.getElementById(id).onchange=e=>{
    prof[{"pf-name":"name","pf-email":"email","pf-target":"target","pf-hrs":"hrsWeek"}[id]]=e.target.value;
    saveF();render()}});
document.querySelectorAll("#pf-mode .pop").forEach(p=>p.onclick=()=>{prof.planMode=p.dataset.pm;saveF();syncProfile();render()});
document.querySelectorAll("#pf-pace .pop").forEach(p=>p.onclick=()=>{cfg.slotMin=+p.dataset.pace;saveC();syncProfile();keepOpen(render)});
document.getElementById("cfg-min").oninput=e=>{cfg.slotMin=+e.target.value;saveC();syncProfile();keepOpen(render)};
document.getElementById("cfg-start").onchange=e=>{if(e.target.value){cfg.start=e.target.value;saveC();keepOpen(render)}};
document.querySelectorAll("#pg-profile [data-mode]").forEach(b=>b.onclick=()=>{cfg.mode=+b.dataset.mode;saveC();syncProfile();keepOpen(render)});
document.getElementById("cfg-reset").onclick=()=>{cfg={...DEF};saveC();syncProfile();keepOpen(render);toast("Plan reset to defaults")};
document.getElementById("wipe").onclick=()=>{
  if(confirm("Erase ALL progress, notes, stars, history and profile on this device?")){
    [KEY,NKEY,RKEY,HKEY,PKEY,FKEY,CKEY].forEach(k=>localStorage.removeItem(k));location.reload()}};

/* copy update (PYQ-solved removed as requested) */
document.getElementById("copy").onclick=()=>{
  let qd=0,ld=0,st=0;DATA.vq.forEach((v,i)=>{done[vid("Q",i)]&&qd++;stars[vid("Q",i)]&&st++});
  DATA.vd.forEach((v,i)=>{done[vid("L",i)]&&ld++;stars[vid("L",i)]&&st++});
  const nxt=firstOpenDay(),pend=[];
  if(nxt){const day=DAYS.find(x=>x.d===nxt);
    for(const sl of day.slots)for(const i of sl.idx)if(!done[vid(sl.tr,i)])pend.push(V(sl.tr)[i][0])}
  const txt=`CAT tracker update (${today()}): QA ${qd}/384, LRDI ${ld}/85 · ${st} starred. On Day ${nxt||"COMPLETE"} of ${DAYS.length} (${prof.planMode} plan). Pending today: ${pend.join(", ")||"none"}.`;
  const box=document.getElementById("copybox");box.value=txt;box.style.display="block";box.select();
  try{navigator.clipboard.writeText(txt)}catch(e){document.execCommand("copy")}
  toast("Update copied — paste it to Claude")};

/* onboarding */
const GS=`<svg class="gsvg" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.5l6.7-6.7C35.6 2.4 30.1 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.3 13.2 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.5z"/><path fill="#FBBC05" d="M10.4 28.7a14.5 14.5 0 0 1 0-9.4l-7.8-6.1a24 24 0 0 0 0 21.6l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.1 0 11.2-2 15-5.5l-7.5-5.8c-2.1 1.4-4.7 2.2-7.5 2.2-6.3 0-11.7-3.7-13.6-9.2l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>`;
function onbStep(n){
  ["sd1","sd2","sd3"].forEach((id,i)=>document.getElementById(id).classList.toggle("on",i<=n-1));
  const el=document.getElementById("onbstep");
  if(n===1)el.innerHTML=`<h1>Crack CAT 2026.</h1>
    <div class="sub">469 mapped Rodha lectures · real CAT paper mocks · topic-tagged PYQs ·<br>a plan that adapts to <i>your</i> life.</div>
    <button class="gbtn" id="gsign">${GS} Continue with Google</button>
    <div style="text-align:center;margin:10px 0;color:var(--faint);font-size:11px">or</div>
    <button class="gbtn" id="manual">Set up locally →</button>
    <div class="onbnote">This preview runs fully on your device. Google sign-in &amp; cloud sync activate when the site is deployed to the web — your setup carries over.</div>`;
  if(n===2)el.innerHTML=`<h1>About you</h1><div class="sub">Used to personalise your plan — editable anytime in Profile.</div>
    <div class="frow"><label>Name</label><input type="text" id="ob-name" placeholder="Your name" value="${prof.name||""}"></div>
    <div class="frow"><label>Email</label><input type="email" id="ob-email" placeholder="you@gmail.com" value="${prof.email||""}"></div>
    <div class="frow"><label>Target exam</label><input type="text" id="ob-target" value="CAT 2026"></div>
    <div class="frow"><label>Study hours / week</label><input type="number" id="ob-hrs" value="30" min="5" max="80" style="max-width:100px"></div>
    <button class="gbtn" id="ob-next" style="margin-top:14px;background:var(--brand);color:#fff;border:none">Continue →</button>`;
  if(n===3)el.innerHTML=`<h1>How do you want to study?</h1><div class="sub">Changeable anytime from Home or Profile.</div>
    <div class="planopt" style="grid-template-columns:1fr">
      <div class="pop" data-om="daily"><b>📅 Daily plan</b><span>Exact lectures for every date — for routine lovers &amp; commuters.</span></div>
      <div class="pop" data-om="weekly"><b>🗓️ Weekly plan</b><span>Topics per week, you choose the days.</span></div>
      <div class="pop" data-om="topic"><b>🧱 Topic-wise</b><span>Just the ordered sheet — fully self-paced.</span></div>
    </div>
    <div class="planopt" style="grid-template-columns:repeat(3,1fr)">
      <div class="pop" data-op="55"><b>🐢 Relaxed</b><span>~55 min/slot</span></div>
      <div class="pop on" data-op="75"><b>🚶 Standard</b><span>~75 min/slot</span></div>
      <div class="pop" data-op="100"><b>🚀 Fast</b><span>~100 min/slot</span></div>
    </div>
    <div class="preview" id="ob-prev"></div>
    <button class="gbtn" id="ob-done" style="margin-top:14px;background:var(--brand);color:#fff;border:none">Build my plan 🚀</button>`;
  // bindings
  const g=document.getElementById("gsign");if(g)g.onclick=()=>{toast("Google sign-in arrives with the hosted version — setting up locally");onbStep(2)};
  const mn=document.getElementById("manual");if(mn)mn.onclick=()=>onbStep(2);
  const nx=document.getElementById("ob-next");if(nx)nx.onclick=()=>{
    prof.name=document.getElementById("ob-name").value.trim()||"Aspirant";
    prof.email=document.getElementById("ob-email").value.trim();
    prof.target=document.getElementById("ob-target").value.trim()||"CAT 2026";
    prof.hrsWeek=+document.getElementById("ob-hrs").value||30;saveF();onbStep(3)};
  if(n===3){
    let om="daily",op=75;
    const upd=()=>{
      document.querySelectorAll("[data-om]").forEach(p=>p.classList.toggle("on",p.dataset.om===om));
      document.querySelectorAll("[data-op]").forEach(p=>p.classList.toggle("on",+p.dataset.op===op));
      const cap=op*60,q=pack("Q",cap).length,l=pack("L",cap).length;
      let dcount;{let qi=0,li=0,c=0;while(qi<q||li<l){if(qi<q)qi++;if(li<l)li++;else if(qi<q)qi++;c++}dcount=c}
      const fin=new Date(cfg.start+"T00:00:00");fin.setDate(fin.getDate()+dcount-1);
      document.getElementById("ob-prev").textContent=`→ ${dcount} days of lectures · finish ${fin.toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"})} · then mocks till CAT`;
    };
    document.querySelectorAll("[data-om]").forEach(p=>p.onclick=()=>{om=p.dataset.om;upd()});
    document.querySelectorAll("[data-op]").forEach(p=>p.onclick=()=>{op=+p.dataset.op;upd()});
    upd();
    document.getElementById("ob-done").onclick=()=>{
      prof.planMode=om;cfg.slotMin=op;saveF();saveC();
      document.getElementById("onb").classList.remove("on");
      syncProfile();render();toast(`Welcome, ${prof.name}! Your plan is live.`)};
  }
}
if(!prof.name){document.getElementById("onb").classList.add("on");onbStep(1)}

let toastT;function toast(m){const t=document.getElementById("toast");t.textContent=m;t.classList.add("show");
  clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove("show"),2400)}
syncProfile();render();
</script>
</body>
</html>
"""
html = html.replace("__DATA__", DATA).replace("__BANK__", BANK).replace("__MOCKS__", MOCKS_J)
open("dashboard.html","w").write(html)
print("v6 written:", len(html), "bytes")
