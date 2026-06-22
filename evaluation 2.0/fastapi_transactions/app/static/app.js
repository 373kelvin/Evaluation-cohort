const form = document.getElementById("transaction-form");
const submitBtn = document.getElementById("submit-btn");
const refreshBtn = document.getElementById("refresh-btn");
const tbody = document.getElementById("transactions-body");
const emptyState = document.getElementById("empty-state");
const formError = document.getElementById("form-error");
const toast = document.getElementById("toast");

const balanceValue = document.getElementById("balance-value");
const balanceMeta = document.getElementById("balance-meta");
const creditsValue = document.getElementById("credits-value");
const debitsValue = document.getElementById("debits-value");

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

const dateFmt = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
});

let toastTimer;

/** Works at / (local) and /services/tx/ (nginx prefix on Railway). */
function apiUrl(path) {
  const base = window.location.pathname.endsWith("/")
    ? window.location.pathname
    : `${window.location.pathname}/`;
  return base + path.replace(/^\//, "");
}

function showToast(message, type = "success") {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function formatAmount(amount, type) {
  const prefix = type === "credit" ? "+" : "−";
  return `${prefix}${currency.format(amount)}`;
}

async function fetchJSON(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    const detail = err.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail || `Request failed (${resp.status})`;
    throw new Error(message);
  }
  return resp.json();
}

function renderTransactions(transactions) {
  if (!transactions.length) {
    tbody.innerHTML = "";
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;
  const sorted = [...transactions].sort((a, b) => b.id - a.id);

  tbody.innerHTML = sorted
    .map(
      (txn) => `
    <tr>
      <td class="id-cell">#${txn.id}</td>
      <td><span class="badge ${txn.type}">${txn.type}</span></td>
      <td class="amount-cell ${txn.type}">${formatAmount(txn.amount, txn.type)}</td>
      <td class="desc-cell" title="${escapeHtml(txn.description || "—")}">${escapeHtml(txn.description || "—")}</td>
      <td class="date-cell">${dateFmt.format(new Date(txn.created_at))}</td>
    </tr>
  `
    )
    .join("");

  let credits = 0;
  let debits = 0;
  for (const txn of transactions) {
    if (txn.type === "credit") credits += txn.amount;
    else debits += txn.amount;
  }
  creditsValue.textContent = currency.format(credits);
  debitsValue.textContent = currency.format(debits);
}

function escapeHtml(str) {
  return str
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function loadData() {
  try {
    const [balance, transactions] = await Promise.all([
      fetchJSON(apiUrl("balance")),
      fetchJSON(apiUrl("transactions")),
    ]);

    balanceValue.textContent = currency.format(balance.balance);
    balanceMeta.textContent = `${balance.transaction_count} transaction${balance.transaction_count === 1 ? "" : "s"}`;
    renderTransactions(transactions);
  } catch (err) {
    balanceValue.textContent = "—";
    balanceMeta.textContent = "Failed to load";
    tbody.innerHTML = `<tr class="loading-row"><td colspan="5">${escapeHtml(err.message)}</td></tr>`;
    showToast(err.message, "error");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.hidden = true;

  const amount = parseFloat(document.getElementById("amount").value);
  const type = form.type.value;
  const description = document.getElementById("description").value.trim();

  if (!amount || amount <= 0) {
    formError.textContent = "Amount must be greater than 0.";
    formError.hidden = false;
    return;
  }

  submitBtn.disabled = true;

  try {
    await fetchJSON(apiUrl("transactions"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount,
        type,
        description: description || null,
      }),
    });

    form.reset();
    form.type.value = "credit";
    showToast("Transaction added successfully");
    await loadData();
  } catch (err) {
    formError.textContent = err.message;
    formError.hidden = false;
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
  }
});

refreshBtn.addEventListener("click", loadData);

loadData();
