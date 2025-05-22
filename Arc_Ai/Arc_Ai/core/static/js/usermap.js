document.addEventListener('DOMContentLoaded', function() {
    // Select the container for our user map
    const mapContainer = document.getElementById('organization_map');
    if (!mapContainer) {
        console.error('Organization map container not found');
        return;
    }
    
    const containerBounds = document.getElementById('organization_map_container').getBoundingClientRect();
    const width = containerBounds.width;
    const height = containerBounds.height;
    
    // Remove example user bubble if it exists
    const exampleBubble = mapContainer.querySelector('.user_bubble');
    if (exampleBubble) {
        exampleBubble.remove();
    }
    
    // Create level sections
    const levelSections = {
        3: createLevelSection('Level 3 - Administrators', 'level-3-section'),
        2: createLevelSection('Level 2 - Staff', 'level-2-section'),
        1: createLevelSection('Level 1 - Users', 'level-1-section')
    };
    
    // Add sections to the map container in reverse order (3, 2, 1)
    // This puts Level 3 at the top visually
    [3, 2, 1].forEach(level => {
        mapContainer.appendChild(levelSections[level]);
    });
    
    function createLevelSection(title, className) {
        const section = document.createElement('div');
        section.className = `level-section ${className}`;
        
        const sectionTitle = document.createElement('div');
        sectionTitle.className = 'section-title';
        sectionTitle.textContent = title;
        
        const sectionContent = document.createElement('div');
        sectionContent.className = 'section-content';
        
        section.appendChild(sectionTitle);
        section.appendChild(sectionContent);
        return section;
    }
    
    // Fetch user data from server
    fetch('/get_all_users_for_usermap/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            createUserBubbles(data, levelSections, width, height);
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            mapContainer.innerHTML = '<p class="error-message">Failed to load user data. Please try again later.</p>';
        });

    // Function to create user bubbles
    function createUserBubbles(userData, levelSections, width, height) {
        // Try to load saved positions
        let savedPositions = {};
        try {
            const savedData = localStorage.getItem('userMapPositions');
            if (savedData) {
                const positions = JSON.parse(savedData);
                positions.forEach(pos => {
                    savedPositions[pos.userId] = { x: pos.x, y: pos.y };
                });
            }
        } catch (e) {
            console.error('Error loading saved positions:', e);
        }
        
        // Group users by level
        const usersByLevel = {
            1: [],
            2: [],
            3: []
        };
        
        userData.forEach(user => {
            // Determine user level using the same logic as admin_users_page.html
            let level = 1;
            if (user.is_superuser) {
                level = 3;
            } else if (user.is_staff) {
                level = 2;
            }
            user.level = level;
            usersByLevel[level].push(user);
        });
        
        // Track all user elements
        const allUserElements = [];
        
        // Create bubbles for each level
        Object.entries(usersByLevel).forEach(([level, users]) => {
            const levelContent = levelSections[level].querySelector('.section-content');
            const levelWidth = width;
            const levelHeight = height / 3; // Divide height by number of levels
            
            const userElements = users.map((user, index) => {
                // Create user bubble element
                const userBubble = document.createElement('div');
                userBubble.className = 'user_bubble';
                userBubble.setAttribute('draggable', 'true');
                userBubble.dataset.userId = user.id;
                userBubble.dataset.userLevel = level;
                
                // Create avatar
                const avatar = document.createElement('img');
                avatar.className = 'user_avatar';
                avatar.src = '/static/Images/avatar.png';  // Default avatar
                avatar.alt = 'User';
                
                // Create user info
                const userInfo = document.createElement('div');
                userInfo.className = 'user_info';
                
                const userName = document.createElement('span');
                userName.className = 'user_name';
                userName.textContent = `${user.first_name} ${user.last_name}`;
                
                // Create department and position info
                const userDept = document.createElement('span');
                userDept.className = 'user_department';
                userDept.textContent = user.department || 'No Department';
                
                const userPos = document.createElement('span');
                userPos.className = 'user_position';
                userPos.textContent = user.position || 'No Position';
                
                // Create level indicator
                const levelIndicator = document.createElement('div');
                levelIndicator.className = 'level-indicator';
                levelIndicator.textContent = `Level ${level}`;
                
                // Create dropdown placeholder
                const dropdown = document.createElement('div');
                dropdown.className = 'Dropdown';
                
                // Assemble user bubble
                userInfo.appendChild(userName);
                userInfo.appendChild(userDept);
                userInfo.appendChild(userPos);
                
                userBubble.appendChild(avatar);
                userBubble.appendChild(userInfo);
                userBubble.appendChild(levelIndicator);
                userBubble.appendChild(dropdown);
                
                // Set position - use saved position or calculate position within section
                let xPos, yPos;
                
                if (savedPositions[user.id]) {
                    // Use saved position
                    xPos = savedPositions[user.id].x;
                    yPos = savedPositions[user.id].y;
                } else {
                    // Calculate grid position within this level section
                    const columns = Math.ceil(Math.sqrt(users.length * 2));
                    const col = index % columns;
                    const row = Math.floor(index / columns);
                    
                    const cellWidth = levelWidth / (columns + 1);
                    
                    // Calculate section top based on the new visual order (3,2,1)
                    // Level 3 is at index 0, Level 2 at index 1, Level 1 at index 2
                    const sectionIndex = 3 - parseInt(level); // Reverse the order
                    const sectionTop = sectionIndex * (height / 3);
                    
                    xPos = cellWidth * (col + 1);
                    yPos = sectionTop + 70 + (row * 120); // 70px from top of section, 120px spacing between rows
                }
                
                // Ensure within bounds
                xPos = Math.max(50, Math.min(width - 50, xPos));
                
                // Calculate section boundaries based on the new visual order (3,2,1)
                const sectionIndex = 3 - parseInt(level); // Reverse the order
                const sectionTop = sectionIndex * (height / 3);
                const sectionBottom = sectionTop + (height / 3);
                
                yPos = Math.max(sectionTop + 50, Math.min(sectionBottom - 50, yPos));
                
                // Set position (subtract half of bubble size for centering)
                userBubble.style.left = `${xPos - 50}px`;
                userBubble.style.top = `${yPos - 50}px`;
                userBubble.style.position = 'absolute';
                
                // Store position in user data for later use
                user.x = xPos;
                user.y = yPos;
                
                mapContainer.appendChild(userBubble);
                allUserElements.push(userBubble);
                return userBubble;
            });
        });
        
        // Setup simple drag behavior without simulation
        allUserElements.forEach((el) => {
            el.addEventListener('mousedown', function(event) {
                // Prevent text selection during drag
                event.preventDefault();
                
                const userId = el.dataset.userId;
                const userLevel = el.dataset.userLevel;
                const userData = usersByLevel[userLevel].find(u => u.id == userId);
                
                if (!userData) return;
                
                const startX = event.clientX;
                const startY = event.clientY;
                const startLeft = parseInt(el.style.left);
                const startTop = parseInt(el.style.top);
                
                function mousemove(e) {
                    const dx = e.clientX - startX;
                    const dy = e.clientY - startY;
                    
                    const newLeft = startLeft + dx;
                    const newTop = startTop + dy;
                    
                    // Calculate section boundaries based on the new visual order (3,2,1)
                    const sectionIndex = 3 - parseInt(userLevel); // Reverse the order
                    const sectionTop = sectionIndex * (height / 3);
                    const sectionBottom = sectionTop + (height / 3);
                    
                    const constrainedLeft = Math.max(0, Math.min(width - 100, newLeft));
                    const constrainedTop = Math.max(sectionTop, Math.min(sectionBottom - 100, newTop));
                    
                    el.style.left = `${constrainedLeft}px`;
                    el.style.top = `${constrainedTop}px`;
                    
                    // Update user data position (add 50 to get center)
                    userData.x = constrainedLeft + 50;
                    userData.y = constrainedTop + 50;
                }
                
                function mouseup() {
                    document.removeEventListener('mousemove', mousemove);
                    document.removeEventListener('mouseup', mouseup);
                }
                
                document.addEventListener('mousemove', mousemove);
                document.addEventListener('mouseup', mouseup);
            });
        });
        
        // Save map button functionality
        const saveButton = document.getElementById('save_map');
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                const positions = [];
                
                // Collect positions from all levels
                Object.values(usersByLevel).forEach(users => {
                    users.forEach(user => {
                        positions.push({
                            userId: user.id,
                            x: user.x,
                            y: user.y,
                            level: user.level
                        });
                    });
                });
                
                localStorage.setItem('userMapPositions', JSON.stringify(positions));
                
                // Show saved message
                const saveStatus = document.getElementById('save_status');
                if (saveStatus) {
                    saveStatus.classList.remove('hidden');
                    setTimeout(() => {
                        saveStatus.classList.add('hidden');
                    }, 2000);
                }
            });
        }
    }
    
    // Add CSS styles for level sections with colors matching level importance
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            .level-section {
                position: relative;
                width: 100%;
                height: ${height / 3}px;
                border-bottom: 2px dashed #ccc;
            }
            
            .level-section:last-child {
                border-bottom: none;
            }
            
            .level-3-section {
                background-color: rgba(255, 220, 220, 0.2);
            }
            
            .level-2-section {
                background-color: rgba(235, 235, 255, 0.2);
            }
            
            .level-1-section {
                background-color: rgba(220, 255, 220, 0.2);
            }
            
            .section-title {
                position: absolute;
                top: 10px;
                left: 20px;
                font-size: 16px;
                font-weight: bold;
                color: #555;
                background: rgba(255, 255, 255, 0.8);
                padding: 5px 10px;
                border-radius: 5px;
                z-index: 100;
            }
            
            .level-indicator {
                position: absolute;
                top: -15px;
                right: -5px;
                background-color: #4682b4;
                color: white;
                font-size: 8px;
                padding: 2px 5px;
                border-radius: 10px;
            }
            
            .user_department, .user_position {
                display: block;
                font-size: 10px;
                color: #666;
                margin-top: 2px;
            }
            
        </style>
    `);
    
    // Add zoom controls
    const zoomControls = document.createElement('div');
    zoomControls.className = 'zoom-controls';

    const zoomInButton = document.createElement('button');
    zoomInButton.innerHTML = '<i class="bx bx-plus"></i>';
    zoomInButton.title = 'Zoom In';
    zoomInButton.className = 'zoom-button';
    zoomInButton.addEventListener('click', () => zoomMap(0.2));

    const zoomOutButton = document.createElement('button');
    zoomOutButton.innerHTML = '<i class="bx bx-minus"></i>';
    zoomOutButton.title = 'Zoom Out';
    zoomOutButton.className = 'zoom-button';
    zoomOutButton.addEventListener('click', () => zoomMap(-0.2));

    const resetZoomButton = document.createElement('button');
    resetZoomButton.innerHTML = '<i class="bx bx-reset"></i>';
    resetZoomButton.title = 'Reset View';
    resetZoomButton.className = 'zoom-button';
    resetZoomButton.addEventListener('click', () => resetView());

    zoomControls.appendChild(zoomInButton);
    zoomControls.appendChild(zoomOutButton);
    zoomControls.appendChild(resetZoomButton);

    document.getElementById('organization_map_container').appendChild(zoomControls);

    // Current zoom level
    let currentZoom = 1;

    // Zoom map function
    function zoomMap(increment) {
        const bubbles = document.querySelectorAll('.user_bubble');
        currentZoom = Math.max(0.5, Math.min(2, currentZoom + increment));
        
        bubbles.forEach(bubble => {
            const originalSize = 100; // Original bubble size
            const newSize = originalSize * currentZoom;
            
            // Keep the same center position
            const centerX = parseInt(bubble.style.left) + originalSize/2;
            const centerY = parseInt(bubble.style.top) + originalSize/2;
            
            bubble.style.width = `${newSize}px`;
            bubble.style.height = `${newSize}px`;
            bubble.style.left = `${centerX - newSize/2}px`;
            bubble.style.top = `${centerY - newSize/2}px`;
        });
    }

    function resetView() {
        currentZoom = 1;
        // Reset all bubbles to their original positions
        const bubbles = document.querySelectorAll('.user_bubble');
        bubbles.forEach(bubble => {
            const userId = bubble.dataset.userId;
            const userLevel = bubble.dataset.userLevel;
            // Reset sizes
            bubble.style.width = '100px';
            bubble.style.height = '100px';
            // You'd need to re-apply original positions here
        });
    }
});