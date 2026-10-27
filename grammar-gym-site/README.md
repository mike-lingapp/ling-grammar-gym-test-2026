# Grammar Gym prototypes (for remote testing)

Two versions of the Grammar Gym prototype as a plain static website. No build step, no server code.

| Link (after hosting) | What it is |
|---|---|
| `…/a/?lang=sr` | Version A: full lesson, 6 games, mixed grammar topics. Languages: `sr` `cz` `de` `th` `it` `fr` |
| `…/b/?lang=sr` | Version B: noun gender only, 4 games. Languages: `sr` `cz` `it` |
| `…/` | Internal index with every link (don't send this to participants) |

`?lang=` sets the course language. Without it, the prototype opens in Serbian.

## Host it on GitHub Pages (free, recommended)

1. On github.com, create a new **public** repository (for example `grammar-gym-prototype`).
   GitHub Free only publishes Pages from public repositories. The site isn't listed anywhere and asks search engines not to index it, but anyone with a link can open it.
2. In the repository, click **Add file → Upload files**. Drag in **everything inside this folder** (including the hidden `.nojekyll` file), then **Commit changes**.
3. Go to **Settings → Pages**. Under *Build and deployment*, choose **Deploy from a branch**, branch **main**, folder **/ (root)**, then **Save**.
4. After 1–2 minutes your site is live at `https://<your-github-name>.github.io/grammar-gym-prototype/`.
   - Version A: `https://<your-github-name>.github.io/grammar-gym-prototype/a/?lang=sr`
   - Version B: `https://<your-github-name>.github.io/grammar-gym-prototype/b/?lang=sr`

**Vercel instead?** Import the same repository at vercel.com (no build settings needed). Its free Hobby plan is limited to personal, non-commercial use, so for company testing you'd need a paid plan.

## Updating

When the prototype changes on the Claude canvas, Claude gives you new files (usually only `components/`).
Upload them to the repository the same way (**Add file → Upload files**, replace when asked, **Commit**).
Pages updates in 1–2 minutes. Avoid updating while a test session is running.

## Useberry

- **Tracking code:** in Useberry, copy the website snippet and paste it into the `<head>` of both `a/index.html` and `b/index.html`
  (look for the comment `USEBERRY SNIPPET`). Edit the files on GitHub with the pencil icon, then commit.
- **Task success by URL:** the address changes as the participant moves through the lesson, for example
  `#learn-tab` → `#learn-the-rule` → `#start` → `#game-1` … → `#results` → `#complete`.
  Use `#results` (or `#complete`) as the success URL.
- **Randomizing A vs B:** one study per language, with the A and B links for that language as randomized variants
  (Serbian, Czech, Italian). German, French and Thai only exist in version A.

## What's inside

- `a/`, `b/`: the two entry pages (phone frame, scales to fit any screen).
- `components/`: the prototype screens, exported unchanged from the Claude canvas.
- `assets/`: illustrations and icons.
- `runtime.js`: small renderer that draws the canvas screens outside Claude.
- `vendor/preact.min.js`: Preact 10 (MIT licence, see `vendor/PREACT-LICENSE.txt`).

Notes: the audio in Ear Detective (version A) uses the browser's built-in text-to-speech, so voices depend on the participant's device.
Language content is a draft for the language team to proofread.
