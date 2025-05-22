document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded");
    
    // Check if dropdown elements exist
    const dropdownButtons = document.querySelectorAll('.icon-button.dropdown-toggle');
    console.log("Found dropdown buttons:", dropdownButtons.length);
    
    // Check for content boxes
    const contentBoxes = document.querySelectorAll('.content-box');
    console.log("Found content boxes:", contentBoxes.length);
    
    // Verify file items
    const fileItems = document.querySelectorAll('.file-item');
    console.log("Found file items:", fileItems.length);
    
    // Set up dropdown toggle functionality
    setupDropdownToggles();
    
    // Handle file/folder delete functionality
    document.querySelectorAll('.delete-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            const fileId = this.getAttribute('data-file-id');
            const folderId = this.getAttribute('data-folder-id');

            if (fileId) {
                if (confirm('Are you sure you want to delete this file?')) {
                    deleteFile(fileId);
                }
            } else if (folderId) {
                if (confirm('Are you sure you want to delete this folder and all its contents?')) {
                    deleteFolder(folderId);
                }
            }
        });
    });

    // Search functionality
    const searchInput = document.getElementById('search-users');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            document.querySelectorAll('.card-container').forEach(function (userCard) {
                const userName = userCard.querySelector('.user-name').textContent.toLowerCase();
                const userEmail = userCard.querySelector('.user-email').textContent.toLowerCase();

                if (userName.includes(searchTerm) || userEmail.includes(searchTerm)) {
                    userCard.style.display = '';
                } else {
                    userCard.style.display = 'none';
                }
            });
        });
    }
    
    // Functions for dropdown handling
    function setupDropdownToggles() {
        // Add click handlers for all dropdown toggles
        document.querySelectorAll('.icon-button.dropdown-toggle').forEach(button => {
            console.log("Adding click event to button:", button);
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleDropdown(this);
            });
        });
        
        // Close all dropdowns when clicking elsewhere
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown-toggle') && !e.target.closest('.content-box')) {
                document.querySelectorAll('.content-box:not(.hidden)').forEach(box => {
                    const container = box.closest('.card-container');
                    if (container) {
                        const button = container.querySelector('.icon-button.dropdown-toggle');
                        if (button) {
                            const icon = button.querySelector('i');
                            if (icon) {
                                icon.className = 'bx bx-caret-down';
                            }
                        }
                        box.classList.add('hidden');
                    }
                });
            }
        });
    }
    
    /**
     * Toggles the dropdown content for file/folder details
     * @param {HTMLElement} button - The dropdown toggle button
     */
    function toggleDropdown(button) {
        console.log("Toggle dropdown called for:", button);
        
        // Find the parent card container
        const container = button.closest('.card-container');
        if (!container) {
            console.error("No card container found");
            return;
        }
        
        // Find the content box to toggle
        const contentBox = container.querySelector('.content-box');
        if (!contentBox) {
            console.error("No content box found");
            return;
        }
        
        // Find the icon element
        const icon = button.querySelector('i');
        
        // Toggle the hidden class and add expanded state
        contentBox.classList.toggle('hidden');
        container.classList.toggle('expanded');
        console.log("Content box visibility:", !contentBox.classList.contains('hidden'));
        
        // Rotate the icon based on dropdown state
        if (icon) {
            if (contentBox.classList.contains('hidden')) {
                icon.className = 'bx bx-caret-down';
            } else {
                icon.className = 'bx bx-caret-up';
            }
        }
        
        // If we're showing the dropdown, scroll it into view
        if (!contentBox.classList.contains('hidden')) {
            setTimeout(() => {
                contentBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    }

    // Functions for delete operations
    function deleteFile(fileId) {
        // Call your API to delete the file
        fetch('/delete-files/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `file_ids[]=${fileId}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the file element from DOM
                    const fileElement = document.querySelector(`[data-file-id="${fileId}"]`).closest('.file-item');
                    fileElement.remove();
                    alert('File deleted successfully');
                } else {
                    alert('Error: ' + data.error);
                }
            });
    }

    function deleteFolder(folderId) {
        // Call your API to delete the folder
        fetch('/delete-folders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `folder_ids[]=${folderId}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the folder element from DOM
                    const folderElement = document.querySelector(`[data-folder-id="${folderId}"]`).closest('.folder-item');
                    folderElement.remove();
                    alert('Folder deleted successfully');
                } else {
                    alert('Error: ' + data.error);
                }
            });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

