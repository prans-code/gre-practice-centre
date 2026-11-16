# Accounts, Harder Tests and Randomized Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Supabase accounts, a shared easy tier, three disjoint fixed tests at 160+ difficulty, and a randomized test to the existing GRE Practice Centre.

**Architecture:**
- The static single page stays: `src/build.py` validates `tests/*.json` and inlines them into `src/app.html`.
- The build gains cross-test checks and a quant answer verifier (`tools/verify_quant.py`).
- Randomized composition is a small pure module (`src/random.js`) that the build inlines and node can test.
- Accounts use supabase-js from jsDelivr; guest mode stays the default.

**Tech Stack:** Python 3.14 (stdlib only), vanilla JS (ES5 style, like `app.html`), Node 24 for JS self-checks, Supabase (Auth + Postgres with row-level security, free plan), GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-11-14-accounts-harder-tests-design.md`

## Global Constraints

**Content and repo**
- No question copied or closely paraphrased from commercial or ETS material. Every item is original.
- Python is stdlib only: no sympy and no pytest. Self-checks are plain `assert` scripts run as `python -I tools/<file>.py`.
- Section sizes are unchanged: V1 and Q1 have 12 questions; V2E/V2M/V2H and Q2E/Q2M/Q2H have 15.
- Question ids, and passage, table and chart keys, are unique across `tests/*.json` and `tests/shared-easy.json`. New ids use the form `T<n>-<section>-<NN>` (e.g. `T2-Q2H-07`); passage, table and chart keys are prefixed `t<n>-`; shared-easy ids use `E-V-NN` / `E-Q-NN` and keys `e-`.
- Quantitative Comparison answer encoding (already used): 0 = A greater, 1 = B greater, 2 = equal, 3 = cannot be determined.

**Difficulty mix per section (1–5)**

| Sections | Mix |
|---|---|
| V1, Q1 | ≥8 of 12 at 3–4, at least one 5, at most two ≤2 |
| V2H, Q2H | ≥10 of 15 at 4–5, none ≤2 |
| V2M, Q2M | ≥11 of 15 at 3–4, none 1 |
| V2E, Q2E | all at 2–3 |

**Accounts**
- Supabase browser key: the **publishable key** (`sb_publishable_…`). Legacy anon keys are being retired in late 2026.
- supabase-js: pin an exact 2.x version that is at least two weeks old, UMD build from `cdn.jsdelivr.net/npm/@supabase/supabase-js@<exact>/dist/umd/supabase.js`. Confirm at build time that this version accepts publishable keys.
- With an empty URL or key, or Supabase unreachable, the app runs as guest and shows one line saying so. Practice is never blocked.
- The build still writes `src/artifact.html`, `GRE-Practice-Centre.html` and `index.html`. In the artifact page, `window.claude.use("db")` stays the store, and Supabase is skipped when `window.claude` exists.

**Delivery**
- Commit on `feature/accounts-and-harder-tests`. Push only when the user OKs it, then open a PR. Never push to `main`.

## Review Focus

1. **Old history after Test 1 is rewritten:** existing attempts must still list with their scores. Their report uses the existing `stale` path (`app.html:777`) and must not crash on missing question ids. Test: Task 3, step 6.
2. **Randomized attempt reopened after a content change** (a stored id is gone): the report shows "question removed" for that slot instead of throwing. Test: Task 3, `test_materialize_missing_id`.
3. **Two people on one laptop:** after A logs out and B logs in, B sees none of A's history or unfinished attempt. Test: Task 4, step 7.
4. **Supabase paused or offline mid-test:** finishing the test saves locally and shows the existing "Saved in this browser only" toast. The answers are never lost. Test: Task 4, step 8.
5. **Answer with alternative forms:** a numeric key like `0.5` versus a fraction key `[1,2]`. `verify_quant` must compare fractions by cross-multiplication and numerics within 1e-9. Test: Task 2, `test_fraction_equivalence`.

---

### Task 1: Build: shared easy tier and cross-test checks

**Files:**
- Modify: `src/build.py` (restructure into functions with an `if __name__ == "__main__":` guard; keep all existing checks)
- Create: `tests/shared-easy.json` (move `V2E`, `Q2E` and the passages/tables/charts they use out of `tests/test-01.json`; rename keys and ids to the `e-` / `E-` forms)
- Modify: `tests/test-01.json` (remove `V2E` and `Q2E`)
- Create: `tools/test_build.py`

**Interfaces:**
- Produces in `build.py`:
  - `load_tests(root: Path) -> list[dict]`: merges `shared-easy.json` into every test.
  - `check_all(tests: list[dict]) -> list[str]`: returns the problem list.
  - `slot_layout(section: dict) -> list[tuple]`: one tuple per slot. A slot is a run of consecutive questions sharing the same `passage`, `table` or `chart` key, or a single question otherwise. Each tuple holds the question types in order.
  - `main()`.
- The data payload gains `"shared": ["V2E", "Q2E"]`. `test.sections` still contains all 8 keys after the merge, so the app is unchanged here.

- [ ] **Step 1: Write failing checks in `tools/test_build.py`**, built on small in-memory fixtures:
  - `test_duplicate_id_across_tests`: two tests sharing `T1-V1-01` yields a problem containing `"duplicate id T1-V1-01"`.
  - `test_duplicate_passage_key_across_tests`: the same passage key in two tests yields `"duplicate passage key"`.
  - `test_shared_easy_not_duplicate`: the merged shared sections in three tests yield no duplicate problems.
  - `test_layout_mismatch`: test A V1 starts `tc tc tc…`, test B V1 starts `se tc tc…`; the result contains `"V1 layout differs"`.
  - `test_difficulty_mix`: a V2H with three items at difficulty 2 yields `"V2H difficulty mix"`.
  - `test_slot_layout`: a section `tc, mc@p, multi@p, mc` gives `[("tc",), ("mc","multi"), ("mc",)]`.
- [ ] **Step 2:** Run `python -I tools/test_build.py`. Expected: ImportError or AssertionError.
- [ ] **Step 3: Implement.**
  - Uniqueness covers ids and passage/table/chart keys across tests; the merged shared sections count once.
  - The layout check compares `slot_layout` per section key against the first test.
  - Difficulty mix follows the Global Constraints table.
  - Run the verbal shuffle once per question object, so shared items aren't reshuffled per test.
- [ ] **Step 4:** Run `python -I tools/test_build.py`. Expected: `all build checks passed`.
- [ ] **Step 5:** Run `python -I src/build.py`. Expected: `Built 1 test(s): test-01`. Test 1 may report difficulty-mix problems; if so, temporarily enforce only V2E/Q2E with an inline note: `shortcut: mix enforced on rewritten tests only, remove after Task 6`.
- [ ] **Step 6:** Open `index.html` in the browser pane. Take Q1 with all answers blank and confirm routing to `Q2E` still works and shows the shared items.
- [ ] **Step 7: Commit.** `git commit -m "build: shared easy tier, cross-test uniqueness, layout and difficulty checks"`

### Task 2: Quant answer verifier

**Files:**
- Create: `tools/verify_quant.py`
- Modify: `src/build.py` (call the verifier from `check_all`)
- Modify: `tools/test_build.py`

**Interfaces:**
- `CHECKS: dict[str, Callable[[], object]]` maps a question id to a function returning the key in the stored form:
  - `int` index for `mc` and `qc`
  - sorted `list[int]` for `multi`
  - `float` or `int` for `numeric`
  - `[n, d]` for `fraction`
- `qc(cases: Iterable[tuple[float, float]]) -> int` returns 0, 1, 2 or 3. It returns 3 as soon as two cases disagree.
- `same_key(q: dict, got) -> bool` compares fractions by cross-multiplication and numerics within 1e-9.
- `verify(tests) -> list[str]` reports `"<id>: no quant check"` or `"<id>: key X, check says Y"`.

- [ ] **Step 1: Failing tests:**
  - `test_qc_cannot_determine`: `qc([(1,2),(3,2)]) == 3`
  - `test_qc_equal`: `qc([(2,2),(5,5)]) == 2`
  - `test_fraction_equivalence`: `same_key({"type":"fraction","answer":[1,2]}, [2,4])`
  - `test_missing_check_reported`: a quant item with no entry yields `"no quant check"`
- [ ] **Step 2:** Run `python -I tools/test_build.py`. Expected: FAIL.
- [ ] **Step 3: Implement**, and write checks for every Test 1 and shared-easy quant item kept so far. The verifier skips Verbal items.
- [ ] **Step 4:** Run `python -I tools/test_build.py` and `python -I src/build.py`. Expected: both pass. If a check disagrees with an existing key, report it to the user; don't silently change the key.
- [ ] **Step 5: Commit.** `git commit -m "build: verify every quant answer key by computation"`

### Task 3: Randomized test

**Files:**
- Create: `src/random.js` (wrapped as `var GRE_RANDOM = (function(){ … return {compose, materialize, indexTests}; })();`; `module.exports` when present, for node)
- Create: `tools/test_random.js`
- Modify: `src/build.py` (inline `random.js` at a `__RANDOM_JS__` marker in `app.html`)
- Modify: `src/app.html`:
  - `testById`
  - `renderHome` (randomized card; history titles)
  - `startAttempt` (accept a composition)
  - `buildRecord` (store `composition`)
  - the `stale` logic at ~`app.html:777`

**Interfaces:**
- `indexTests(tests) -> {q: {id: question}, passages, tables, charts, essays: {testId: essay}, slots: {sectionKey: [[ [ids…] per test ] per slot]}}`
- `compose(index, rand: () => number) -> {sections: {V1: [ids], V2E, V2M, V2H, Q1, Q2E, Q2M, Q2H}, essayFrom: testId}`
- `materialize(comp, index, id: string) -> test object` in the same shape as a fixed test. It carries `id`, the title `"Randomized test"`, the order `["V1","V2","Q1","Q2"]`, the `essay` drawn from `essayFrom`, merged `passages`/`tables`/`charts`, and `version: "random"`. A missing id becomes the placeholder `{id, type: "removed"}`, counted wrong.
- Random ids look like `random-<Date.now()>`. `progress[id].composition` and `record.composition` hold the `comp`.

- [ ] **Step 1: Failing tests in `tools/test_random.js`** (plain `assert`, fixtures of 3 tiny tests):
  - `test_compose_counts`: every section has the fixture's question count.
  - `test_passage_set_kept_together`: all questions of a passage set come from one test, in order.
  - `test_shared_sections_fixed`: `V2E` equals the shared ids.
  - `test_materialize_roundtrip`: `materialize(compose(...))` gives `sections.V1.questions.map(q => q.id)` equal to the composition.
  - `test_materialize_missing_id`: the removed id yields a `type: "removed"` placeholder, with no throw.
- [ ] **Step 2:** Run `node tools/test_random.js`. Expected: FAIL.
- [ ] **Step 3: Implement `src/random.js`.**
- [ ] **Step 4:** Run `node tools/test_random.js`. Expected: `random: all passed`.
- [ ] **Step 5: Wire into `app.html`.**
  - `testById(id)`: for `random-…`, materialize from `progress[id].composition`, or else from the history record's `composition`. Cache the result in a map.
  - The home screen gets a "Randomized test" card, styled like the others, with a Start button and an in-progress Resume/Discard when one exists.
  - `isCorrect`, `answered` and the report/practice renderers treat `type: "removed"` as wrong and render "This question was removed after you took the test."
  - The stale check for random attempts is "any removed placeholder", not the version check.
- [ ] **Step 6: Browser check** with the build output:
  - Start the randomized test, answer two questions, reload, and Resume. The same questions appear.
  - Finish with Report. The report and practice mode open.
  - Load an old-format Test 1 history record (saved before Task 6) and confirm it lists and opens via the stale path without errors.
- [ ] **Step 7: Commit.** `git commit -m "feat: randomized full-length test assembled from all fixed tests"`

### Task 4: Accounts (Supabase)

**Files:**
- Create: `docs/supabase-setup.md` (click-by-click steps; the SQL below; Authentication → Providers → Email: turn off "Confirm email"; Site URL = the GitHub Pages address; where to find the project URL and publishable key)
- Create: `supabase/schema.sql`
- Modify: `src/app.html` (storage block, ~`app.html:168-205`; home header; config constants `SUPABASE_URL`, `SUPABASE_KEY` at the top of the script)
- Modify: `README.md` (accounts section)

**Schema (exact):**

```sql
create table public.attempts (
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  id text not null,
  data jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);
alter table public.attempts enable row level security;
create policy "own rows" on public.attempts for all
  using (user_id = auth.uid()) with check (user_id = auth.uid());
```

**Interfaces:**
- Local keys:
  - `K_HIST + ":" + who` and `K_PROG + ":" + who`, where `who` is the user id or `"guest"`.
  - On first run, migrate the existing un-suffixed keys to `":guest"`.
- `account = null | {id, email}`.
- `store` takes the values `"browser" | "account" | "claude"`.
- `syncFromServer()`: `select data from attempts`, then `mergeHist` with local, then upsert any local-only records.
- `saveAttempt` / `updateAttempt`: also upsert `{id, data}` when signed in.
- Guest import:
  - Shown once per account per device, when the guest history is non-empty: "Copy N guest results into this account?"
  - On yes: upsert them, then delete them from the guest keys.
- Log out: `signOut()`, then remove that user's local keys, then switch to guest.

- [ ] **Step 1: User sets up Supabase** following `docs/supabase-setup.md` and pastes the URL and publishable key into chat. Fill in the constants.
- [ ] **Step 2:** Implement the guest-only refactor (per-`who` keys plus the migration). Check: the build still produces a working guest app, and old history still shows.
- [ ] **Step 3:** Implement the login/sign-up/log-out/reset-password UI on the home screen, plus the "Signed in as …" line and the one-line "accounts unavailable, using guest mode" notice.
- [ ] **Step 4:** Implement the sync, the upserts and the guest import.
- [ ] **Step 5:** Empty-config check: blank the constants, rebuild, and confirm guest mode with the notice and no console errors. Then restore them.
- [ ] **Step 6: Browser check of the main flow.**
  - Sign up user A with a test email, finish a short test, and see it in history.
  - In a fresh browser tab or profile, log in as A; the same history appears.
- [ ] **Step 7: Shared-laptop check.**
  - A logs out, and B signs up on the same browser.
  - B's history and in-progress list are empty.
  - Run `select * from attempts` with B's session in the console; it returns only B's rows.
- [ ] **Step 8: Offline check.**
  - Block `*.supabase.co` in the browser pane, or set a wrong URL, and finish a test.
  - Expected: the record is saved locally and the existing "Saved in this browser only…" toast appears.
- [ ] **Step 9: Commit.** `git commit -m "feat: Supabase accounts with guest mode, sync and guest import"`

### Tasks 5–8: Content

Each content task follows the same loop. A task is done when `python -I src/build.py` passes with the new files and the checks below are recorded.

**Loop for each section:**
1. **Draft** (main model, or Opus subagents run in parallel, one per section).
   - Write original items to the section's layout (Task 1 `slot_layout` of Test 1's section) and difficulty mix.
   - Each item needs `skill`, `difficulty` and an `explain` that walks through the reasoning without option letters.
   - Quant topics follow the ETS Math Review (arithmetic and number properties, algebra, geometry, data analysis including probability and counting).
   - Hard items lean on multi-step reasoning and traps, not big arithmetic.
2. **Quant key check:** add a `CHECKS` entry per quant item, and run `python -I src/build.py`.
3. **Blind solve** (Sonnet subagent, given items without keys or explanations, returns its answers).
   - Any item where it disagrees with the key is reviewed.
   - Fix the item if it's ambiguous, or the key if it's wrong.
   - Drop the item if it's still contested.
4. **Difficulty review:** Fable rates 5 random items per section against ETS's published difficulty, using the POWERPREP and ETS sample questions as reference. Rewrite any item rated below its slot's band.
5. Record the blind-solve disagreements and Fable ratings in `docs/content-review/<test>.md`: one line per flagged item and what changed.

- [ ] **Task 5: Shared easy tier.** Raise `tests/shared-easy.json` V2E and Q2E to difficulty 2–3, rewriting as needed. Commit `content: shared easy tier at difficulty 2-3`.
- [ ] **Task 6: Test 1 rewrite.**
  - In V1, V2M, V2H, Q1, Q2M and Q2H, keep the items already at 4–5 that pass the loop, and rewrite the rest to the mix.
  - Move every id to the `T1-` form.
  - Remove the Task 1 `shortcut:` for the difficulty mix.
  - Commit `content: test 1 rewritten to 160+ difficulty`.
- [ ] **Task 7: Test 2.** New `tests/test-02.json`: 84 new items, one new essay prompt, and its own passages/tables/charts. Commit `content: test 2`.
- [ ] **Task 8: Test 3.** Same as Task 7, in `tests/test-03.json`. Commit `content: test 3`.

After Task 8, spot-check: show the user 10 random Verbal items (5 hard, 5 medium) with keys for their sign-off.

### Task 9: Finish

**Files:** Modify `README.md` (accounts, three tests, randomized mode, shared easy tier, how content is verified, and the copyright note that items are original). Rebuild the three HTML outputs.

- [ ] **Step 1:** Run `python -I tools/test_build.py`, `node tools/test_random.js` and `python -I src/build.py`. Expected: all pass, and the build prints `Built 3 test(s): test-01, test-02, test-03`.
- [ ] **Step 2:** Full browser run-through of one fixed test (at speed), at phone width as well. Check login, report and practice mode.
- [ ] **Step 3:** Commit, then ask the user before pushing. On yes, run `git push -u origin feature/accounts-and-harder-tests` and open a PR into `main` describing the changes and the Supabase setup the repo owner needs to know about.
