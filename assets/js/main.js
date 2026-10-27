// Año dinámico en el footer
document.querySelectorAll("[data-year]").forEach(function (el) {
  el.textContent = new Date().getFullYear();
});

// Botón "copiar" en los bloques de código
document.querySelectorAll(".code-block").forEach(function (block) {
  var btn = block.querySelector(".code-block__copy");
  var code = block.querySelector("code");
  if (!btn || !code) return;

  btn.addEventListener("click", function () {
    navigator.clipboard.writeText(code.innerText).then(function () {
      btn.textContent = "copiado";
      setTimeout(function () { btn.textContent = "copiar"; }, 1800);
    }).catch(function () {
      btn.textContent = "error";
      setTimeout(function () { btn.textContent = "copiar"; }, 1800);
    });
  });
});

// Sesión de usuario: usa la autenticación integrada de Azure Static Web Apps
// (/.auth/me, /.auth/login/<proveedor>, /.auth/logout). En local esas rutas no existen
// y la página simplemente se comporta como "sin sesión".
(function () {
  var isLogin = location.pathname.indexOf("/login") === 0;
  var params = new URLSearchParams(location.search);

  // Solo se aceptan rutas internas ("/algo"), nunca "//dominio" ni URLs externas.
  function safePath(p) {
    return typeof p === "string" && /^\/(?![\/\\])/.test(p) ? p : "/";
  }
  var volver = safePath(params.get("volver"));

  var PROVEEDORES = { github: "GitHub", aad: "Microsoft" };

  document.querySelectorAll("[data-login]").forEach(function (a) {
    a.href = "/.auth/login/" + a.getAttribute("data-login") +
      "?post_login_redirect_uri=" + encodeURIComponent(location.origin + volver);
  });

  var entrar = document.querySelector("[data-auth-in]");
  if (entrar && !isLogin) {
    entrar.href = "/login.html?volver=" + encodeURIComponent(location.pathname);
  }

  fetch("/.auth/me", { credentials: "same-origin" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      var user = data && data.clientPrincipal;
      if (!user) return;

      var nombre = user.userDetails || "Cuenta";
      var destinoSalida = location.origin + (isLogin ? "/" : location.pathname);
      var salirHref = "/.auth/logout?post_logout_redirect_uri=" + encodeURIComponent(destinoSalida);

      if (entrar) entrar.hidden = true;

      var salir = document.querySelector("[data-auth-out]");
      if (salir) { salir.href = salirHref; salir.hidden = false; }

      var etiqueta = document.querySelector("[data-auth-user]");
      if (etiqueta) { etiqueta.textContent = nombre; etiqueta.title = nombre; etiqueta.hidden = false; }

      var cuenta = document.querySelector("[data-account-panel]");
      var login = document.querySelector("[data-login-panel]");
      if (cuenta && login) {
        cuenta.querySelector("[data-account-name]").textContent = nombre;
        cuenta.querySelector("[data-account-provider]").textContent =
          PROVEEDORES[user.identityProvider] || user.identityProvider || "";
        cuenta.querySelector("[data-account-logout]").href = salirHref;
        login.hidden = true;
        cuenta.hidden = false;
      }
    })
    .catch(function () { /* sin red o sin /.auth: se queda como visitante */ });
})();
