function selectProfilePicture(imageElement) {
    // Get the source of the clicked image
    const selectedImageSrc = imageElement.src;

    // Update the active profile picture
    const activeProfilePic = document.getElementById('selected_profile_pic');
    activeProfilePic.src = selectedImageSrc;
}