window.addEventListener('DOMContentLoaded', function () {
    // Get the navbar toggle button
    const btnToggle = document.querySelector('.navbar-toggler');
    // Add an event listener to the toggle button
    btnToggle.addEventListener('click', function (event) {
        // Toggle the collapse
        const menu = document.querySelector('#navbarNav');
        menu.classList.toggle('collapse');
        // Close the dropdown if it's open
        const dropdown = document.querySelector('.dropdown-menu');
        if (dropdown !== null && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    });
});