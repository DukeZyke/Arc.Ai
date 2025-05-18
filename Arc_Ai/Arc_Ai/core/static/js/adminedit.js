document.addEventListener('DOMContentLoaded', function() {
    // File removal functionality
    initFileRemoval();
    
    // Team member management
    initTeamMemberFields();
    
    // File upload handler
    initFileUpload();
});

/**
 * Initialize file removal functionality
 */
function initFileRemoval() {
    document.querySelectorAll('.adminedit-remove-file').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const li = btn.closest('li');
            if (li) li.remove();
        });
    });
}

/**
 * Initialize and manage team member input fields
 */
function initTeamMemberFields() {
    const teamCountSelect = document.getElementById('team_count');
    const teamList = document.getElementById('team_list');
    
    if (teamCountSelect && teamList) {
        // Update team member fields based on selected count
        function updateTeamMemberFields() {
            const count = parseInt(teamCountSelect.value);
            
            // Clear existing fields
            teamList.innerHTML = '';
            
            // Add new fields based on count
            for (let i = 1; i <= count; i++) {
                const input = document.createElement('input');
                input.type = 'email';
                input.className = 'adminedit-input';
                input.name = `team_member_${i}`;
                input.placeholder = `team${i}@example.com`;
                teamList.appendChild(input);
            }
        }
        
        // Initialize with default selection
        updateTeamMemberFields();
        
        // Update when selection changes
        teamCountSelect.addEventListener('change', updateTeamMemberFields);
    }
}

/**
 * Initialize file upload handling
 */
function initFileUpload() {
    const fileInput = document.getElementById('add_file');
    const fileList = document.querySelector('.adminedit-file-list');
    
    if (fileInput && fileList) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const file = this.files[i];
                    
                    // Create list item
                    const li = document.createElement('li');
                    
                    // Create filename span
                    const filenameSpan = document.createElement('span');
                    filenameSpan.textContent = file.name;
                    
                    // Create remove button
                    const removeBtn = document.createElement('span');
                    removeBtn.className = 'adminedit-remove-file';
                    removeBtn.title = 'Remove';
                    removeBtn.innerHTML = '&#10006;';
                    removeBtn.addEventListener('click', function() {
                        li.remove();
                    });
                    
                    // Add elements to list item
                    li.appendChild(filenameSpan);
                    li.appendChild(removeBtn);
                    
                    // Add list item to file list
                    fileList.appendChild(li);
                }
                
                // Clear input so same file can be added again if needed
                fileInput.value = '';
            }
        });
    }
}
