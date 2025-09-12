document.getElementById('editImageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
      const imgPreview = document.getElementById('profileImagePreview');
      imgPreview.src = URL.createObjectURL(file);
      imgPreview.onload = function() {
        URL.revokeObjectURL(imgPreview.src);
      }
    }
  });

  function openPopup(imgPath, title, description, id) {
  var modal = document.getElementById("imageModal");
  var popupImg = document.getElementById("popupImage");
  var captionText = document.getElementById("caption");
  var deleteBtn = document.getElementById("deleteBtn");

  modal.style.display = "block";
  popupImg.src = imgPath;
  captionText.innerHTML = "<b>" + title + "</b><br>" + description;
  deleteBtn.href = `/delete/${id}`;
}
function closePopup() {
  document.getElementById("imageModal").style.display = "none";
}

window.onclick = function(event) {
  const uploadModal = document.getElementById('uploadModal');
  const editUserModal = document.getElementById('editUserModal');
  const imageModal = document.getElementById('imageModal');

  if (event.target == uploadModal) uploadModal.style.display = "none";
  if (event.target == editUserModal) editUserModal.style.display = "none";
  if (event.target == imageModal) imageModal.style.display = "none";
}

document.getElementById('file').onchange = function() {
  document.getElementById('file-name').textContent = this.files[0]?.name || "No file chosen";
}

const themeToggle = document.getElementById("themeToggle");
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("light");
  localStorage.setItem("theme", document.body.classList.contains("light") ? "light" : "dark");
});

if (localStorage.getItem("theme") === "light") {
  document.body.classList.add("light");
}
