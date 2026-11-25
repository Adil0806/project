/* Автообновление DOM без перезагрузки страницы.
 * Элементы связываются с состоянием прибора через data-атрибуты:
 *   data-bind="path"        — подставить значение в текст (data-digits — знаков после запятой)
 *   data-check="path"       — выставить checked по булевому значению
 *   data-width="path"       — ширина progress-bar в процентах
 *   data-class-key/-true/-false  — переключение CSS-класса по булеву значению
 *   data-level-key/-classes — выбор класса по номеру уровня
 * Поля ввода (name=...) не затрагиваются, чтобы не стирать то, что вводит оператор.
 */
(() => {
  const slug = document.body.dataset.slug;
  if (!slug) return;
  const period = Number(document.body.dataset.refresh) || 2000;
  const auto = document.getElementById("auto-refresh");
  const badge = document.getElementById("conn-badge");

  const flatten = (obj, prefix = "", out = {}) => {
    for (const [k, v] of Object.entries(obj)) {
      const key = prefix ? `${prefix}.${k}` : k;
      if (v !== null && typeof v === "object") flatten(v, key, out);
      else out[key] = v;
    }
    return out;
  };

  const render = (state) => {
    const flat = flatten(state);
    document.querySelectorAll("[data-bind]").forEach((el) => {
      let v = flat[el.dataset.bind];
      if (v === undefined) return;
      if (typeof v === "number" && el.dataset.digits) v = v.toFixed(Number(el.dataset.digits));
      el.textContent = v;
    });
    document.querySelectorAll("[data-check]").forEach((el) => {
      if (el.dataset.check in flat) el.checked = Boolean(flat[el.dataset.check]);
    });
    document.querySelectorAll("[data-width]").forEach((el) => {
      const v = flat[el.dataset.width];
      if (v !== undefined) el.style.width = `${v}%`;
    });
    document.querySelectorAll("[data-class-key]").forEach((el) => {
      const v = flat[el.dataset.classKey];
      if (v === undefined) return;
      el.classList.remove(el.dataset.classTrue, el.dataset.classFalse);
      el.classList.add(v ? el.dataset.classTrue : el.dataset.classFalse);
    });
    document.querySelectorAll("[data-level-key]").forEach((el) => {
      const classes = el.dataset.levelClasses.split(",");
      const v = flat[el.dataset.levelKey];
      if (v === undefined) return;
      el.classList.remove(...classes);
      el.classList.add(classes[v]);
    });
  };

  const renderLogs = (logs) => {
    const body = document.getElementById("log-body");
    if (!body) return;
    const colors = { INFO: "success", WARN: "warning", ERROR: "danger" };
    body.replaceChildren(...logs.map((l) => {
      const tr = document.createElement("tr");
      const td = (node) => { const c = document.createElement("td"); c.append(node); tr.append(c); };
      td(l.time);
      const b = document.createElement("span");
      b.className = `badge text-bg-${colors[l.level] || "secondary"}`;
      b.textContent = l.level;
      td(b);
      td(l.message);
      return tr;
    }));
  };

  const setOnline = (ok) => {
    if (!badge) return;
    badge.textContent = ok ? "онлайн" : "нет связи";
    badge.className = `badge text-bg-${ok ? "success" : "danger"}`;
  };

  const refresh = async () => {
    try {
      const limit = document.getElementById("log-limit")?.value || 10;
      const [s, l] = await Promise.all([
        fetch(`/api/${slug}/state`).then((r) => r.json()),
        fetch(`/api/${slug}/logs?limit=${limit}`).then((r) => r.json()),
      ]);
      render(s);
      renderLogs(l);
      setOnline(true);
    } catch (e) {
      setOnline(false);
    }
  };

  document.getElementById("poll-btn")?.addEventListener("click", async () => {
    await fetch(`/api/${slug}/poll`, { method: "POST" });
    refresh();
  });

  setInterval(() => { if (!auto || auto.checked) refresh(); }, period);
})();
