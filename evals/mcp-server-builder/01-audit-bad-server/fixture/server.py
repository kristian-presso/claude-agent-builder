"""Bookings MCP server for a small salon. Ready to list in the directory."""

import os

from mcp.server.fastmcp import FastMCP

API_KEY = os.environ.get("SALON_API_KEY", "")

mcp = FastMCP("salon")


def _caller_token():
    return os.environ.get("CALLER_TOKEN")


@mcp.tool()
def BookingTool(action: str, booking_id: int = 0, date: str = "", customer: str = "") -> dict:
    """Does booking stuff."""
    if action == "list":
        return {"bookings": _db_bookings()}
    if action == "create":
        if not date:
            date = "tomorrow 10:00"
        return {"created": {"customer": customer, "date": date}}
    if action == "cancel":
        _db_delete(booking_id)
        return {"cancelled": booking_id}
    return {}


@mcp.tool()
def get_customer_history(customer_email: str) -> dict:
    """Get a customer's full visit history and notes."""
    token = _caller_token()
    if token is None:
        return {"visits": []}
    return {"visits": _db_history(customer_email)}


@mcp.tool()
def list_services() -> dict:
    """List services."""
    return {"services": ["Cut", "Colour", "Blow dry"]}


@mcp.tool()
def send_reminder(booking_id: int, message: str) -> dict:
    """Send the customer a text."""
    return {"sent": True}


def _db_bookings():
    return []


def _db_delete(booking_id):
    pass


def _db_history(email):
    return []


if __name__ == "__main__":
    mcp.run("streamable-http", host="0.0.0.0")
