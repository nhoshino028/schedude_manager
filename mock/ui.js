export function qs(selector) {
  const element = document.querySelector(selector);
  if (!element) throw new Error(`Element not found: ${selector}`);
  return element;
}

export function qsa(selector) {
  return Array.from(document.querySelectorAll(selector));
}

export function setAlert(message) {
  const alert = document.querySelector("[data-alert]");
  if (!alert) return;
  alert.textContent = message ?? "";
  alert.setAttribute("data-show", message ? "true" : "false");
}

export function readQuery() {
  const url = new URL(window.location.href);
  const params = {};
  url.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  return params;
}

export function fillSelect(select, items, { valueKey, labelKey, includeEmpty }) {
  select.innerHTML = "";
  if (includeEmpty) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = includeEmpty;
    select.appendChild(option);
  }
  for (const item of items) {
    const option = document.createElement("option");
    option.value = String(item[valueKey]);
    option.textContent = String(item[labelKey]);
    select.appendChild(option);
  }
}

export function renderTable(tbody, rowsHtml) {
  tbody.innerHTML = rowsHtml;
}

