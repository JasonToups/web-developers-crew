document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll for navigation links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }
    });
  });

  // Get Started button click handler
  const getStartedBtn = document.querySelector('.btn-primary');
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', async () => {
      try {
        // Future authentication logic will go here
        console.log('Get Started clicked');
      } catch (error) {
        console.error('Error:', error);
      }
    });
  }

  // Add intersection observer for animation
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
        }
      });
    },
    {
      threshold: 0.1,
    }
  );

  // Observe all feature cards and step cards
  document.querySelectorAll('.feature-card, .step-card').forEach((el) => {
    observer.observe(el);
  });
});
