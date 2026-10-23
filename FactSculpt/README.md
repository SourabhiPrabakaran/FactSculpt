# Application source

For the browser demonstration, serve this directory's `web/` folder and open `index.html`. From the repository root:

```text
python -m http.server 8080 --bind 127.0.0.1 --directory FactSculpt/web
```

Open http://localhost:8080/index.html . Upload supports text files and paired JSON, not PDF/DOCX extraction. The browser uses JavaScript heuristics and is separate from the Python research pipeline. See the root README for exact format handling, limitations, optional Streamlit instructions and experiments.

Historical unsupported README claims are retained only in `../docs/HISTORICAL_README_UNVERIFIED.md`.
