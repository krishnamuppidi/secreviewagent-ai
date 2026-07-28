(function () {
  "use strict";

  // Shared research-product GA4 stream. Paths distinguish SecReviewAgent traffic.
  const MEASUREMENT_ID = "G-9C5B48SR3B";
  const CONSENT_KEY = "sra_analytics_consent";
  const VALID_CHOICES = new Set(["granted", "denied"]);
  let loaded = false;

  const storedChoice = () => {
    try {
      const choice = window.localStorage.getItem(CONSENT_KEY);
      return VALID_CHOICES.has(choice) ? choice : null;
    } catch (_error) {
      return null;
    }
  };

  const storeChoice = (choice) => {
    try {
      window.localStorage.setItem(CONSENT_KEY, choice);
    } catch (_error) {
      // Analytics remains optional when storage is unavailable.
    }
  };

  const deleteAnalyticsCookies = () => {
    const cookiePaths = new Set([
      "/",
      "/secreviewagent-ai/",
      window.location.pathname,
      window.location.pathname.replace(/[^/]*$/, ""),
    ]);
    const cookieDomains = [null, window.location.hostname, `.${window.location.hostname}`];
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      if (name === "_ga" || name.startsWith("_ga_")) {
        cookiePaths.forEach((path) => {
          cookieDomains.forEach((domain) => {
            const domainAttribute = domain ? `; Domain=${domain}` : "";
            document.cookie = `${name}=; Max-Age=0; Path=${path}${domainAttribute}; SameSite=Lax`;
          });
        });
      }
    });
  };

  const loadAnalytics = () => {
    if (loaded || storedChoice() !== "granted") return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag =
      window.gtag ||
      function () {
        window.dataLayer.push(arguments);
      };
    window.gtag("consent", "default", {
      ad_personalization: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      analytics_storage: "granted",
    });
    window.gtag("set", "ads_data_redaction", true);
    window.gtag("js", new Date());
    window.gtag("config", MEASUREMENT_ID, {
      allow_ad_personalization_signals: false,
      allow_google_signals: false,
      anonymize_ip: true,
      page_location: `${window.location.origin}${window.location.pathname}`,
      page_title: document.title,
      transport_type: "beacon",
    });
    const script = document.createElement("script");
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    document.head.appendChild(script);
  };

  const record = (eventName, parameters) => {
    if (storedChoice() !== "granted") return;
    loadAnalytics();
    window.gtag?.("event", eventName, {
      product: "secreviewagent",
      page_path: window.location.pathname,
      ...(parameters || {}),
    });
  };

  const setChoice = (choice) => {
    if (!VALID_CHOICES.has(choice)) return;
    storeChoice(choice);
    if (choice === "granted") {
      loadAnalytics();
      record("analytics_consent_granted");
    } else {
      window.gtag?.("consent", "update", { analytics_storage: "denied" });
      deleteAnalyticsCookies();
    }
    document.getElementById("analytics-consent")?.setAttribute("hidden", "");
  };

  const showPreferences = () => {
    const banner = document.getElementById("analytics-consent");
    if (!banner) return;
    banner.removeAttribute("hidden");
    banner.querySelector("button")?.focus();
  };

  window.sraAnalytics = Object.freeze({
    consent: storedChoice,
    event: record,
    measurementId: MEASUREMENT_ID,
    showPreferences,
  });

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-analytics-choice]").forEach((button) => {
      button.addEventListener("click", () => setChoice(button.dataset.analyticsChoice));
    });
    document.getElementById("analytics-preferences")?.addEventListener("click", showPreferences);
    if (storedChoice() === "granted") loadAnalytics();
    else if (storedChoice() === null) showPreferences();
  });
})();
