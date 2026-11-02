import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

AUTHORIZATION_HEADER = "authorization"
MISSING_AUTHORIZATION_MESSAGE = (
    "Missing Authorization header. Configure your MCP client to send "
    "'Authorization: Bearer <YNAB personal access token>'."
)

async def forward_caller_authorization(request: httpx.Request) -> None:
    caller_headers = get_http_headers(include={AUTHORIZATION_HEADER})
    caller_authorization = caller_headers.get(AUTHORIZATION_HEADER)
    if not caller_authorization:
        raise ToolError(MISSING_AUTHORIZATION_MESSAGE)

    request.headers["Authorization"] = caller_authorization
