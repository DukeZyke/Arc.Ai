const folderItems = document.querySelector('#folder_items'); // Select the folder items container

let isDown = false;
let startX;
let scrollLeft;

folderItems.addEventListener('mousedown', (e) => {
  isDown = true;
  folderItems.classList.add('active');
  startX = e.pageX - folderItems.offsetLeft;
  scrollLeft = folderItems.scrollLeft;
  document.body.style.userSelect = 'none'; // Disable text selection
});

folderItems.addEventListener('mouseleave', () => {
  isDown = false;
  folderItems.classList.remove('active');
  document.body.style.userSelect = ''; // Re-enable text selection
});

folderItems.addEventListener('mouseup', () => {
  isDown = false;
  folderItems.classList.remove('active');
  document.body.style.userSelect = ''; // Re-enable text selection
});

folderItems.addEventListener('mousemove', (e) => {
  if (!isDown) return; // Exit if the mouse is not pressed
  e.preventDefault();
  const x = e.pageX - folderItems.offsetLeft;
  const walk = (x - startX) * 1; // Adjust scroll speed (1 is default)
  folderItems.scrollLeft = scrollLeft - walk; // Scroll horizontally
});

function toggleDropdownTrash() {
    document.getElementById("trashDropdown").classList.toggle("show");
}

window.onclick = function(event) {
    // Check if click was NOT on the image
    if (!event.target.classList.contains('dropdown-icon')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

function toggleDropdownFolders(event) {
    const dropdown = document.getElementById("myDropdownFolders");
    dropdown.classList.toggle("show");

    // Prevent the dropdown from closing when clicking inside the dropdown
    dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}


let checkboxesVisible = false; // Track the visibility state of checkboxes

    function toggleCheckboxes() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const deleteButton = document.getElementById('delete-selected-btn'); // Keep the same ID for simplicity
    checkboxesVisible = !checkboxesVisible; // Toggle the visibility state

    // Show or hide checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.style.display = checkboxesVisible ? 'inline-block' : 'none';
    });

    // Show or hide the move to trash button (still using delete-selected-btn ID)
    if (deleteButton) {
        deleteButton.style.display = checkboxesVisible ? 'block' : 'none';
    }

    // Add or remove the event listener for hiding checkboxes
    if (checkboxesVisible) {
        window.addEventListener('click', hideCheckboxesOnClickOutside);
    } else {
        window.removeEventListener('click', hideCheckboxesOnClickOutside);
    }
}

    function hideCheckboxesOnClickOutside(event) {
    const deleteButton = document.querySelector('[onclick="toggleCheckboxes()"]');
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const deleteForm = document.getElementById('delete-files-form');
    const isClickOnCheckbox = Array.from(checkboxes).some(checkbox => checkbox.contains(event.target));

    if (!deleteButton.contains(event.target) && !isClickOnCheckbox) {
        // Hide checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.style.display = 'none';
        });

        // Hide the delete button
        if (deleteForm) {
            deleteForm.style.display = 'none';
        }

        checkboxesVisible = false; // Reset visibility state
        window.removeEventListener('click', hideCheckboxesOnClickOutside); // Remove the event listener
    }
}

