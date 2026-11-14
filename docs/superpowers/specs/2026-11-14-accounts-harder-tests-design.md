# Accounts, harder tests, randomized mode: design

Date: 2026-11-14 · Branch: `feature/accounts-and-harder-tests`

## Intent

A free GRE General Test mock platform for a small group of friends, because paid platforms cost too much. It must feel as close to the real test as possible. The engine exists (`src/app.html`, `src/build.py`); what is missing is separate accounts, real GRE-level difficulty, more than one test, and a randomized test.

## Goals

1. **Accounts.** Each person logs in and sees only their own history, on any device. Free.
2. **Harder content.** Quant and Verbal at real GRE difficulty for people aiming at 160+.
3. **Three fixed tests** (Test 1 rewritten, Tests 2 and 3 new) that share no questions, except one shared easy second section per measure.
4. **Randomized test.** Builds a new full-length test from all fixed tests' questions.
5. Keep everything the engine already does: test-day procedure, section-level adaptivity, calculator, review, scoring estimates, practice mode.

## Non-goals (this release)

- Tests 4 and 5 (later, same format).
- A separate question pool just for randomized mode.
- Essay auto-marking. Analytical Writing (AW) scores stay "pending" as today.
- Steering randomized mode toward unseen questions; plain random is enough at this size.
- Syncing an unfinished attempt across devices. Only finished attempts sync.

## Anti-goals

- Any question copied or closely paraphrased from Kaplan, Magoosh, ETS books or other commercial material. The repo and site are public.
- Answer keys that are wrong or ambiguous. One bad key undermines trust in the scores.
- A login that blocks practice when Supabase is down or paused.

## Constraints

- Hosting stays GitHub Pages: a static page, no server of our own.
- Free tier only (Supabase free plan: a project pauses after about 7 days without use and needs one click in the dashboard to resume; the built-in email sender is heavily rate-limited).
- Content sources for calibration: ETS Math Review PDF, ETS free POWERPREP and published sample questions, Khan Academy. The GregMat and Vocab Mountain lists may guide word choice. The pirated books in the shared Drive are not used.
- Changes go to a branch and a pull request, so the repo owner reviews before anything goes live.

## Approaches considered

**Accounts**
- *Supabase (chosen).* Real email+password login, one table with row-level security, free, works from a static page via its JS client. Cost: an outside service someone must set up; free projects pause when idle.
- *Profile-name picker in localStorage.* About 30 lines, no service, but history stays on one device. Rejected: the user wants real accounts.
- *Firebase.* Equivalent, no advantage here.

**Content structure**
- *Keep one file per test; randomized mode samples slot by slot across tests (chosen).* Fits the existing engine and validator; the type and difficulty mix of each slot is kept for free.
- *Restructure into a question bank with blueprints.* More flexible, but rewrites the engine and validator for no gain at three tests.

**Easy tier** (users target 160+): one shared easy second section per measure used by all tests (chosen), instead of a separate one per test. Saves about 60 questions in a tier these users rarely reach.

## Design

### 1. Accounts (Supabase)

