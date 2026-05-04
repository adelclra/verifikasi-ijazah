const fileInput = document.getElementById("ijazah-file");
const previewBox = document.getElementById("selected-file-preview");
const fileList = document.getElementById("file-list");
const verificationForm = document.getElementById("verification-form");

fileInput.addEventListener("change", function () {
  fileList.innerHTML = "";

  if (fileInput.files.length > 0) {
    previewBox.style.display = "block";

    Array.from(fileInput.files).forEach((file) => {
      let icon = "📁";

      if (file.type.startsWith("image/")) {
        icon = "🖼️";
      } else if (file.type === "application/pdf") {
        icon = "📄";
      }

      const div = document.createElement("div");
      div.className = "file-card";

      div.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-info">
          <p class="file-name">${file.name}</p>
        </div>
      `;

      fileList.appendChild(div);
    });
  }
});
