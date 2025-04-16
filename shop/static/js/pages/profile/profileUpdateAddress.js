document.addEventListener('DOMContentLoaded', function() {
    setCurrentCountry();
});

function setCurrentCountry(){
    let addressCountry = window.config.address.country;  // From your Django template
    let selectElement = document.querySelector('.form-control-select');
    for (let i = 0; i < selectElement.length; i++) {
        if (selectElement.options[i].text === addressCountry) {
            selectElement.selectedIndex = i;
            break;
        }
    }
}
const addressDict = window.config.address;
console.log(addressDict)
document.getElementById('form-address-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(document.getElementById('form-address-form'));
    const jsonObject = {
        old: addressDict, // Use the parsed JSON object directly
        new: Object.fromEntries(formData.entries())
    };
    const csrftoken = getCookie('csrftoken');

    let url = window.config.updateAddressUrl;
    url = url.replace("BIG", addressDict.address_id);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(jsonObject),
    })
    .then(response => response.json())
    .then(data => {
        console.log(vocabulary)
        alert(vocabulary["The address has been successfully updated!"]);

        window.location.href = window.config.profileAddressesUrl;
    }).catch(error => console.error('Error:', error));
});