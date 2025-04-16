document.addEventListener("DOMContentLoaded", function () {
        const toggle = document.getElementById("collections-toggle-mobile");
        const menu = document.getElementById("collections-menu-mobile");

        toggle.addEventListener("click", function (e) {
            e.preventDefault();
            menu.style.display = menu.style.display === "flex" ? "none" : "flex";
        });

        // Закрываем меню, если клик вне dropdown
        document.addEventListener("click", function (e) {
            if (!toggle.contains(e.target) && !menu.contains(e.target)) {
                menu.style.display = "none";
            }
        });
    });
    document.getElementById('menuBtnMobile').addEventListener('click', menuPanelOpen);
    function menuPanelOpen() {
        let accPanel = document.getElementById('side_menu_wrap');
        let overlay = document.getElementById('overlay');

        if (accPanel.classList.contains('open')) {
            accPanel.classList.remove('open');
            overlay.style.display = 'none'; // Hide the overlay when the account panel is closed
        } else {
            // Unlike the cart, we don't need to load data here since we're not populating with dynamic content
            // Open the account panel and overlay
            accPanel.classList.add('open');
            overlay.style.display = 'block';
        }
    }