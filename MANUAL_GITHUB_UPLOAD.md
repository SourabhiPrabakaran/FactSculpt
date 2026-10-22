# Upload manually to your own GitHub account

Nothing has been connected, committed or pushed by the preparer. Do not upload the whole original workspace, the ZIP as a single repository file, or the portable document tools. Upload the extracted contents of this prepared folder.

## Before upload

1. Sign in to your own GitHub account in the browser. Confirm the displayed username; do not use your teammate's connected plugin account.
2. Confirm with the project owners that the source may be published. No new license was chosen automatically. Keep the repository private while rights and conference anonymity are unresolved; only make it public when those are settled.
3. Create an empty repository named `FactSculpt` under your account. For the Git method below, do not initialize a remote README, license or gitignore; the prepared folder already contains documentation and a gitignore.

## Option A: browser upload

Open the new repository's upload-files control and drag the CONTENTS of this extracted folder (including `FactSculpt`, `paper_foundation`, `docs` and root documentation). Check `.gitignore` is included; hidden files may need selecting separately. Commit with a message such as “Add FactSculpt prototype and verified evaluation artifacts”. Compare the resulting tree with this folder. Do not upload `FactSculpt_GitHub_Upload.zip` itself as a substitute for source files.

## Option B: local Git

Open PowerShell in this prepared folder, not in the original workspace. Replace the example name/email/URL with your own real values. The `--local` settings below affect only this repository.

```powershell
git init
git config --local user.name "YOUR NAME"
git config --local user.email "YOUR GITHUB NOREPLY OR AUTHOR EMAIL"
git branch -M main
git add .
git status
git diff --cached --stat
git commit -m "Add FactSculpt prototype and verified evaluation artifacts"
git remote add origin https://github.com/YOUR_USERNAME/FactSculpt.git
git remote -v
git push -u origin main
```

Before pushing, authenticate as YOUR account. A browser session and Git's saved credentials can belong to different people; stop if authentication shows the teammate's account and select your own account. Do not paste passwords/tokens into tracked files, chat or the remote URL. If the remote is not empty, do not force push; reconcile its existing content separately.

## After upload

1. Inspect the online README, source and results; check that no raw external data, model weights or secrets were added.
2. Create release `v1.0-paper` from the checked commit and use `RELEASE_NOTES.md` for its description. For local Git, `git rev-parse HEAD` returns the complete commit identifier. Do not change an already cited release tag to point to different code; publish a new release for corrections.
3. Record the repository URL, release URL and full commit SHA. A private repository does not provide public reviewer access. Resolve review anonymity and access before citing a public identifying link.
4. Send those actual links/commit to the manuscript editor. The Word paper still says the public deposit is pending; its link must be updated only after this step. The artifact does not resolve missing human annotations, predecessor comparison or repair-quality evidence.

The source and archive were locally checked on 22 October 2026. `PACKAGING_CHECKS.json` and `SHA256SUMS.json` document the prepared contents; no GitHub account or remote was accessed.
