# Manual GitHub update for the browser demonstration

No remote changes have been made. Use your own browser account.

1. Open the repository root, choose Add file then Upload files. Drag the CONTENTS of `github_update_browser` (including its `FactSculpt` folder and root files), not the enclosing folder. This patch contains only the changed files and refreshed checksums; existing repository files are retained. Commit as “Document browser uploads and correct demo evidence labels”. If updating files individually, replace each at its exact matching repository path.
2. Confirm `FactSculpt/web/index.html`, `app.js` and `style.css` are updated, the root README shows the browser command, and the optional Python instructions are separate. Test the local browser with a small text file and the paired JSON example. Syntax/handler checks do not substitute for your browser test.
3. Create a NEW tag `v1.1-paper` on the updated main commit. Use `RELEASE_NOTES.md` for the release description. Do not move or delete `v1.0-paper`, which was already cited. Verify the release's source archive includes the update.
4. Send the new release URL and complete commit SHA to the paper editor. The updated Word draft describes the browser feature, but its artifact hyperlink still targets existing `v1.0-paper` until the new release actually exists. Replace it after verification before submission.

The patch changes HTML labels/documentation and packages the current app.js/style.css; it does not connect the browser to Python, add PDF/DOCX parsing or run new research experiments. The original application source outside the prepared upload copy is preserved.
