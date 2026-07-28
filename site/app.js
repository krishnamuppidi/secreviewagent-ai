(function () {
  "use strict";

  const nav = document.querySelector(".nav");
  const menuButton = document.querySelector(".menu-button");
  const navLinks = document.querySelector(".nav-links");
  const analytics = (eventName, parameters) =>
    window.sraAnalytics?.event(eventName, parameters);

  const updateNav = () => nav?.classList.toggle("scrolled", window.scrollY > 10);
  updateNav();
  window.addEventListener("scroll", updateNav, { passive: true });

  if (menuButton && navLinks) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      menuButton.setAttribute("aria-label", open ? "Open navigation" : "Close navigation");
      navLinks.classList.toggle("open", !open);
    });
    navLinks.addEventListener("click", () => {
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.setAttribute("aria-label", "Open navigation");
      navLinks.classList.remove("open");
    });
  }

  const revealItems = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.07, rootMargin: "0px 0px -28px" },
    );
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("visible"));
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest?.("a");
    if (!link) return;
    const url = new URL(link.getAttribute("href") || "", window.location.href);
    if (link.dataset.track === "paper_download") {
      analytics("research_paper_download", { paper: "secreviewagent_icufn_2026" });
    } else if (
      url.hostname === "github.com" &&
      url.pathname.startsWith("/krishnamuppidi/secreviewagent-ai")
    ) {
      analytics("github_engagement", {
        destination: url.pathname.includes("/issues") ? "issues" : "repository",
      });
    } else if (url.hostname === window.location.hostname && url.pathname !== window.location.pathname) {
      analytics("internal_guide_navigation", {
        destination_path: url.pathname,
      });
    }
  });

  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
