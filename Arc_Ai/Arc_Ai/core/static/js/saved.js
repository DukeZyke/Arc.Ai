const folderItems = document.querySelector('#folder_items'); // Select the folder items container

let isDown = false;
let startX;
let scrollLeft;

folderItems.addEventListener('mousedown', (e) => {
  isDown = true;
  folderItems.classList.add('active');
  startX = e.pageX - folderItems.offsetLeft;
  scrollLeft = folderItems.scrollLeft;
  document.body.style.userSelect = 'none'; // Disable text selection
});

folderItems.addEventListener('mouseleave', () => {
  isDown = false;
  folderItems.classList.remove('active');
  document.body.style.userSelect = ''; // Re-enable text selection
});

folderItems.addEventListener('mouseup', () => {
  isDown = false;
  folderItems.classList.remove('active');
  document.body.style.userSelect = ''; // Re-enable text selection
});

folderItems.addEventListener('mousemove', (e) => {
  if (!isDown) return; // Exit if the mouse is not pressed
  e.preventDefault();
  const x = e.pageX - folderItems.offsetLeft;
  const walk = (x - startX) * 1; // Adjust scroll speed (1 is default)
  folderItems.scrollLeft = scrollLeft - walk; // Scroll horizontally
});