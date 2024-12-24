// static/js/navbar.js

document.addEventListener("DOMContentLoaded", function () {
  // Navbar scroll effect
  var navbar = document.querySelector(".navbar");
  var navbarCollapse = document.querySelector(".navbar-collapse");
  var navbarToggler = document.querySelector(".navbar-toggler");

  window.addEventListener("scroll", function () {
    if (window.scrollY > 50) {
      navbar.classList.add("navbar-scrolled");
    } else {
      navbar.classList.remove("navbar-scrolled");
    }
  });

  // Close navbar on click (mobile)
  document
    .querySelectorAll(".navbar-nav .nav-link")
    .forEach(function (navLink) {
      navLink.addEventListener("click", function () {
        if (window.innerWidth < 992) {
          navbarCollapse.classList.remove("show");
          navbarToggler.setAttribute("aria-expanded", "false");
        }
      });
    });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });
});
