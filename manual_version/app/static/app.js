const state = {
  token: localStorage.getItem("access_token") || "",
  currentUser: null,
  tariffs: [],
};

const $ = (id) => document.getElementById(id);
const els = {
  tokenState: $("tokenState"),
  sessionMetric: $("sessionMetric"),
  activeTariffMetric: $("activeTariffMetric"),
  activeTariffDescription: $("activeTariffDescription"),
  tariffCount: $("tariffCount"),
  invoiceCount: $("invoiceCount"),
  tariffs: $("tariffs"),
  invoices: $("invoices"),
  output: $("output"),
  console: $("console"),
  toast: $("toast"),
};

function routeTo(route) {
  const next = ["overview", "tariffs", "invoices", "admin"].includes(route) ? route : "overview";
  document.querySelectorAll("[data-page]").forEach((page) => {
    page.classList.toggle("active", page.dataset.page === next);
  });
  document.querySelectorAll("[data-route]").forEach((button) => {
    button.classList.toggle("active", button.dataset.route === next);
  });
  if (location.hash !== `#${next}`) history.replaceState(null, "", `#${next}`);
}

function authHeaders(extra = {}) {
  return state.token ? { ...extra, Authorization: `Bearer ${state.token}` } : extra;
}

function money(value, currency = "KZT") {
  return `${Number(value).toLocaleString("ru-RU")} ${currency}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showApi(data) {
  els.output.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  els.console.classList.add("open");
}

function notify(message, isError = false) {
  els.toast.textContent = message;
  els.toast.classList.toggle("error", isError);
  els.toast.classList.add("show");
  window.setTimeout(() => els.toast.classList.remove("show"), 3200);
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  showApi({ status: response.status, body: data });
  if (!response.ok) notify(data.detail || `HTTP ${response.status}`, true);
  return data;
}

function currentTariff() {
  if (!state.currentUser?.active_tariff_id) return null;
  return state.tariffs.find((tariff) => tariff.id === state.currentUser.active_tariff_id) || null;
}

function renderSession() {
  const hasToken = Boolean(state.token);
  els.tokenState.textContent = hasToken ? "есть" : "нет";
  els.tokenState.classList.toggle("ok", hasToken);
  els.sessionMetric.textContent = hasToken ? "Есть" : "Нет";
  renderActiveTariff();
}

function renderActiveTariff() {
  const tariff = currentTariff();
  if (tariff) {
    els.activeTariffMetric.textContent = tariff.name;
    els.activeTariffDescription.textContent = `${money(tariff.monthly_fee)} · ${tariff.description || "без описания"}`;
    return;
  }
  els.activeTariffMetric.textContent = state.currentUser?.active_tariff_id ? `ID ${state.currentUser.active_tariff_id}` : "Нет";
  els.activeTariffDescription.textContent = state.token
    ? "Тариф не выбран или каталог еще не загружен."
    : "Войдите и загрузите профиль.";
}

function renderTariffs() {
  if (!state.tariffs.length) {
    els.tariffs.innerHTML = '<div class="empty">Тарифы не найдены.</div>';
    els.tariffCount.textContent = "0";
    renderActiveTariff();
    return;
  }

  els.tariffCount.textContent = String(state.tariffs.length);
  els.tariffs.innerHTML = state.tariffs.map((tariff) => {
    const isMine = state.currentUser?.active_tariff_id === tariff.id;
    const availabilityClass = tariff.is_active ? "badge-success" : "badge-warning";
    const availabilityText = tariff.is_active ? "Доступен" : "Недоступен";
    return `
      <article class="item">
        <div>
          <div class="item-title">
            ${escapeHtml(tariff.name)}
            ${isMine ? '<span class="badge badge-primary">Мой тариф</span>' : ""}
            <span class="badge ${availabilityClass}">${availabilityText}</span>
          </div>
          <div class="item-meta">
            <span>ID ${tariff.id}</span>
            <span>${money(tariff.monthly_fee)}</span>
            <span>${escapeHtml(tariff.description || "без описания")}</span>
          </div>
        </div>
        <div class="toolbar">
          <button class="button button-primary" type="button" data-pick-tariff="${tariff.id}" ${isMine ? "disabled" : ""}>
            ${isMine ? "Выбран" : "Выбрать"}
          </button>
        </div>
      </article>
    `;
  }).join("");
  renderActiveTariff();
}

function renderInvoices(data) {
  if (!Array.isArray(data) || data.length === 0) {
    els.invoices.innerHTML = '<div class="empty">Счета не найдены или нужен login.</div>';
    els.invoiceCount.textContent = "0";
    return;
  }

  els.invoiceCount.textContent = String(data.length);
  els.invoices.innerHTML = data.slice(0, 20).map((invoice) => `
    <article class="item">
      <div>
        <div class="item-title">
          Invoice #${invoice.id}
          <span class="badge">${escapeHtml(String(invoice.status))}</span>
        </div>
        <div class="item-meta">
          <span>Период ${escapeHtml(invoice.billing_period)}</span>
          <span>${money(invoice.amount, invoice.currency)}</span>
          <span>User ${invoice.user_id}</span>
          <span>Tariff ${invoice.tariff_id}</span>
        </div>
      </div>
      <div class="toolbar">
        <button class="button" type="button" data-open-invoice="${invoice.id}">Открыть</button>
      </div>
    </article>
  `).join("");
}

async function loadTariffs() {
  const data = await parseResponse(await fetch("/tariffs"));
  state.tariffs = Array.isArray(data) ? data : [];
  renderTariffs();
}

async function loadMe() {
  if (!state.token) return;
  const data = await parseResponse(await fetch("/auth/me", { headers: authHeaders() }));
  if (data.id) {
    state.currentUser = data;
    renderSession();
    renderTariffs();
  }
}

async function registerUser() {
  const body = {
    username: $("regUsername").value,
    email: $("regEmail").value,
    phone_number: $("regPhone").value,
    password: $("regPassword").value,
  };
  const data = await parseResponse(await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }));
  if (data.id) notify("Клиент создан");
}

async function login() {
  const body = {
    username: $("loginUsername").value,
    password: $("loginPassword").value,
  };
  const data = await parseResponse(await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }));
  if (data.access_token) {
    state.token = data.access_token;
    localStorage.setItem("access_token", state.token);
    renderSession();
    await loadMe();
    notify("Вход выполнен");
  }
}

function logout() {
  state.token = "";
  state.currentUser = null;
  localStorage.removeItem("access_token");
  renderSession();
  renderTariffs();
  showApi("token удален");
  notify("Token удален");
}

async function activateTariff() {
  const data = await parseResponse(await fetch("/tariffs/activate", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ tariff_id: Number($("tariffId").value) }),
  }));
  if (data.id) {
    state.currentUser = data;
    renderSession();
    renderTariffs();
    notify("Тариф активирован");
  }
}

async function loadMyInvoices() {
  const data = await parseResponse(await fetch("/billing/my-invoices", { headers: authHeaders() }));
  renderInvoices(data);
}

async function loadInvoice() {
  await parseResponse(await fetch(`/billing/invoices/${$("invoiceId").value}`, { headers: authHeaders() }));
}

async function generateInvoice() {
  const body = {
    user_id: Number($("billUserId").value),
    billing_period: $("billPeriod").value,
  };
  const data = await parseResponse(await fetch("/billing/generate-invoice", {
    method: "POST",
    headers: authHeaders({
      "Content-Type": "application/json",
      "X-Internal-API-Key": $("internalKey").value,
    }),
    body: JSON.stringify(body),
  }));
  if (data.id) notify("Invoice создан");
}

document.querySelectorAll("[data-route]").forEach((button) => {
  button.addEventListener("click", () => routeTo(button.dataset.route));
});

document.querySelectorAll("[data-modal]").forEach((button) => {
  button.addEventListener("click", () => $(button.dataset.modal).showModal());
});

document.addEventListener("click", (event) => {
  const tariffButton = event.target.closest("[data-pick-tariff]");
  if (tariffButton) {
    $("tariffId").value = tariffButton.dataset.pickTariff;
    $("activateTariffModal").showModal();
    return;
  }

  const invoiceButton = event.target.closest("[data-open-invoice]");
  if (invoiceButton) {
    $("invoiceId").value = invoiceButton.dataset.openInvoice;
    loadInvoice();
  }
});

window.addEventListener("hashchange", () => routeTo(location.hash.slice(1)));

$("logoutButton").addEventListener("click", logout);
$("refreshTariffsButton").addEventListener("click", loadTariffs);
$("refreshInvoicesButton").addEventListener("click", loadMyInvoices);
$("loadTariffsButton").addEventListener("click", loadTariffs);
$("loadInvoicesButton").addEventListener("click", loadMyInvoices);
$("loginButton").addEventListener("click", login);
$("registerButton").addEventListener("click", registerUser);
$("activateTariffButton").addEventListener("click", activateTariff);
$("openInvoiceButton").addEventListener("click", loadInvoice);
$("generateInvoiceButton").addEventListener("click", generateInvoice);
$("consoleToggle").addEventListener("click", () => els.console.classList.toggle("open"));

renderSession();
routeTo(location.hash.slice(1) || "overview");
loadTariffs();
loadMe();
