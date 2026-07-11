#!/usr/bin/env python3
"""CAT 2026 planner: parse Rodha playlist data, build syllabus map + day-by-day schedule."""
import json, datetime

# ---------------- QUANT (384 videos, seconds from YouTube API) ----------------
# (main_topic, sub_topic, [(short_name, secs), ...]) in exact playlist order
Q = []
def t(main, sub, names_secs): Q.append((main, sub, names_secs))

t("Number System","Course Intro",[("Course Intro – Full Course Overview",676)])
t("Number System","Numbers Basics",[("Numbers 1",1690),("Numbers 2",1382),("Numbers 3",1566)])
t("Number System","Factorials",[("Factorials 1",2059),("Factorials 2",2093),("Factorials 3",2141),("Factorials 4",1408),("Factorials 5",1128),("Factorials 6",1711)])
t("Number System","Last 2 Digits",[("Last 2 Digits – Odd Numbers",1374),("Last 2 Digits – Even Numbers",1436)])
t("Number System","Divisibility Rules",[("Divisibility Rules 1",1808),("Divisibility Rules 2",1536),("Divisibility Rules 3",1229),("Divisibility Rules 4",1512)])
t("Number System","Remainders",[("Remainders 1",1803),("Remainders 2",1441),("Remainders 3",2069),("Remainders 4 Part 1",1110),("Remainders 4 Part 2",1657),("Remainders 5",1460),("Remainders 6",1460),("Remainders 7",1667),("Remainders 8",1766)])
t("Number System","Difference of Perfect Squares",[("Diff of Perfect Square 1",1276),("Diff of Perfect Square 2",1133),("Diff of Perfect Square 3",919)])
t("Number System","Factors",[("Factors 1",1695),("Factors 2",1648),("Factors 3",1498),("Factors 4",2205),("Factors 5",1527),("Factors 6",2153),("Factors 7",1926),("Factors 8",1626),("Factors 9",1394),("Factors 10",1487),("Factors 11",1315),("Factors 12",1664)])
t("Number System","HCF & LCM",[("HCF LCM 1",1543),("HCF LCM 2",1181),("HCF LCM 3",1320),("HCF LCM 4",1534),("HCF LCM 5",1512)])
t("Geometry","Triangles",[("Triangles 1",1973),("Triangles 2",1423),("Triangles 3",1364),("Triangles 4",1697),("Triangles 5",1218),("Triangles 6",2301),("Triangles 7",1321),("Triangles 8",1656),("Triangles 9",1671),("Triangles 10",1329),("Triangles 11",1630),("Triangles 12",1460),("Triangles 13",1449)])
t("Geometry","Quadrilaterals",[("Quadrilaterals 1",2314),("Quadrilaterals 2",1329),("Quadrilaterals 3",797)])
t("Geometry","Circles",[("Circles 1",1548),("Circles 2",1197),("Circles 3",1466)])
t("Geometry","Mensuration",[("Mensuration 1",1487),("Mensuration 2",1742),("Mensuration 3",1294),("Mensuration 4",1432),("Mensuration 5",1375)])
t("Arithmetic","Speed Maths",[("Speed Maths 1",1882),("Speed Maths 2",1201),("Speed Maths 3",1339),("Speed Maths 4",1232),("Speed Maths 5",1659),("Speed Maths 6",1242)])
t("Arithmetic","Percentages",[("Percentages 1",1579),("Percentages 2",1366),("Percentages 3",1216)])
t("Arithmetic","Profit & Loss",[("Profit and Loss 1",1565),("Profit and Loss 2",1464),("Profit and Loss 3",2312),("Profit and Loss 4",1621),("Profit and Loss 5",1466),("Profit and Loss 6",1299)])
t("Arithmetic","Averages",[("Averages 1",1390),("Averages 2",1837),("Averages 3",1919),("Averages 4",1605)])
t("Arithmetic","Alligation & Mixture",[("Alligation & Mixture 1",1907),("Alligation & Mixture 2",1040),("Alligation & Mixture 3",1415),("Alligation & Mixture 4",1588),("Alligation & Mixture 5",1604),("Alligation & Mixture 6",1288)])
t("Arithmetic","Ratio",[("Ratio 1",1438),("Ratio 2",1126),("Ratio 3",2315),("Ratio 4",1438),("Ratio 5",1914),("Ratio 6",997)])
t("Arithmetic","Proportion & Variation",[("Proportion Variation 1",1555),("Proportion Variation 2",1675)])
t("Arithmetic","SI & CI",[("SI & CI 1",1297),("SI & CI 2",1574),("SI & CI 3",1425),("SI & CI 4",1122),("SI & CI 5",991),("SI & CI 6",1421)])
t("Arithmetic","Time & Work",[("Time and Work 1",1318),("Time and Work 2",1465),("Time and Work 3",1565)])
t("Arithmetic","Time Speed Distance",[("TSD 1",1337),("TSD 2",1418),("TSD 3",1609),("TSD 4",1917),("TSD 5",1516),("TSD 6",1681),("TSD 7 (Escalators)",1587),("TSD 8 (Escalators contd)",1453)])
t("Arithmetic","TSD – Boats & Streams",[("Boat Streams 1",1787),("Boat Streams 2",1356)])
t("Arithmetic","TSD – Relative Speed",[("Relative Speed 1",1632),("Relative Speed 2",1331),("Relative Speed 3",1641),("Relative Speed 4",1302)])
t("Arithmetic","TSD – Linear Tracks",[("Linear Tracks 1",1660),("Linear Tracks 2",1748),("Linear Tracks 3",1474)])
t("Arithmetic","TSD – Linear Races",[("Linear Races 1",1344),("Linear Races 2",1593)])
t("Arithmetic","Clocks",[("Time & Distance Clocks 1",1339)])
t("Arithmetic","Circular Tracks",[("Circular Tracks 1",1339),("Circular Tracks 2",1412),("Circular Tracks 3",1141)])
t("Algebra","Advance Algebra",[("Advance Algebra 1",2081),("Advance Algebra 2",1688),("Advance Algebra 3",1149),("Advance Algebra 4",1199),("Advance Algebra 5",855),("Advance Algebra 6",664)])
t("Algebra","Sequence & Series",[("Sequence Series 1",1509)])
t("Algebra","Arithmetic Progression",[("Arithmetic Progression 1",1345),("Arithmetic Progression 2",1399)])
t("Algebra","Geometric Progression",[("Geometric Progression 1",1298),("Geometric Progression 2",975),("Geometric Progression 3",790)])
t("Algebra","Simple Equations",[("Simple Equations 1",1569),("Simple Equations 2",1712),("Simple Equations 3",1298),("Simple Equations 4",1368),("Simple Equations 5",1558),("Simple Equations 6",1339)])
t("Algebra","Cubic Equations",[("Cubic Equation 1",1137),("Cubic Equation 2",1422)])
t("Algebra","Quadratic Equations",[("Quadratic Equation 1",1707),("Quadratic Equation 2",1253),("Quadratic Equation 3",1219),("Quadratic Equation 4",1544)])
t("Algebra","Inequalities",[("Inequalities 1",1132),("Inequalities 2",1788),("Inequalities 3",1134),("Inequalities 4",1202),("Inequalities 5",1358),("Inequalities 6",1697),("Inequalities 7",702),("Inequalities 8",444),("Inequalities 9",912)])
t("Algebra","Graphs",[("Graphs 1",826),("Graphs 2",1230),("Graphs 3",1208),("Graphs 4",1655)])
t("Algebra","Indices & Surds",[("Indices Surds 1",1203),("Indices Surds 2",1490),("Indices Surds 3",1298),("Indices Surds 4",1219),("Indices Surds 5",719)])
t("Algebra","Logarithms",[("Logarithms 1",1843),("Logarithms 2",1446)])
t("Algebra","Statistics",[("Statistics 1",989),("Statistics 2",1025),("Statistics 3",897)])
t("Algebra","Functions",[("Functions 1",1276),("Functions 2",1152),("Functions 3",1167),("Functions 4",994),("Functions 5",987),("Functions 6",818),("Functions 7",1045),("Functions 8",939),("Functions 9",590),("Functions 10",783)])
t("Modern Math","Permutations & Combinations",[("P&C 1",1615),("P&C 2",2189),("P&C 3",2087),("P&C 4",1722),("P&C 5",1496),("P&C 6",1510),("P&C 7",1516),("P&C 8",1021),("P&C 9",1666),("P&C 10",1511),("P&C 11",1274),("P&C 12",1937),("P&C 13",1194),("P&C 14",1036),("P&C 15",1619),("P&C 16",1544),("P&C 17",953),("P&C 18",1263),("P&C 19",1485),("P&C 20",1622),("P&C 21",1039)])
t("Modern Math","Probability",[("Probability 1",1291),("Probability 2",1269)])
t("Number System","Base Systems",[("Base Systems 1",2342),("Base Systems 2",1395),("Base Systems 3",1286),("Base Systems 4",1175),("Base Systems 5",908)])
t("Number System","Recurring Decimals & Cyclicity",[("Recurring Decimal Cyclicity (marathon)",3467)])
t("Practice & Revision","Numbers – Advanced Practice",[(f"Practice Numbers {i+1}",s) for i,s in enumerate([779,746,1261,702,960,712,926,700,629,879,880,702,977,920,1293,798])])
t("Practice & Revision","Geometry – Advanced Practice",[("Practice Geometry 1",1242),("Practice Geometry 2",1070),("Practice Geometry 3",907),("10 Must-Know Geometry Concepts",1099)])
t("Practice & Revision","Arithmetic – Advanced Questions",[(f"Arithmetic Advance Q{i+1}",s) for i,s in enumerate([596,232,746,427,617,305,286,480,445,525,404,708,370,214,551,689,357,647,622,290,315,325,771,444,459,465,621,526,444,456,489,647,541,677,400,917,960,370,661,522,466,1082,707,875,512,692,604,710,469,414,1291,741,611,761,743,1079,601,662,756])] + [("Arithmetic Top Questions Marathon",10937)])
t("Practice & Revision","Algebra – Practice Sessions",[(f"Algebra Practice {i+1}",s) for i,s in enumerate([667,428,311,401,469,565,744,563,486,463,441,688,433,596,448,540,227,294])])
t("Practice & Revision","Mixed Quant – Advanced Level",[(f"Quant Advance {n}",s) for n,s in [(1,533),(2,363),(3,332),(4,287),(5,449),(6,287),(7,361),(8,364),(9,488),(10,384),(11,510),(12,745),(13,516),(14,357),(15,747),(16,360),(17,507),(18,436),(19,550),(20,678),(21,511),(22,427),(23,523),(24,315),(25,591),(26,417),(27,734),(28,507),(29,596),(30,378),(31,634),(32,472),(33,442),(35,522),(37,960),(38,522),(39,688),(40,192),(41,574),(42,406),(43,512),(44,349)]] + [("Revision Best Concepts 44",416),("Revision Best Concepts 45",347)])
t("Practice & Revision","Algebra – Advanced Topic Questions",[("Adv NS Practice",700),("Adv Algebra: Quadratic Eqn",447),("Adv Algebra: Maxima Minima",484),("Adv Algebra: Advance Quadratic",398),("Adv Algebra: Inequality",475),("Adv Algebra: Symmetry",558),("Adv Algebra: Trigo Max Min",528),("Adv Algebra: Series Logarithm",718),("Adv Algebra: Cubic Equation",506),("Adv Algebra: Logarithms Tough I",762),("Adv Algebra: Logarithms Tough II",474),("Adv Algebra: Indices Surds",647),("Adv Algebra: Inequalities",573),("Adv Algebra: Mixed",597),("Adv Algebra: Functions Tough",294),("Adv Algebra: Functions–Inequalities",573),("Adv Algebra: Algebra + Trigo",318),("Adv Algebra: Cubic Tough Max Min",1364),("Adv Algebra: Equations Difficult",1038),("Adv Algebra: Series Tough",269),("Adv Algebra: Difficult GP",346),("Adv Algebra: Logarithms Tough III",718)])

