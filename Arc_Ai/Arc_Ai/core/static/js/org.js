const container = document.querySelector('.card-container');  // cards

let isDown = false;
let startX;
let scrollLeft;
let hasMoved = false; // Add this flag to track if the mouse has moved

container.addEventListener('mousedown', (e) => {
    // Don't start dragging if clicking on a project card
    if (e.target.closest('.project-container')) {
        return;
    }
    
    isDown = true;
    hasMoved = false; // Reset the flag
    container.classList.add('active');
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
    document.body.style.userSelect = 'none';
});

container.addEventListener('mouseleave', () => {
    isDown = false;
    container.classList.remove('active');
    document.body.style.userSelect = '';
});

container.addEventListener('mouseup', (e) => {
    isDown = false;
    container.classList.remove('active');
    document.body.style.userSelect = '';
    
    // If we haven't moved and we're clicking on a project card, don't prevent the click
    if (!hasMoved && e.target.closest('.project-container')) {
        // Let the project card click handler run
        return;
    }
});

container.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    hasMoved = true; // Set the flag when mouse moves
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * 1; // Adjust scroll speed here
    container.scrollLeft = scrollLeft - walk;
});


// Make each time slot toggle active state when clicked
document.querySelectorAll('.time-slot').forEach(slot => {
    slot.addEventListener('click', () => {
    slot.classList.toggle('active');
    });
});

const weekLabel = document.getElementById('week-label');
const prevWeekBtn = document.getElementById('prev-week');
const nextWeekBtn = document.getElementById('next-week');
const scheduleBarsContainer = document.querySelector('.schedule-bars');

// Example week data with schedule bars
const weeks = [
    {
        label: 'March 25-31',
        bars: [
            { gridRow: 3, gridColumn: '2 / 5', color: '#353A56' },
            { gridRow: 5, gridColumn: '6 / 10', color: '#6AFF3C' },
        ],
    },
    {
        label: 'April 1-5',
        bars: [
            { gridRow: 4, gridColumn: '4 / 4', color: '#6AFF3C' },
            { gridRow: 5, gridColumn: '8 / 12', color: '#FFD700' },
            { gridRow: 6, gridColumn: '15 / 24', color: '#353A56' },
        ],
    },
    {
        label: 'April 6-12',
        bars: [
            { gridRow: 2, gridColumn: '3 / 7', color: '#FF5733' },
            { gridRow: 6, gridColumn: '5 / 9', color: '#33FF57' },
        ],
    },
    {
        label: 'April 13-19',
        bars: [
            { gridRow: 3, gridColumn: '1 / 4', color: '#FFC300' },
            { gridRow: 7, gridColumn: '6 / 10', color: '#DAF7A6' },
        ],
    },
    {
        label: 'April 20-26',
        bars: [
            { gridRow: 4, gridColumn: '2 / 5', color: '#C70039' },
            { gridRow: 5, gridColumn: '7 / 11', color: '#900C3F' },
        ],
    },
];

let currentWeekIndex = 1; // Start at "April 1-5"

// Function to update the week label and schedule bars
function updateWeek() {
    // Update the week label
    weekLabel.textContent = weeks[currentWeekIndex].label;

    // Clear existing bars
    scheduleBarsContainer.innerHTML = '';

    // Add new bars for the selected week
    weeks[currentWeekIndex].bars.forEach((bar, index) => {
        const barElement = document.createElement('div');
        barElement.classList.add('bar');
        barElement.style.gridRow = bar.gridRow;
        barElement.style.gridColumn = bar.gridColumn;
        barElement.style.backgroundColor = bar.color;

        // Add data-details for the popup
        barElement.dataset.details = JSON.stringify({
            title: `Worksheet #${index + 1}`,
            date: 'Yesterday, January 29, 2025',
            description: `Details for bar ${index + 1}`,
        });

        scheduleBarsContainer.appendChild(barElement);
    });
}

// Navigate to the previous week
prevWeekBtn.addEventListener('click', () => {
    if (currentWeekIndex > 0) {
        currentWeekIndex--;
        updateWeek();

        // Hide the popup if it is open
        popupWrapper.classList.add('hidden');
    }
});

// Navigate to the next week
nextWeekBtn.addEventListener('click', () => {
    if (currentWeekIndex < weeks.length - 1) {
        currentWeekIndex++;
        updateWeek();

        // Hide the popup if it is open
        popupWrapper.classList.add('hidden');
    }
});

// Initialize the week label and schedule bars
updateWeek();

// Select the popup and close button
const barPopup = document.getElementById('bar-popup');
const popupCloseBtn = document.getElementById('popup-close-btn');
const popupWrapper = document.querySelector('.popup-wrapper');

// Function to show the popup
function showPopup(bar, details) {
    // Set popup content
    document.getElementById('popup-title').textContent = details.title || 'Worksheet #4';
    document.getElementById('popup-date').textContent = details.date || 'Yesterday, January 29, 2025';
    document.getElementById('popup-description').textContent = details.description || 'Meeting details here.';

    // Temporarily make the popup visible to calculate its dimensions
    popupWrapper.classList.remove('hidden');
    popupWrapper.style.visibility = 'hidden'; // Make it invisible but still measurable
    popupWrapper.style.display = 'block'; // Ensure it takes up space in the DOM

    // Get the bar's position within the grid
    const barRect = bar.getBoundingClientRect();
    const containerRect = scheduleBarsContainer.getBoundingClientRect();

    // Calculate the popup's position relative to the grid container
    const top = barRect.top - containerRect.top + barRect.height / 2 - popupWrapper.offsetHeight / 2; // Center vertically
    const left = barRect.right - containerRect.left + 10; // Place it to the right of the bar

    // Position the wrapper
    popupWrapper.style.top = `${top}px`;
    popupWrapper.style.left = `${left}px`;

    // Restore visibility and show the popup
    popupWrapper.style.visibility = 'visible';
    popupWrapper.style.display = ''; // Reset to default display
    popupWrapper.classList.remove('hidden');

    // Set the overlay color to match the bar's color
    const overlay = document.getElementById('popup-overlay');
    overlay.style.backgroundColor = bar.style.backgroundColor;
}

// Function to hide the popup
popupCloseBtn.addEventListener('click', () => {
    popupWrapper.classList.add('hidden'); // Hide the entire wrapper, not just the popup
});

// Add click event to each bar
scheduleBarsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('bar')) {
        const barDetails = JSON.parse(e.target.dataset.details);
        showPopup(e.target, barDetails);
    }
});