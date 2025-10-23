(function () {
  const root = document.getElementById("lp-root");
  if (!root) return;

  const createUrl = root.dataset.createUrl;
  const cta = document.getElementById("lp-cta");
  const fab = document.getElementById("lp-fab");
  const list = document.getElementById("lp-list");
  const modal = document.getElementById("lp-modal");
  const modalBody = document.getElementById("lp-modal-body");
  const emptyBox = document.getElementById("lp-empty");


  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return m ? decodeURIComponent(m[2]) : null;
  }
  const csrftoken = getCookie("csrftoken");

  function parseMaybeJson(text) {
    try {
      const data = JSON.parse(text);
      if (data && typeof data === "object" && "html" in data) return data.html;
    } catch (_) {}
    return text;
  }

  function setupGunungCombobox(scope) {
    const select = scope.querySelector("#id_gunung");
    if (!select) return;
    const wrap = document.createElement("div");
    wrap.className = "lp-combobox";
    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    const input = document.createElement("input");
    input.type = "text";
    input.className = "lp-input lp-combo-input";
    input.placeholder = "Cari gunung… (ketik awalan)";
    wrap.insertBefore(input, select);

    // Sembunyikan select asli (tetap ikut submit)
    select.classList.add("lp-select-hidden");

    // Panel daftar opsi
    const panel = document.createElement("ul");
    panel.className = "lp-combo-list";
    panel.setAttribute("hidden", "");
    wrap.appendChild(panel);

    // Cache opsi awal
    const ALL = Array.from(select.options).map(o => ({
      value: o.value,
      text: o.text,
    }));

    // Helper untuk render panel
    function renderList(items, q) {
      panel.innerHTML = "";
      if (items.length === 0) {
        const empty = document.createElement("li");
        empty.className = "lp-combo-empty";
        empty.textContent = q
          ? `Tidak ada gunung yang cocok untuk “${q}”.`
          : "Tidak ada pilihan.";
        panel.appendChild(empty);
      } else {
        items.forEach((o, idx) => {
          const li = document.createElement("li");
          li.className = "lp-combo-item";
          li.textContent = o.text;
          li.dataset.value = o.value;
          if (o.value === select.value) li.classList.add("is-active");
          panel.appendChild(li);
        });

        // footer tip
        const foot = document.createElement("div");
        foot.className = "lp-combo-foot";
        foot.textContent = "Enter: pilih • Esc: tutup • ↑/↓: navigasi";
        panel.appendChild(foot);
      }
    }

    function currentItems() {
      const q = (input.value || "").trim().toLowerCase();
      if (!q) return ALL;
      return ALL.filter(o => o.text.toLowerCase().startsWith(q));
    }

    function openPanel() {
      renderList(currentItems(), input.value);
      panel.removeAttribute("hidden");
    }
    function closePanel() {
      panel.setAttribute("hidden", "");
      activeIndex = -1;
      Array.from(panel.querySelectorAll(".lp-combo-item")).forEach(li => li.classList.remove("is-active"));
    }

    function setSelection(value) {
      // set ke select + input
      const opt = ALL.find(o => o.value === value);
      if (!opt) return;
      select.value = opt.value;
      input.value = opt.text;
      closePanel();
    }

    // Interaksi: klik item
    panel.addEventListener("mousedown", (e) => {
      const li = e.target.closest(".lp-combo-item");
      if (!li) return;
      e.preventDefault();
      setSelection(li.dataset.value);
    });

    // Interaksi: buka/tutup panel
    input.addEventListener("focus", openPanel);
    input.addEventListener("input", openPanel);
    document.addEventListener("click", (e) => {
      if (!wrap.contains(e.target)) closePanel();
    });

    // Keyboard nav
    let activeIndex = -1;
    function moveActive(delta) {
      const items = Array.from(panel.querySelectorAll(".lp-combo-item"));
      if (!items.length) return;
      activeIndex = (activeIndex + delta + items.length) % items.length;
      items.forEach(li => li.classList.remove("is-active"));
      const li = items[activeIndex];
      li.classList.add("is-active");
      // scroll into view
      const liRect = li.getBoundingClientRect();
      const pRect = panel.getBoundingClientRect();
      if (liRect.top < pRect.top || liRect.bottom > pRect.bottom) {
        li.scrollIntoView({ block: "nearest" });
      }
    }

    input.addEventListener("keydown", (e) => {
      if (panel.hasAttribute("hidden") && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
        openPanel();
        e.preventDefault();
        return;
      }
      if (e.key === "ArrowDown") { moveActive(+1); e.preventDefault(); }
      else if (e.key === "ArrowUp") { moveActive(-1); e.preventDefault(); }
      else if (e.key === "Enter") {
        const act = panel.querySelector(".lp-combo-item.is-active");
        if (act) {
          setSelection(act.dataset.value);
          e.preventDefault();
        }
      } else if (e.key === "Escape") {
        closePanel();
      }
    });

    // Set nilai awal (jika ada yang terpilih)
    const init = ALL.find(o => o.value === select.value);
    if (init && init.text && init.value) input.value = init.text;

    // Validasi: sebelum submit, pastikan select punya value valid
    const form = scope.querySelector("#logpendakian-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        // jika user ngetik tapi tidak memilih apa pun, cocokkan prefix 1 item
        if (!select.value) {
          const q = (input.value || "").trim().toLowerCase();
          const match = ALL.find(o => o.text.toLowerCase() === q);
          if (match) select.value = match.value;
        }
        if (!select.value) {
          e.preventDefault();
          openPanel();
          input.focus();
          // tampilkan pesan kalau kosong
          renderList(currentItems(), input.value);
        }
      });
    }
  }

