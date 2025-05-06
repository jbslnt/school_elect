document.addEventListener("DOMContentLoaded", function () {
    // --- Account Dropdown ---
    const dropdown = document.querySelector(".account-toggle");
    const dropdownMenu = document.querySelector("#accountDropdown");

    dropdown.addEventListener("mouseenter", function () {
        dropdownMenu.style.display = "block";
        setTimeout(() => dropdownMenu.classList.add("show-dropdown"), 10);
    });

    dropdown.addEventListener("mouseleave", function () {
        setTimeout(() => {
            if (!dropdownMenu.matches(":hover")) {
                dropdownMenu.classList.remove("show-dropdown");
                setTimeout(() => dropdownMenu.style.display = "none", 300);
            }
        }, 200);
    });

    dropdownMenu.addEventListener("mouseenter", function () {
        dropdownMenu.classList.add("show-dropdown");
    });

    dropdownMenu.addEventListener("mouseleave", function () {
        dropdownMenu.classList.remove("show-dropdown");
        setTimeout(() => dropdownMenu.style.display = "none", 300);
    });

    // --- Sidebar Toggle for Mobile ---
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const overlay = document.getElementById('sidebar-overlay');

    if (toggleBtn) { // Only add sidebar toggle if the button exists
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            mainContent.classList.toggle('shifted');
            overlay.style.display = sidebar.classList.contains('active') ? 'block' : 'none';
        });

        overlay.addEventListener('click', function () {
            sidebar.classList.remove('active');
            mainContent.classList.remove('shifted');
            overlay.style.display = 'none';
        });
    }
});
