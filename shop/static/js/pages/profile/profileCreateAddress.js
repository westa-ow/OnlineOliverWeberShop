
document.getElementById('form-address-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(document.getElementById('form-address-form'));
    const jsonObject = {
        address_data: Object.fromEntries(formData.entries())
    };
    const csrftoken = getCookie('csrftoken');
    fetch(window.config.createAddressUrl, { // Ensure the URL is correct
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(jsonObject),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert(vocabulary["The address has been successfully added!"]);
        window.location.href = window.config.profileAddressesUrl;
    }).catch(error => console.error('Error:', error));
});