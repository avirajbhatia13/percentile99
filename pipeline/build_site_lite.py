#!/usr/bin/env python3
"""Vercel v1: DATA+BANK inline, MOCKS via fetch('mocks.json') with graceful fallback. Minified."""
import re, json, subprocess

html = open("dashboard.html").read()

m_mocks = re.search(r"const MOCKS = (\[.*?\]);\n", html, re.S)
assert m_mocks
# replace MOCKS embed with async fetch + boot wrapper
html = html.replace("const MOCKS = " + m_mocks.group(1) + ";\n", "let MOCKS = [];\n")

# wrap main code so it runs after mocks fetch attempt
html = html.replace("<script>\n", """<script>
async function __boot(){
  try{const r=await fetch('mocks.json');if(r.ok)MOCKS=await r.json()}catch(e){}
  __main();
}
""", 1)
html = html.replace("const DATA = ", "function __main(){\nconst DATA = ", 1)
html = html.replace("syncProfile();render();\n</script>", "syncProfile();render();\n}\n__boot();\n</script>")

# graceful note when mocks absent
html = html.replace(
  "const mockCard=`<div class=\"pcard\"><h3>🏆 Full-Paper Mocks — actual CAT papers</h3>",
  "const mockCard=MOCKS.length===0?`<div class=\"pcard\"><h3>🏆 Full-Paper Mocks</h3><div class=\"hint\">Real CAT paper mocks (2017 & 2020, 391 questions) are being prepared for the live site — coming in the next update. Topic drills below are fully live.</div></div>`:`<div class=\"pcard\"><h3>🏆 Full-Paper Mocks — actual CAT papers</h3>", 1)

open("site_full.html","w").write(html)

# split for minification
mjs = re.search(r"<script>\n(.*)\n</script>", html, re.S)
mcss = re.search(r"<style>\n(.*)\n</style>", html, re.S)
js, css = mjs.group(1), mcss.group(1)
open("_app.js","w").write(js)

# safe JS shrink: strip leading indentation + blank lines (line breaks preserved)
mini_js = "\n".join(l.strip() for l in js.split("\n") if l.strip())
css_min = re.sub(r"\s+", " ", css)
css_min = re.sub(r"\s*([{}:;,>])\s*", r"\1", css_min)

def wrap_json_line(s, width=1400):
    """insert newlines after commas outside string literals every ~width chars"""
    outp, count, in_str, esc = [], 0, False, False
    for ch in s:
        outp.append(ch); count += 1
        if esc: esc = False
        elif ch == "\\": esc = True
        elif ch == '"': in_str = not in_str
        elif ch == "," and not in_str and count >= width:
            outp.append("\n"); count = 0
    return "".join(outp)

css_min = css_min.replace("}", "}\n")  # safe CSS line breaks
mini_js = "\n".join(wrap_json_line(l) if len(l) > 1800 else l for l in mini_js.split("\n"))

out = html[:mcss.start()] + "<style>\n" + css_min + "</style>" + html[mcss.end():]
mjs2 = re.search(r"<script>\n(.*)\n</script>", out, re.S)
out = out[:mjs2.start()] + "<script>\n" + mini_js + "\n</script>" + out[mjs2.end():]
# collapse html indentation lines
out = "\n".join(l.strip() for l in out.split("\n") if l.strip())
open("site_index.html","w").write(out)
lines = out.split("\n")
print("full:", len(html), "→ minified:", len(out), "bytes |", len(lines), "lines | max line:", max(len(l) for l in lines))
