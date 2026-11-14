# Content review (November 2026)

How the questions in `tests/` were checked before release.

- **Originality:** every item was written new for this project; none is copied or paraphrased from ETS or any prep source.
- **Blind solve:** a separate solver answered every item without the key. Agreement before fixes: shared easy 30/30, Test 1 82/84, Test 2 83/84, Test 3 83/84. Each disagreement was either a solver error, confirmed by the Quant check or by the clue in the sentence, or the item was rewritten (T2-V2M-02, T2-V2H-03, T3-V2H-04, T3-Q1-05). The 9 Verbal items rewritten later were solved again: 9/9.
- **Quant checks:** `tools/checks/*.py` recomputes every Quant key from the problem's conditions; the build fails on any mismatch (142 checks).
- **Difficulty review:** an advisor model rated a random 60-item sample (3 per section) against ETS items. It found no wrong keys. The 14 items it flagged were fixed or re-rated. It rated the hard Verbal sample below target (mostly 3 of 5); only the flagged items were reworked, so the unsampled hard Verbal items may still be easier than real 165+ items.
- **Style:** US spelling and $ throughout, as on the real test.
