
const container = document.querySelector('.card-container');  // cards

let isDown = false;
let startX;
let scrollLeft;

container.addEventListener('mousedown', (e) => {
  isDown = true;
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

container.addEventListener('mouseup', () => {
  isDown = false;
  container.classList.remove('active');
  document.body.style.userSelect = ''; // Fix added here
});

container.addEventListener('mousemove', (e) => {
  if (!isDown) return;
  e.preventDefault();
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
            { gridRow: 6, gridColumn: '15 / 24', color: '#353A56' },
            { gridRow: 4, gridColumn: '4 / 8', color: '#6AFF3C' },
            { gridRow: 5, gridColumn: '8 / 12', color: '#FFD700' },
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
    weeks[currentWeekIndex].bars.forEach(bar => {
        const barElement = document.createElement('div');
        barElement.classList.add('bar');
        barElement.style.gridRow = bar.gridRow;
        barElement.style.gridColumn = bar.gridColumn;
        barElement.style.backgroundColor = bar.color;
        scheduleBarsContainer.appendChild(barElement);
    });
}

// Navigate to the previous week
prevWeekBtn.addEventListener('click', () => {
    if (currentWeekIndex > 0) {
        currentWeekIndex--;
        updateWeek();
    }
});

// Navigate to the next week
nextWeekBtn.addEventListener('click', () => {
    if (currentWeekIndex < weeks.length - 1) {
        currentWeekIndex++;
        updateWeek();
    }
});

// Initialize the week label and schedule bars
updateWeek();