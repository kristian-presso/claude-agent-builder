"""Team wiki MCP server (streamable HTTP, deployed at https://wiki-mcp.example.com/mcp).

Clients sign in with our IdP (Auth0) and send the access token as a bearer header.
"""

import jwt  # PyJWT
from mcp.server.fastmcp import Context, FastMCP

from wiki import db

mcp = FastMCP("team-wiki", stateless_http=True)


def _claims(ctx: Context) -> dict | None:
    header = ctx.request_context.request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        return None
    # The IdP already checked the user, so we only need the claims here.
    return jwt.decode(header[7:], options={"verify_signature": False})


@mcp.tool()
def search_pages(query: str, ctx: Context) -> dict:
    """Search wiki pages the signed-in user can see."""
    claims = _claims(ctx)
    if claims is None:
        return {"results": []}
    return {"results": db.search(query, team=claims.get("team"))}


@mcp.tool()
def get_page(page_id: str, ctx: Context) -> dict:
    """Read one wiki page."""
    claims = _claims(ctx)
    if not claims:
        return {"error": "login required"}
    return db.get_page(page_id)


@mcp.tool()
def edit_page(page_id: str, body: str, ctx: Context) -> dict:
    """Replace a page's body."""
    claims = _claims(ctx)
    if not claims or claims.get("team") != db.page_team(page_id):
        return {"error": "Unauthorized"}
    return db.save(page_id, body, author=claims["sub"])


@mcp.tool()
def delete_space(space_id: str, ctx: Context) -> dict:
    """Admin: delete a whole space."""
    claims = _claims(ctx)
    if claims and claims.get("role") == "admin":
        return db.delete_space(space_id)
    return {"error": "not allowed"}


@mcp.tool()
def export_all_pages() -> dict:
    """Export every page as markdown, for backups."""
    return {"pages": db.export_all()}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
