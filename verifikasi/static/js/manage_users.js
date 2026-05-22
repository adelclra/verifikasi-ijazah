function openAddModal() {
  document.getElementById("addModal").style.display = "flex";
}

function closeAddModal() {
  document.getElementById("addModal").style.display = "none";
}

function openEditModal(id, username, email, role) {
  document.getElementById("editForm").action =
    "/settings/users/edit/" + id + "/";
  document.getElementById("edit-username").value = username;
  document.getElementById("edit-email").value = email;
  document.getElementById("edit-role").value = role;
  document.getElementById("editModal").style.display = "flex";
}

function closeEditModal() {
  document.getElementById("editModal").style.display = "none";
}