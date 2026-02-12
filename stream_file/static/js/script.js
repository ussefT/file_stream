   function classify(mime, ext) {
  mime = (mime || "").toLowerCase();
  ext = (ext || "").toLowerCase();

  if (mime.startsWith("image/")) return "image";
  if (mime.startsWith("video/")) return "video";
  if (mime.startsWith("audio/")) return "audio";
  if (mime === "application/pdf" || ext === "pdf") return "pdf";
  if (mime.startsWith("text/") || ["txt","md","py","js","html","css","json","csv","log"].includes(ext)) return "text";
  if (["zip","rar","7z","tar","gz"].includes(ext)) return "zip";
  return "other";
}

function applyFilters() {
  const q = (document.getElementById("searchInput").value || "").toLowerCase();
  const type = document.getElementById("typeFilter").value;

  document.querySelectorAll(".list-item").forEach(item => {
    const name = (item.getAttribute("data-name") || "").toLowerCase();
    const mime = item.getAttribute("data-mime") || "";
    const ext = item.getAttribute("data-ext") || "";
    const isDir = item.getAttribute("data-type") === "dir";

    const matchesSearch = !q || name.includes(q);
    const matchesType = !type || isDir || classify(mime, ext) === type;

    item.style.display = (matchesSearch && matchesType) ? "" : "none";
  });
}

function openFileDialog() {
  const input = document.getElementById('fileInput');
  if (!input) {
    console.error("fileInput not found");
    return;
  }
  input.click();
}

async function handleFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const container = document.getElementById('uploadContainer');
  const fill = document.getElementById('progressFill');
  const text = document.getElementById('uploadText');

  if (container && fill && text) {
    container.style.display = 'block';
    fill.style.width = '0%';
    text.innerText = 'Uploading... 0%';
  }

  const currentPath = ((document.body.dataset.currentPath || "").trim() || ".");

  const formData = new FormData();
  formData.set('file', file);
  formData.set('path', currentPath);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/uploadFile', true);

  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable && fill && text) {
      const percent = Math.round((e.loaded / e.total) * 100);
      fill.style.width = percent + '%';
      text.innerText = `Uploading... ${percent}%`;
    }
  };

  xhr.onload = () => {
    if (xhr.status === 200 || xhr.status === 201) {
      if (fill && text) {
        fill.style.width = '100%';
        text.innerText = 'Upload successful!';
      }

      // ✅ refresh the page after a short delay
      setTimeout(() => {
        if (container) container.style.display = 'none';
        window.location.reload(); // or: window.location.href = window.location.href;
      }, 800);

    } else {
      let msg = xhr.responseText;
      try {
        const j = JSON.parse(xhr.responseText);
        msg = j.detail || msg;
      } catch (e) {}
      if (text) text.innerText = `Upload failed (${xhr.status}): ${msg}`;
      console.error('Upload error:', xhr.status, xhr.responseText);
    }
  };

  xhr.onerror = () => {
    if (text) text.innerText = 'Upload failed (network error)';
    console.error('Upload error: network error');
  };

  xhr.send(formData);

  // allow selecting same file again
  event.target.value = '';
}

function sortItems(criteria) {
  const lists = ['dirList', 'fileList'];

  lists.forEach(listId => {
    const list = document.getElementById(listId);
    if (!list) return; // ✅ guard

    const items = Array.from(list.getElementsByClassName('list-item'));

    items.sort((a, b) => {
      if (criteria === 'name') {
        const nameA = (a.getAttribute('data-name') || "").toLowerCase();
        const nameB = (b.getAttribute('data-name') || "").toLowerCase();
        return nameA.localeCompare(nameB);
      } else if (criteria === 'date') {
        const timeA = Number(a.getAttribute('data-timestamp')) || 0;
        const timeB = Number(b.getAttribute('data-timestamp')) || 0;
        return timeB - timeA; // newest first
      }
    });

    items.forEach(item => list.appendChild(item));
  });
}