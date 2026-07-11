#!/usr/bin/env python3
"""Parse CAT 2020 (3 slots) and CAT 2017 (2 slots) compiled PDFs into structured paper JSON."""
import re, json, subprocess, sys, glob

UP = "/sessions/practical-wizardly-gates/mnt/uploads/"

def text_of(pattern):
    f = glob.glob(UP + "*" + pattern + "*.pdf")[0]
    return subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout

SEC_CANON = {"Verbal Ability": "VARC", "DI & Reasoning": "DILR", "Quantitative Ability": "QA"}

def clean(s):
    s = re.sub(r"Actual CAT \d{4} Slot [IVX]+", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def _scan(tail, pat, letters):
    marks = []; expected = 0
    for m in re.finditer(pat, tail):
        L = letters.index(m.group(1))
        if L == expected and (m.start() == 0 or tail[m.start()-1] in " \n\t"):
            marks.append((m.start(), m.end())); expected += 1
            if expected == len(letters): break
    opts = []
    for i, (s, e) in enumerate(marks):
        end = marks[i+1][0] if i+1 < len(marks) else len(tail)
        t = tail[e:end].strip()
        t = re.split(r"\bDIRECTIONS?\b", t)[0].strip()  # cut bleed from next group
        opts.append(t)
    return opts

def parse_options(tail):
    """ordered A)->D) scan; fallback to 1.->4. numbered options."""
    opts = _scan(tail, r"([A-E])\)", "ABCDE")
    if len([o for o in opts if o]) < 4:
        num = _scan(tail, r"([1-4])\.", "1234")
        if len([o for o in num if o]) == 4:
            return num
    return opts

def parse_slot(slot_text, slot_name, year):
    # walk through: Section markers, Question blocks, Answer blocks
    events = []
    for m in re.finditer(r"Section : ([A-Za-z &]+)", slot_text):
        events.append((m.start(), "sec", m.group(1).strip()))
    for m in re.finditer(r"Question No\. : (\d+)", slot_text):
        events.append((m.start(), "q", int(m.group(1))))
    for m in re.finditer(r"QNo:-\s*(\d+)\s*,\s*Correct Answer:-\s*([^\n]+)", slot_text):
        events.append((m.start(), "a", (int(m.group(1)), m.group(2).strip())))
    for m in re.finditer(r"DIRECTIONS", slot_text):
        events.append((m.start(), "d", None))
    events.sort()
    sections = []  # each: {name, qs: {num: {...}}}
    cur = None; pending_dir = False
    for idx, (pos, kind, val) in enumerate(events):
        end = events[idx+1][0] if idx+1 < len(events) else len(slot_text)
        chunk = slot_text[pos:end]
        if kind == "sec":
            name = SEC_CANON.get(val, val)
            if not sections or sections[-1]["name"] != name:
                sections.append({"name": name, "qs": {}, "order": []})
            cur = sections[-1]; pending_dir = False
        elif kind == "d":
            pending_dir = True
        elif kind == "q" and cur is not None:
            body = re.sub(r"^Question No\. : \d+\s*", "", chunk)
            # strip footer noise
            body = re.sub(r"QNo:-.*", "", body, flags=re.S)
            cur["qs"][val] = {"raw": clean(body), "lead": pending_dir}
            cur["order"].append(val)
            pending_dir = False
        elif kind == "a" and cur is not None:
            qn, ans = val
            expl = ""
            em = re.search(r"Explanation:-?\s*(.*)", chunk, flags=re.S)
            if em:
                expl = clean(re.sub(r"(Section :|Question No\. :).*", "", em.group(1), flags=re.S))
            if qn in cur["qs"]:
                cur["qs"][qn]["ans_raw"] = ans
                cur["qs"][qn]["sol"] = expl
    # post-process questions: directions groups, ctx, options
    out_sections = []
    for sec in sections:
        qs_out = []
        ctx_current = None
        for qn in sec["order"]:
            q = sec["qs"][qn]
            raw = q["raw"]
            has_dir = q.get("lead", False)
            if has_dir:
                raw = re.sub(r"^DIRECTIONS[^\n]*\n?", "", raw).strip()
                ctx_current = None  # new group
            # options split
            om = re.search(r"(?:^|[\s])A\)", raw)
            if om:
                stem_part = raw[:om.start()].strip()
                opts = parse_options(raw[om.start():])
            else:
                stem_part = raw.strip()
                opts = None
            # TITA detection: "(in numerical value)" marker, or empty B/C/D options
            is_tita = "(in numerical value" in stem_part.lower() or (
                opts is not None and len(opts) >= 2 and
                sum(1 for o in opts[1:] if not o or o in ("B)","C)","D)")) >= len(opts[1:]) - 0
                and all(len(o) <= 2 for o in opts[1:]))
            # ctx extraction for group-leading question with a long body
            stem = stem_part
            if has_dir and len(stem_part) > 600:
                lines = [l for l in stem_part.split("\n")]
                tail, tl = [], 0
                for l in reversed(lines):
                    tail.insert(0, l); tl += len(l)
                    if tl >= 200: break
                head = "\n".join(lines[:len(lines)-len(tail)]).strip()
                if len(head) > 400:
                    ctx_current = head
                    stem = "\n".join(tail).strip()
                else:
                    ctx_current = None
            elif has_dir:
                ctx_current = None
            item = {"n": qn, "q": stem}
            if ctx_current: item["ctx"] = ctx_current
            ar = q.get("ans_raw", "").strip()
            if is_tita:
                item["type"] = "tita"
                item["ans"] = ar or (opts[0] if opts else "")
                if not item["ans"]: item["flag"] = "no_tita_ans"
            elif opts and len(opts) >= 4 and all(o for o in opts[:4]):
                item["type"] = "mcq"; item["opts"] = opts[:4]
                L = ar.upper()[:1]
                if L in "ABCD":
                    item["ans"] = "ABCD".index(L)
                else:
                    item["flag"] = "bad_mcq_ans:" + ar
            elif opts:
                item["type"] = "mcq"; item["opts"] = opts; item["flag"] = "few_opts"
                L = ar.upper()[:1]
                if L in "ABCD": item["ans"] = "ABCD".index(L)
            else:
                item["type"] = "tita"; item["ans"] = ar
                if not ar: item["flag"] = "no_tita_ans"
            item["sol"] = q.get("sol", "")
            # mark image-lost questions (formulas/figures dropped by text extraction)
            if item["type"] == "mcq":
                bad_opts = len(item.get("opts", [])) < 4 or any(not o for o in item["opts"])
                bad_ans = "ans" not in item or item.get("ans") is None or (item.get("ans", 0) >= len(item.get("opts", [])))
                if bad_opts or bad_ans or len(item["q"]) < 15:
                    item["img"] = True
            elif not item.get("ans"):
                item["img"] = True
            # TITA whose 'answer' is an option letter = MCQ with image options -> unusable
            if item["type"] == "tita" and re.fullmatch(r"[A-Da-d]", str(item.get("ans",""))):
                item["img"] = True
            qs_out.append(item)
        out_sections.append({"name": sec["name"], "qs": qs_out})
    return {"name": slot_name, "sections": out_sections}

def parse_file(pattern, year, sec_min):
    txt = text_of(pattern)
    # split on slot headers
    slots = []
    marks = [(m.start(), m.group(0)) for m in re.finditer(r"Actual CAT \d{4} (?:Slot|Shift) [IVX]+\nDirections of Test", txt)]
    for i, (pos, head) in enumerate(marks):
        end = marks[i+1][0] if i+1 < len(marks) else len(txt)
        name = head.split("\n")[0]
        slots.append((name, txt[pos:end]))
    papers = []
    for name, body in slots:
        p = parse_slot(body, name, year)
        p["id"] = re.sub(r"[^a-z0-9]+", "", name.lower())
        p["secMin"] = sec_min
        p["year"] = year
        papers.append(p)
    return papers

papers = parse_file("CAT 2020", 2020, 40) + parse_file("CAT 2017", 2017, 60)

# ---- validation report ----
total_q = 0; flags = 0
for p in papers:
    counts = {s["name"]: len(s["qs"]) for s in p["sections"]}
    n = sum(counts.values()); total_q += n
    miss_ans = sum(1 for s in p["sections"] for q in s["qs"] if q.get("ans") in (None, ""))
    miss_sol = sum(1 for s in p["sections"] for q in s["qs"] if not q.get("sol"))
    fl = [q.get("flag") for s in p["sections"] for q in s["qs"] if q.get("flag")]
    flags += len(fl)
    ctxn = sum(1 for s in p["sections"] for q in s["qs"] if q.get("ctx"))
    tita = sum(1 for s in p["sections"] for q in s["qs"] if q["type"]=="tita")
    img = sum(1 for s in p["sections"] for q in s["qs"] if q.get("img"))
    print(f'{p["name"]}: {counts} total={n} tita={tita} withCtx={ctxn} img-lost={img} missingAns={miss_ans} missingSol={miss_sol} flags={len(fl)}')
print(f"TOTAL questions: {total_q}, flagged: {flags}")
json.dump(papers, open("papers.json","w"), ensure_ascii=False)
print("papers.json size:", len(open('papers.json').read()), "bytes")
