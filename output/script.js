// Add smooth scrolling to the landing page
window.onscroll = function() {
  // Get the current scroll position
  var scrollPosition = window.pageYOffset;
  // Calculate the distance from the top of the document for each section
  var firstSectionTop = document.querySelector('.first-section').offsetTop;
  var secondSectionTop = document.querySelector('.second-section').offsetTop;
  var thirdSectionTop = document.querySelector('.third-section').offsetTop;
  // Add smooth scrolling to each section when clicked
  document.querySelector('.first-section a').onclick = function() {
    window.scrollTo(0, firstSectionTop);
    return false;
  }
  document.querySelector('.second-section a').onclick = function() {
    window.scrollTo(0, secondSectionTop);
    return false;
  }
  document.querySelector('.third-section a').onclick = function() {
    window.scrollTo(0, thirdSectionTop);
    return false;
  }
}