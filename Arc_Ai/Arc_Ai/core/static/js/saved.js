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


window.addEventListener('click', function(event) {
    // Handle dropdowns
    if (!event.target.matches('.dropdown-icon')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
    
    // Handle checkboxes and delete button
    if (checkboxesVisible) {
        const deleteToggleButton = document.querySelector('[onclick="toggleCheckboxes()"]');
        const moveToTrashButton = document.getElementById('delete-selected-btn');
        const checkboxes = document.querySelectorAll('.file-checkbox');
        
        // Check if click is on relevant elements
        const isClickOnToggle = deleteToggleButton && deleteToggleButton.contains(event.target);
        const isClickOnCheckbox = Array.from(checkboxes).some(checkbox => checkbox.contains(event.target));
        const isClickOnButton = moveToTrashButton && moveToTrashButton.contains(event.target);
        
        // If click is outside our elements, hide everything
        if (!isClickOnToggle && !isClickOnCheckbox && !isClickOnButton) {
            // Hide checkboxes
            checkboxes.forEach(checkbox => {
                checkbox.style.display = 'none';
            });
            
            // Hide the delete button
            if (moveToTrashButton) {
                moveToTrashButton.style.display = 'none';
            }
            
            checkboxesVisible = false;
        }
    }
});

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
    const deleteButton = document.getElementById('delete-selected-btn');
    
    checkboxesVisible = !checkboxesVisible; // Toggle state
    
    // Show/hide checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.style.display = checkboxesVisible ? 'inline-block' : 'none';
        
        // Add event listeners only when making visible
        if (checkboxesVisible) {
            checkbox.addEventListener('change', updateDeleteButtonVisibility);
        }
    });
    
    // Always hide the button initially when toggling checkboxes
    if (deleteButton) {
        deleteButton.style.display = 'none';
    }
}

// New function to update button visibility
function updateDeleteButtonVisibility() {
    const deleteButton = document.getElementById('delete-selected-btn');
    const checkedBoxes = document.querySelectorAll('.file-checkbox:checked');
    
    if (deleteButton) {
        // Only show button if at least one checkbox is checked
        deleteButton.style.display = checkedBoxes.length > 0 ? 'block' : 'none';
    }
}


let trashCheckboxesVisible = false;

function toggleTrashCheckboxes() {
    const trashFiles = document.querySelectorAll('.trash-file');
    const restoreButton = document.getElementById('restore-selected-btn');
    trashCheckboxesVisible = !trashCheckboxesVisible;

    // Toggle checkboxes visibility
    trashFiles.forEach(file => {
        const checkbox = file.querySelector('.trash-checkbox');
        if (checkbox) {
            checkbox.style.display = trashCheckboxesVisible ? 'inline-block' : 'none';
        }
    });

    // Toggle restore button visibility
    if (restoreButton) {
        restoreButton.style.display = trashCheckboxesVisible ? 'block' : 'none';
    }
}