//  Client-side validation 
function computeErrors(form){
  const errs = [];
  const start = form.querySelector("#id_start_date")?.value || "";
  const end = form.querySelector("#id_end_date")?.value || "";
  const team = form.querySelector("#id_team_size")?.value || "";
  const rate = form.querySelector("#id_rating")?.value || "";

  // Tanggal (format YYYY-MM-DD -> bisa banding string aman)
  if (start && end && end < start){
    errs.push("Tanggal selesai tidak boleh lebih awal dari tanggal mulai.");
  }

  // Team size (opsional, tapi kalau diisi minimal 1)
  if (team !== "" && Number(team) < 1){
    errs.push("Ukuran tim minimal 1 orang.");
  }

  // Rating (opsional, tapi kalau diisi 1–5)
  if (rate !== "" && (Number(rate) < 1 || Number(rate) > 5)){
    errs.push("Rating harus antara 1–5.");
  }

  return errs;
}

function renderErrors(form, errs){
  const box = form.querySelector("#lp-errors");
  const submit = form.querySelector('button[type="submit"], input[type="submit"]');

  if (!box) return;

  if (errs.length){
    const items = errs.map(e => `<li>${e}</li>`).join("");
    box.innerHTML = `<strong>Perlu diperbaiki:</strong><ul>${items}</ul>`;
    box.removeAttribute("hidden");
    submit && (submit.disabled = true);
  } else {
    box.setAttribute("hidden", "");
    box.innerHTML = "";
    submit && (submit.disabled = false);
  }
}

