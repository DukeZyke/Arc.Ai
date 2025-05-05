
    const navIcon = document.getElementById("nav_icon");
    const sidebar = document.getElementById("sidebar");
    const sidebarContent = document.getElementById("sidebar_content");
    const navItems = document.querySelectorAll(".nav_item p");

    // Function to toggle sidebar expansion
    const toggleSidebar = () => {
        sidebar.classList.toggle("expanded");

        if (sidebar.classList.contains("expanded")) {
            sidebarContent.classList.remove("hidden");
            navItems.forEach((item) => {
                item.style.display = "block";
            });
        } else {
            sidebarContent.classList.add("hidden");
            navItems.forEach((item) => {
                item.style.display = "none";
            });
        }
    };

    // Add click event to the navigation icon
    navIcon.addEventListener("click", (event) => {
        event.stopPropagation(); // Prevent click from propagating to the document
        toggleSidebar();
    });

    // Add click event to the "Navigate" <p> text
    document.querySelector(".nav_item p").addEventListener("click", (event) => {
        event.stopPropagation(); // Prevent click from propagating to the document
        toggleSidebar();
    });

    // Close sidebar when clicking outside
    document.addEventListener("click", (event) => {
        if (!sidebar.contains(event.target)) {
            sidebar.classList.remove("expanded");
            sidebarContent.classList.add("hidden");
            navItems.forEach((item) => {
                item.style.display = "none";
            });
        }
    });

    // Initially hide the <p> elements
    navItems.forEach((item) => {
        item.style.display = "none";
    });
const notificationIcon = document.querySelector('.sidebar_icns[src*="Notification.png"]');
const notificationPopup = document.getElementById('notification_popup');
const detailedNotification = document.getElementById('detailed_notification');
const notificationItems = document.querySelectorAll('.notification_item');
const closeNotificationPopup = document.getElementById('close_notification_popup');
const closeDetailedNotification = document.getElementById('close_detailed_notification');
const notificationDetail = document.getElementById('notification_detail');

// Function to update the position of detailed notification
const updateDetailedNotificationPosition = () => {
    const notificationPopupWidth = notificationPopup.classList.contains("hidden") ? 0 : notificationPopup.offsetWidth;
    detailedNotification.style.left = `${220 + 20 + notificationPopupWidth + 20}px`; // Sidebar width + gap + notification popup width + gap
};

// Show notification pop-up
notificationIcon.addEventListener('click', () => {
    notificationPopup.classList.remove('hidden'); // Show notification pop-up
});

// Close notification pop-up
closeNotificationPopup.addEventListener('click', () => {
    notificationPopup.classList.add('hidden'); // Hide notification pop-up
});

// Show detailed notification without hiding the notification pop-up
notificationItems.forEach(item => {
    item.addEventListener('click', () => {
        const detail = item.getAttribute('data-detail');
        notificationDetail.textContent = detail;
        detailedNotification.classList.remove('hidden'); // Show detailed notification
    });
});

// Close detailed notification
closeDetailedNotification.addEventListener('click', () => {
    detailedNotification.classList.add('hidden'); // Hide detailed notification
});