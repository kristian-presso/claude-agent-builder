"""Inventory MCP server. Runs in the `mcp` container on port 8000 behind nginx."""

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["mcp.example.com"],
    allowed_origins=["https://mcp.example.com"],
)

mcp = FastMCP(
    "inventory",
    host="0.0.0.0",
    port=8000,
    stateless_http=True,
    transport_security=security,
)


@mcp.tool()
def stock_level(sku: str) -> dict:
    """How many units of a SKU are in stock."""
    return {"sku": sku, "units": 12}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
