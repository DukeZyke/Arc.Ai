document.addEventListener('DOMContentLoaded', function() {
    // Get references to search elements
    const searchInput = document.getElementById('search-projects');
    const searchButton = document.getElementById('search-button');
    const searchResultsCount = document.querySelector('.search-results-count');
    const searchResultsLabel = searchResultsCount.querySelector('span:first-child');
    const searchResultsValue = document.getElementById('search-count');
    
    // Store the total project count
    const totalProjects = document.querySelectorAll('.project-card').length;
    
    // Set initial counts
    document.querySelector('.project-count strong').textContent = totalProjects;
    
    // Initialize the search results count
    searchResultsValue.textContent = totalProjects;
    
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
        const projectCards = document.querySelectorAll('.project-card');
        let matchCount = 0;
        
        // Add loading indicator
        document.querySelector('.project-management-header h1').classList.add('searching');
        
        setTimeout(() => {
            projectCards.forEach(card => {
                // Only search within project titles (h3)
                const projectTitle = card.querySelector('.project-info h3').textContent.toLowerCase();
                
                // Check if the project title contains the search term
                if (projectTitle.includes(searchTerm)) {
                    card.style.display = 'flex';
                    matchCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update the search results count and text
            if (searchTerm) {
                searchResultsLabel.textContent = 'Search Results: ';
                updateSearchResultsCount(matchCount);
                searchResultsCount.style.display = 'block';
            } else {
                searchResultsLabel.textContent = 'All Projects: ';
                updateSearchResultsCount(totalProjects);
                searchResultsCount.style.display = 'block';
            }
            
            // Show or hide search results count based on whether there's a search term
            if (searchTerm) {
                searchResultsCount.style.display = 'block';
            } else {
                searchResultsCount.style.display = 'none';
            }
            
            // Show no results message if needed
            const noResultsMessage = document.getElementById('no-results-message');
            if (matchCount === 0 && searchTerm !== '') {
                if (!noResultsMessage) {
                    const message = document.createElement('div');
                    message.id = 'no-results-message';
                    message.className = 'no-results';
                    message.textContent = `No projects found with title matching "${searchTerm}"`;
                    document.querySelector('.project-list').appendChild(message);
                } else {
                    noResultsMessage.textContent = `No projects found with title matching "${searchTerm}"`;
                    noResultsMessage.style.display = 'block';
                }
            } else if (noResultsMessage) {
                noResultsMessage.style.display = 'none';
            }
            
            // Remove loading indicator
            document.querySelector('.project-management-header h1').classList.remove('searching');
        }, 200); // Small delay for visual feedback
    }
    
    // Function to update the search results count display
    function updateSearchResultsCount(count) {
        if (searchResultsValue) {
            searchResultsValue.textContent = count;
        } else {
            console.warn('Search results count element not found in the DOM');
        }
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
});
