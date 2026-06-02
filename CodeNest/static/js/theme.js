(() => {
    const storageKey = "codenest-theme";
    const root = document.documentElement;
    const toggle = document.querySelector("[data-theme-toggle]");

    if (!toggle) {
        return;
    }

    const systemPreference = window.matchMedia("(prefers-color-scheme: dark)");

    const getStoredTheme = () => {
        try {
            const storedTheme = localStorage.getItem(storageKey);
            return ["light", "dark"].includes(storedTheme) ? storedTheme : null;
        } catch (error) {
            return null;
        }
    };

    const storeTheme = (theme) => {
        try {
            localStorage.setItem(storageKey, theme);
        } catch (error) {
            // The selected theme still applies for this page when storage is unavailable.
        }
    };

    const applyTheme = (theme) => {
        const isDark = theme === "dark";
        const label = isDark ? toggle.dataset.labelLight : toggle.dataset.labelDark;
        const icon = toggle.querySelector("i");

        root.dataset.theme = isDark ? "dark" : "light";
        toggle.setAttribute("aria-label", label);
        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute("title", label);

        if (icon) {
            icon.classList.toggle("bi-sun-fill", isDark);
            icon.classList.toggle("bi-moon-fill", !isDark);
        }
    };

    applyTheme(root.dataset.theme);

    toggle.addEventListener("click", () => {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        storeTheme(nextTheme);
        applyTheme(nextTheme);
    });

    const syncSystemPreference = (event) => {
        if (!getStoredTheme()) {
            applyTheme(event.matches ? "dark" : "light");
        }
    };

    if (systemPreference.addEventListener) {
        systemPreference.addEventListener("change", syncSystemPreference);
    } else {
        systemPreference.addListener(syncSystemPreference);
    }
})();
