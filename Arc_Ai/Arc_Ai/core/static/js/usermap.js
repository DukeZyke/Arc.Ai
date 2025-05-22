document.addEventListener('DOMContentLoaded', function() {
    // Fetch users from the API
    fetch('/api/users-for-map/')
        .then(response => response.json())
        .then(data => {
            // Use the fetched users data
            initializeUserMap(data);
        })
        .catch(error => {
            console.error('Error fetching users:', error);
            // Use sample data as fallback
            initializeUserMap([
                { name: 'Aristique, Ginno D.', position: { x: 100, y: 100 }, level: 3, files: [
                    { name: 'Project Proposal.docx', type: 'D', size: '245 KB', date: '2 days ago' },
                    { name: 'Budget.xlsx', type: 'X', size: '120 KB', date: '3 days ago' }
                ] },
                { name: 'Santos, Maria L.', position: { x: 300, y: 150 }, level: 2, files: [
                    { name: 'Meeting Notes.pdf', type: 'P', size: '1.2 MB', date: '1 day ago' }
                ] },
                { name: 'Reyes, Juan C.', position: { x: 500, y: 100 }, level: 1, files: [] },
                { name: 'Cruz, Ana B.', position: { x: 700, y: 150 }, level: 2, files: [
                    { name: 'Analysis Report.pptx', type: 'P', size: '3.4 MB', date: 'Today' }
                ] },
                { name: 'Lim, Robert M.', position: { x: 100, y: 300 }, level: 1, files: [] },
                { name: 'Garcia, Elena P.', position: { x: 300, y: 350 }, level: 1, files: [] },
                { name: 'Tan, David K.', position: { x: 500, y: 300 }, level: 2, files: [
                    { name: 'Code Review.txt', type: 'T', size: '45 KB', date: 'Yesterday' }
                ] },
                { name: 'Mendoza, Patricia Q.', position: { x: 700, y: 350 }, level: 3, files: [
                    { name: 'Strategic Plan.docx', type: 'D', size: '380 KB', date: '5 days ago' },
                    { name: 'Team Roster.xlsx', type: 'X', size: '85 KB', date: '1 week ago' }
                ] },
                { name: 'Bautista, Ramon F.', position: { x: 100, y: 500 }, level: 1, files: [] },
                { name: 'Villanueva, Sofia J.', position: { x: 300, y: 550 }, level: 2, files: [
                    { name: 'Client Feedback.pdf', type: 'P', size: '520 KB', date: '3 days ago' }
                ] },
                { name: 'Aquino, Benjamin L.', position: { x: 500, y: 500 }, level: 1, files: [] }
            ]);
        });
    
        function initializeUserMap(users) {
            // Sample connections data
            let connections = [];

            const organizationMap = document.getElementById('organization_map');
            const arrowsContainer = document.getElementById('arrows_container');
            
            // Clear any existing content in the map
            organizationMap.innerHTML = '';
            arrowsContainer.innerHTML = '';
            
            // Create user bubbles and add them to the map
            users.forEach((user, index) => {
        const userBubble = document.createElement('div');
        userBubble.className = 'user_bubble';
        if (user.level) {
            userBubble.classList.add(`level-${user.level}`);
        }
        userBubble.setAttribute('data-user-id', index);
        
        // Position the bubble
        userBubble.style.left = `${user.position.x}px`;
        userBubble.style.top = `${user.position.y}px`;
        
        // Get real file data for this user
        const recentFiles = user.files || [];
        
        // Create files list HTML
        const filesHTML = recentFiles.length > 0 ? 
            recentFiles.map(file => `
                <div class="file_item">
                    <div class="file_icon">${file.type || 'F'}</div>
                    <div class="file_name">${file.name}</div>
                    <div class="file_size">${file.size}</div>
                    <div class="file_date">${file.date}</div>
                </div>
            `).join('') : 
            '<div class="file_item no_files">No files found</div>';
        
        // Calculate number of files
        const fileCount = recentFiles.length;
        
        // Get user level text
        let userLevelText = '';
        if (user.level === 3) {
            userLevelText = '<span class="user_level">Administrator</span>';
        } else if (user.level === 2) {
            userLevelText = '<span class="user_level">Staff</span>';
        } else if (user.level === 1) {
            userLevelText = '<span class="user_level">User</span>';
        }
        
        // Construct user bubble HTML
        userBubble.innerHTML = `
            <img src="/static/Images/avatar.png" alt="User" class="user_avatar">
            <div class="user_info">
                <span class="user_name">${user.name}</span>
                ${userLevelText}
                <span class="file_count">${fileCount} files</span>
            </div>
            <div class="toggle_dropdown">
                <img src="/static/Images/chevron-down.png" alt="Toggle">
            </div>
            <div class="files_dropdown">
                <div class="files_header">Recent Files</div>
                ${filesHTML}
            </div>
        `;
        
        organizationMap.appendChild(userBubble);
        
        // Set up dropdown toggle functionality
        setupDropdown(userBubble);
        
        // Set up drag functionality
        makeDraggable(userBubble);
    });
        
        // Setup dropdown toggle functionality
        function setupDropdown(bubble) {
            const toggleBtn = bubble.querySelector('.toggle_dropdown');
            
            toggleBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation(); // Prevent bubble dragging
                
                // Close other open dropdowns
                document.querySelectorAll('.user_bubble.expanded').forEach(b => {
                    if (b !== bubble) {
                        b.classList.remove('expanded');
                    }
                });
                
                // Toggle dropdown for this bubble
                bubble.classList.toggle('expanded');
                
                // Update connections when dropdown is toggled to ensure proper positioning
                setTimeout(() => {
                    updateAllConnections();
                }, 50);
            });
        }
        
        // Original makeDraggable function will be modified later
        
        // Arrow creation and management functionality
        const createArrowBtn = document.getElementById('create_arrow_btn');
        const arrowProperties = document.getElementById('arrow_properties');
        const arrowDirectionSelect = document.getElementById('arrow_direction');
        const deleteArrowBtn = document.getElementById('delete_arrow_btn');

        let connectionMode = false;
        let selectedBubbles = [];
        let selectedConnection = null;

        // Initialize connection creation mode
        createArrowBtn.addEventListener('click', function() {
            if (connectionMode) {
                // Exit connection mode
                exitConnectionMode();
            } else {
                // Enter connection mode
                enterConnectionMode();
            }
        });

        function enterConnectionMode() {
            connectionMode = true;
            createArrowBtn.textContent = 'Cancel';
            createArrowBtn.style.backgroundColor = '#d32f2f';
            document.body.classList.add('connection-mode');
            
            // Clear any selected bubbles
            selectedBubbles.forEach(bubble => {
                bubble.classList.remove('selected');
            });
            selectedBubbles = [];
            
            // Hide arrow properties panel
            arrowProperties.classList.add('hidden');
        }

        function exitConnectionMode() {
            connectionMode = false;
            createArrowBtn.textContent = 'Connect Users';
            createArrowBtn.style.backgroundColor = '#353A56';
            document.body.classList.remove('connection-mode');
            
            // Clear any selected bubbles
            selectedBubbles.forEach(bubble => {
                bubble.classList.remove('selected');
            });
            selectedBubbles = [];
        }

        // Handle user bubble selection for connections
        organizationMap.addEventListener('click', function(e) {
            let target = e.target;
            
            // Find the bubble element (might be clicking on child elements)
            while (target && !target.classList.contains('user_bubble')) {
                if (target === organizationMap) {
                    target = null;
                    break;
                }
                target = target.parentElement;
            }
            
            if (target) {
                const userBubble = target;
                
                if (connectionMode) {
                    // In connection mode, handle selection for creating connections
                    if (selectedBubbles.includes(userBubble)) {
                        // Deselect if already selected
                        userBubble.classList.remove('selected');
                        selectedBubbles = selectedBubbles.filter(bubble => bubble !== userBubble);
                    } else {
                        // Add to selection
                        userBubble.classList.add('selected');
                        selectedBubbles.push(userBubble);
                        
                        // If we have two bubbles selected, create a connection
                        if (selectedBubbles.length === 2) {
                            createConnection(selectedBubbles[0], selectedBubbles[1]);
                            exitConnectionMode();
                        }
                    }
                } else if (!isDragging) {
                    // When not in connection mode and not dragging, deselect everything first
                    document.querySelectorAll('.user_bubble.selected').forEach(bubble => {
                        if (bubble !== userBubble) {
                            bubble.classList.remove('selected');
                        }
                    });
                    
                    document.querySelectorAll('.connection-path.selected, .connection-arrow.selected').forEach(elem => {
                        elem.classList.remove('selected');
                    });
                    
                    selectedConnection = null;
                    arrowProperties.classList.add('hidden');
                }
            }
        });

        // Handle arrow selection
        arrowsContainer.addEventListener('click', function(e) {
            if (!connectionMode && (e.target.classList.contains('connection-path') || e.target.classList.contains('connection-arrow'))) {
                e.stopPropagation();
                
                // Find the connection ID
                const connectionId = e.target.getAttribute('data-connection-id');
                
                // Deselect all connections first
                document.querySelectorAll('.connection-path.selected, .connection-arrow.selected').forEach(elem => {
                    elem.classList.remove('selected');
                });
                
                // Select this connection
                document.querySelectorAll(`.connection-path[data-connection-id="${connectionId}"], .connection-arrow[data-connection-id="${connectionId}"]`).forEach(elem => {
                    elem.classList.add('selected');
                });
                
                // Set as selected connection
                selectedConnection = connections.find(conn => conn.id === connectionId);
                
                // Update properties panel
                updateArrowPropertiesPanel();
            }
        });

        // Update arrow properties when selection changes
        function updateArrowPropertiesPanel() {
            if (selectedConnection) {
                arrowDirectionSelect.value = selectedConnection.direction;
                arrowProperties.classList.remove('hidden');
            } else {
                arrowProperties.classList.add('hidden');
            }
        }

        // Handle arrow property changes
        arrowDirectionSelect.addEventListener('change', function() {
            if (selectedConnection) {
                selectedConnection.direction = this.value;
                updateConnectionVisual(selectedConnection);
            }
        });

        // Delete connection
        deleteArrowBtn.addEventListener('click', function() {
            if (selectedConnection) {
                // Remove connection elements
                document.querySelectorAll(`.connection-path[data-connection-id="${selectedConnection.id}"], .connection-arrow[data-connection-id="${selectedConnection.id}"], marker[id^="arrow-"][id$="-${selectedConnection.id}"]`).forEach(elem => {
                    elem.remove();
                });
                
                // Remove from connections array
                connections = connections.filter(conn => conn.id !== selectedConnection.id);
                
                // Clear selection
                selectedConnection = null;
                arrowProperties.classList.add('hidden');
            }
        });

        // Create a connection between two user bubbles
        function createConnection(sourceBubble, targetBubble) {
            const connectionId = `conn_${Date.now()}`;
            const sourceId = parseInt(sourceBubble.getAttribute('data-user-id'));
            const targetId = parseInt(targetBubble.getAttribute('data-user-id'));
            
            // Create connection object
            const connection = {
                id: connectionId,
                sourceId: sourceId,
                targetId: targetId,
                direction: 'forward', // Default
                weight: 2, // Fixed value (no longer user-configurable)
                curve: 0 // Fixed value (no longer user-configurable)
            };
            
            connections.push(connection);
            
            // Create visual connection
            createConnectionVisual(connection);
            
            // Set as selected connection
            selectedConnection = connection;
            updateArrowPropertiesPanel();
        }

        // Create arrow markers for SVG
        function createArrowMarker(connection) {
            const markersGroup = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            
            // Fixed size markers that will work with zooming
            const markerWidth = 15;
            const markerHeight = 15;
            
            // Forward arrow with fixed positioning
            const markerEnd = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
            markerEnd.setAttribute('id', `arrow-end-${connection.id}`);
            markerEnd.setAttribute('viewBox', '0 0 10 10');
            markerEnd.setAttribute('refX', '8'); // Increased to prevent overlap with bubble edge
            markerEnd.setAttribute('refY', '5');
            markerEnd.setAttribute('markerUnits', 'userSpaceOnUse');
            markerEnd.setAttribute('markerWidth', markerWidth);
            markerEnd.setAttribute('markerHeight', markerHeight);
            markerEnd.setAttribute('orient', 'auto-start-reverse');
            markerEnd.setAttribute('stroke-width', '1');
            
            const endPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            endPath.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
            endPath.setAttribute('class', 'connection-arrow');
            endPath.setAttribute('data-connection-id', connection.id);
            markerEnd.appendChild(endPath);
            
            // Backward arrow with fixed positioning
            const markerStart = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
            markerStart.setAttribute('id', `arrow-start-${connection.id}`);
            markerStart.setAttribute('viewBox', '0 0 10 10');
            markerStart.setAttribute('refX', '2');
            markerStart.setAttribute('refY', '5');
            markerStart.setAttribute('markerUnits', 'userSpaceOnUse'); // This is crucial for consistent positioning during zoom
            markerStart.setAttribute('markerWidth', markerWidth);
            markerStart.setAttribute('markerHeight', markerHeight);
            markerStart.setAttribute('orient', 'auto');
            markerStart.setAttribute('stroke-width', '1'); // Fixed stroke width
            
            const startPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            startPath.setAttribute('d', 'M 10 0 L 0 5 L 10 10 z');
            startPath.setAttribute('class', 'connection-arrow');
            startPath.setAttribute('data-connection-id', connection.id);
            markerStart.appendChild(startPath);
            
            markersGroup.appendChild(markerEnd);
            markersGroup.appendChild(markerStart);
            
            return markersGroup;
        }

        // Create visual elements for a connection
        function createConnectionVisual(connection) {
            const sourceBubble = document.querySelector(`.user_bubble[data-user-id="${connection.sourceId}"]`);
            const targetBubble = document.querySelector(`.user_bubble[data-user-id="${connection.targetId}"]`);
            
            if (!sourceBubble || !targetBubble) return;
            
            // Calculate connection points
            const points = calculateEdgeConnectionPoints(sourceBubble, targetBubble);
            
            // Create SVG path for the connection line with curve
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            
            // Set path attributes
            path.setAttribute('class', 'connection-path');
            path.setAttribute('data-connection-id', connection.id);
            path.setAttribute('vector-effect', 'non-scaling-stroke'); // Important for consistent stroke width
            path.style.strokeWidth = connection.weight;
            
            // Add pointer-events to make the path clickable
            path.style.pointerEvents = 'stroke';
            
            // Calculate curve control point if needed
            updatePathWithCurve(path, points, connection.curve);
            
            // Create arrowhead(s)
            const arrowMarker = createArrowMarker(connection);
            
            // Apply direction
            if (connection.direction === 'forward' || connection.direction === 'both') {
                path.setAttribute('marker-end', `url(#arrow-end-${connection.id})`);
            }
            
            if (connection.direction === 'backward' || connection.direction === 'both') {
                path.setAttribute('marker-start', `url(#arrow-start-${connection.id})`);
            }
            
            // Add to SVG
            arrowsContainer.appendChild(arrowMarker);
            arrowsContainer.appendChild(path);
        }

        // Update visual representation of a connection
        function updateConnectionVisual(connection) {
            // Remove existing connection visuals
            document.querySelectorAll(`.connection-path[data-connection-id="${connection.id}"], marker[id^="arrow-"][id$="-${connection.id}"]`).forEach(elem => {
                elem.remove();
            });
            
            // Recreate connection visuals
            createConnectionVisual(connection);
        }

        // Update path with curve (simplified - uses fixed curve value)
        function updatePathWithCurve(path, points, curveAmount) {
            const { x1, y1, x2, y2 } = points;
            
            // Always use straight line since curve control is removed
            path.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y2}`);
        }

        // Calculate connection points at the edges of bubbles
        function calculateEdgeConnectionPoints(sourceBubble, targetBubble) {
            // Get bubble positions from their actual style properties
            const sourceLeft = parseFloat(sourceBubble.style.left);
            const sourceTop = parseFloat(sourceBubble.style.top);
            const targetLeft = parseFloat(targetBubble.style.left);
            const targetTop = parseFloat(targetBubble.style.top);
            
            // Use getBoundingClientRect for dimensions
            const sourceRect = sourceBubble.getBoundingClientRect();
            const targetRect = targetBubble.getBoundingClientRect();
            
            // Calculate bubble dimensions adjusted for zoom
            const sourceWidth = 280; // Updated width from CSS
            const sourceHeight = sourceRect.height / currentZoom;
            const targetWidth = 280; // Updated width from CSS
            const targetHeight = targetRect.height / currentZoom;
            
            // Center points using direct position values
            const sourceX = sourceLeft + sourceWidth / 2;
            const sourceY = sourceTop + sourceHeight / 2;
            const targetX = targetLeft + targetWidth / 2;
            const targetY = targetTop + targetHeight / 2;
            
            // Get the angle between bubbles
            const angle = Math.atan2(targetY - sourceY, targetX - sourceX);
            
            // Calculate edge points - improved for consistent edge connection
            let x1, y1, x2, y2;
            
            // Handle source bubble edge point with updated width
            if (Math.abs(Math.cos(angle)) * sourceHeight > Math.abs(Math.sin(angle)) * sourceWidth) {
                // Intersect with left/right edge
                const sign = Math.cos(angle) >= 0 ? 1 : -1;
                
                // Adjust offset for dropdown icon on right side (approx. 30px)set)
                const offsetX = sign > 0 ? 1 : 0; // Add offset on right edge for dropdown icon offset
                x1 = sourceX + sign * (sourceWidth / 2 - offsetX);
                y1 = sourceY + Math.tan(angle) * sign * (sourceWidth / 2 - offsetX);
            } else {
                // Intersect with top/bottom edge
                const sign = Math.sin(angle) >= 0 ? 1 : -1;
                y1 = sourceY + sign * (sourceHeight / 2);
                x1 = sourceX + (Math.abs(Math.tan(angle)) < 0.001 ? 0 : 1 / Math.tan(angle)) * sign * (sourceHeight / 2);
            }
            
            // Handle target bubble edge point with updated width
            const reverseAngle = Math.atan2(sourceY - targetY, sourceX - targetX);
            if (Math.abs(Math.cos(reverseAngle)) * targetHeight > Math.abs(Math.sin(reverseAngle)) * targetWidth) {
                // Intersect with left/right edge
                const sign = Math.cos(reverseAngle) >= 0 ? 1 : -1;
                
                // Adjust offset for dropdown icon on right side (approx. 30px)set)
                const offsetX = sign > 0 ? 1 : 0; // Add offset on right edge for dropdown icon offset
                x2 = targetX + sign * (targetWidth / 2 - offsetX);
                y2 = targetY + Math.tan(reverseAngle) * sign * (targetWidth / 2 - offsetX);
            } else {
                // Intersect with top/bottom edge
                const sign = Math.sin(reverseAngle) >= 0 ? 1 : -1;
                y2 = targetY + sign * (targetHeight / 2);
                x2 = targetX + (Math.abs(Math.tan(reverseAngle)) < 0.001 ? 0 : 1 / Math.tan(reverseAngle)) * sign * (targetHeight / 2);
            }
            
            return { x1, y1, x2, y2 };
        }

        // Update all connections when bubbles are moved
        function updateAllConnections() {
            connections.forEach(connection => {
                updateConnectionVisual(connection);
            });
        }
        
        // Update makeDraggable function to update connections when bubbles are moved
        function makeDraggable(element) {
            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            let isDragging = false;
            
            element.onmousedown = dragMouseDown;
            
            function dragMouseDown(e) {
                // Don't start dragging if clicking on dropdown toggle or content
                if (e.target.closest('.toggle_dropdown') || 
                    e.target.closest('.files_dropdown') ||
                    connectionMode) {
                    return;
                }
                
                e = e || window.event;
                e.preventDefault();
                // Get the mouse cursor position at startup
                pos3 = e.clientX;
                pos4 = e.clientY;
                
                element.classList.add('dragging');
                isDragging = true;
                
                document.onmouseup = closeDragElement;
                // Call a function whenever the cursor moves
                document.onmousemove = elementDrag;
            }
            
            function elementDrag(e) {
                e = e || window.event;
                e.preventDefault();
                
                // Calculate the new cursor position
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                
                // Set the element's new position
                element.style.top = (element.offsetTop - pos2) + "px";
                element.style.left = (element.offsetLeft - pos1) + "px";
                
                // Update connections when dragging
                updateAllConnections();
            }
            
            function closeDragElement() {
                // Stop moving when mouse button is released
                element.classList.remove('dragging');
                document.onmouseup = null;
                document.onmousemove = null;
                isDragging = false;
                
                // Save the new position (you might want to send this to a server)
                const userId = element.getAttribute('data-user-id');
                const userIndex = parseInt(userId, 10);
                users[userIndex].position = {
                    x: element.offsetLeft,
                    y: element.offsetTop
                };
            }
        }
        
        // Zoom functionality
        const organizationMapContainer = document.getElementById('organization_map_container');
        const zoomInButton = document.getElementById('zoom_in');
        const zoomOutButton = document.getElementById('zoom_out');
        const zoomResetButton = document.getElementById('zoom_reset');
        
        let currentZoom = 1;
        const zoomFactor = 0.1;
        const minZoom = 0.5;
        const maxZoom = 2;
        let isDragging = false;
        let startX, startY, scrollLeft, scrollTop;
        
        // Zoom in function
        function zoomIn() {
            if (currentZoom < maxZoom) {
                currentZoom += zoomFactor;
                applyZoom();
            }
        }
        
        // Zoom out function
        function zoomOut() {
            if (currentZoom > minZoom) {
                currentZoom -= zoomFactor;
                applyZoom();
            }
        }
        
        // Reset zoom function
        function resetZoom() {
            currentZoom = 1;
            applyZoom();
        }
        
        // Apply zoom level
        function applyZoom() {
            const mapContainer = document.getElementById('organization_map_container');
            const map = document.getElementById('organization_map');
            const arrows = document.getElementById('arrows_container');
            
            // Get current scroll position and container dimensions
            const containerWidth = mapContainer.clientWidth;
            const containerHeight = mapContainer.clientHeight;
            const scrollLeft = mapContainer.scrollLeft;
            const scrollTop = mapContainer.scrollTop;
            
            // Calculate the center point of the current view
            const centerX = scrollLeft + containerWidth / 2;
            const centerY = scrollTop + containerHeight / 2;
            
            // Apply zoom transforms
            map.style.transform = `scale(${currentZoom})`;
            arrows.style.transform = `scale(${currentZoom})`;
            
            // Ensure transform origins are exactly the same
            map.style.transformOrigin = 'center center';
            arrows.style.transformOrigin = 'center center';
            
            // Add transition for smooth zoom
            map.classList.add('zooming');
            arrows.classList.add('zooming');
            
            // Calculate new scroll position to maintain center point
            const newScrollLeft = (centerX * currentZoom) - (containerWidth / 2);
            const newScrollTop = (centerY * currentZoom) - (containerHeight / 2);
            
            // Apply new scroll position after transform is complete
            setTimeout(() => {
                mapContainer.scrollLeft = newScrollLeft;
                mapContainer.scrollTop = newScrollTop;
                
                map.classList.remove('zooming');
                arrows.classList.remove('zooming');
                
                // Update all connections to ensure correct positioning
                updateAllConnections();
            }, 200);
        }
        
        // Wheel zoom event
        organizationMapContainer.addEventListener('wheel', function(e) {
            if (e.ctrlKey) {
                e.preventDefault();
                if (e.deltaY < 0) {
                    zoomIn();
                } else {
                    zoomOut();
                }
            }
        }, { passive: false });
        
        // Button event listeners
        zoomInButton.addEventListener('click', function() {
            zoomIn();
            updateAllConnections(); // Ensure connections update after zoom
        });
        
        zoomOutButton.addEventListener('click', function() {
            zoomOut();
            updateAllConnections(); // Ensure connections update after zoom
        });
        
        zoomResetButton.addEventListener('click', function() {
            resetZoom();
            updateAllConnections(); // Ensure connections update after zoom
        });

        // Pan functionality (drag to move when zoomed in)
        organizationMapContainer.addEventListener('mousedown', function(e) {
            // Only allow panning if we're zoomed in
            if (currentZoom > 1) {
                isDragging = true;
                startX = e.pageX - organizationMapContainer.offsetLeft;
                startY = e.pageY - organizationMapContainer.offsetTop;
                scrollLeft = organizationMapContainer.scrollLeft;
                scrollTop = organizationMapContainer.scrollTop;
            }
        });
        
        organizationMapContainer.addEventListener('mouseleave', function() {
            isDragging = false;
        });
        
        organizationMapContainer.addEventListener('mouseup', function() {
            isDragging = false;
        });
        
        organizationMapContainer.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            e.preventDefault();
            
            const x = e.pageX - organizationMapContainer.offsetLeft;
            const y = e.pageY - organizationMapContainer.offsetTop;
            const walkX = (x - startX) * 1;
            const walkY = (y - startY) * 1;
            
            organizationMapContainer.scrollLeft = scrollLeft - walkX;
            organizationMapContainer.scrollTop = scrollTop - walkY;
        });
        
        // Handle sidebar expansion
        const sidebar = document.getElementById('sidebar');
        const mapContainer = document.getElementById('organization_map_container');
        
        // Update map container position when sidebar expands/collapses
        function updateMapPosition() {
            if (sidebar.classList.contains('expanded')) {
                mapContainer.style.width = 'calc(100% - 200px)';
                mapContainer.style.marginLeft = '200px';
            } else {
                mapContainer.style.width = 'calc(100% - 70px)';
                mapContainer.style.marginLeft = '70px';
            }
        }
        
        // Update on page load
        updateMapPosition();
        
        // Listen for sidebar changes
        const observer = new MutationObserver(() => {
            updateMapPosition();
        });
        
        observer.observe(sidebar, { attributes: true });
        
        // Save functionality
        const saveButton = document.getElementById('save_map');
        const saveStatus = document.getElementById('save_status');
        
        saveButton.addEventListener('click', saveMapArrangement);
        
        function saveMapArrangement() {
            // Collect data about user positions
            const userPositions = users.map((user, index) => {
                return {
                    id: index,
                    name: user.name,
                    position: user.position
                };
            });
            
            // Collect data about connections
            const connectionData = connections.map(conn => {
                return {
                    id: conn.id,
                    sourceId: conn.sourceId,
                    targetId: conn.targetId,
                    direction: conn.direction,
                    weight: conn.weight
                };
            });
            
            // Prepare data object for saving
            const mapData = {
                users: userPositions,
                connections: connectionData,
                lastSaved: new Date().toISOString()
            };
            
            // Send data to server (AJAX)
            fetch('/api/save-user-map/', {
                method: 'POST',
                headers: