function getCheckoutMetaConfig() {
    const metaTag = document.querySelector('meta[name="cartConfig"]');
    if (metaTag) {
      try {
        const content = metaTag.getAttribute("content").replaceAll("'", '"');
        return JSON.parse(content);
      } catch (err) {
        console.error("Ошибка при парсинге meta tag config:", err);
      }
    } else {
      console.error('Meta tag с именем "config" не найден');
    }
    return {};
}
function getScriptConfig() {
    const configScript = document.getElementById('config-data');
    if (configScript) {
      try {
        return JSON.parse(configScript.textContent);
      } catch (err) {
        console.error("Ошибка при парсинге config-data из script:", err);
      }
    } else {
      console.error('Элемент с id "config-data" не найден');
    }
    return {};
}
function getMergedConfig() {
    const metaConfig = getCheckoutMetaConfig();
    const scriptConfig = getScriptConfig();
    return { ...metaConfig, ...scriptConfig };
}
window.config = {
  ...(window.config || {}),
  ...getMergedConfig()
};

import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const {fetchAllItems, fetchFavouriteItems, fetchStones} = module;

        let product_documents = [];
        let sale = window.config.sale;
        let price_category = window.config.price_category;
        let allItems = {};
        let favouriteItems = {};
        const show_quantities = window.config.show_quantities;
        function init() {
            product_documents = window.config.documents;
            console.log("WE BEGIN");
            calculate_final(0, 0, currency, product_documents);
        }
        async function initializeContent(){
            showOverlay();

           let unfilteredItems = await fetchAllItems();
           let email = window.config.user_email;
           favouriteItems = await fetchFavouriteItems(email);
           let {all: stones} = await fetchStones();

           allItems = productsTransmutation(unfilteredItems, price_category, sale, stones, window.config.customer_type==="B2B");

           isCheckout = true;
           init();

           document.querySelectorAll('.document-container').forEach(documentContainer => {
              const dataDocument = documentContainer.getAttribute('data-document');
              const doc = JSON.parse(dataDocument.replaceAll("'",'"'));

              saveState('quantity-'+doc.name, doc.quantity)
           });
           updateCarouselItems();

           hideOverlay();
        }

        function updateCarouselItems(){
           let similarItems = [];
           product_documents.forEach(product => {
             similarItems.push(...(productGroups[product.product_name] || []));
           });
           similarItems = [...new Set(similarItems)];
           similarItems = similarItems.filter(similarItem => {
              return !product_documents.some(cartItem => getNormalizedItemName(cartItem.name, cartItem) === similarItem);
           });
           const filteredItems = allItems.filter(item => similarItems.includes(getNormalizedItemName(item.name, item)));

           if (filteredItems.length > 0){
               const containerCarousel = document.querySelector('.complementary-products');
               containerCarousel.style.display = "block";
               // Now build the carousel items dynamically
               const carouselContainer = document.querySelector('.carousel-items');

               // Clear any existing content if necessary
               carouselContainer.innerHTML = '';

               filteredItems.forEach((item, index) => {
                  const carouselItem = document.createElement('div');
                  carouselItem.classList.add('carousel-product');

                  const img = document.createElement('img');
                  img.src = item.image_url;
                  img.alt = item.name;

                  const p = document.createElement('p');
                  p.textContent = `${index + 1}. ${item.name}`;

                  carouselContainer.appendChild(createProductCard(false, item, index, allItems, filteredItems, favouriteItems, window.config.preOrderIconUrl, vocabulary, translations_categories, currency, window.config.changeFavouritesStateUrl, show_quantities, window.config.addToCatalogUrl, getCookie('csrftoken'), window.config.cartUrl, window.config.isAuthenticated, window.config.shopPageUrl, true));
               });

               constructCarousel();
           }
           else{
               const containerCarousel = document.querySelector('.complementary-products');
               containerCarousel.style.display = "none";
           }
        }

        function constructCarousel(){
          const leftArrow = document.querySelector('.left-arrow');
          const rightArrow = document.querySelector('.right-arrow');
          const carousel = document.querySelector('.carousel-items');

          leftArrow.addEventListener('click', () => {
            carousel.scrollBy({
              left: -300, // adjust scroll distance as needed
              behavior: 'smooth'
            });
          });

          rightArrow.addEventListener('click', () => {
            carousel.scrollBy({
              left: 300, // adjust scroll distance as needed
              behavior: 'smooth'
            });
          });
        }

        function parameters_final(productId, newQuantity){
            product_documents = product_documents.map(doc => {
                if (doc.name === productId) {
                    doc.quantity = newQuantity;
                }
                return doc;

            });
            calculate_final(0,0, currency, product_documents);
        }
        function saveState(name, value) {
            localStorage.setItem(name, value);
        }


        document.querySelectorAll('.slider-body input[type="number"]').forEach(slider => slider.addEventListener('input', function(event) {
             const input = event.target;
             const documentContainer = input.closest('.document-container');
             const documentValue = JSON.parse(documentContainer.getAttribute('data-document').replace(/'/g, '"'));
             const productId = documentValue['name'];

             const button = document.getElementById("quantity-input-apply-" + productId);
             button.innerText = vocabulary["Confirm"];
             button.style.background = "#003665";

             const inp = document.getElementById('quantity-input-inp-' + productId);
             const quantity = parseInt(inp.value);

             if (isNaN(quantity) || quantity <= 0) {
                alert(vocabulary["Type of written quantity has to be numeric and greater than 0"]);
                inp.value = 1;
             } else if (quantity > documentValue.quantity_max) {
                alert(vocabulary["Quantity has to be less than maximum on storage"]);
                inp.value = documentValue.quantity_max;
             }
        }));

        document.getElementById('documents-list').addEventListener('click', function(event) {

            let deleteButton = event.target.closest('.deleteBut');
            if (deleteButton) {
                const documentId = deleteButton.getAttribute('data-product-id');
                const documentContainer = deleteButton.closest('.document-container');

                const confirmed = confirm(vocabulary["Do you really want to delete this product from your cart?"]);

                if (confirmed) {
                    deleteBut(documentId, documentContainer);
                }
            }

            const quantityInputButton = event.target.closest('.quantity-input-button');
            if (quantityInputButton) {
                const documentContainer = quantityInputButton.closest('.document-container');
                const documentValue = JSON.parse(documentContainer.getAttribute('data-document').replace(/'/g, '"'));
                const productId = documentValue['name'];

                const inp = document.getElementById('quantity-input-inp-' + productId);
                const quantity = parseInt(inp.value);

                if (isNaN(quantity) || quantity <= 0) {
                    alert(vocabulary["Type of written quantity has to be numeric and greater than 0"]);
                }
                else if (quantity > documentValue.quantity_max) {
                    alert(vocabulary["Quantity has to be less than maximum on storage"]);
                }
                else {
                    updateQuantityInput(productId, quantity, documentValue);
                }
            }
        });

        function updateQuantityInput(product_id, quantity_new, doc) {
            fetch(window.config.updateInputUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: product_id, quantity_new: quantity_new, 'document': doc, price:doc.price})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {

                    changeCurrentQuantityText(product_id, quantity_new);

                    const button = document.getElementById("quantity-input-apply-"+ product_id);
                    button.innerText = vocabulary["Confirmed!"];
                    button.style.background = "#077a07";

                    const sum  = document.getElementById('sum-'+data.product_id);
                    sum.innerHTML = currency+ "" + data.sum;

                    saveState('sum-'+product_id, data.sum);
                    saveState('quantity-'+data.product_id, data.quantity);
                    parameters_final(product_id, quantity_new);
                } else {
                }
            });
        }

        function deleteBut(documentId, documentContainer){
            fetch(window.config.deleteDocumentUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ document_id: documentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    let documents = product_documents.filter(doc => doc.name !== documentId);
                    product_documents = product_documents.filter(doc => doc.name !== documentId);
                    console.log('Document deleted successfully');
                    documentContainer.remove();

                    data.updated_documents.forEach(doc => {
                        console.log(`${doc.id}`);
                        let docElement = document.querySelector(`[data-document-id="${doc.id}"]`);
                        console.log(docElement);
                    });
                    updateCarouselItems();
                    calculate_final(0,0, currency, documents);
                  } else {
                      console.error('Error in deletion');
                  }
            })
            .catch(error => console.error('Error:', error));
        }

        document.getElementById('finishOrderButton').addEventListener('click', function() {
            if (product_documents.length > 0){
                if (window.config.isAuthenticated) {
                    window.location.href = window.config.checkoutAddressesUrl;
                }
                else{
                    window.location.href = window.config.checkoutAnonymUrl;
                }
            }
            else{
                alert(vocabulary["You must add at least 1 order to your cart to proceed to checkout"])
            }
        });

        document.getElementById("promocode-label").addEventListener('click', function () {
            document.getElementById('overlay-cart').classList.remove('hidden');
            document.getElementById('promo-modal').classList.remove('hidden');
        });

        document.getElementById('close-modal').addEventListener('click', closeModal);
        document.getElementById('overlay-cart').addEventListener('click', closeModal);

        document.getElementById('submit-promocode').addEventListener('click', function () {
            const submitButton = document.getElementById('submit-promocode');
            const promocode = document.getElementById('promocode-input').value;
            const errorMessage = document.getElementById('error-message');
            console.log(promocode);
            submitButton.setAttribute('disabled', 'true');
            fetch(window.config.checkPromocodeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ promocode: promocode })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();
                } else {
                    errorMessage.classList.remove('hidden');
                    errorMessage.textContent = data.message || 'Something went wrong';
                    submitButton.removeAttribute('disabled');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitButton.removeAttribute('disabled');
            });
        });

        function closeModal() {
            document.getElementById('overlay-cart').classList.add('hidden');
            document.getElementById('promo-modal').classList.add('hidden');
            document.getElementById('promocode-input').value = '';
            document.getElementById('error-message').classList.add('hidden');
        }
        function changeCurrentQuantityText(productId, quantity){
            const current_quantity = document.getElementById('current-quantity-'+productId);
            current_quantity.innerText = vocabulary["In cart"] + ": "+ quantity;
        }
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initializeContent);
        } else {
          initializeContent();
        }

     })
    .catch(error => {
        console.error("Ошибка при динамическом импорте:", error);
    });