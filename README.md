# mcp-ynab

FastMCP server that exposes the [YNAB API](https://api.ynab.com/) via MCP using YNAB's published OpenAPI spec.

## Requirements

- Python 3.12+
- A YNAB personal access token
- `uv` (recommended) or `pip`

## Configuration

Environment variables:

- `TRANSPORT` (optional): `http` (default) or `stdio`
- `YNAB_TOKEN` (required in `stdio` mode only): your YNAB API token

## Authentication

How the server authenticates with YNAB depends on the transport:

- **HTTP:** the server holds no token. Each MCP client sends its own YNAB token with every request, and the server forwards it to YNAB:

  ```
  Authorization: Bearer <YNAB personal access token>
  ```

  Requests without this header fail with a "Missing Authorization header" error.

- **stdio:** there are no request headers, so the server reads a single token from `YNAB_TOKEN` at startup.

## Run Locally

Using `uv`:

```bash
uv sync
export TRANSPORT="http"   # optional, defaults to http
uv run python main.py
```

HTTP mode starts the server on `0.0.0.0:8080`, with the MCP endpoint at `/mcp`.

For stdio mode:

```bash
export YNAB_TOKEN="your_token_here"
export TRANSPORT="stdio"
uv run python main.py
```

## Docker

Use the prebuilt image from GHCR:

```bash
docker pull ghcr.io/alexfu/mcp-ynab:latest
```

Run prebuilt image in HTTP mode:

```bash
docker run --rm -p 8080:8080 \
  -e TRANSPORT="http" \
  ghcr.io/alexfu/mcp-ynab:latest
```

Run prebuilt image in stdio mode:

```bash
docker run --rm -i \
  -e YNAB_TOKEN="your_token_here" \
  -e TRANSPORT="stdio" \
  ghcr.io/alexfu/mcp-ynab:latest
```

## Connecting a Client

### Claude (custom connector)

In Claude, add a custom connector:

1. Set the URL to `https://<your-host>/mcp`.
2. Under **Authentication**, choose **No sign-in**.
3. Under **Request headers**, add `authorization` with the value `Bearer <your YNAB token>`.

### Claude Code

```bash
claude mcp add --transport http ynab https://<your-host>/mcp \
  --header "Authorization: Bearer <your YNAB token>"
```

## Notes

- The server fetches YNAB's OpenAPI spec at startup from `https://api.ynab.com/papi/open_api_spec.yaml`.
- Startup will fail if `TRANSPORT` is invalid, `YNAB_TOKEN` is missing in stdio mode, or the spec request fails.
- Serve HTTP mode over HTTPS when it's reachable outside your machine, since every request carries a YNAB token.
