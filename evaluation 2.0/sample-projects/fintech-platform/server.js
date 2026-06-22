// Express gateway — additional routes for B2 endpoint detection
const express = require("express");
const app = express();

app.get("/api/v1/status", (req, res) => res.json({ ok: true }));

app.post("/api/v1/webhooks/stripe", (req, res) => {
  res.json({ received: true });
});

app.get("/api/v1/merchants/:id/settlements", (req, res) => {
  res.json([]);
});

app.listen(3000, () => console.log("gateway on :3000"));
