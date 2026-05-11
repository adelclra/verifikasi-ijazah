document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const rows = document.querySelectorAll("table tr");

  function filterTable() {
    const searchValue = searchInput.value.toLowerCase();
    const statusValue = statusFilter.value;

    rows.forEach((row, index) => {
      if (index === 0) return; // skip header

      const text = row.innerText.toLowerCase();
      const status = row.innerText.toUpperCase();

      const matchSearch = text.includes(searchValue);
      const matchStatus =
        !statusValue || status.includes(statusValue);

      row.style.display = matchSearch && matchStatus ? "" : "none";
    });
  }

  searchInput.addEventListener("keyup", filterTable);
  statusFilter.addEventListener("change", filterTable);
});

function openEditModal(id, nama, tahun, status) {

  document.getElementById("editModal").style.display = "flex";

  document.getElementById("edit-nama").value = nama;

  document.getElementById("edit-tahun").value = tahun;
}

function closeEditModal() {
  document.getElementById("editModal").style.display = "none";
}