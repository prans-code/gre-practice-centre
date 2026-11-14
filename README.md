# GRE Practice Centre

Full-length, timed GRE General Test practice in the current shorter format (since 22 September 2023), as a single web page.

**Use it online:** open the GitHub Pages site for this repository (Settings → Pages shows the address), or open `index.html` in any browser.

## What it does

- Test-day procedure: practice agreement, general directions, the Analytical Writing essay first, then two Verbal and two Quantitative sections; no breaks; no returning to finished sections; Help, Mark, Review and a hide-able clock.
- Section-level adaptivity: your first section in each measure routes you to an easier, medium or harder second section.
- ETS-style scoring: every question counts equally; a conversion table per second-section tier gives an estimated 130–170 score with a likely range and ETS percentile.
- On-screen calculator following ETS's rules (order of operations, 8-digit display, memory, Transfer Display).
- Three full-length practice tests with no shared questions, written at 160+ difficulty, plus a **randomized test** that draws a fresh mix from all of them (passage and data sets stay together).
- One shared easier second section per measure, used only when the first section goes badly.
- Report or cancel scores at the end, score report with explanations, score history, and an untimed practice mode for tests you have finished.

## Accounts

Sign up with an email and password to keep your score history across devices; each account sees only its own results. You can also continue as a guest, which keeps history in this browser only, and import that history into an account later. If the account server can't be reached, results are saved in the browser and uploaded the next time you open the site.

Accounts use [Supabase](https://supabase.com) (free tier). Setup steps for a new project are in [docs/supabase-setup.md](docs/supabase-setup.md), and the table and access rules are in [supabase/schema.sql](supabase/schema.sql). The page holds only the publishable key; row-level security keeps each user to their own rows.

## Important

- All questions are **original practice material** written to ETS's published specifications. They are not ETS questions and are not copied or paraphrased from any prep book or course.
- Every question was answered by an independent solver without the key; disagreements were rewritten or dropped. Every Quant answer is also recomputed by a script at build time (`tools/checks/`).
- Scores are **estimates**. ETS does not publish its conversion tables for this format, and these questions have not been calibrated on real test takers. Treat estimates above about 160 as optimistic. ETS's free POWERPREP tests are the official benchmark.
- Percentiles and measurement error come from the ETS *GRE Guide to the Use of Scores 2026–27* (test takers 1 July 2022 – 30 June 2025).

## Project layout

| Path | What it is |
|---|---|
| `tests/test-NN.json` | One file per practice test: sections V1, V2M/V2H, Q1, Q2M/Q2H, the essay prompt, passages, tables and charts |
| `tests/shared-easy.json` | The easier second sections (V2E, Q2E) shared by all tests |
| `src/random.js` | Builds the randomized test from the fixed tests |
| `tools/verify_quant.py`, `tools/checks/` | Independent answer checks for every Quant question, run by the build |
| `tools/check_draft.py` | Checks a draft set of new questions before it is merged into a test |
| `supabase/` | Database table and access rules for accounts |
| `src/app.html` | The app (engine and design) |
| `src/build.py` | Validates every test, shuffles verbal answer options with a fixed seed, adds the scoring tables, and writes the pages |
| `index.html` | Built page served by GitHub Pages |
| `GRE-Practice-Centre.html` | Same page, for offline use |
| `archive/v1` | The first single-test version |

## Rebuild after editing a test

```bash
python -I src/build.py
```

Add `--table` to print the score conversion table. The build stops with a list of problems if a test file breaks a rule (wrong section layout or difficulty mix, a question id or passage reused across tests, a Quant key its check disagrees with, explanations that mention option letters, and so on).

Self-tests:

```bash
python -I tools/test_build.py
node tools/test_random.js
```

To add a test, write a new `tests/test-NN.json` plus a `tools/checks/tNN_quant.py` with one check per Quant question, then rebuild.
