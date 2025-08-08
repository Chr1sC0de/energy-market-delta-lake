// Function to toggle menu and save state
function toggleMenu(id) {
    const menu = document.getElementById(id);
    if (menu.classList.contains("hidden")) {
        menu.classList.remove("hidden");
        localStorage.setItem(id + "-state", "open");
    } else {
        menu.classList.add("hidden");
        localStorage.setItem(id + "-state", "closed");
    }
}

// Function to restore menu state on page load
document.addEventListener("DOMContentLoaded", function() {
    // List of all menu IDs
    const menuIds = ["nem-menu", "dwgm-menu", "sttm-menu", "gsh-menu"];

    // Check URL path to determine which menu should be open
    const path = window.location.pathname;

    // Auto-open menus based on URL
    if (path.includes("/plots/electricity/") || path.includes("/plots/nem/")) {
        document.getElementById("nem-menu")?.classList.remove("hidden");
        localStorage.setItem("nem-menu-state", "open");
    }

    if (
        path.includes("/plots/gas/dwgm/") ||
        path.includes("/plots/gas/price_and_withdrawals")
    ) {
        document.getElementById("dwgm-menu")?.classList.remove("hidden");
        localStorage.setItem("dwgm-menu-state", "open");
    }

    if (path.includes("/plots/gas/sttm/")) {
        document.getElementById("sttm-menu")?.classList.remove("hidden");
        localStorage.setItem("sttm-menu-state", "open");
    }

    if (path.includes("/plots/gas/gsh/")) {
        document.getElementById("gsh-menu")?.classList.remove("hidden");
        localStorage.setItem("gsh-menu-state", "open");
    }

    // Restore state from localStorage for all menus
    menuIds.forEach((id) => {
        const state = localStorage.getItem(id + "-state");
        if (state === "open") {
            document.getElementById(id)?.classList.remove("hidden");
        }
    });
});
