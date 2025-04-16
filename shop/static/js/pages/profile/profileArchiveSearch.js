document.addEventListener("DOMContentLoaded", function() {
  const inputSearchArchived = document.getElementById("input-search-archived");
  if (inputSearchArchived) {
      inputSearchArchived.addEventListener("keyup", updateDropdownArchived);
  }
});
function updateDropdownArchived() {
    const inputElem = document.getElementById('input-search-archived');
    let inputVal = inputElem.value;
    if (inputVal.length === 0) {
        document.getElementById('dropdown-archive').innerHTML = '';
        return;
    }
    let fetchUrl = window.config.fetchNumbersUrl + "?term=" + encodeURIComponent(inputVal);
    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            let dropdownHTML = '';
            data.forEach((item) => {
                dropdownHTML += `
                    <div class="container-search-result" data-item-name="${item.name}">
                        <img src="${item.image_url}" alt="Product Image" class="img-search-archive">
                        <div class="properties-search-container-archive">
                            <span class="name-search-archive">${item.name}</span>
                            <span class="product-name-search-archive">${item.product_name}</span>
                        </div>
                    </div>
                    <hr class="products-divider">
                `;
            });
            const dropdown = document.getElementById('dropdown-archive');
            dropdown.innerHTML = dropdownHTML;

            const results = dropdown.querySelectorAll('.container-search-result');
            results.forEach(element => {
                element.addEventListener('click', function() {
                    const productId = this.getAttribute('data-item-name');
                    fillInputArchived(productId);
                });
            });
        })
        .catch(error => console.error("Error fetching dropdown data:", error));
}

function fillInputArchived(productId) {
    // Construct the URL using the product ID
    // Redirect to the constructed URL
    let url = window.config.shopPageUrlPattern;

    // Replace the placeholder "DUMMY_ID" with the actual productId dynamically
    url = url.replace('DUMMY_ID', productId);

    // Redirect to the dynamically constructed URL
    let form = document.createElement('form');
    form.method = 'POST';
    form.action = url;  // Keep productId in the URL as a GET parameter

    // Add a hidden input field for the search_type parameter
    let searchTypeInput = document.createElement('input');
    searchTypeInput.type = 'hidden';
    searchTypeInput.name = 'search_type';
    searchTypeInput.value = 'archived';
    form.appendChild(searchTypeInput);

    // Add a CSRF token if needed (for Django)
    let csrfToken = document.createElement('input');
    csrfToken.type = 'hidden';
    csrfToken.name = 'csrfmiddlewaretoken';
    csrfToken.value = getCookie('csrftoken');  // Django template variable for CSRF token
    form.appendChild(csrfToken);

    // Append the form to the body and submit it
    document.body.appendChild(form);
    form.submit();
}
