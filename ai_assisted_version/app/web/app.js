const state = {
  token: localStorage.getItem("ai_access_token") || "",
  user: null,
  plans: [],
};

const byId = (id) => document.getElementById(id);

function headers(extra = {}) {
  return state.token ? { ...extra, Authorization: `Bearer ${state.token}` } : extra;
}

function money(value) {
  return `${Number(value).toLocaleString("ru-RU")} KZT`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function output(data) {
  byId("apiOutput").textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  document.querySelector(".api-console").classList.add("open");
}

function toast(message, error = false) {
  const node = byId("toast");
  node.textContent = message;
  node.classList.toggle("error", error);
  node.classList.add("show");
  setTimeout(() => node.classList.remove("show"), 3000);
}

async function parse(response) {
  const data = await response.json().catch(() => ({}));
  output({ status: response.status, body: data });
  if (!response.ok) toast(data.detail || `HTTP ${response.status}`, true);
  return data;
}

function route(pageName) {
  const page = ["dashboard", "plans", "invoices", "admin"].includes(pageName) ? pageName : "dashboard";
  document.querySelectorAll("[data-page]").forEach((node) => node.classList.toggle("active", node.dataset.page === page));
  document.querySelectorAll("[data-page-button]").forEach((node) => {
    node.classList.toggle("active", node.dataset.pageButton === page);
  });
  if (location.hash !== `#${page}`) history.replaceState(null, "", `#${page}`);
}

function renderSession() {
  byId("tokenState").textContent = state.token ? "есть" : "нет";
  byId("tokenState").classList.toggle("ok", Boolean(state.token));
  byId("userState").textContent = state.user ? state.user.username : "не вошел";
  const plan = state.plans.find((item) => item.id === state.user?.active_plan_id);
  byId("activePlan").textContent = plan ? plan.title : state.user?.active_plan_id ? `ID ${state.user.active_plan_id}` : "нет";
}

function renderPlans() {
  byId("planCount").textContent = String(state.plans.length);
  if (!state.plans.length) {
    byId("plansList").innerHTML = '<div class="empty">Тарифы не загружены.</div>';
    renderSession();
    return;
  }
  byId("plansList").innerHTML = state.plans.map((plan) => {
    const mine = state.user?.active_plan_id === plan.id;
    return `
      <article class="item">
        <div>
          <div class="item-title">
            ${escapeHtml(plan.title)}
            ${mine ? '<span class="badge mine">Мой тариф</span>' : ""}
            <span class="badge ok">Доступен</span>
          </div>
          <div class="item-meta">
            <span>ID ${plan.id}</span>
            <span>${money(plan.monthly_price)}</span>
            <span>${plan.traffic_limit_gb} GB</span>
            <span>${escapeHtml(plan.description)}</span>
          </div>
        </div>
        <button data-plan="${plan.id}" ${mine ? "disabled" : ""}>${mine ? "Выбран" : "Выбрать"}</button>
      </article>
    `;
  }).join("");
  renderSession();
}

function renderInvoices(invoices) {
  byId("invoiceCount").textContent = Array.isArray(invoices) ? String(invoices.length) : "0";
  if (!Array.isArray(invoices) || !invoices.length) {
    byId("invoiceList").innerHTML = '<div class="empty">Счета не найдены.</div>';
    return;
  }
  byId("invoiceList").innerHTML = invoices.map((invoice) => `
    <article class="item">
      <div>
        <div class="item-title">Invoice #${invoice.id}<span class="badge">${invoice.status}</span></div>
        <div class="item-meta">
          <span>${escapeHtml(invoice.billing_month)}</span>
          <span>${money(invoice.amount)}</span>
          <span>Customer ${invoice.customer_id}</span>
          <span>Plan ${invoice.plan_id}</span>
        </div>
      </div>
      <button data-invoice="${invoice.id}">Открыть</button>
    </article>
  `).join("");
}

async function loadPlans() {
  const data = await parse(await fetch("/plans"));
  state.plans = Array.isArray(data) ? data : [];
  renderPlans();
}

async function loadMe() {
  if (!state.token) return;
  const data = await parse(await fetch("/auth/me", { headers: headers() }));
  if (data.id) {
    state.user = data;
    renderSession();
    renderPlans();
  }
}

async function login() {
  const data = await parse(await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: byId("loginUsername").value, password: byId("loginPassword").value }),
  }));
  if (data.access_token) {
    state.token = data.access_token;
    localStorage.setItem("ai_access_token", state.token);
    await loadMe();
    toast("Вход выполнен");
  }
}

async function register() {
  const data = await parse(await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: byId("regUsername").value,
      email: byId("regEmail").value,
      phone: byId("regPhone").value,
      password: byId("regPassword").value,
    }),
  }));
  if (data.id) toast("Клиент создан");
}

async function activatePlan() {
  const data = await parse(await fetch("/plans/activate", {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ plan_id: Number(byId("planId").value) }),
  }));
  if (data.id) {
    state.user = data;
    renderPlans();
    toast("Тариф активирован");
  }
}

async function loadInvoices() {
  const data = await parse(await fetch("/billing/invoices", { headers: headers() }));
  renderInvoices(data);
}

async function loadInvoice(id) {
  await parse(await fetch(`/billing/invoices/${id}`, { headers: headers() }));
}

async function generateInvoice() {
  const data = await parse(await fetch("/billing/generate", {
    method: "POST",
    headers: headers({
      "Content-Type": "application/json",
      "X-Internal-Billing-Key": byId("internalKey").value,
    }),
    body: JSON.stringify({
      customer_id: Number(byId("invoiceCustomerId").value),
      billing_month: byId("billingMonth").value,
    }),
  }));
  if (data.id) toast("Invoice создан");
}

document.querySelectorAll("[data-page-button]").forEach((button) => {
  button.addEventListener("click", () => route(button.dataset.pageButton));
});
document.querySelectorAll("[data-modal]").forEach((button) => {
  button.addEventListener("click", () => byId(button.dataset.modal).showModal());
});
document.addEventListener("click", (event) => {
  const plan = event.target.closest("[data-plan]");
  if (plan) {
    byId("planId").value = plan.dataset.plan;
    byId("activateDialog").showModal();
  }
  const invoice = event.target.closest("[data-invoice]");
  if (invoice) loadInvoice(invoice.dataset.invoice);
});

byId("logoutButton").addEventListener("click", () => {
  state.token = "";
  state.user = null;
  localStorage.removeItem("ai_access_token");
  renderSession();
  renderPlans();
  output("token удален");
});
byId("loadPlansButton").addEventListener("click", loadPlans);
byId("loadInvoicesButton").addEventListener("click", loadInvoices);
byId("generateInvoiceButton").addEventListener("click", generateInvoice);
byId("loginButton").addEventListener("click", login);
byId("registerButton").addEventListener("click", register);
byId("activatePlanButton").addEventListener("click", activatePlan);
byId("consoleToggle").addEventListener("click", () => document.querySelector(".api-console").classList.toggle("open"));
window.addEventListener("hashchange", () => route(location.hash.slice(1)));

route(location.hash.slice(1));
renderSession();
loadPlans();
loadMe();
