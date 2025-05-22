document.addEventListener('DOMContentLoaded', function() {
    // File removal functionality
    initFileRemoval();
    
    // Team member management
    initTeamMemberFields();
    
    // File upload handler
    initFileUpload();
    
    // Add member button click handler
    const addMemberBtn = document.getElementById('add_member_btn');
    if (addMemberBtn) {
        addMemberBtn.addEventListener('click', function() {
            addMember();
        });
    }
    
    // Initialize member count on page load
    updateDropdownCount();
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
    const teamCountInput = document.getElementById('team_count');
    const teamList = document.getElementById('members');
    
    if (teamCountInput && teamList) {
        // Initialize remove member button event handlers
        document.querySelectorAll('.remove-member-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                removeMember(this);
            });
        });
    }
}

/**
 * Add a new team member field
 */
function addMember() {
    const membersDiv = document.getElementById('members');
    if (!membersDiv) return;
    
    // Create member row elements
    const wrapper = document.createElement('div');
    wrapper.className = 'member-row';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'member_names';
    input.className = 'adminedit-input';
    input.placeholder = 'Enter team member name';
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-member-btn';
    removeBtn.innerHTML = '&times;';
    removeBtn.title = 'Remove member';
    removeBtn.addEventListener('click', function() {
        removeMember(this);
    });
    
    // Assemble and add to the DOM
    wrapper.appendChild(input);
    wrapper.appendChild(removeBtn);
    membersDiv.appendChild(wrapper);
    
    // Update the counter
    updateDropdownCount();
}

/**
 * Remove a team member field
 */
function removeMember(btn) {
    const row = btn.closest('.member-row') || btn.parentElement;
    if (row) {
        row.remove();
        updateDropdownCount();
    }
}

/**
 * Update team member fields based on count
 */
function updateMemberFields() {
    const membersDiv = document.getElementById('members');
    if (!membersDiv) return;
    
    const count = parseInt(document.getElementById('team_count').value);
    const currentInputs = membersDiv.querySelectorAll('input[name="member_names"]');
    
    // Store current values
    const currentValues = Array.from(currentInputs).map(input => input.value);
    
    // Clear existing fields
    membersDiv.innerHTML = '';
    
    // Add new fields based on count
    for (let i = 0; i < count; i++) {
        createMemberRow(membersDiv, currentValues[i] || '');
    }
}

/**
 * Update count to match the number of member fields
 */
function updateDropdownCount() {
    const membersDiv = document.getElementById('members');
    if (!membersDiv) return;
    
    const teamCountInput = document.getElementById('team_count');
    const teamCountDisplay = document.getElementById('team_count_display');
    const count = membersDiv.querySelectorAll('.member-row').length;
    
    // Update hidden input and display
    if (teamCountInput && teamCountDisplay) {
        teamCountInput.value = count;
        teamCountDisplay.textContent = count;
    }
}

/**
 * Create a member row with input field and remove button
 */
function createMemberRow(container, value = '') {
    const row = document.createElement('div');
    row.className = 'member-row';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'member_names';
    input.className = 'adminedit-input';
    input.placeholder = 'Enter team member name';
    input.value = value;
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-member-btn';
    removeBtn.innerHTML = '&times;';
    removeBtn.title = 'Remove member';
    removeBtn.addEventListener('click', function() {
        removeMember(this);
    });
    
    row.appendChild(input);
    row.appendChild(removeBtn);
    container.appendChild(row);
    
    return row;
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