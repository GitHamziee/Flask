document.addEventListener("DOMContentLoaded", function () {
  // Intersection Observer for stat counters
  const observerOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0.1,
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const element = entry.target;
        element.classList.add("visible");

        if (element.dataset.animation === "countUp") {
          const target = parseInt(element.dataset.target);
          animateCounter(element.querySelector(".display-4"), target);
        }
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll("[data-animation]").forEach((element) => {
    observer.observe(element);
  });

  // Counter animation function
  function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const duration = 2000;
    const step = duration / 50;

    const counter = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(counter);
      }
      element.textContent =
        Math.round(current).toLocaleString() +
        (element.textContent.includes("%") ? "%" : "+");
    }, step);
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
});

// Initialize all Bootstrap toasts in the container
document.addEventListener("DOMContentLoaded", function () {
  const toastElements = document.querySelectorAll(".toast");
  toastElements.forEach((toastEl) => {
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  });
});
