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
                    
                    // Check if the user name or email contains the search term
                    if (userName.includes(searchTerm) || userEmail.includes(searchTerm)) {
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
});