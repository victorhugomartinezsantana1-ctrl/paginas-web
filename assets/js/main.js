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
