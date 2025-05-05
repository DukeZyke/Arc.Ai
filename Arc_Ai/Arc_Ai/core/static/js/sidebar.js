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
