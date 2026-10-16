import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export function build(clientSupportsUi: boolean) {
  const server = new McpServer({ name: "orders", version: "0.3.0" });
  if (clientSupportsUi) {
    server.registerTool("list_orders", {
      description: "List orders",
      _meta: { ui: { resourceUri: "ui://orders/view.html", csp: { connectDomains: ["https://api.example.com"] } } },
    }, async () => ({ structuredContent: { orders: await getOrders() } }));
  }
  return server;
}