# ---------------- DILR (85 videos, mm:ss) ----------------
def ms(s):
    m, sec = s.split(":"); return int(m)*60+int(sec)
D = []
def d(main, sub, names_secs): D.append((main, sub, [(n, ms(x)) for n,x in names_secs]))

d("LR Foundations","Introduction",[("LRDI Introduction","8:08")])
d("LR Foundations","Arrangements (Linear & Circular)",[("Linear & Circular Arrangement I","20:11"),("Linear & Circular Arrangement II","9:15"),("Linear Arrangement Set 1","10:57"),("Linear Arrangement Set 2","17:46"),("Linear Arrangement Set 3","14:40")])
d("LR Foundations","Cubes",[("Cubes 1","25:06"),("Cubes 2","27:08"),("Cubes 3","18:37"),("Cubes 4","31:27")])
d("LR Foundations","Number Series",[("Number Series 1","24:13"),("Number Series 2","17:27"),("Number Series 3","26:15"),("Number Series 4","20:39"),("Number Series 5","14:56"),("Number Series 6","20:14")])
d("Puzzles","Quant-Based Puzzles (Sets 1–19)",[("QB Puzzles Set 1","13:08"),("QB Puzzles Set 2","29:38"),("QB Puzzles Set 3","36:53"),("QB Puzzles Set 4","27:18"),("QB Puzzles Set 5 (Magic Box 3x3)","15:49"),("QB Puzzles Set 6 Pt1 (Ring Cutting)","18:11"),("QB Puzzles Set 6 Pt2 (Ring Cutting)","12:31"),("QB Puzzles Set 7 Pt1 (Weighing Balls)","8:15"),("QB Puzzles Set 7 Pt2 (Weighing Balls)","15:02"),("QB Puzzles Set 7 Pt3","6:27"),("QB Puzzles Set 8","20:36"),("QB Puzzles Set 9 (Tough)","26:40"),("QB Puzzles Set 10","10:41"),("QB Puzzles Set 11 (Magic Box 4x4)","10:30"),("QB Puzzles Set 12","15:28"),("QB Puzzles Set 13","17:39"),("QB Puzzles Set 14 (CryptArithmetic)","20:39"),("QB Puzzles Set 15","14:01"),("QB Puzzles Set 16","19:26"),("QB Puzzles Set 17","14:01"),("QB Puzzles Set 18","21:35"),("QB Puzzles Set 19","27:14")])
d("Logic Sets","Venn Diagrams",[("Venn Diagrams 1 (Intro)","9:39"),("Venn Diagrams 2 (4-param)","29:42"),("Venn Diagrams 3","30:49"),("Venn Diagrams 4","23:01"),("Venn Diagrams 5","23:31"),("Venn Diagrams 6","20:44"),("Venn Diagrams 7","23:19"),("Venn Diagrams 8 (Unconventional)","22:25"),("Venn Diagrams 9 (Maxima-Minima)","32:47")])
d("Logic Sets","Maxima-Minima & Chocolate Distribution",[("Max-Min 1 (Chocolate Dist)","20:07"),("Max-Min 2 (Chocolate Dist)","21:16"),("Chocolate Distribution 1","19:21"),("Chocolate Distribution 2","21:00")])
d("Logic Sets","Games & Tournaments",[("Games & Tournaments 1","26:14"),("Games & Tournaments 2","21:07"),("Games & Tournaments 3","20:44"),("Games & Tournaments 4","23:04"),("Games & Tournaments 5","27:18"),("Games & Tournaments 6","20:47"),("Games & Tournaments 8 (Knockout Adv)","23:33")])
d("Data Interpretation","Pie Charts",[("Pie Chart 1","30:10"),("Pie Chart 2","17:17"),("Pie Chart 3","18:12"),("Pie Chart 4","25:28"),("Pie Chart 5","28:58")])
d("Data Interpretation","Tables",[("Tabular Set","21:38")])
d("Data Interpretation","Routes & Networks",[("Routes & Networks 1","24:27"),("Routes & Networks 2","19:18"),("Routes & Networks 3","23:37")])
d("Logic Sets","Maxima-Minima (Advanced)",[("Max-Min 5 (Thinking Cap)","17:31"),("Max-Min 6 (Logical)","19:40")])
d("LR Foundations","Calendars",[("Calendars 1","31:08"),("Calendars 2","11:35"),("Calendars 3","25:17")])
d("Advanced Practice","High-Level Mixed Sets",[("LRDI Practice Set 3","12:32"),("G&T Difficult Set","37:20"),("Advance Level Sets Intro","3:21"),("Ranking Puzzle","22:52"),("Alligation & Averages Set","39:15"),("Difficult Puzzles Set","24:52"),("QB Puzzle Set 20 Pt1","22:40"),("QB Puzzle Set 20 Pt2","30:38"),("QB Puzzle Set 21","25:15"),("QB Puzzle Set 22 Pt1","19:51"),("QB Puzzle Set 22 Pt2","26:33"),("QB Puzzle Set 23","28:12"),("Maxima-Minima & Distribution (99+ile)","42:42")])

