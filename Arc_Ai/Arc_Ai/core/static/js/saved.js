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

function toggleDropdownFiles() {
    const dropdown = document.getElementById("myDropdown");
    dropdown.classList.toggle("show");
}

function toggleDropdownFolders() {
    const dropdown = document.getElementById("myDropdownFolders");
    dropdown.classList.toggle("show");
}

function toggleDropdownTrash() {
    document.getElementById("trashDropdown").classList.toggle("show");
}

// Enhanced dropdown closing functionality
document.addEventListener('click', function(event) {
    // Get all dropdown elements
    const fileDropdown = document.getElementById("myDropdown");
    const folderDropdown = document.getElementById("myDropdownFolders");
    const trashDropdown = document.getElementById("trashDropdown");
    
    // Get all dropdown trigger icons
    const dropdownIcons = document.querySelectorAll('.dropdown-icon');
    
    // Check if the click was on any dropdown icon or inside any dropdown
    let clickedOnDropdownArea = false;
    
    // Check if clicked on dropdown icons
    dropdownIcons.forEach(icon => {
        if (icon.contains(event.target)) {
            clickedOnDropdownArea = true;
        }
    });
    
    // Check if clicked inside any dropdown content
    const allDropdowns = [fileDropdown, folderDropdown, trashDropdown].filter(dropdown => dropdown);
    allDropdowns.forEach(dropdown => {
        if (dropdown && dropdown.contains(event.target)) {
            clickedOnDropdownArea = true;
        }
    });
    
    // If clicked outside dropdown area, close all dropdowns
    if (!clickedOnDropdownArea) {
        if (fileDropdown && fileDropdown.classList.contains('show')) {
            fileDropdown.classList.remove('show');
        }
        if (folderDropdown && folderDropdown.classList.contains('show')) {
            folderDropdown.classList.remove('show');
        }
        if (trashDropdown && trashDropdown.classList.contains('show')) {
            trashDropdown.classList.remove('show');
        }
    }
    
    // Handle file options dropdown (three-dot menu)
    if (!event.target.matches('.action-button')) {
        const fileOptionsDropdowns = document.querySelectorAll('.file-options-dropdown');
        fileOptionsDropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    }
    
    // Handle checkboxes and delete button
    if (checkboxesVisible) {
        const deleteToggleButton = document.querySelector('[onclick="toggleCheckboxes()"]');
        const actionButtonsGroup = document.getElementById('action-buttons-group');
        const checkboxes = document.querySelectorAll('.file-checkbox');
        
        // Check if click is on relevant elements
        const isClickOnToggle = deleteToggleButton && deleteToggleButton.contains(event.target);
        const isClickOnCheckbox = Array.from(checkboxes).some(checkbox => checkbox.contains(event.target));
        const isClickOnActionButtons = actionButtonsGroup && actionButtonsGroup.contains(event.target);
        
        // If click is outside our elements, hide everything
        if (!isClickOnToggle && !isClickOnCheckbox && !isClickOnActionButtons) {
            // Hide checkboxes
            checkboxes.forEach(checkbox => {
                checkbox.style.display = 'none';
            });
            
            // Hide the action buttons group
            if (actionButtonsGroup) {
                actionButtonsGroup.style.display = 'none';
            }
            
            checkboxesVisible = false;
        }
    }
});

let checkboxesVisible = false; // Track the visibility state of checkboxes

function toggleCheckboxes() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const actionButtonsGroup = document.getElementById('action-buttons-group');
    
    // Check if checkboxes are currently hidden
    const isHidden = checkboxes.length > 0 && checkboxes[0].style.display === 'none';
    
    // Toggle visibility
    checkboxes.forEach(checkbox => {
        checkbox.style.display = isHidden ? 'inline-block' : 'none';
        checkbox.checked = false; // Uncheck when toggling
    });
    
    // Toggle action buttons group visibility
    actionButtonsGroup.style.display = isHidden ? 'flex' : 'none';
    
    // Update the visibility state
    checkboxesVisible = isHidden;
    
    // Close the dropdown after toggling checkboxes
    const fileDropdown = document.getElementById("myDropdown");
    if (fileDropdown && fileDropdown.classList.contains('show')) {
        fileDropdown.classList.remove('show');
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

// Move these functions from HTML to JS file to avoid conflicts
window.toggleDropdownFiles = toggleDropdownFiles;
window.toggleDropdownFolders = toggleDropdownFolders;
window.toggleCheckboxes = toggleCheckboxes;

