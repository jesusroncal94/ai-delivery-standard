# Penpot MCP server

Penpot's official MCP server (`@penpot/mcp` 2.17.0 from npm, built from the Penpot repository) running in Docker, for projects with the `diagrams` capability that work with https://design.penpot.app. It is the local alternative to a hosted Penpot MCP connector: everything runs on your machine, and the agent reaches Penpot through the plugin open in your browser.

| Service  | Host URL                              | Purpose                                    |
|----------|---------------------------------------|--------------------------------------------|
| `plugin` | http://localhost:4400/manifest.json   | Serves the Penpot MCP plugin               |
| `server` | http://localhost:4401/mcp             | MCP Streamable HTTP endpoint (SSE: `/sse`) |
| `server` | ws://localhost:4402                   | WebSocket the plugin connects to           |

All ports are bound to `127.0.0.1` only. Inside the containers the servers listen on `0.0.0.0`.

## Start and stop

From the root of this repository:

```
docker compose -f tools/penpot-mcp/compose.yaml up -d --build
docker compose -f tools/penpot-mcp/compose.yaml down
docker compose -f tools/penpot-mcp/compose.yaml logs -f
```

The containers use `restart: unless-stopped`, so they come back with Docker until you run `down`.

## One-time setup in Penpot

1. Sign in at https://design.penpot.app and open (or create) the design file, `<project> · docs` for a project on the standard.
2. Main menu > Plugins (or `Ctrl+Alt+P`), paste `http://localhost:4400/manifest.json`, click Install, and allow the requested permissions.
3. Open the "Penpot MCP Plugin" and click "Connect to MCP server". The status must read "Connected to MCP server".
4. When Chrome or Edge asks to let design.penpot.app access devices on your local network, click Allow.
5. Keep the plugin panel open while working; closing it drops the connection.

After the first install the plugin appears in the Plugins list; in each new session reopen it and click Connect.

## Register the server in a project

Each project that uses it registers the server in its own `.mcp.json`, as an HTTP server named `penpot`:

```json
{
  "mcpServers": {
    "penpot": {
      "type": "http",
      "url": "http://localhost:4401/mcp"
    }
  }
}
```

With Claude Code, the same entry can be added from the project's root with `claude mcp add --transport http --scope project penpot http://localhost:4401/mcp`; without `--scope project` it is registered for you only and not committed. Approve the server when the agent asks, or reconnect with `/mcp`. A new MCP server is approved by the human on the PR checklist, and `ads check` counts it towards the limit of five.

## Files

`tools/penpot-mcp/files` is mounted at `/files` in the server container; Git ignores everything in it except `.gitkeep`. The `import_image` and `export_shape` tools only see container paths, so use `/files/<name>`: put `logo.png` in `tools/penpot-mcp/files` and import `/files/logo.png`.

## Upgrading

Change `PENPOT_MCP_VERSION` and the image tag in `compose.yaml` (and `PNPM_VERSION` in `Dockerfile` if the package's `packageManager` field changed), then run `up -d --build`. Match the MCP version to the Penpot version shown in the plugin's version warning when a matching release exists: `docker run --rm node:22-bookworm-slim npm view @penpot/mcp dist-tags`.
