# Promotion checklist

## Manual prerequisites (do these first — nothing below works without them)

1. **PyPI trusted publisher** — on https://pypi.org/manage/account/publishing/, add a pending publisher
   for project `pitstop`, repo `praneethravuri/pitstop`, workflow `release.yml`, environment (none).
   One-time; enables the `pypi` job in `.github/workflows/release.yml` to publish on `v*` tags
   without a stored password.
2. **mcp-publisher auth** — install and authenticate for the `io.github.praneethravuri` namespace
   (GitHub OAuth proves ownership of the `praneethravuri` GitHub org/user, which the `io.github.*`
   namespace maps to):
   ```bash
   brew install mcp-publisher   # or: go install github.com/modelcontextprotocol/registry/cmd/mcp-publisher@latest
   mcp-publisher login github
   ```

## 1. Official MCP Registry

```bash
mcp-publisher publish --file server.json
```

`server.json` (repo root) already declares `io.github.praneethravuri/pitstop`, pointing at the PyPI
package. Re-run after each version bump (keep `server.json`'s `version` in sync with
`pyproject.toml`).

## 2. Directories

Submit `server.json` / repo link to:

- [Smithery.ai](https://smithery.ai/)
- [Glama.ai](https://glama.ai/mcp/servers)
- [PulseMCP](https://www.pulsemcp.com/)
- [mcp.so](https://mcp.so/)
- [mcpservers.org](https://mcpservers.org/)
- [Docker MCP Catalog](https://hub.docker.com/mcp) (uses the GHCR image already published by `release.yml`)

## 3. Awesome list

PR to [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — add a line
under the appropriate language/category section pointing at the repo.

## 4. Community posts

- **Show HN** — factual title ("Show HN: Pitstop – an F1 MCP server with a queryable 1950-present database"), no hype.
- **r/mcp**, **r/ClaudeAI** — standard show-and-tell post.
- **r/formula1** — check current self-promotion rules before posting; angle it as a data/dev post,
  not marketing (e.g. "I built a tool that can answer any F1 stats question").
- **X / dev.to** — short writeup with a demo GIF. GIF ideas:
  - "Verstappen family tree" (`driver_family_relationship` query)
  - "Aston Martin lineage" (`constructor_chronology` query, Jordan → ... → Aston Martin)
  - live race Q&A during a session (`get_live_data` + `query_f1_database` together)

## 5. Timing

Launch and re-promote around race weekends (Thu–Sun), when F1 search/social interest peaks.
