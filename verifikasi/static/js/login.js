function togglePassword() {
  const input = document.getElementById("password");
  const eyeOpen = document.getElementById("eyeOpen");
  const eyeClosed = document.getElementById("eyeClosed");

  if (input.type === "password") {
    input.type = "text";
    eyeOpen.style.display = "none";
    eyeClosed.style.display = "block";
  } else {
    input.type = "password";
    eyeOpen.style.display = "block";
    eyeClosed.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".login-form");
  const btn = document.querySelector(".login-btn");

  if (form && btn) {
    form.addEventListener("submit", function () {
      btn.disabled = true;
      btn.innerHTML = '<span class="login-spinner"></span> Memproses...';
      btn.style.opacity = "0.7";
    });
  }
});