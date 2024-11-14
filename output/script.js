// Script.js
const header = document.querySelector('header');
const navbarToggler = header.querySelector('.navbar-toggler');
const navbarMenu = header.querySelector('.navbar-menu');
const body = document.body;
// Add event listener to the navbar toggler button
navbarToggler.addEventListener('click', () => {
    // Toggle class active on both the header and the menu
    header.classList.toggle('active');
    navbarMenu.classList.toggle('active');
});