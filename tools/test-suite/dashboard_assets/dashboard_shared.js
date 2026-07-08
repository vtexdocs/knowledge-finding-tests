(function () {
  const STORAGE_KEY = "analysis-dashboard-presentation-mode";

  const PANELS_BY_MODE = {
    analysis: {
      open: ["overview", "paths", "path-families", "locales", "locale-gaps"],
      closed: [
        "styles",
        "personas",
        "styles-locale",
        "personas-locale",
        "portals",
        "issues",
        "failures",
        "issue-detail",
      ],
    },
    comparison: {
      open: ["overview", "movers", "paths", "path-families", "locales", "locale-gaps"],
      closed: [
        "styles",
        "personas",
        "styles-locale",
        "personas-locale",
        "issue-comparison",
        "failure-delta",
      ],
    },
  };

  function initPresentationMode() {
    const button = document.querySelector("[data-presentation-mode]");
    if (!button) {
      return;
    }

    const mode = document.body.dataset.dashboardMode || "analysis";
    const panelConfig = PANELS_BY_MODE[mode];
    let savedPanelState = null;

    function setTimelinePresentation(on) {
      document.querySelectorAll(".section.presentation-core").forEach((section) => {
        if (on) {
          section.classList.add("visible");
        }
      });
      if (on) {
        Object.values(window.timelineCharts || {}).forEach((chart) => {
          if (chart && typeof chart.resize === "function") {
            chart.resize();
          }
        });
      }
    }

    function applyPanels(on) {
      if (!panelConfig) {
        return;
      }
      const panels = Array.from(document.querySelectorAll(".panel"));
      if (!panels.length) {
        return;
      }
      if (on) {
        savedPanelState = {};
        panels.forEach((panel) => {
          savedPanelState[panel.id] = panel.open;
          if (panelConfig.open.includes(panel.id)) {
            panel.open = true;
          } else if (panelConfig.closed.includes(panel.id)) {
            panel.open = false;
          }
        });
        return;
      }
      if (savedPanelState) {
        panels.forEach((panel) => {
          if (Object.prototype.hasOwnProperty.call(savedPanelState, panel.id)) {
            panel.open = savedPanelState[panel.id];
          }
        });
        savedPanelState = null;
      }
    }

    function setPresentation(on) {
      document.body.classList.toggle("presentation-mode", on);
      button.textContent = on ? "Exit presentation" : "Presentation mode";
      button.setAttribute("aria-pressed", String(on));
      applyPanels(on);
      if (mode === "timeline" || mode === "multi-comparison") {
        setTimelinePresentation(on);
      }
      try {
        localStorage.setItem(STORAGE_KEY, on ? "1" : "0");
      } catch (_error) {
        /* ignore storage errors */
      }
    }

    button.addEventListener("click", () => {
      setPresentation(!document.body.classList.contains("presentation-mode"));
    });

    try {
      if (localStorage.getItem(STORAGE_KEY) === "1") {
        setPresentation(true);
      }
    } catch (_error) {
      /* ignore storage errors */
    }
  }

  function initPrintExpand() {
    window.addEventListener("beforeprint", () => {
      document.querySelectorAll(".panel").forEach((panel) => {
        panel.dataset.printWasOpen = panel.open ? "1" : "0";
        panel.open = true;
      });
      document.querySelectorAll(".section.presentation-core, .section:not(.presentation-hide)").forEach((section) => {
        section.classList.add("visible");
      });
      document.querySelectorAll(".heatmap-view").forEach((view) => {
        view.classList.add("visible");
      });
    });
    window.addEventListener("afterprint", () => {
      document.querySelectorAll(".panel").forEach((panel) => {
        if (panel.dataset.printWasOpen !== undefined) {
          panel.open = panel.dataset.printWasOpen === "1";
          delete panel.dataset.printWasOpen;
        }
      });
    });
  }

  function resetHelpTipPosition(tip) {
    const popup = tip.querySelector(".help-tip__popup");
    tip.classList.remove("is-positioned");
    if (!popup) {
      return;
    }
    popup.style.position = "";
    popup.style.left = "";
    popup.style.top = "";
    popup.style.bottom = "";
    popup.style.right = "";
    popup.style.transform = "";
    popup.style.width = "";
    popup.style.maxWidth = "";
    popup.style.whiteSpace = "";
    popup.style.overflowWrap = "";
    popup.style.visibility = "";
    popup.style.opacity = "";
    popup.style.pointerEvents = "";
  }

  function positionHelpTip(tip) {
    const popup = tip.querySelector(".help-tip__popup");
    const icon = tip.querySelector(".help-tip__icon");
    if (!popup || !icon) {
      return;
    }

    tip.classList.add("is-positioned");
    popup.style.position = "fixed";
    popup.style.visibility = "hidden";
    popup.style.opacity = "1";
    popup.style.pointerEvents = "none";
    popup.style.left = "0px";
    popup.style.top = "0px";
    popup.style.bottom = "auto";
    popup.style.right = "auto";
    popup.style.transform = "none";
    popup.style.width = "min(280px, calc(100vw - 16px))";
    popup.style.maxWidth = "min(280px, calc(100vw - 16px))";
    popup.style.whiteSpace = "normal";
    popup.style.overflowWrap = "break-word";

    const gap = 6;
    const margin = 8;
    const iconRect = icon.getBoundingClientRect();
    const popupRect = popup.getBoundingClientRect();
    let top = iconRect.top - popupRect.height - gap;
    if (top < margin) {
      top = iconRect.bottom + gap;
    }
    top = Math.min(top, window.innerHeight - margin - popupRect.height);
    top = Math.max(margin, top);

    let left = iconRect.left + (iconRect.width - popupRect.width) / 2;
    left = Math.max(margin, Math.min(left, window.innerWidth - margin - popupRect.width));

    popup.style.left = `${Math.round(left)}px`;
    popup.style.top = `${Math.round(top)}px`;
    popup.style.visibility = "";
  }

  function isHelpTipActive(tip) {
    return tip.classList.contains("is-open") || tip.matches(":hover");
  }

  function hideHelpTipIfInactive(tip) {
    if (!isHelpTipActive(tip)) {
      resetHelpTipPosition(tip);
    }
  }

  function closeAllHelpTips(tips) {
    tips.forEach((tip) => {
      tip.classList.remove("is-open");
      resetHelpTipPosition(tip);
    });
  }

  function initHelpTips() {
    const tips = Array.from(document.querySelectorAll("[data-help-tip]"));
    tips.forEach((tip) => {
      tip.addEventListener("mouseenter", () => positionHelpTip(tip));
      tip.addEventListener("mouseleave", () => hideHelpTipIfInactive(tip));
      tip.addEventListener("focusin", () => positionHelpTip(tip));
      tip.addEventListener("focusout", () => hideHelpTipIfInactive(tip));
      tip.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        const open = tip.classList.contains("is-open");
        tips.forEach((other) => {
          if (other !== tip) {
            other.classList.remove("is-open");
            resetHelpTipPosition(other);
          }
        });
        if (!open) {
          tip.classList.add("is-open");
          positionHelpTip(tip);
        } else {
          tip.classList.remove("is-open");
          resetHelpTipPosition(tip);
        }
      });
    });
    document.addEventListener("click", () => closeAllHelpTips(tips));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeAllHelpTips(tips);
      }
    });
    window.addEventListener(
      "scroll",
      () => {
        tips.filter((tip) => isHelpTipActive(tip)).forEach((tip) => positionHelpTip(tip));
      },
      true
    );
    window.addEventListener("resize", () => {
      tips.filter((tip) => isHelpTipActive(tip)).forEach((tip) => positionHelpTip(tip));
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    try {
      initPresentationMode();
      initPrintExpand();
      initHelpTips();
    } catch (error) {
      console.error("Dashboard init failed: presentation/print/help", error);
    }
  });
})();
