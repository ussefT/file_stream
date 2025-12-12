    // 1. VIEW TOGGLE LOGIC
    function setView(viewType) {
        const lists = document.querySelectorAll('.file-list');
        const btnList = document.getElementById('btnList');
        const btnGrid = document.getElementById('btnGrid');

        lists.forEach(list => {
            if (viewType === 'grid') {
                list.classList.add('grid-view');
                btnGrid.classList.add('active');
                btnList.classList.remove('active');
            } else {
                list.classList.remove('grid-view');
                btnList.classList.add('active');
                btnGrid.classList.remove('active');
            }
        });
    }

    // 2. SORTING LOGIC
    function sortItems(criteria) {
        const lists = ['dirList', 'fileList']; // IDs of the ULs

        lists.forEach(listId => {
            const list = document.getElementById(listId);
            const items = Array.from(list.getElementsByClassName('list-item'));

            items.sort((a, b) => {
                if (criteria === 'name') {
                    // Sort by Name (A-Z)
                    const nameA = a.getAttribute('data-name').toLowerCase();
                    const nameB = b.getAttribute('data-name').toLowerCase();
                    return nameA.localeCompare(nameB);
                } else if (criteria === 'date') {
                    // Sort by Date (Newest First) - using data-timestamp
                    const timeA = parseInt(a.getAttribute('data-timestamp'));
                    const timeB = parseInt(b.getAttribute('data-timestamp'));
                    return timeB - timeA;
                }
            });

            // Re-append sorted items
            items.forEach(item => list.appendChild(item));
        });
    }
    const dialog = document.getElementById('fileInfoDialog');

    function openFileDialog(buttonElement) {
        // 1. Find the parent List Item
        const listItem = buttonElement.closest('.list-item');

        // 2. Extract data from data-attributes
        const name = listItem.dataset.name;
        const size = listItem.dataset.size;
        const time = listItem.dataset.time;
        
        // Format Permissions (Read/Write/Execute)
        const r = listItem.dataset.permR === 'True' ? 'Read' : '';
        const w = listItem.dataset.permW === 'True' ? 'Write' : '';
        const e = listItem.dataset.permE === 'True' ? 'Exec' : '';
        const perms = [r, w, e].filter(Boolean).join(', ') || 'None';

        // 3. Inject data into the dialog
        document.getElementById('modal-name').textContent = name;
        document.getElementById('modal-size').textContent = size;
        document.getElementById('modal-time').textContent = time;
        document.getElementById('modal-perm').textContent = perms;

        // 4. Show the dialog
        dialog.showModal();
    }

    function closeFileDialog() {
        dialog.close();
    }

    // Optional: Close dialog if clicking outside the box
    dialog.addEventListener('click', (event) => {
        if (event.target === dialog) {
            dialog.close();
        }
    });