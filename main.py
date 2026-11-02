import os
import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from caller_authorization import forward_caller_authorization

async def sanitize_headers(request):
    # seeing x-forwarded headers being carried over.
    # strip them out before making a request to YNAB.
    strip_headers = ["x-forwarded-for", "x-forwarded-host", "x-forwarded-port", "x-forwarded-proto", "x-forwarded-server", "x-real-ip"]
    for header in strip_headers:
        request.headers.pop(header, None)

if __name__ == "__main__":
    transport = os.getenv('TRANSPORT') or 'http'

    openapi_spec_response = httpx.get("https://api.ynab.com/papi/open_api_spec.yaml", timeout=10.0)
    openapi_spec_response.raise_for_status()
    openapi_spec = yaml.safe_load(openapi_spec_response.text)

    if transport == 'http':
        client = httpx.AsyncClient(
            base_url="https://api.ynab.com/v1",
            event_hooks={"request": [sanitize_headers, forward_caller_authorization]}
        )
    else:
        ynab_token = os.getenv('YNAB_TOKEN')
        if not ynab_token:
            raise ToolError("YNAB_TOKEN is required in stdio mode!")
        client = httpx.AsyncClient(
            base_url="https://api.ynab.com/v1",
            headers={"Authorization": f"Bearer {ynab_token}"},
        )

    mcp = FastMCP.from_openapi(openapi_spec=openapi_spec, client=client, name="YNAB MCP Server")
    if transport == 'http':
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    elif transport == 'stdio':
        mcp.run()
    else:
        raise ToolError(f"Unknown transport: {transport}!")
