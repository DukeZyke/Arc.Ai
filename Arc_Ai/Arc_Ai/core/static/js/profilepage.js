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

// Add this to your profilepage.js or create a new file
document.addEventListener('DOMContentLoaded', function() {
    const logoutForm = document.querySelector('form[action="{% url "core:logout" %}"]');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            const confirmLogout = confirm('Are you sure you want to log out?');
            if (!confirmLogout) {
                e.preventDefault();
            } else {
                // Clear any local storage items you might have set
                localStorage.removeItem('user_preferences');
                
                // You could also add:
                // sessionStorage.clear();
            }
        });
    }
});
