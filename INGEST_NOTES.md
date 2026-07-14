# Question ingest & topic-tagging convention

Every question in `mocks.json` MUST have a non-empty `sub` (topic) field. The custom-test
pool and topic picker are built from `sub` (see `MPOOL` in index.html). Untagged questions
now fall back to their section name, but always assign a real topic during ingest.

## Topic vocabulary by section

**QA** — use the fine-grained subtopics already in `DATA.subs`, e.g.:
Percentages, Profit & Loss, SI & CI, Averages, Alligation & Mixture, Ratio, Time & Work,
Time Speed Distance, Simple Equations, Quadratic Equations, Inequalities, Logarithms,
Functions, Sequence & Series, Arithmetic Progression, Geometric Progression, Indices & Surds,
Permutations & Combinations, Probability, Triangles, Circles, Quadrilaterals, Mensuration,
Remainders, Factors, HCF & LCM, Numbers Basics, Base Systems.

**DILR** — tag each SET (context) with one bucket, all questions in the set share it:
Tables & Data Sets, Venn Diagrams & Set Theory, Games & Tournaments, Networks & Routes,
Grid & Arrangements, Sequencing & Scheduling, Selection & Distribution, Conditional Logic & Puzzles.

**VARC** — tag by question type:
Reading Comprehension (any question attached to a passage), Para-jumble, Para-summary,
Odd One Out, Para-completion.

## Rule of thumb
- VARC question with a passage context (`c` set) → "Reading Comprehension".
- DILR question → the set's bucket (classify the shared context once).
- QA question → the finest QA subtopic that fits the stem.
