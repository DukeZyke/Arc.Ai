document.addEventListener('DOMContentLoaded', function() {
    // Get references to search elements
    const searchInput = document.getElementById('search-users');
    const searchButton = document.getElementById('search-button');
    const searchResultsCount = document.querySelector('.search-results-count');
    const searchResultsLabel = searchResultsCount.querySelector('span:first-child');
    const searchResultsValue = document.getElementById('active-users');
    
    // Store the total user count
    const totalUsers = document.querySelectorAll('.user-card').length;
    
    // Set initial counts
    document.getElementById('total-users').textContent = totalUsers;
    
    // Initialize the search results count
    searchResultsValue.textContent = totalUsers;
    
    // Add event listeners for search
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            performSearch();
        }
    });
    
    // Optional: Real-time search as user types (with debounce)
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(performSearch, 300);
    });
    
    // DELETE USER FUNCTIONALITY - MAIN IMPLEMENTATION
    setupDeleteUserButtons();
    
    function setupDeleteUserButtons() {
        console.log('Setting up delete buttons...');
        
        // Add event listeners to all delete buttons
        const deleteButtons = document.querySelectorAll('.delete-btn');
        console.log('Found delete buttons:', deleteButtons.length);
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Delete button clicked');
                
                const userId = this.getAttribute('data-user-id');
                const userCard = this.closest('.user-card');
                const userName = userCard.querySelector('.user-info h3').textContent;
                
                console.log('User ID:', userId, 'User name:', userName);
                
                // Confirm deletion
                if (confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) {
                    deleteUser(userId, userCard);
                }
            });
        });
    }
    
    function deleteUser(userId, userCard) {
        console.log('Deleting user:', userId);
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('CSRF token:', csrfToken ? 'Found' : 'Not found');
        
        // Show loading state
        const deleteBtn = userCard.querySelector('.delete-btn');
        const originalHTML = deleteBtn.innerHTML;
        deleteBtn.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i>';
        deleteBtn.disabled = true;
        
        // Send delete request
        fetch('/delete_user/', {
            method: 'POST',
            body: new URLSearchParams({
                'user_id': userId,
                'csrfmiddlewaretoken': csrfToken
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            
            if (data.success) {
                // Remove user card with animation
                userCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                userCard.style.opacity = '0';
                userCard.style.transform = 'translateX(-100px)';
                
                setTimeout(() => {
                    userCard.remove();
                    updateUserCounts(data.was_active);
                    showMessage(data.message, 'success');
                }, 300);
            } else {
                // Reset button state
                deleteBtn.innerHTML = originalHTML;
                deleteBtn.disabled = false;
                showMessage(data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            // Reset button state
            deleteBtn.innerHTML = originalHTML;
            deleteBtn.disabled = false;
            showMessage('An error occurred while deleting the user.', 'error');
        });
    }
    
    function updateUserCounts(wasActive) {
        // Update total users count
        const totalUsersElement = document.getElementById('total-users');
        const currentTotal = parseInt(totalUsersElement.textContent);
        totalUsersElement.textContent = currentTotal - 1;
        
        // Update active users count if the deleted user was active
        if (wasActive) {
            const activeUsersElement = document.getElementById('active-users');
            const currentActive = parseInt(activeUsersElement.textContent);
            activeUsersElement.textContent = currentActive - 1;
        }
    }
    
    function showMessage(message, type) {
        // Create message popup
        const messagePopup = document.createElement('div');
        messagePopup.className = `message-popup ${type}`;
        messagePopup.innerHTML = `<div class="message-content">${message}</div>`;
        
        // Add to body
        document.body.appendChild(messagePopup);
        
        // Show with animation
        setTimeout(() => {
            messagePopup.classList.add('show');
        }, 100);
        
        // Hide after 3 seconds
        setTimeout(() => {
            messagePopup.classList.remove('show');
            setTimeout(() => {
                if (messagePopup.parentNode) {
                    messagePopup.parentNode.removeChild(messagePopup);
                }
            }, 300);
        }, 3000);
    }
    
    // Function to perform the search
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const userCards = document.querySelectorAll('.user-card');
        let matchCount = 0;
        
        // Add loading indicator
        document.querySelector('.user-admin-header h1').classList.add('searching');
        
        setTimeout(() => {
            userCards.forEach(card => {
                // If search term is empty, show all users
                if (searchTerm === '') {
                    card.style.display = 'flex';
                    matchCount++;
                } else {
                    // Search within user name and email
                    const userName = card.querySelector('.user-info h3').textContent.toLowerCase();
                    const userEmail = card.querySelector('.user-email').textContent.toLowerCase();
                    const department = card.querySelector('.department span').textContent.toLowerCase();
                    const position = card.querySelector('.position span').textContent.toLowerCase();
                    
                    // Check if the user name, email, department, or position contains the search term
                    if (userName.includes(searchTerm) || userEmail.includes(searchTerm) || department.includes(searchTerm) || position.includes(searchTerm)) {
                        card.style.display = 'flex';
                        matchCount++;
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
            
            // Update the search results count and text
            if (searchTerm) {
                searchResultsLabel.textContent = 'Found Users: ';
                updateSearchResultsCount(matchCount);
            } else {
                searchResultsLabel.textContent = 'Active Users: ';
                updateSearchResultsCount(totalUsers);
                // Make sure count matches total when empty search
                matchCount = totalUsers;
            }
            
            // Always keep search results count visible
            searchResultsCount.style.display = 'block';
            
            // Show no results message if needed
            const noResultsMessage = document.getElementById('no-results-message');
            if (matchCount === 0 && searchTerm !== '') {
                if (!noResultsMessage) {
                    const message = document.createElement('div');
                    message.id = 'no-results-message';
                    message.className = 'no-results';
                    message.textContent = `No users found matching "${searchTerm}"`;
                    document.querySelector('.user-list').appendChild(message);
                } else {
                    noResultsMessage.textContent = `No users found matching "${searchTerm}"`;
                    noResultsMessage.style.display = 'block';
                }
            } else if (noResultsMessage) {
                noResultsMessage.style.display = 'none';
            }
            
            // Remove loading indicator
            document.querySelector('.user-admin-header h1').classList.remove('searching');
        }, 200); // Small delay for visual feedback
    }
    
    // Function to update the search results count display
    function updateSearchResultsCount(count) {
        searchResultsValue.textContent = count;
    }
    
    // Clear search function
    function clearSearch() {
        searchInput.value = '';
        performSearch();
        searchInput.focus();
    }
    
    // Add clear button functionality if input has content
    searchInput.addEventListener('input', function() {
        if (this.value) {
            this.classList.add('has-content');
        } else {
            this.classList.remove('has-content');
        }
    });
    
    // Append search field with a clear button
    const clearButton = document.createElement('button');
    clearButton.className = 'clear-search-btn';
    clearButton.innerHTML = '&times;';
    clearButton.addEventListener('click', clearSearch);
    searchInput.parentNode.insertBefore(clearButton, searchInput.nextSibling);
    
    // Add level control functionality
    document.querySelectorAll('.level-control').forEach(control => {
        const levelValue = control.querySelector('.level-value');
        const upBtn = control.querySelector('.level-up');
        const downBtn = control.querySelector('.level-down');
        
        upBtn.addEventListener('click', () => {
            let currentLevel = parseInt(levelValue.textContent);
            if (currentLevel < 5) {
                levelValue.textContent = currentLevel + 1;
            }
        });
        
        downBtn.addEventListener('click', () => {
            let currentLevel = parseInt(levelValue.textContent);
            if (currentLevel > 1) {
                levelValue.textContent = currentLevel - 1;
            }
        });
    });
    
    // Search functionality (if not already implemented)
    function setupSearch() {
        const searchInput = document.getElementById('search-users');
        const searchButton = document.getElementById('search-button');
        
        if (searchInput && searchButton) {
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                const userCards = document.querySelectorAll('.user-card');
                let visibleCount = 0;
                
                userCards.forEach(card => {
                    const userName = card.querySelector('.user-info h3').textContent.toLowerCase();
                    const userEmail = card.querySelector('.user-email').textContent.toLowerCase();
                    const userDepartment = card.querySelector('.department span').textContent.toLowerCase();
                    const userPosition = card.querySelector('.position span').textContent.toLowerCase();
                    
                    const isMatch = userName.includes(searchTerm) || 
                                   userEmail.includes(searchTerm) || 
                                   userDepartment.includes(searchTerm) || 
                                   userPosition.includes(searchTerm);
                    
                    if (isMatch) {
                        card.style.display = 'flex';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // Update search results indicator
                updateSearchResults(visibleCount, searchTerm);
            }
            
            searchInput.addEventListener('input', performSearch);
            searchButton.addEventListener('click', performSearch);
            
            // Enter key support
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
        }
    }
    
    function updateSearchResults(count, searchTerm) {
        const searchIndicator = document.querySelector('.search-indicator');
        if (searchIndicator) {
            if (searchTerm) {
                searchIndicator.textContent = `(${count} results)`;
                searchIndicator.style.display = 'inline';
            } else {
                searchIndicator.style.display = 'none';
            }
        }
    }
    
    // Initialize search when page loads
    document.addEventListener('DOMContentLoaded', setupSearch);
});

// Function to get CSRF token from cookies
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