const fileInput = document.getElementById("ijazah-file");
const previewBox = document.getElementById("selected-file-preview");
const fileList = document.getElementById("file-list");
const verificationForm = document.getElementById("verification-form");

const resultsContainer = document.getElementById("results-container");
const emptyMessage = document.getElementById("empty-message");
const uploadProgress = document.getElementById("upload-progress");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const progressCount = document.getElementById("progress-count");

fileInput.addEventListener("change", function () {
  fileList.innerHTML = "";

  if (fileInput.files.length > 0) {
    previewBox.style.display = "block";

    Array.from(fileInput.files).forEach((file) => {
      let iconClass = "fas fa-file";
      if (file.type.startsWith("image/")) iconClass = "fas fa-file-image";
      else if (file.type === "application/pdf") iconClass = "fas fa-file-pdf";

      const div = document.createElement("div");
      div.className = "file-card";
      div.innerHTML = `
        <div class="file-icon"><i class="${iconClass}"></i></div>
        <div class="file-info"><p class="file-name">${file.name}</p></div>
      `;
      fileList.appendChild(div);
    });
  }
});

function getCSRFToken() {
  const cookies = document.cookie.split(";");
  for (let c of cookies) {
    c = c.trim();
    if (c.startsWith("csrftoken=")) return c.substring("csrftoken=".length);
  }
  const input = document.querySelector("[name=csrfmiddlewaretoken]");
  return input ? input.value : "";
}

verificationForm.addEventListener("submit", async function (e) {
  e.preventDefault();

  const files = fileInput.files;
  if (files.length === 0) return;

  const csrfToken = getCSRFToken();
  const totalFiles = files.length;
  let completed = 0;

  emptyMessage.style.display = "none";
  resultsContainer.style.display = "flex";
  resultsContainer.innerHTML = "";
  uploadProgress.style.display = "block";
  progressBar.style.width = "0%";
  progressCount.textContent = `0 / ${totalFiles}`;
  progressText.textContent = "Memproses...";

  const submitBtn = verificationForm.querySelector("button[type='submit']");
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sedang memproses...';

  for (let i = 0; i < totalFiles; i++) {
    const file = files[i];
    progressText.textContent = `Memproses: ${file.name}`;

    const loadingCard = document.createElement("div");
    loadingCard.className = "file-card";
    loadingCard.innerHTML = `
      <div class="file-icon"><i class="fas fa-spinner fa-spin"></i></div>
      <div class="file-info">
        <p class="file-name">${file.name}</p>
        <p style="color: var(--color-primary); font-size: 12px;">Sedang diproses...</p>
      </div>
    `;
    resultsContainer.appendChild(loadingCard);

    try {
      const formData = new FormData();
      formData.append("ijazah", file);

      const response = await fetch("/upload-single/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData,
      });

      const data = await response.json();

      let iconClass = "fas fa-file";
      if (data.is_image) iconClass = "fas fa-file-image";
      else if (data.is_pdf) iconClass = "fas fa-file-pdf";

      loadingCard.innerHTML = `
        <div class="file-icon"><i class="${iconClass}"></i></div>
        <div class="file-info">
          <p class="file-name">${data.nama}</p>
          <p>Tahun: ${data.tahun}</p>
        </div>
        <div class="file-action">
          ${data.file_url ? `<a href="${data.file_url}" target="_blank" class="btn-view"><i class="fas fa-eye"></i> Lihat</a>` : ""}
        </div>
      `;
    } catch (err) {
      loadingCard.innerHTML = `
        <div class="file-icon" style="color: var(--color-error);"><i class="fas fa-times-circle"></i></div>
        <div class="file-info">
          <p class="file-name">${file.name}</p>
          <p style="color: var(--color-error); font-size: 12px;">Gagal memproses file</p>
        </div>
      `;
    }

    completed++;
    const percent = Math.round((completed / totalFiles) * 100);
    progressBar.style.width = percent + "%";
    progressCount.textContent = `${completed} / ${totalFiles}`;
  }

  progressText.textContent = "Selesai!";

  const resetBtn = document.createElement("a");
  resetBtn.className = "btn btn-primary";
  resetBtn.href = "?reset=1";
  resetBtn.innerHTML = '<i class="fas fa-redo"></i> Unggah Lagi';
  resetBtn.style.marginTop = "10px";
  resultsContainer.appendChild(resetBtn);

  submitBtn.disabled = false;
  submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Unggah & Verifikasi';
});