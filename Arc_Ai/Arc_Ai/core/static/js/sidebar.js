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
const notificationParagraph = document.getElementById('notification_paragraph');

// Function to toggle notification pop-up visibility
const toggleNotificationPopup = () => {
    if (notificationPopup.classList.contains('hidden')) {
        console.log('Showing notification pop-up');
        notificationPopup.classList.remove('hidden'); // Show notification pop-up
    } else {
        console.log('Hiding notification pop-up');
        notificationPopup.classList.add('hidden'); // Hide notification pop-up
        detailedNotification.classList.add('hidden'); 
    }
};

// Add click event to both the notification icon and paragraph
notificationIcon.addEventListener('click', toggleNotificationPopup);
notificationParagraph.addEventListener('click', toggleNotificationPopup);

// Function to update the position of detailed notification
const updateDetailedNotificationPosition = () => {
    const notificationPopupWidth = notificationPopup.classList.contains('hidden') ? 0 : notificationPopup.offsetWidth;
    console.log('Notification Popup Width:', notificationPopupWidth); // Debugging
    detailedNotification.style.left = `${220 + 20 + notificationPopupWidth + 20}px`; // Sidebar width + gap + notification popup width + gap
    console.log('Detailed Notification Left:', detailedNotification.style.left); // Debugging
};

// Close notification pop-up
closeNotificationPopup.addEventListener('click', () => {
    notificationPopup.classList.add('hidden'); // Hide notification pop-up
});

// Close detailed notification
closeDetailedNotification.addEventListener('click', () => {
    detailedNotification.classList.add('hidden'); // Hide detailed notification
});


// Data context for the notification items TEST
document.addEventListener('DOMContentLoaded', () => {
    const notificationList = document.getElementById('notification_list').querySelector('ul');

    // Fetch notifications from the backend
    fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
            notificationList.innerHTML = ''; // Clear existing notifications
            data.forEach(notification => {
                const listItem = document.createElement('li');
                listItem.classList.add('notification_item');
                listItem.setAttribute('data-detail', notification.description); // Ensure full description is set
                listItem.setAttribute('data-title', notification.title); // Set the title as data-title
                listItem.setAttribute('data-date', notification.created_at); // Set the date as data-date
                listItem.setAttribute('data-posted-by', notification.posted_by); // Set the posted-by as data-posted-by
                listItem.innerHTML = `
                    <div class="title-and-date">
                        <p>${notification.title}</p><span>${notification.created_at}</span>
                    </div>
                    <p class="short-description">${notification.description}</p>
                    <p class="posted-by">- ${notification.posted_by}</p>
                `;
                notificationList.appendChild(listItem);

                // Attach click event listener to show detailed notification
                listItem.addEventListener('click', () => {
                    // Use the full description directly from the notification object
                    notificationDetail.textContent = notification.description; // Fetch directly from the notification object
                    document.getElementById('notification_title').textContent = notification.title;
                    document.querySelector('#detailed_notification .notification_date').textContent = notification.created_at;
                    document.querySelector('#detailed_notification .posted-by').textContent = `- ${notification.posted_by}`;
                    detailedNotification.classList.remove('hidden'); // Show detailed notification
                });
            });
        })
        .catch(error => console.error('Error fetching notifications:', error));
});

// Ensure DOM is fully loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", () => {
    const closeDetailedNotification = document.getElementById("close_detailed_notification");
    const detailedNotification = document.getElementById("detailed_notification");

    // Function to toggle detailed notification visibility
    const toggleDetailedNotification = (isVisible) => {
        if (isVisible) {
            detailedNotification.classList.remove("hidden");
        } else {
            detailedNotification.classList.add("hidden");
        }
    };

    // Close button for detailed notification
    if (closeDetailedNotification) {
        closeDetailedNotification.addEventListener("click", () => {
            toggleDetailedNotification(false);
        });
    } else {
        console.error("Close button for detailed notification not found.");
    }
});