# ---------------- Verify ----------------
qn = sum(len(v) for _,_,v in Q); dn = sum(len(v) for _,_,v in D)
qs = sum(s for _,_,v in Q for _,s in v); ds = sum(s for _,_,v in D for _,s in v)
print(f"QUANT videos={qn} (expect 384)  total={qs}s = {qs/3600:.1f}h")
print(f"DILR  videos={dn} (expect 85)   total={ds}s = {ds/3600:.1f}h")
assert qn == 384, f"quant count mismatch: {qn}"
assert dn == 85, f"dilr count mismatch: {dn}"

# ---------------- Schedule (greedy, keep playlist order, 60-75 min/day) ----------------
CAP = 75*60
def schedule(topics):
    days = []; cur = []; cur_s = 0
    for main, sub, vids in topics:
        for name, secs in vids:
            if cur and cur_s + secs > CAP:
                days.append((cur, cur_s)); cur = []; cur_s = 0
            cur.append({"main": main, "sub": sub, "name": name, "secs": secs})
            cur_s += secs
    if cur: days.append((cur, cur_s))
    return days

qdays = schedule(Q); ddays = schedule(D)
print(f"Quant days: {len(qdays)}  |  DILR days: {len(ddays)}")

# ---------------- Merge into calendar: morning=Quant, evening=DILR then Quant ----------------
start = datetime.date(2026, 7, 13)  # Monday
calendar = []
qi = 0; di = 0; day = 0
while qi < len(qdays) or di < len(ddays):
    entry = {"day": day+1, "date": str(start + datetime.timedelta(days=day))}
    if qi < len(qdays):
        entry["morning"] = {"track":"QA","videos":qdays[qi][0],"secs":qdays[qi][1]}; qi += 1
    if di < len(ddays):
        entry["evening"] = {"track":"LRDI","videos":ddays[di][0],"secs":ddays[di][1]}; di += 1
    elif qi < len(qdays):
        entry["evening"] = {"track":"QA","videos":qdays[qi][0],"secs":qdays[qi][1]}; qi += 1
    calendar.append(entry); day += 1

