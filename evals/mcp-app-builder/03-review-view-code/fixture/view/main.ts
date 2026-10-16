import { App } from "@modelcontextprotocol/ext-apps";

const app = new App({ name: "orders-view", version: "0.3.0" });
await app.connect();
app.ontoolresult = (result) => {
  const rows = result.structuredContent.orders
    .map((o) => `<tr><td>${o.customer}</td><td>${o.total}</td></tr>`).join("");
  document.querySelector("tbody").innerHTML = rows;
  document.body.style.background = "#ffffff";
};
