// Node.js worker: the runner that connects the service and the Rust engine.
//
// Loop: GET /transactions/pending -> for each txn, spawn the Rust binary,
// pipe the txn JSON to its stdin, read the Score JSON from stdout ->
// POST /transactions/{id}/score. Sleep ~1s between polls.
//
// Config via env vars (with sensible defaults):
//   SERVICE_URL  base URL of the FastAPI service
//   ENGINE_BIN   path to the compiled Rust binary
//
// Requires Node 18+ (uses the built-in global `fetch`).

const { spawn } = require("node:child_process");

const SERVICE_URL = process.env.SERVICE_URL || "http://127.0.0.1:8000";
const ENGINE_BIN =
  process.env.ENGINE_BIN || "../engine/target/release/engine";
const POLL_MS = 1000;
const BACKOFF_MS = 3000; // longer wait when the service is unreachable

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Run the Rust engine on one transaction. Resolves with the parsed Score.
function scoreTransaction(txn) {
  return new Promise((resolve, reject) => {
    const child = spawn(ENGINE_BIN);
    let stdout = "";
    let stderr = "";

    // Fires when the binary cannot be launched at all (e.g. missing file).
    child.on("error", (err) => {
      if (err.code === "ENOENT") {
        reject(
          new Error(
            `Rust engine not found at "${ENGINE_BIN}". Build it with ` +
              `\`cd engine && cargo build --release\` or set ENGINE_BIN.`
          )
        );
      } else {
        reject(err);
      }
    });

    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));

    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`engine exited ${code}: ${stderr.trim()}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (e) {
        reject(new Error(`engine produced invalid JSON: ${stdout}`));
      }
    });

    // Send the transaction to the engine's stdin.
    child.stdin.write(JSON.stringify(txn));
    child.stdin.end();
  });
}

async function processOne(txn) {
  console.log(`[worker] scoring txn ${txn.id} (amount=${txn.amount} ${txn.currency})`);
  const score = await scoreTransaction(txn);
  const resp = await fetch(`${SERVICE_URL}/transactions/${txn.id}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(score),
  });
  if (!resp.ok) {
    throw new Error(`POST score failed: ${resp.status} ${await resp.text()}`);
  }
  console.log(`[worker] txn ${txn.id} scored ${score.score} -> [${score.reasons.join(", ")}]`);
}

async function main() {
  console.log(`[worker] polling ${SERVICE_URL} every ${POLL_MS}ms`);
  console.log(`[worker] engine binary: ${ENGINE_BIN}`);

  while (true) {
    try {
      const resp = await fetch(`${SERVICE_URL}/transactions/pending`);
      if (!resp.ok) {
        throw new Error(`GET pending failed: ${resp.status}`);
      }
      const pending = await resp.json();

      for (const txn of pending) {
        try {
          await processOne(txn);
        } catch (e) {
          // One bad txn (e.g. engine missing) should not kill the loop.
          console.error(`[worker] error on txn ${txn.id}: ${e.message}`);
        }
      }
      await sleep(POLL_MS);
    } catch (e) {
      // Service unreachable / other poll failure -> back off, keep running.
      console.error(`[worker] poll error: ${e.message}. Retrying in ${BACKOFF_MS}ms.`);
      await sleep(BACKOFF_MS);
    }
  }
}

main();
