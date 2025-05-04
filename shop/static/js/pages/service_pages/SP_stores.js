let map;
let geocoder;
let markers = [];
const API_ROOT   = document.querySelector('meta[name="api-root"]').getAttribute('content');

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 50.0755, lng: 14.4378 }, // Prague by default, its a plug
        zoom: 6,
        disableDefaultUI: true,
    });
    geocoder = new google.maps.Geocoder();

    document.getElementById('find').addEventListener('click', function() {
        const useraddress = document.getElementById('user-address').value;
        const radius = document.getElementById('radius').value;

        if (!useraddress) {
            alert(vocabulary['Please enter the address, zip / postal code, city or country.']);
            return;
        }

        geocoder.geocode({ 'address': useraddress }, function(results, status) {
            if (status === 'OK') {
                map.setCenter(results[0].geometry.location);
                map.setZoom(12);
                clearMarkers();
                let url = API_ROOT + `stores/nearby/?useraddress=${useraddress}&radius=${radius}`
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        const list = document.getElementById('result-list');
                        list.innerHTML = '';
                        if (data && data.length > 0) {
                            data.forEach(item => {
                                const pos = { lat: item.latitude, lng: item.longitude };
                                const marker = new google.maps.Marker({ map: map, position: pos, title: item.name || item.address });
                                markers.push(marker);
                                const listItem = document.createElement('li');

                                const iconItem = document.createElement('i');
                                iconItem.classList.add('fa-solid', 'fa-location-dot');

                                const listText = document.createElement('span');
                                listText.textContent =  ` ${item.name || item.address} (${item.distance_km} km) `;

                                const routeLink = document.createElement('a');
                                routeLink.classList.add('btn-show-route');
                                routeLink.href = `https://www.google.com/maps/place/${item.latitude} + ${item.longitude}`;
                                routeLink.textContent = vocabulary['Show route'];
                                routeLink.target = '_blank';
                                routeLink.rel = 'noopener noreferrer';

                                listItem.appendChild(iconItem);
                                listItem.appendChild(listText);
                                listItem.appendChild(routeLink);
                                list.appendChild(listItem);
                            });
                        } else {
                            list.innerHTML = `<li> ${vocabulary['No stores were found in the area.']} </li>`;
                        }
                    })
                    .catch(error => {
                        console.error("Error while data retrieve:", error);
                        const list = document.getElementById('result-list');
                        list.innerHTML = `<li>{${vocabulary["An error occurred while loading stores."]}</li>`;
                    });

            } else {
                alert("Error: " + status);
            }
        });
    });
}

function clearMarkers() {
    markers.forEach(m => m.setMap(null));
    markers = [];
}

const addressInput = document.getElementById('user-address');
const addressSuggestions = document.getElementById('address-suggestions');
addressInput.addEventListener('input', async () => {
    const query = addressInput.value.trim();
    if (query.length > 2) {
        const suggestions = await getAddressSuggestions(query);
        showSuggestions(addressInput, addressSuggestions, suggestions);
    } else {
        addressSuggestions.innerHTML = '';
    }
});

async function getAddressSuggestions(query) {
    if (!query.trim()) {
        return [];
    }
    try {
        let url = API_ROOT + `stores/get_suggestions/?query=${query}`
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error while addresses retrieving:', response.status);
            return [];
        }
    } catch (error) {
        console.error('Error while addresses retrieving:', error);
        return [];
    }
}

function showSuggestions(inputElement, suggestionsElement, suggestions) {
    suggestionsElement.innerHTML = '';
    if (suggestions && suggestions.length > 0) {
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.classList.add('address-suggestion');
            div.textContent = suggestion;
            div.addEventListener('click', () => {
                inputElement.value = suggestion;
                suggestionsElement.innerHTML = '';
            });
            suggestionsElement.appendChild(div);
        });
    }
}
