# GRE Practice Centre

Full-length, timed GRE General Test practice in the current shorter format (since 22 September 2023), as a single web page.

**Use it online:** open the GitHub Pages site for this repository (Settings → Pages shows the address), or open `index.html` in any browser.

## What it does

- Test-day procedure: practice agreement, general directions, the Analytical Writing essay first, then two Verbal and two Quantitative sections; no breaks; no returning to finished sections; Help, Mark, Review and a hide-able clock.
- Section-level adaptivity: your first section in each measure routes you to an easier, medium or harder second section.
- ETS-style scoring: every question counts equally; a conversion table per second-section tier gives an estimated 130–170 score with a likely range and ETS percentile.
- On-screen calculator following ETS's rules (order of operations, 8-digit display, memory, Transfer Display).
- Report or cancel scores at the end, score report with explanations, score history, and an untimed practice mode for tests you have finished.

Score history on the GitHub Pages site is saved in your browser only.

## Important

- All questions are **original practice material** written to ETS's published specifications. They are not ETS questions.
- Scores are **estimates**. ETS does not publish its conversion tables for this format, and these questions have not been calibrated on real test takers. Treat estimates above about 160 as optimistic. ETS's free POWERPREP tests are the official benchmark.
- Percentiles and measurement error come from the ETS *GRE Guide to the Use of Scores 2026–27* (test takers 1 July 2022 – 30 June 2025).

## Project layout

| Path | What it is |
|---|---|
| `tests/test-NN.json` | One file per practice test: sections V1, V2E/V2M/V2H, Q1, Q2E/Q2M/Q2H, the essay prompt, passages, tables and charts |
| `src/app.html` | The app (engine and design) |
| `src/build.py` | Validates every test, shuffles verbal answer options with a fixed seed, adds the scoring tables, and writes the pages |
| `index.html` | Built page served by GitHub Pages |
| `GRE-Practice-Centre.html` | Same page, for offline use |
| `archive/v1` | The first single-test version |

## Rebuild after editing a test

```bash
python -I src/build.py
```

Add `--table` to print the score conversion table. The build stops with a list of problems if a test file breaks a rule (wrong question counts, missing difficulty ratings, explanations that mention option letters, and so on).
