function togglePassword() {
  const input = document.getElementById("password");
  const icon = document.getElementById("eyeIcon");

  if (input.type === "password") {
    input.type = "text";
    icon.className = "fas fa-eye-slash";
  } else {
    input.type = "password";
    icon.className = "fas fa-eye";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".login-form");
  const btn = document.querySelector(".login-btn");

  if (form && btn) {
    form.addEventListener("submit", function () {
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';
      btn.style.opacity = "0.7";
    });
  }
});