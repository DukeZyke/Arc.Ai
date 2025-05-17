document.addEventListener('DOMContentLoaded', function () {
    const dropdownToggle = document.getElementById('dropdown-toggle');
    const contentBox = document.getElementById('content-box');
    const icon = dropdownToggle.querySelector('i');

    if (!dropdownToggle || !contentBox || !icon) {
        console.error('One or more elements are missing:', { dropdownToggle, contentBox, icon });
        return;
    }

    dropdownToggle.addEventListener('click', function () {
        console.log('Dropdown button clicked');

        // Toggle the expanded state
        if (contentBox.classList.contains('expanded')) {
            console.log('Collapsing content box');
            contentBox.classList.remove('expanded');
            setTimeout(() => contentBox.classList.add('hidden'), 300); // Add hidden after animation
        } else {
            console.log('Expanding content box');
            contentBox.classList.remove('hidden'); // Make it visible
            contentBox.classList.add('expanded');
        }

        // Rotate the icon
        icon.classList.toggle('rotate');
        console.log('Icon classes:', icon.className);

        function toggleFolder(folderId) {
    const folderContents = document.getElementById(`folder-${folderId}`);
    if (folderContents) {
        folderContents.classList.toggle('hidden');
    }
}
    });


    
});