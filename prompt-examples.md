Produce docs/atlas/ARCHITECTURE.md: a cited architecture reference for the repos. Use Graphify for code structure and read the files yourself for everything else. Every claim cites a path (file:line where possible). If you can't cite it, put it under "Open questions". Never invent.

1. GRAPH: Run `graphify update .` (or `/graphify .` if graphify-out/ doesn't exist). Read graphify-out/GRAPH_REPORT.md. Use only links tagged EXTRACTED as evidence; INFERRED or AMBIGUOUS links go under Open questions.

2. NON-CODE EVIDENCE (Graphify doesn't cover this; find it yourself):
   - `git ls-files | wc -l`; the language mix; `git log -1 --format='%h %ad' --date=short`
   - Churn: `git log --format= --name-only | sort | uniq -c | sort -rn | head -25`
   - Read IN FULL: every manifest (package.json, pyproject.toml, pom.xml, go.mod, *.csproj, ...), Dockerfile*, docker-compose*, Makefile, and every CI file (.github/workflows/*, .gitlab-ci.yml, azure-pipelines.yml, Jenkinsfile). CI is the ground truth for build/test commands.
   - Env vars: grep for os.environ, process.env, getenv, System.getenv, @Value("${, viper.Get. Compare against .env.example and list the undocumented ones (names only, never values).
   - Note any README vs. CI disagreements.

3. STRUCTURE (from Graphify, then confirm by opening the files):
   - Hotspots: the 5 most-connected modules in the graph, cross-checked with churn. Read each IN FULL. Cite line ranges for key symbols.
   - Architecture: map Graphify's clusters to directories. Name the pattern and cite evidence. Flag any dependency that points the wrong way (domain → infra).
   - Lifecycle: pick the main operation. Run `graphify path <entry point> <DB or external call>`, then open every hop. At least 6 hops, each `path:line → function()`.

4. WRITE these sections, in order:
   - YAML front matter (repo, commit, updated, files, language, generator: graphify+prompt)
   - Executive summary (≤3 sentences) · Tech stack (table with an Evidence column)
   - Architecture (one paragraph + a Mermaid flowchart LR with 6–15 nodes, real paths as labels, labeled edges) · Directory map · Request lifecycle · Core modules · Day-1 setup (commands from CI/scripts, each with its source) · Gotchas · Reading order (5 files, each with why)
   - Open questions
   - Changelog

5. VERIFY before finishing. Every backticked path must exist:
   bash:       grep -o '`[^`]*/[^`]*`' docs/atlas/ARCHITECTURE.md | tr -d '`' | sed 's/:.*//' | sort -u | while read p; do git ls-files --error-unmatch "$p" >/dev/null 2>&1 || ls -d "$p" >/dev/null 2>&1 || echo "MISSING $p"; done
   PowerShell: (Select-String -Path docs/atlas/ARCHITECTURE.md -Pattern '`([^`]*/[^`]*)`' -AllMatches).Matches | % { ($_.Groups[1].Value -split ':')[0] } | Sort-Object -Unique | ? { -not (Test-Path $_) } | % { "MISSING $_" }
   Fix every MISSING entry and re-run until it prints nothing. If you skipped any required read, line 1 must say INCOMPLETE: <what>.

Save the file; don't commit. Reply with the executive summary and the verification result only.
