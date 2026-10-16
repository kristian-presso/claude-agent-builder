"""Invoicing MCP server. Deployed on Cloud Run (min instances 1, max 4), stateless HTTP."""

import secrets

from mcp.server.fastmcp import FastMCP

from billing import api

mcp = FastMCP("invoicing", stateless_http=True, host="0.0.0.0", port=8080)

# Drafts waiting for the user to say yes before they are sent.
PENDING: dict[str, dict] = {}


@mcp.tool()
def draft_invoice(customer_id: str, lines: list[dict]) -> dict:
    """Prepare an invoice and return a preview. Nothing is sent until confirm_invoice."""
    draft_id = secrets.token_hex(4)
    PENDING[draft_id] = {"customer_id": customer_id, "lines": lines}
    total = sum(l["qty"] * l["unit_price"] for l in lines)
    return {"draft_id": draft_id, "total": total, "preview": lines}


@mcp.tool()
def confirm_invoice(draft_id: str) -> dict:
    """Send a drafted invoice to the customer. Call only after the user approves the preview."""
    draft = PENDING.pop(draft_id, None)
    if draft is None:
        return {"error": "Draft not found"}
    return api.send_invoice(draft["customer_id"], draft["lines"])


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
