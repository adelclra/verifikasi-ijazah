document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const rows = document.querySelectorAll("table tr");

  function filterTable() {
    if (!searchInput || !statusFilter) return;

    const searchValue = searchInput.value.toLowerCase();
    const statusValue = statusFilter.value;

    rows.forEach((row, index) => {
      if (index === 0) return;

      const text = row.innerText.toLowerCase();
      const status = row.innerText.toUpperCase();

      const matchSearch = text.includes(searchValue);
      const matchStatus = !statusValue || status.includes(statusValue);

      row.style.display = matchSearch && matchStatus ? "" : "none";
    });
  }

  if (searchInput) searchInput.addEventListener("keyup", filterTable);
  if (statusFilter) statusFilter.addEventListener("change", filterTable);
});

function openEditModal(id, nama, tahun) {
  document.getElementById("editModal").style.display = "flex";
  document.getElementById("edit-id").value = id;
  document.getElementById("edit-nama").value = nama;
  document.getElementById("edit-tahun").value = tahun;

  var params = new URLSearchParams(window.location.search);
  document.getElementById("edit-page").value = params.get("page") || "1";
}

function closeEditModal() {
  document.getElementById("editModal").style.display = "none";
}