function wireLiveValidation(form){
  const start = form.querySelector("#id_start_date");
  const end = form.querySelector("#id_end_date");
  const team = form.querySelector("#id_team_size");
  const rate = form.querySelector("#id_rating");
  // Lock min end-date = start-date
  function syncMin(){
    if (end){
      end.min = start?.value || "";
      // kalau end terlanjur kurang dari start -> kosongkan agar valid
      if (start?.value && end.value && end.value < start.value){
        end.value = "";
      }
    }
  }
  start && start.addEventListener("change", () => { syncMin(); renderErrors(form, computeErrors(form)); });
  end   && end.addEventListener("change",   () => { renderErrors(form, computeErrors(form)); });
  team  && team.addEventListener("input",   () => { renderErrors(form, computeErrors(form)); });
  rate  && rate.addEventListener("input",   () => { renderErrors(form, computeErrors(form)); });

  syncMin();
  renderErrors(form, computeErrors(form));
}

  function openModalWith(html) {
    modalBody.innerHTML = html;
    modal.removeAttribute("hidden");
    modal.querySelectorAll("[data-close-modal]").forEach(el => el.addEventListener("click", closeModal));

    const form = modalBody.querySelector("form");
    if (form && form.id === "logpendakian-form") {
      form.addEventListener("submit", onSubmitForm);
      setupGunungCombobox(modalBody);
      wireLiveValidation(form);
    }

    const del = modalBody.querySelector("#lp-delete-form");
    if (del) del.addEventListener("submit", onSubmitDelete);

    document.addEventListener("keydown", escHandler);
  }

  function closeModal() {
    modal.setAttribute("hidden", "");
    modalBody.innerHTML = "";
    document.removeEventListener("keydown", escHandler);
  }
  function escHandler(e) { if (e.key === "Escape") closeModal(); }

  async function openCreateForm() {
    const res = await fetch(createUrl, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin"
    });
    const text = await res.text();
    openModalWith(parseMaybeJson(text));
  }

  async function onSubmitForm(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const fd = new FormData(form);

  const res = await fetch(form.action, {
    method: "POST",
    body: fd,
    headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrftoken || "" }
  });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = null; }
  if (res.ok && data && data.ok && data.html) {
    const tpl = document.createElement("template");
    tpl.innerHTML = data.html.trim();
    const node = tpl.content.firstElementChild;

    if (data.id) {
      const old = document.getElementById(`lp-item-${data.id}`) ||
                  list.querySelector(`[data-id="${data.id}"]`);
      if (old && node) old.replaceWith(node);
    } else {
      if (node) list.prepend(node);
      if (emptyBox && !emptyBox.hasAttribute("hidden")) emptyBox.setAttribute("hidden", "");
    }
    closeModal();
    return;
  }
  if (data && data.html) {
    openModalWith(data.html);
  } else {
    openModalWith(parseMaybeJson(text));
  }
}


async function onSubmitDelete(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const action = form.getAttribute("action") || window.location.href;
  const fd = new FormData(form);
  const token = fd.get("csrfmiddlewaretoken") || csrftoken || "";
  const res = await fetch(action, {
    method: "POST",
    body: fd,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": token
    },
    credentials: "same-origin"
  });

  let data = {};
  try { data = await res.json(); } catch (_) {}

  if (res.ok && data.ok && data.id) {
    const byData = list.querySelector(`[data-id="${data.id}"]`);
    const byId = document.getElementById(`lp-item-${data.id}`);
    (byData || byId)?.remove();
    if (list.children.length === 0 && emptyBox) emptyBox.removeAttribute("hidden");
    closeModal();
  } else {
    alert("Gagal menghapus.");
  }
}

    list?.addEventListener("click", async (ev) => {
    const btn = ev.target.closest(".lp-action");
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;
    const base = window.location.pathname.replace(/\/$/, ""); // contoh: /log

    async function fetchJsonOrAlert(url) {
        const res = await fetch(url, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
          credentials: "same-origin"
        });
        const text = await res.text();
        let json = null;
        try { json = JSON.parse(text); } catch (_) {}
        if (!json) {
          console.error("Expected JSON but got:", text.slice(0, 500));
          alert("Gagal membuka form. Coba refresh halaman.");
          return null;
        }
        return json;
    }

    if (action === "edit") {
      const json = await fetchJsonOrAlert(`${base}/${id}/edit/`);
      if (json && json.html) openModalWith(json.html);
    } else if (action === "delete") {
      const json = await fetchJsonOrAlert(`${base}/${id}/delete/`);
      if (json && json.html) openModalWith(json.html);
    }
    });


  cta?.addEventListener("click", openCreateForm);
  fab?.addEventListener("click", openCreateForm);
})();
