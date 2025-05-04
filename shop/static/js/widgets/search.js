(function(){
  const inputSearch = document.getElementById('input-search');
  if (inputSearch) {
    inputSearch.addEventListener('input', debouncedUpdateDropdown);
  }
  function getSearchUrls() {
    const metaTag = document.querySelector('meta[name="search-urls"]');
    if (metaTag) {
      try {
        return JSON.parse(metaTag.getAttribute("content"));
      } catch (error) {
        console.error("Error while parsing search-urls confing:", error);
      }
    } else {
      console.error('Meta tag with name "django-urls" was not found');
    }
    return {};
  }

  function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrftoken"]');
    return metaTag ? metaTag.getAttribute("content") : "";
  }

  const djangoData = getSearchUrls();
  const csrfToken = getCsrfToken();

  let debounceTimeout;
  function debouncedUpdateDropdown() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(updateDropdown, 200);
  }

  function updateDropdown() {
    const inputSearch = document.getElementById('input-search');
    if (!inputSearch) {
      console.error("Input-search element not found");
      return;
    }
    let inputVal = inputSearch.value;
    if (inputVal.length === 0) {
      document.getElementById('dropdown').innerHTML = '';
      return;
    }
    let fetchUrl = djangoData.fetchNumbersUrl + "?term=" + encodeURIComponent(inputVal);

    fetch(fetchUrl)
      .then(response => response.json())
      .then(data => {
        let dropdownHTML = '';
        data.forEach((item) => {
          dropdownHTML += `
            <div class="container-search-result" data-item-name="${item.name}">
              <img src="${item.image_url}" alt="Product Image" class="search-item-img">
              <div class="properties-search-container">
                <span class="name-search">${item.name}</span>
                <span class="product-name-search">${item.product_name}</span>
              </div>
            </div>
            <hr">
          `;
        });
        const dropdown = document.getElementById('dropdown');
        dropdown.innerHTML = dropdownHTML;

        const results = dropdown.querySelectorAll('.container-search-result');
        results.forEach(element => {
          element.addEventListener('click', function() {
            const productId = this.getAttribute('data-item-name');
            fillInput(productId);
          });
        });
      })
      .catch(error => console.error("Error fetching dropdown data:", error));
  }

  function fillInput(productId) {
    let urlPattern = djangoData.shopPageUrlPattern;
    if (!urlPattern) {
      console.error("shopPageUrlPattern is undefined");
      return;
    }
    let url = urlPattern.replace("DUMMY_ID", productId);

    let form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    let searchTypeInput = document.createElement('input');
    searchTypeInput.type = 'hidden';
    searchTypeInput.name = 'search_type';
    searchTypeInput.value = 'default';
    form.appendChild(searchTypeInput);

    let csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    document.body.appendChild(form);
    form.submit();
  }

  window.debouncedUpdateDropdown = debouncedUpdateDropdown;
})();