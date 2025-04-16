vocabulary = getVocabulary();
document.addEventListener("click", function(e) {
    if (e.target.dataset.linkAction === "delete-address" || e.target.closest("[data-link-action='delete-address']")) {
        e.preventDefault(); // Prevent the default behavior
        const deleteButton = e.target.closest("[data-link-action='delete-address']");
        const addressId = deleteButton.dataset.addressId;
        const addressElement = document.getElementById(`address-${addressId}`);
        const csrftoken = getCookie('csrftoken');

        // Confirm deletion
        if (!confirm(vocabulary["Are you sure you want to delete this address?"])) {
            return;
        }

        // Construct the URL for deletion
        let url = window.config.deleteAddressUrl;
        url = url.replace("BIG", addressId);

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address_id: addressId })
        })
        .then(response => response.json())
        .then(data => {
        if(data.status === 'success') {
            // Fade out first
            addressElement.style.opacity = '0';
            addressElement.addEventListener('transitionend', function fadeOutComplete() {
                addressElement.removeEventListener('transitionend', fadeOutComplete);
                // Now collapse
                addressElement.style.height = '0';
                addressElement.style.padding = '0';
                addressElement.style.margin = '0';

                addressElement.addEventListener('transitionend', function collapseComplete() {
                    // This part changes:
                    // Instead of removing immediately, we use a timeout to ensure the
                    // CSS transitions have a moment to reflow the layout
                    setTimeout(() => {
                        addressElement.remove();
                        // Optionally, trigger a reflow of any JS-based layout or UI components here
                    }, 500); // This delay should match your longest transition duration
                }, { once: true });
            }, { once: true });
        } else {
            alert("Error deleting address: " + data.message);
        }
    })
        .catch(error => console.error('Error:', error));
    }
});