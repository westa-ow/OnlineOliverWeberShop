document.getElementById('accountBtnMobile').addEventListener('click', accountPanelOpen);
    document.getElementById('accountBtn').addEventListener('click', accountPanelOpen);
    function accountPanelOpen() {
            let accPanel = document.getElementById('side_acc_wrap');
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
        };
    function confirmLogout(event) {
        // Show a confirmation dialog
        let confirmation = confirm("Are you sure you want to log out?");

        // If the user clicks "Cancel", prevent the default link action
        if (!confirmation) {
          event.preventDefault();
          return false;
        }
        // If the user confirms, allow the default link action (logout)
        return true;
    }