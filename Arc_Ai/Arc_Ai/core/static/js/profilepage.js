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
