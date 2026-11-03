(function () {
  "use strict";

  var S = window.SITE, CATS = window.CATEGORIES, PRODUCTS = window.PRODUCTS, I18N = window.I18N;
  var state = { lang: "ru", cat: "all", sort: "popular" };

  try { var saved = localStorage.getItem("lang"); if (saved === "kz" || saved === "ru") state.lang = saved; } catch (e) {}

  function t(key, vars) {
    var s = (I18N[state.lang] && I18N[state.lang][key]) || I18N.ru[key] || key;
    if (vars) Object.keys(vars).forEach(function (k) { s = s.split("{" + k + "}").join(vars[k]); });
    return s;
  }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function money(n) { return n.toLocaleString("ru-RU").replace(/,/g, " ") + " " + S.currency; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function waUrl(text) { return "https://wa.me/" + S.whatsapp + (text ? "?text=" + encodeURIComponent(text) : ""); }

  /* ---------- Static site data ---------- */
  function applySiteData() {
    $$("[data-brand]").forEach(function (el) { el.textContent = S.brand; });
    $$("[data-phone]").forEach(function (el) { el.textContent = S.phone; });
    $$("[data-phone-link]").forEach(function (el) { el.href = "tel:" + S.phone.replace(/[^\d+]/g, ""); });
    $$("[data-wa-link]").forEach(function (el) { el.href = waUrl(); });
    $$("[data-ig-link]").forEach(function (el) { el.href = S.instagram; });
    $$("[data-address]").forEach(function (el) { el.textContent = S.address[state.lang]; });
    $$("[data-hours]").forEach(function (el) { el.textContent = S.hours[state.lang]; });
    $("#year").textContent = new Date().getFullYear();
    var star = '<svg><use href="#i-star"/></svg>';
    $$(".stars").forEach(function (el) { el.innerHTML = star + star + star + star + star; });
  }

  /* ---------- i18n ---------- */
  function applyLang() {
    document.documentElement.lang = state.lang === "kz" ? "kk" : "ru";
    $$("[data-i18n]").forEach(function (el) { el.textContent = t(el.getAttribute("data-i18n")); });
    $$("[data-lang]").forEach(function (b) { b.classList.toggle("is-active", b.dataset.lang === state.lang); });
    document.title = S.brand + " — " + (state.lang === "kz" ? "үйге арналған тренажерлер" : "тренажёры для дома");
    applySiteData();
    renderCats();
    renderProducts();
    renderForm($("#leadForm"), "lead");
    renderForm($("#modalForm"), "modal");
  }

  /* ---------- Categories ---------- */
  function renderCats() {
    var html = '<button type="button" class="cat' + (state.cat === "all" ? " is-active" : "") + '" data-cat="all">' +
      '<svg><use href="#i-all"/></svg>' + esc(t("cats.all")) + "</button>";
    CATS.forEach(function (c) {
      html += '<button type="button" class="cat' + (state.cat === c.id ? " is-active" : "") + '" data-cat="' + c.id + '">' +
        '<svg><use href="#i-' + c.icon + '"/></svg>' + esc(c[state.lang]) + "</button>";
    });
    $("#cats").innerHTML = html;
  }

  /* ---------- Products ---------- */
  function iconFor(catId) {
    for (var i = 0; i < CATS.length; i++) if (CATS[i].id === catId) return CATS[i].icon;
    return "all";
  }
  function renderProducts() {
    var list = PRODUCTS.filter(function (p) { return state.cat === "all" || p.cat === state.cat; });
    if (state.sort === "asc") list.sort(function (a, b) { return a.price - b.price; });
    if (state.sort === "desc") list.sort(function (a, b) { return b.price - a.price; });

    if (!list.length) { $("#products").innerHTML = '<p class="empty">' + esc(t("catalog.empty")) + "</p>"; return; }

    $("#products").innerHTML = list.map(function (p) {
      var L = p[state.lang] || p.ru;
      var badge = p.badge ? '<span class="badge badge--' + p.badge + '">' + esc(t("badge." + p.badge)) + "</span>" : "";
      var monthly = Math.ceil(p.price / 12 / 100) * 100;
      return '<article class="product card">' +
        '<div class="product__img">' + badge + '<svg><use href="#i-' + iconFor(p.cat) + '"/></svg></div>' +
        '<div class="product__body">' +
          '<h3 class="product__name">' + esc(L.name) + "</h3>" +
          '<ul class="product__specs">' + L.specs.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>" +
          '<div class="product__price"><b>' + money(p.price) + "</b>" + (p.oldPrice ? "<s>" + money(p.oldPrice) + "</s>" : "") + "</div>" +
          '<div class="product__inst">' + esc(t("card.installment", { x: monthly.toLocaleString("ru-RU").replace(/,/g, " ") })) + "</div>" +
          '<button type="button" class="btn btn--primary btn--block" data-order="' + p.id + '">' + esc(t("card.order")) + "</button>" +
        "</div></article>";
    }).join("");
  }

  /* ---------- Forms ---------- */
  function renderForm(form, kind) {
    var keep = {};
    $$("input", form).forEach(function (i) { keep[i.name] = i.value; });
    var id = kind + "-";
    form.innerHTML =
      '<div class="field"><label for="' + id + 'name">' + esc(t("form.name")) + '</label>' +
        '<input id="' + id + 'name" name="name" autocomplete="name" required><span class="field__err"></span></div>' +
      '<div class="field"><label for="' + id + 'phone">' + esc(t("form.phone")) + '</label>' +
        '<input id="' + id + 'phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required><span class="field__err"></span></div>' +
      (kind === "lead"
        ? '<div class="field"><label for="' + id + 'product">' + esc(t("form.product")) + '</label><input id="' + id + 'product" name="product"></div>'
        : '<input type="hidden" name="product">') +
      '<button type="submit" class="btn btn--primary btn--block">' + esc(t("form.submit")) + "</button>" +
      '<p class="form__note">' + esc(t("form.privacy")) + "</p>";
    $$("input", form).forEach(function (i) { if (keep[i.name]) i.value = keep[i.name]; });
  }

  function formatPhone(value) {
    var d = value.replace(/\D/g, "");
    if (d.charAt(0) === "8") d = "7" + d.slice(1);
    if (d && d.charAt(0) !== "7") d = "7" + d;
    d = d.slice(0, 11);
    var r = d ? "+7" : "";
    if (d.length > 1) r += " (" + d.slice(1, 4);
    if (d.length >= 4) r += ")";
    if (d.length > 4) r += " " + d.slice(4, 7);
    if (d.length > 7) r += "-" + d.slice(7, 9);
    if (d.length > 9) r += "-" + d.slice(9, 11);
    return r;
  }

  function setErr(input, msg) {
    var f = input.closest(".field");
    f.classList.toggle("has-error", !!msg);
    $(".field__err", f).textContent = msg || "";
  }

  function submitForm(form) {
    var name = form.elements.name, phone = form.elements.phone, product = form.elements.product;
    var ok = true;
    if (name.value.trim().length < 2) { setErr(name, t("form.errName")); ok = false; } else setErr(name);
    if (phone.value.replace(/\D/g, "").length !== 11) { setErr(phone, t("form.errPhone")); ok = false; } else setErr(phone);
    if (!ok) return;

    var msg = t("form.msg", { name: name.value.trim(), phone: phone.value });
    if (product && product.value.trim()) msg += t("form.msgProduct", { product: product.value.trim() });

    var note = $(".form__ok", form);
    if (!note) { note = document.createElement("p"); note.className = "form__ok"; form.appendChild(note); }
    note.textContent = t("form.ok");
    window.open(waUrl(msg), "_blank", "noopener");
  }

  /* ---------- Modal ---------- */
  var lastFocus = null;
  function openModal(productId) {
    var p = PRODUCTS.filter(function (x) { return x.id === productId; })[0];
    if (!p) return;
    var L = p[state.lang] || p.ru;
    lastFocus = document.activeElement;
    $("#modalProduct").textContent = L.name + " — " + money(p.price);
    var form = $("#modalForm");
    form.elements.product.value = L.name + " (" + money(p.price) + ")";
    var ok = $(".form__ok", form); if (ok) ok.remove();
    $("#modal").hidden = false;
    document.body.style.overflow = "hidden";
    form.elements.name.focus();
  }
  function closeModal() {
    $("#modal").hidden = true;
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  /* ---------- Events ---------- */
  document.addEventListener("click", function (e) {
    var el;
    if ((el = e.target.closest("[data-lang]"))) {
      state.lang = el.dataset.lang;
      try { localStorage.setItem("lang", state.lang); } catch (err) {}
      applyLang();
    } else if ((el = e.target.closest("[data-cat]"))) {
      state.cat = el.dataset.cat;
      renderCats(); renderProducts();
      if (el.closest("#categories")) $("#catalog").scrollIntoView({ behavior: "smooth" });
    } else if ((el = e.target.closest("[data-order]"))) {
      openModal(Number(el.dataset.order));
    } else if (e.target.closest("[data-close]")) {
      closeModal();
    } else if (e.target.closest("#nav a")) {
      toggleMenu(false);
    }
  });

  document.addEventListener("input", function (e) {
    if (e.target.name === "phone") e.target.value = formatPhone(e.target.value);
    if (e.target.closest(".field.has-error")) setErr(e.target);
  });

  document.addEventListener("submit", function (e) {
    if (e.target.classList.contains("form")) { e.preventDefault(); submitForm(e.target); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !$("#modal").hidden) closeModal();
  });

  $("#sort").addEventListener("change", function (e) { state.sort = e.target.value; renderProducts(); });

  function toggleMenu(force) {
    var nav = $("#nav"), btn = $("#burger");
    var open = typeof force === "boolean" ? force : !nav.classList.contains("is-open");
    nav.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", String(open));
  }
  $("#burger").addEventListener("click", function () { toggleMenu(); });

  applyLang();
})();