- Supabase JS client v2 loaded from jsDelivr with a pinned exact version.
- Project URL and anon key live in `src/config.js`-style constants inside `app.html`. They are safe to publish: row-level security protects the data.
- Table `attempts`: `id text primary key`, `user_id uuid not null default auth.uid()`, `data jsonb not null`, `updated_at timestamptz default now()`. Row-level security: a user can select, insert and update only rows where `user_id = auth.uid()`.
- Sign-up is open to anyone with the link. Email+password, email confirmation turned off, so the rate-limited email sender is needed only for password reset.
- The home screen shows "Log in / Sign up" or "Signed in as … · Log out". "Continue as guest" keeps today's browser-only behaviour.
- History is stored per user in the browser (key includes the user id, or `guest`), so two people on one laptop don't see each other's history.
- On first login on a device, guest attempts on that device are offered for copying into the account.
- If Supabase can't be reached, or the URL/key constants are empty, the app works as guest and says so in one line. *(Builder's call: login can be coded against empty placeholders and switched on by filling them in.)*
- After guest attempts are copied into an account, they are removed from the guest list so they don't show twice. Logging out clears that user's cached history from the browser (shared laptops). *(Builder's call.)*
- The existing Claude-artifact store (`window.claude.use("db")`) stays as is for `src/artifact.html`; Supabase is used only when that store isn't present.
- A short `docs/supabase-setup.md` gives click-by-click setup (create project, run one SQL snippet, turn off email confirmation, paste URL and key).

### 2. Content format and the build

- Tests stay in `tests/test-NN.json` with today's sections and question types.
- New `tests/shared-easy.json` holds `V2E` and `Q2E` plus their passages, tables and charts. The build copies these into every test; test files no longer contain `V2E`/`Q2E`.
- Question ids, and passage, table and chart keys, must be unique across all tests. The build checks this, which makes the fixed tests disjoint.
- The shared easy sections are the same questions in every test and in randomized mode. Someone routed to the easy tier on two tests sees them twice; that is accepted.
- **Same layout in every test.** For each section key, every test has the same sequence of slots: the same question type in each position and the same passage-set sizes. The build checks this. Real GRE sections also follow a fixed layout, and it makes randomized sampling trivial. *(Builder's call.)*
- New build checks: the difficulty mix per section (below); every quant question has a check in `tools/verify_quant.py` (section 4). The build imports that file and fails on a missing check or a mismatch.
- The build still writes `src/artifact.html`, `GRE-Practice-Centre.html` and `index.html`. The shared-easy merge and randomized mode work in all three.

### 3. Randomized mode

- A "Randomized test" card on the home screen. Starting it builds a test object with id `random-<timestamp>`.
- For each section key (V1, V2M, V2H, Q1, Q2M, Q2H), each slot is filled from the same slot in a randomly chosen fixed test. A passage set counts as one slot: all its questions come from the same test and stay together. Because every test uses the same layout (section 2), counts and types always match. V2E and Q2E are the shared sections.
- The essay prompt is drawn from one of the tests at random.
- The attempt (in progress and in history) stores the list of question ids per section. The app rebuilds the test from those ids using a global id index, so reports and practice mode work after a rebuild.
- If a stored id no longer exists after a content change, the report shows that question as "removed" instead of crashing.

### 4. Content: difficulty targets and quality

Difficulty on the 1–5 scale already in the data:

| Section | Mix |
|---|---|
| V1, Q1 (first sections) | mostly 3–4, with one 2 and one 5 |
| V2H, Q2H (hard) | mostly 4–5 |
| V2M, Q2M (medium) | 3–4 |
| V2E, Q2E (shared easy) | 2–3 |

- Quant topics and type mix follow the ETS Math Review and the real test: Quantitative Comparison, multiple choice, select-all, numeric entry, data interpretation sets. Hard items lean on multi-step reasoning, traps and less familiar framings, not big arithmetic.
- Verbal: denser Text Completion vocabulary, two- and three-blank items with logical reversals, Sentence Equivalence with tempting near-synonym pairs, and reading passages with academic argument structure.
- Test 1: keep its strong difficulty 4–5 items and rewrite the rest. Test 1's current easy sections become the base of `shared-easy.json`, raised to difficulty 2–3.
- **Quant check:** `tools/verify_quant.py` holds one function per quant question id, returning the key in the same form the test file stores it. It works by direct calculation, brute force, or, for Quantitative Comparison, an exhaustive search over the allowed values that confirms the relationship ("cannot be determined" needs two cases that disagree). A mismatch fails the build.
- **Blind solve:** every item is solved by a separate model pass that doesn't see the key. Items where it disagrees are fixed or dropped.
- **Difficulty review:** Fable (the advisor model) rates a sample of each section's items against ETS's published difficulty (POWERPREP and the ETS sample questions), and items rated too easy for their slot are rewritten. The user spot-checks a sample of Verbal. No authority can certify "real GRE difficulty" for unofficial items, so this review plus user feedback is the standard.
- Scores stay labelled as estimates; the conversion table is unchanged.

## What's left to the builder

- Exact UI copy and layout of the login and randomized cards, in the app's existing style.
- How the per-user browser key and guest import are coded.
- The per-slot sampling details within the rules above.
- Which Test 1 items are good enough to keep.
- Which subagents and models draft and blind-solve items.
