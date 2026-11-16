# Supabase setup (accounts)

Accounts use a free Supabase project. Without it, the site still works in guest mode: results are saved in the browser only.

1. Go to supabase.com, sign in, and click **New project**. Pick any name, a strong database password and the nearest region.
2. **SQL Editor → New query**: paste all of [`supabase/schema.sql`](../supabase/schema.sql) and click **Run**. This creates the `attempts` table, where each person can read and write only their own rows.
3. **Authentication → Sign In / Providers → Email**: turn **off** "Confirm email" and save. People can then sign up and start straight away. Supabase's free email sender allows only a few emails an hour, so it's kept for password resets.
4. **Authentication → URL Configuration**: set **Site URL** to the GitHub Pages address (for example `https://prans-code.github.io/gre-practice-centre/`). Password-reset emails link back there.
5. **Project Settings → Data API**: copy the **Project URL**. Then **Project Settings → API Keys**: copy the **publishable key** (`sb_publishable_…`).
6. Paste both into `SUPABASE_URL` and `SUPABASE_KEY` at the top of the script in `src/app.html`, then run `python -I src/build.py`.

The publishable key is meant to be public. The database rules from step 2 are what keep each person's data private. Never put the **secret** key in the page.

**Free plan pausing.** If nobody uses the site for about a week, Supabase pauses the project. Open the Supabase dashboard and click **Restore project**; no data is lost. While it's paused, the site falls back to guest mode.
