function getMetaConfig() {
    const metaTag = document.querySelector('meta[name="config"]');
    if (metaTag) {
      try {
        // Если JSON в meta-теге сформирован с одинарными кавычками,
        // можно заменить их на двойные, чтобы JSON.parse сработал.
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

  // Функция для получения данных из <script id="config-data">
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

  // Функция объединяет оба объекта
  function getMergedConfig() {
    const metaConfig = getMetaConfig();
    const scriptConfig = getScriptConfig();
    // Объединяем: в случае совпадения ключей значения из scriptConfig будут иметь приоритет.
    return { ...metaConfig, ...scriptConfig };
  }

  // Глобально задаём объединённую конфигурацию
  window.config = getMergedConfig();
import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const { fetchItemsWithQuantityGreaterThan30, fetchFavouriteItems, fetchStones } = module;
            let vocabulary = getVocabulary();
            const show_quantities = window.config.show_quantities;
            let favouriteItems = [];
            let bestseller_items = window.config.bestseller_items;
            let sale = window.config.sale;
            const price_category = window.config.price_category;
            let bestsellers = [
                "22572R", "32034 001", "11025R", "11910R", "61125 BLU", "11030R", "11616 BLU", "11025G", "61191",
                "11815", "11321", "32003", "12309G", "61185", "11058", "11571R", "63520", "32088", "12066", "23140G",
                "11640R", "32022R", "22066R", "11819", "11910G", "32034G", "11903R", "32158R", "11615R", "22750R",
                "12007 202", "22066G", "22086", "11740 202", "11410", "32034 202", "22074R", "32091", "11984R 266",
                "11395", "11859", "11134", "11903G", "11879", "11765", "22426R", "12093", "11613RG", "63520L",
                "11182", "11571G", "22870", "11615RG", "32158RG", "12053", "11613R", "32037R", "32167", "32186R",
                "32160R", "11570R", "11605", "22708", "32034RG", "22750G", "11948", "11548R", "11743", "57004 WHI",
                "22331 001", "11752", "11025RG", "22074G", "22821 202", "11590", "61119", "32030R", "12234 206",
                "11792 BLU", "22082G", "22815 202", "22623 202", "22406G", "11246 202", "22186", "22145R", "11713",
                "22759 202", "22861", "11788", "32228R", "32165R", "22697", "22304 001", "11010", "12034", "22442",
                "22067", "11757 266", "22206G", "22388 001", "22646", "11126 229", "22778", "22082", "32160RG",
                "22778G", "11740 AB", "32186G", "11512G", "32184", "22329R", "12077", "11337", "12285", "11974 202",
                "32228G", "32257", "32326 001"
            ]

            function shuffleArray(array) {
                for (let i = array.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [array[i], array[j]] = [array[j], array[i]]; // Swap elements
                }
            }
            document.addEventListener("DOMContentLoaded", async function () {

                setupItemsCarousel();

                buildPageFavourites(bestseller_items);
                let unfilteredItems = await fetchItemsWithQuantityGreaterThan30(bestsellers); // Fetch all items on load
                let email = window.config.userEmail;
                favouriteItems = await fetchFavouriteItems(email);
                let {all: stones} = await fetchStones();
                bestseller_items = productsTransmutation(unfilteredItems, price_category, sale, stones, window.config.customer_type==="B2B");
                shuffleArray(bestseller_items);
                bestseller_items = bestseller_items.slice(0, 15);

                buildPageFavourites(bestseller_items);
            });


            function setupItemsCarousel(){
                const prev = document.getElementById('prev-btn');
                const next = document.getElementById('next-btn');
                const list = document.getElementById('item-list');

                const itemWidth = 250;
                let autoScroll = setInterval(function () {
                    list.scrollLeft += itemWidth;
                    // Reset to the beginning if it reaches the end
                    if (list.scrollWidth - list.clientWidth === list.scrollLeft) {
                        list.scrollLeft = 0;
                    }
                }, 6000); // Scroll every 9000 milliseconds

                prev.addEventListener('click', () => {
                    list.scrollLeft -= itemWidth;  // Adjusted to include gap
                    resetAutoScroll();
                });
                next.addEventListener('click', () => {
                    list.scrollLeft += itemWidth;  // Adjusted to include gap
                    resetAutoScroll();
                });

                function resetAutoScroll() {
                    clearInterval(autoScroll);
                    autoScroll = setInterval(function () {
                        list.scrollLeft += itemWidth;
                        // Reset to the beginning if it reaches the end
                        if (list.scrollWidth - list.clientWidth === list.scrollLeft) {
                            list.scrollLeft = 0;
                        }
                    }, 6000);
                }
            }

            function buildPageFavourites(items){

                if (bestseller_items.length > 0){
                    const productsGrid = document.querySelector('.item-list');
                    productsGrid.innerHTML = '';
                    let itemCounter= 0;

                    items.forEach((item) => {
                        // Append the product container to the products grid
                        productsGrid.appendChild(createProductCard(false, item, itemCounter, bestseller_items, bestseller_items, favouriteItems, window.config.preOrderIconUrl, vocabulary, translations_categories, currency, window.config.changeFavouritesStateUrl, show_quantities, window.config.addToCatalogUrl, getCookie('csrftoken'), window.config.cartUrl, window.config.isAuthenticated, window.config.shopPageUrl, false));
                        itemCounter+=1;
                    });
                }
                else{
                    console.log("Null");
                }
            }

        document.getElementById('product-card').addEventListener('click', async (event) => {
            const heartIconContainer = event.target.closest('.mobile-heart-container');
            if (!heartIconContainer) return;

            const item = JSON.parse(heartIconContainer.getAttribute('data-item-name')); // Assumes each heartIconContainer has `data-item-name`

            const favouriteItem = favouriteItems.find(item_fav => item_fav.name === item.name); // Assuming `item.name` is the name of your current item
            const isFavBefore = Boolean(favouriteItem); // Converts the result to a boolean


            // Stop the event from propagating to other elements
            event.stopPropagation();
            try {
                const response = await fetch(window.config.changeFavouritesStateUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({item: JSON.stringify(item), "alreadyFavourite": isFavBefore ? "true":"false"}),
                });

                if (!response.ok) throw new Error('Network response was not ok.');

                // Assuming the backend responds with the updated favorite status
                const data = await response.json();
                const isFavourite = data.isFavourite === "true";
                const itemToAddOrRemove = JSON.parse(data.item); // Assuming this is an object {name_id: "someId", ...}
                const existingTooltip = document.querySelector('.custom-tooltip');
                if (existingTooltip) {
                    existingTooltip.remove();
                }
                if (isFavourite) {
                    // Add to favoriteItems if not already present
                    const exists = favouriteItems.some(item => item.name === itemToAddOrRemove.name);
                    if (!exists) {
                        favouriteItems.push(itemToAddOrRemove);
                    }
                } else {
                    // Remove from favoriteItems
                    favouriteItems = favouriteItems.filter(item => item.name !== itemToAddOrRemove.name);
                }

                // Update the heart icon based on `isFavourite`
                heartIconContainer.innerHTML = isFavourite ?
                `<div class="favourites-mobile-container"><span class="mobile-favourites-btn">` + vocabulary['Remove from favorites'] + `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:#000000;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i> </span></div>` :
                `<div class="favourites-mobile-container"><span class="mobile-favourites-btn">` + vocabulary["Add to favorites"] + `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i> </span></div>`; // Example with FontAwesome

            } catch (error) {
                console.error('Error updating favorites:', error);
            }
        });

        // If there are multiple videos on a page
        // (for example, 5 videos in one row), you can implement
        // lazy-loading or playback control via JavaScript using
        // Intersection Observer. This will help to reduce
        // the load on the user's device
        document.addEventListener('DOMContentLoaded', function() {
            const videos = document.querySelectorAll('video');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.play();
                    } else {
                        entry.target.pause();
                    }
                });
            }, { threshold: 0.5 });
            videos.forEach(video => observer.observe(video));
        });

        document.addEventListener('click', (event) => {
            const clickedElement = event.target.closest('.card-carousel-item'); // Ищем ближайший родитель с этим классом

            if (clickedElement) {
                console.log("Clicked element has class card-carousel-item");
                let id = clickedElement.getAttribute('data-item-id');
                let dialog = document.getElementById('product-card');

                // Closing the dialog with animation
                closeDialogWithAnimation(dialog, true);

                // Wait for the animation to complete, then open a new window
                dialog.addEventListener(
                    'transitionend',
                    () => {
                        const favouriteItem = favouriteItems.find(item_fav => item_fav.name === id);
                        let itemIsFavourite = Boolean(favouriteItem);
                        generateDialogContent(
                            id,
                            bestseller_items,
                            currency,
                            show_quantities,
                            window.config.addToCatalogUrl,
                            vocabulary,
                            getCookie('csrftoken'),
                            window.config.cartUrl,
                            itemIsFavourite,
                            window.config.isAuthenticated,
                            window.config.shopPageUrl,
                            bestseller_items,
                            favouriteItems,
                            window.config.preOrderIconUrl,
                            window.config.changeFavouritesStateUrl,
                            translations_categories,
                            false
                        );
                    },
                    { once: true } // Remove the handler after the first execution
                );
            }
        });

    })
    .catch(error => {
        console.error("Ошибка при динамическом импорте:", error);
    });
