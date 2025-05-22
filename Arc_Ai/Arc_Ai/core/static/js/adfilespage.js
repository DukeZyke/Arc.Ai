document.addEventListener('DOMContentLoaded', function () {
    // Add console logs to debug
    console.log("DOM fully loaded");
    
    // Make all dropdown toggles work with better selector
    const toggleButtons = document.querySelectorAll('.icon-button.dropdown-toggle, .dropdown-toggle');
    console.log("Found toggle buttons:", toggleButtons.length);
    
    toggleButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            console.log("Button clicked");
            e.preventDefault();
            const cardContainer = this.closest('.card-container');
            if (!cardContainer) {
                console.error("No card container found for this button");
                return;
            }
            
            const contentBox = cardContainer.querySelector('.content-box');
            if (!contentBox) {
                console.error("No content box found in this card container");
                return;
            }
            
            console.log("Content box found:", contentBox);
            contentBox.classList.toggle('hidden');
        });
    });

    // Add event delegation for dynamically added toggle buttons
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // Check if clicked element or its parent is a dropdown toggle button
        const toggleButton = target.closest('.dropdown-toggle');
        
        if (toggleButton) {
            console.log("Delegation: toggle button clicked");
            event.preventDefault();
            const cardContainer = toggleButton.closest('.card-container');
            const contentBox = cardContainer.querySelector('.content-box');
            contentBox.classList.toggle('hidden');
        }
    });

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

    /**
     * Toggles the dropdown content for file/folder details
     * @param {HTMLElement} button - The dropdown toggle button
     */
    function toggleDropdown(button) {
        // Find the parent card container
        const container = button.closest('.card-container');
        if (!container) return;
        
        // Find the content box to toggle
        const contentBox = container.querySelector('.content-box');
        if (!contentBox) return;
        
        // Find the icon element
        const icon = button.querySelector('i');
        
        // Toggle the hidden class
        contentBox.classList.toggle('hidden');
        
        // Rotate the icon based on dropdown state
        if (contentBox.classList.contains('hidden')) {
            icon.className = 'bx bx-caret-down';
        } else {
            icon.className = 'bx bx-caret-up';
        }
        
        // Log for debugging
        console.log('Dropdown toggled');
    }

    // Add event listeners when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Add click handlers for all dropdown toggles
        document.querySelectorAll('.icon-button.dropdown-toggle').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleDropdown(this);
            });
        });
        
        // Close all dropdowns when clicking elsewhere on the page
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.card-container')) {
                document.querySelectorAll('.content-box:not(.hidden)').forEach(box => {
                    const container = box.closest('.card-container');
                    const button = container.querySelector('.icon-button.dropdown-toggle');
                    const icon = button.querySelector('i');
                    
                    box.classList.add('hidden');
                    icon.className = 'bx bx-caret-down';
                });
            }
        });
    });

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