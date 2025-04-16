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
        console.error("Ошибка при парсинге django-urls:", error);
      }
    } else {
      console.error('Meta tag с именем "django-urls" не найден');
    }
    return {};
  }

  // Функция для получения CSRF токена из meta-тега
  function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrftoken"]');
    return metaTag ? metaTag.getAttribute("content") : "";
  }

  const djangoData = getSearchUrls();
  const csrfToken = getCsrfToken();

  let debounceTimeout;
  function debouncedUpdateDropdown() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(updateDropdown, 200); // Настройте задержку по необходимости
  }

  function updateDropdown() {
    const inputSearch = document.getElementById('input-search');
    if (!inputSearch) {
      console.error("Элемент input-search не найден");
      return;
    }
    let inputVal = inputSearch.value;
    if (inputVal.length === 0) {
      document.getElementById('dropdown').innerHTML = '';
      return;
    }
    // Формируем URL для поиска, подставляя значение из meta-тега
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
        // Назначаем обработчик клика для всех результатов без использования inline onclick
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
    // Получаем шаблон URL для страницы товара из meta-данных
    let urlPattern = djangoData.shopPageUrlPattern;  // например, "/shop/DUMMY_ID/"
    if (!urlPattern) {
      console.error("shopPageUrlPattern не определён");
      return;
    }
    // Заменяем маркер DUMMY_ID на фактический productId
    let url = urlPattern.replace("DUMMY_ID", productId);

    // Создаем форму для отправки POST-запроса
    let form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    // Добавляем скрытый инпут с параметром search_type
    let searchTypeInput = document.createElement('input');
    searchTypeInput.type = 'hidden';
    searchTypeInput.name = 'search_type';
    searchTypeInput.value = 'default';
    form.appendChild(searchTypeInput);

    // Добавляем скрытый инпут с CSRF-токеном
    let csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    document.body.appendChild(form);
    form.submit();
  }

  // Экспорт функций в глобальный объект, если потребуется использовать их вне данного файла
  window.debouncedUpdateDropdown = debouncedUpdateDropdown;
})();