print(f"Total calendar days: {len(calendar)}  finish: {calendar[-1]['date']}")
tot = qs + ds
print(f"Grand total video time: {tot/3600:.1f}h")

# syllabus map summary
def sylmap(topics):
    from collections import OrderedDict
    m = OrderedDict()
    for main, sub, vids in topics:
        m.setdefault(main, []).append({"sub": sub, "count": len(vids), "secs": sum(s for _,s in vids), "videos":[{"name":n,"secs":s} for n,s in vids]})
    return m

out = {"generated": str(datetime.date.today()), "start_date": str(start),
       "quant": {"count": qn, "secs": qs, "days": len(qdays), "map": sylmap(Q)},
       "dilr": {"count": dn, "secs": ds, "days": len(ddays), "map": sylmap(D)},
       "calendar": calendar}
with open("plan_data.json","w") as f: json.dump(out, f, indent=1)
print("wrote plan_data.json")

# per-main-topic stats
for label, topics in (("QA", Q), ("LRDI", D)):
    from collections import OrderedDict
    agg = OrderedDict()
    for main, sub, vids in topics:
        c, s = agg.get(main, (0,0)); agg[main] = (c+len(vids), s+sum(x for _,x in vids))
    for k,(c,s) in agg.items(): print(f"{label} | {k}: {c} videos, {s/3600:.1f}h")
