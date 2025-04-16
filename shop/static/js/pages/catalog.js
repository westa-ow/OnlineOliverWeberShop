function getCatalogMetaConfig() {
    const metaTag = document.querySelector('meta[name="catalog_config"]');
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
window.config = getCatalogMetaConfig();

import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const {fetchAllItems, fetchFavouriteItems, fetchStones} = module;

        let vocabulary = getVocabulary()
        let sale = window.config.sale;
        const price_category = window.config.price_category;
        const show_quantities = window.config.show_quantities;
        let itemsPerPage = 20;
        let order_name = "Name";
        let order_type = "asc";
        let number_of_documents;
        let currentPage = 1;
        let total_pages = 1;
        let allItems = [];
        let favouriteItems = [];
        let filteredItems = [];
        let filters = [];
        let stones = {};
        let stones_reversed = {};
        let platingFilters =  window.config.plating_catalog ? [window.config.plating_catalog] : [];
        let baseFilters = window.config.base_catalog ? [window.config.base_catalog] : [];
        let stoneFilters = [];
        let sizeFilters = [];
        let subcat = {"Necklaces": ["Necklace","Chain","Pearlchain", "Pendant", "Collier"], "All Earrings": ["Earrings","Post Earrings", "Clip", "Hoop", "Creole"], "Bracelets":["Bracelet","Bangle", "Anklet"],"Accessories":[ "Nailfile", "Pen","Key","Brooch", "Match", "Extension"]}
        let category = window.config.category_catalog || "All";
        let collection_catalog = window.config.collection_catalog || "";
        let categories = [""];
        let all_crystals = [];
        let all_platings = [];
        let all_bases = [];
        let fromSlider = document.querySelector('#fromSlider');
        let toSlider = document.querySelector('#toSlider');
        let fromInputText = document.querySelector('.fromInput-text');
        let toInputText = document.querySelector('.toInput-text');

        document.addEventListener("DOMContentLoaded", async function () {
            fromSlider = document.querySelector('#fromSlider');
            toSlider = document.querySelector('#toSlider');
            fromInputText = document.querySelector('.fromInput-text');
            toInputText = document.querySelector('.toInput-text');
            showOverlay();

            itemsPerPage = Number(document.getElementById('select-items-per-page').value);

            let unfilteredItems = await fetchAllItems(); // Fetch all items on load

            favouriteItems = await fetchFavouriteItems(window.config.userEmail);

            ({ all: stones, reversed: stones_reversed } = await fetchStones());

            allItems = productsTransmutation(unfilteredItems, price_category, sale, stones, window.config.customer_type==="B2B");


            total_pages = Math.ceil(allItems.length / itemsPerPage);

            updatePage();

            buildUpPages();
            changePage(currentPage);

            constructCategories();
            const categoriesLabel = document.querySelector('.categories-label');
            const categories = document.querySelector('.categories');

            categoriesLabel.addEventListener('click', function() {
                categories.classList.toggle('collapsed');
            });

            const crystal_imgs_folder = window.config.crystalImgsFolder;

            constructFilters(allItems, filters_dict, crystal_imgs_folder);

            setupFiltersEventListeners('.plating-checkbox', platingFilters);
            setupFiltersEventListeners('.base-checkbox', baseFilters);
            setupFiltersEventListeners('.size-checkbox', sizeFilters);

            applyFilters();
            updateURL();
            hideOverlay();
            responsiveLayout();
        });
        function responsiveLayout(){
            let mql = window.matchMedia("(max-width: 769px)");
            if( mql.matches) {
                document.getElementById('categoriesPanel').classList.toggle('collapsed');
                document.getElementById('filtersPanel').classList.toggle('collapsed-filters');
                document.getElementById('iconFiltersCollaps').classList.remove('fa-plus');
                document.getElementById('iconFiltersCollaps').classList.add('fa-minus');
            }

        }
        document.getElementById('filtersCollapsTrigger').addEventListener('click', function() {
           document.getElementById('filtersPanel').classList.toggle('collapsed-filters');
           if(document.getElementById('iconFiltersCollaps').classList.contains('fa-plus')){
                document.getElementById('iconFiltersCollaps').classList.remove('fa-plus');
                document.getElementById('iconFiltersCollaps').classList.add('fa-minus');
           }else{
                document.getElementById('iconFiltersCollaps').classList.remove('fa-minus');
                document.getElementById('iconFiltersCollaps').classList.add('fa-plus');
           }
        });
        document.addEventListener('click', (event) => {
            const clickedElement = event.target.closest('.card-carousel-item');

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
                            allItems,
                            currency,
                            show_quantities,
                            window.config.addToCatalogUrl,
                            vocabulary,
                            getCookie('csrftoken'),
                            indow.config.cartUrl,
                            itemIsFavourite,
                            window.config.isAuthenticated,
                            window.config.shopPageUrl,
                            allItems,
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
        function buildUpPages() {
            const pagesContainer = document.getElementById('current-page');
            let pagesToShow = document.createDocumentFragment(); // Use a document fragment to hold elements before inserting them into the DOM

            function addPageLink(page, isCurrentPage) {
                const pageElement = document.createElement('a');
                if (isCurrentPage) {
                    const boldText = document.createElement('b');
                    boldText.textContent = page;
                    if(currentPage === 1){
                        boldText.style.padding = '10px';
                    }
                    pagesToShow.appendChild(boldText);
                } else {
                    pageElement.href = "";
                    pageElement.textContent = page;
                    pageElement.addEventListener('click', function(event) {
                        event.preventDefault();
                        changePage(page);
                    });
                    pagesToShow.appendChild(pageElement);
                }
                pagesToShow.appendChild(document.createTextNode(' ')); // Add space between links
            }

            function addEllipsis() {
                pagesToShow.appendChild(document.createTextNode('... '));
            }

            if (total_pages <= 5) {
                for (let i = 1; i <= total_pages; i++) {
                    addPageLink(i, i === currentPage);
                }
            } else {
                addPageLink(1, currentPage === 1);

                if (currentPage > 3) {
                    addEllipsis();
                }

                let startPage = Math.max(2, currentPage - 1);
                let endPage = Math.min(currentPage + 1, total_pages - 1);

                if (currentPage === 1) {
                    endPage = Math.min(3, total_pages - 1);
                } else if (currentPage === total_pages) {
                    startPage = Math.max(total_pages - 2, 2);
                }

                for (let i = startPage; i <= endPage; i++) {
                    addPageLink(i, i === currentPage);
                }

                if (currentPage < total_pages - 2) {
                    addEllipsis();
                }

                addPageLink(total_pages, currentPage === total_pages);
            }

            // Clear the current content and append the new set of page links
            pagesContainer.innerHTML = '';
            pagesContainer.appendChild(pagesToShow);
        }
        function changePage(page) {
            if(page === 1){
                document.getElementById("previous-button").style.display = 'none';
            }
            else{
                document.getElementById("previous-button").style.display = 'block';
            }
            if(page === total_pages){
                document.getElementById("next-button").style.display = 'none';
            }
            else{
                document.getElementById("next-button").style.display = 'block';
            }
            currentPage = page;
            updatePage(); // Assuming you have this function implemented to refresh the content based on the current page

            buildUpPages();
        }
        function constructCategories(){
            const categories_div = document.querySelector('.categories');
            const categoriesList = document.querySelector('.categories-list');
            categoriesList.innerHTML = ''; // Clear existing list items

            // Assuming 'subcat' is defined globally
            const generalCategories = Object.keys(subcat);
            const subCategories = new Set([].concat(...Object.values(subcat)));

            let categories = allItems.reduce((acc, item) => {
                if (!acc.includes(item.category) && !subcat.hasOwnProperty(item.category)) {
                    acc.push(item.category);
                }
                return acc;
            }, []);

            const categoryList = ["All", ...generalCategories, ...categories];

            categoryList.forEach(categoryVar => {

                if (subCategories.has(categoryVar)) return; // Skip adding sub-categories here

                const li = document.createElement('li');

                const categorySpan = createCategorySpan(categoryVar);
                const categoryDivForLi = document.createElement('div');
                categoryDivForLi.classList.add('container-subcategories');
                categoryDivForLi.appendChild(categorySpan);
                li.appendChild(categoryDivForLi);
                categoriesList.appendChild(li);

                if (subcat.hasOwnProperty(categoryVar)) {
                    const chevron = createChevron();
                    categoryDivForLi.appendChild(chevron);
                    const ul = createSubCategoryList(subcat[categoryVar]);
                    li.appendChild(ul);

                    setupChevronToggle(chevron, ul);
                }

                setupCategoryClickListener(categorySpan);
            });

            categories_div.style.display = 'block';
        }


        function constructCollections(){
            const collections_div = document.querySelector('.collections');
            const collectionsList = document.querySelector('.collections-list');
            collectionsList.innerHTML = ''; // Clear existing list items

            let collections = allItems.reduce((acc, item) => {
                if (!acc.includes(item.collection)) {
                    acc.push(item.collection);
                }
                return acc;
            }, []);
            const index = collections.indexOf("");
            if (index > -1) { // only splice array when item is found
              collections.splice(index, 1); // 2nd parameter means remove one item only
            }
            const collectionList = ["All", ...collections];
            collectionList.forEach(collectionVar => {

                const li = document.createElement('li');

                const collectionSpan = createCollectionSpan(collectionVar);
                const collectionDivForLi = document.createElement('div');
                collectionDivForLi.appendChild(collectionSpan);
                li.appendChild(collectionDivForLi);
                collectionsList.appendChild(li);

                setupCollectionClickListener(collectionSpan);
            });

            collections_div.style.display = 'block';
        }


        function createCollectionSpan(currentCollection) {
            const span = document.createElement('span');
            span.textContent = synonyms_collections[currentCollection];
            span.setAttribute("data-collection-name", currentCollection);
            span.className = 'collection-name';

            if (currentCollection === collection_catalog) span.style.fontWeight = "600";
            return span;
        }

        // This function is used to set up a click listener for a category span element
        function setupCollectionClickListener(span) {
            span.addEventListener('click', () => {
                document.querySelectorAll('.collections-list li span').forEach(li => li.style.fontWeight = "");
                collection_catalog = span.getAttribute("data-collection-name"); // Assuming 'category' is a global variable
                span.style.fontWeight = "600";
                const newUrl = `?collection=${encodeURIComponent(collection_catalog)}`;
                history.pushState({path: newUrl}, '', newUrl);

                applyFilters(); // Call the applyFilters function
                updateURL();
            });
        }

        // This function is used to create a span element for a category
        function createCategorySpan(currentCategory) {
            const span = document.createElement('span');
            span.textContent = synonyms[currentCategory];
            span.setAttribute("data-category-name", currentCategory);
            span.setAttribute("category-id", categories_codes[currentCategory]);
            span.className = 'category-name';
            console.log(currentCategory);

            if (currentCategory === category) span.style.fontWeight = "600";
            return span;
        }

        // This function creates a chevron element for categories
        function createChevron() {
            const chevron = document.createElement('i');
            chevron.className = 'fa-solid fa-chevron-down';
            chevron.style.cursor = "pointer";
            return chevron;
        }

        //This function creates a list of subcategories
        function createSubCategoryList(subCategories) {
            const ul = document.createElement('ul');
            ul.className = 'sub-category-list';
            subCategories.forEach(sub => {
                const subLi = document.createElement('li');
                const subSpan = document.createElement('span');
                subSpan.setAttribute("data-category-name", sub);
                subSpan.textContent = synonyms[sub];
                subLi.appendChild(subSpan);
                ul.appendChild(subLi);
                setupCategoryClickListener(subSpan);
            });
            return ul;
        }

        //This function adds click listener to list chevron
        function setupChevronToggle(chevron, ul) {
            chevron.addEventListener('click', () => {
                const isOpen = ul.style.height !== '0px' && ul.style.height !== '';
                if (isOpen) {
                    ul.style.height = '0'; // Close the ul by setting height to 0
                    chevron.className = 'fa-solid fa-chevron-down';
                } else {
                    ul.style.height = `${ul.scrollHeight}px`; // Open the ul by setting height to its natural height
                    chevron.className = 'fa-solid fa-chevron-up';
                }
            });
        }

        // This function adds click listener to category's span
        function setupCategoryClickListener(span) {
            span.addEventListener('click', () => {
                document.querySelectorAll('.categories-list li span').forEach(li => li.style.fontWeight = "");
                category = span.getAttribute("data-category-name"); // Assuming 'category' is a global variable
                span.style.fontWeight = "600";

                applyFilters(); // Call the applyFilters function
                updateURL();
            });
        }

        //This function is used to add corresponding category to crystal span
        function constructCrystals(items, filters_dict, static_folder) {
            let uniqueStones = new Set();
            let stones_all = ['241', '327', '515', '260', '288', '501', '208', '227', '220', 'DAR', '276', '379', '205', '277', '922', '280', '243', '204', '291', '236', '215', '228', '502', '207', '203', '219', '206', '147', '0', '394', '266', '289', '539', '542', '920', '398', '142', '229', '214', '226', '209', 'GSHA', '390', '263', '391', '267', '292', '212', '257', '202', '371', '262', '283', '211', '319', '261', '238', '362', '265', '223', '508', 'CRE', '234', '395', '361', '285', '001', 'AB'];
            let stones_names = []
            for (let i = 0; i < stones_all.length; i++) {
              stones_names[i] = stones[stones_all[i]];
            }

            if (Array.isArray(items) && items.length > 0) {
                items.forEach(document => {
                    if (document.platings) { // Check if there is a platings in document
                        Object.values(document.platings).forEach(plating => {
                            if (plating.stones) { //  Check if there is a stones in plating
                                Object.keys(plating.stones).forEach(stoneCategory => {
                                    if (stones_names.includes(stoneCategory)) { // Check if there is a stoneCategory in stones
                                        uniqueStones.add(stoneCategory);
                                    }
                                });
                            }
                        });
                    }
                });
            } else {
                console.log("Items is either empty or not an array.");
            }

            createCrystalElements('crystals',Array.from(uniqueStones), 'crystal', filters_dict, static_folder);
        }
        //This function creates the crystal elements and applies the honeycomb layout
        function createCrystalElements(containerClass, itemsArray, prefix, filters_dict, static_folder) {
            const container = document.querySelector(`.${containerClass}`);
            container.innerHTML = ''; // Clear existing content

            // Create a div to hold the images in a grid
            const grid = document.createElement('div');
            grid.className = 'crystal-grid';
            let imagesLoaded = 0;
            // Loop through images and create an img element within a div for each
            itemsArray.forEach((item, index) => {
                const img = new Image();
                img.width = 20;
                img.height = 20;
                img.src = `${static_folder}/${stones_reversed[item]}.png`;
                img.alt = `Crystal ${index + 1}`;
                img.className = 'crystal-image';

                img.onload = () => {
                    const imgDiv = document.createElement('div');
                    imgDiv.className = 'crystal-container';
                    imgDiv.setAttribute('data-value', item); // Set the crystal number

                    imgDiv.appendChild(img);
                    grid.appendChild(imgDiv);
                    imagesLoaded++;

                    // Check if all images are loaded
                    if (imagesLoaded === itemsArray.length) {
                        // Apply the honeycomb layout
                        // Set up click event listeners for the crystals
                        setupCrystalClickListeners(stoneFilters);
                    }
                };

                img.addEventListener('mouseenter', (event) => {

                    showTooltip(event, item);
                });
            });

            // Append the grid to the container
            container.appendChild(grid);

            // Apply the honeycomb layout
            applyHoneycombLayout(grid);
        }


        // Function to apply honeycomb layout
        function applyHoneycombLayout(grid) {
            const containers = grid.querySelectorAll('.crystal-container');
            containers.forEach((container, index) => {
                if (Math.floor(index / 4) % 3 === 1) {
                    container.style.marginLeft = '30px'; // Adjust as needed for our layout
                } else {
                    container.style.marginLeft = '0';
                }
            });
        }


        // Function to simulate changing the page (I might have my actual logic to fetch/update content here)
        function setupCrystalClickListeners(filtersArray) {
            const containers = document.querySelectorAll('.crystal-container');

            containers.forEach(container => {
                container.addEventListener('click', function() {
                    removeTooltip();
                    const remove_button = this.parentElement.parentElement.parentElement.querySelector('.remove-filters-container');
                    let selectedValue = this.getAttribute('data-value');
                    // Remove 'selected' class from all containers
                    containers.forEach(c => {
                        c.children[0].classList.remove('selected');

                    });

                    // Add 'selected' class to the clicked container
                    container.children[0].classList.add('selected');
                    filtersArray.length = 0;
                    remove_button.style.display = "block";
                    filtersArray.push(selectedValue);
                    // Perform the required action when a crystal is clicked
                    console.log(`Crystal clicked: ${container.getAttribute('data-value')}`);
                    // Add your filtering logic here
                    applyFilters();
                    updateURL();
                });
            });
        }

        // This function adds click listeners to filter, so after clicking them some specific actions will be performed
        function setupFiltersEventListeners(checkboxClassName, filtersArray) {
            document.querySelectorAll(checkboxClassName).forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const checkboxes = document.querySelectorAll(checkboxClassName);
                    const remove_button = this.parentElement.parentElement.parentElement.querySelector('.remove-filters-container');
                    const label = this.parentElement.querySelector('label');
                    let textValue = this.value;

                    if (this.checked) {
                        toggleOffUnnecessaryCheckboxes(checkboxes, textValue);
                        filtersArray.length = 0; // Clear the filters array
                        remove_button.style.display = "block";
                        label.style.fontWeight = "600";
                        filtersArray.push(textValue);
                    } else {
                        filtersArray.splice(filtersArray.indexOf(textValue), 1);
                        if (filtersArray.length === 0) {
                            remove_button.style.display = "none"; // Hide remove button if filters array is empty
                        }
                        label.style.fontWeight = "";
                    }

                    applyFilters();
                    updateURL();
                });
            });
            document.querySelectorAll(checkboxClassName).forEach(checkbox => {
                if (filtersArray.includes(checkbox.value)) {
                    // Programmatically check the checkbox without triggering the event
                    checkbox.checked = true;

                    // Now manually trigger the change event
                    let event = new Event('change', {
                        'bubbles': true,
                        'cancelable': true
                    });
                    checkbox.dispatchEvent(event);
                }
            });
        }

        //This function is responsible for updating the URL based on the selected filters
        function updateURL() {
            const currentUrl = new URL(window.location.href);

            // Extract the language code from the current path
            const pathSegments = currentUrl.pathname.split('/').filter(segment => segment); // Remove the empty segments
            let categoryPath = '';

            // Check if category is specified, add it to the path
            if (category) {

                let code = categories_codes[category.toString()];
                if(!code) code="404";
                let cat_name_url = code + "-" + categories_code_to_name[code];
                // If there is already a category in the URL, replace it with
                if (pathSegments[1]) {
                    pathSegments[1] = cat_name_url;
                } else {
                    // If there is no category, add a new one
                    pathSegments.push(cat_name_url);
                }
                categoryPath = pathSegments.slice(0, 2).join('/');
            } else {
                // If no category is specified, leave the current path
                categoryPath = pathSegments.join('/');
            }

            // Generate a base URL with the current language code and category
            const baseUrl = `${window.location.protocol}//${window.location.host}/${categoryPath}`;

            // Create and fill queryParams with filter parameters
            const queryParams = new URLSearchParams();
            if (collection_catalog) {
                queryParams.set('collection', collection_catalog);
            }
            if (baseFilters.length > 0) {
                queryParams.set('base', baseFilters.join(','));
            }
            if (platingFilters.length > 0) {
                queryParams.set('plating', platingFilters.join(','));
            }
            if (stoneFilters.length > 0) {
                queryParams.set('crystal', stoneFilters.join(','));
            }
            if (sizeFilters.length > 0) {
                queryParams.set('size', sizeFilters.join(','));
            }

            // Update URL using history.pushState
            const newUrl = queryParams.toString() ? `${baseUrl}?${queryParams.toString()}` : baseUrl;
            history.pushState({}, '', newUrl);
        }


        function toggleOffUnnecessaryCheckboxes(checkboxes, currentValue ){
            checkboxes.forEach(checkbox => {
                if (checkbox.value !== currentValue) {
                    checkbox.checked = false;
                    checkbox.parentElement.querySelector('label').style.fontWeight = "";
                }
            });
        }


        document.querySelectorAll('.remove-filters-container').forEach(container=> {
            container.addEventListener('click', function (){
               if(container.id === "platings"){
                    platingFilters.length = 0;
                    const platingCheckboxes = document.querySelectorAll('.plating-checkbox');
                    platingCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                        checkbox.parentElement.querySelector('label').style.fontWeight = "";
                    });
                    removeQueryParam('plating');
               }
               else if(container.id === "sizes"){
                    sizeFilters.length = 0;
                    const sizesCheckboxes = document.querySelectorAll('.size-checkbox');
                    sizesCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                        checkbox.parentElement.querySelector('label').style.fontWeight = "";
                    });
                    removeQueryParam('size');
               }
               else if(container.id === "bases"){
                    baseFilters.length = 0;
                    const baseCheckboxes = document.querySelectorAll('.base-checkbox');
                    baseCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                        checkbox.parentElement.querySelector('label').style.fontWeight = "";
                    });
                    removeQueryParam('base');
               }
               else if(container.id === "crystals"){
                    stoneFilters.length = 0;
                    const crystal_checkboxes = document.querySelectorAll('.crystal-checkbox');
                    crystal_checkboxes.forEach(checkbox => {
                        checkbox.checked = false;
                        checkbox.parentElement.querySelector('label').style.fontWeight = "";
                    });
                    const crystal_type_select = document.querySelector('.crystal-select');
                    if (crystal_type_select) {
                crystal_type_select.selectedIndex = 0; // Reset to the first option
            }
                    removeQueryParam('crystal');
               }
               this.style.display = "none";
               applyFilters();

            });
        });


        function removeQueryParam(param) {
            const baseUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            const queryParams = new URLSearchParams(window.location.search);

            // Remove the specific query parameter
            queryParams.delete(param);

            // Update the URL without reloading the page
            const newUrl = queryParams.toString() ? `${baseUrl}?${queryParams.toString()}` : baseUrl;
            history.pushState({}, '', newUrl);
        }


        document.getElementById('contains-in-name').addEventListener('input', applyFilters);


        fillSlider(fromSlider, toSlider, '#C6C6C6', '#003665', toSlider);
        setToggleAccessible(toSlider);

        fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInputText, currency);
        toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInputText, currency);

        fromSlider.addEventListener('change', applyFilters);
        toSlider.addEventListener('change', applyFilters);

        function paginateItems(items, pageNumber, pageSize) {
            const startIndex = (pageNumber - 1) * pageSize;
            return items.slice(startIndex, startIndex + pageSize);
        }


        function filterItems(items, pageNumber, pageSize) {
            const startIndex = (pageNumber - 1) * pageSize;
            return items.slice(startIndex, startIndex + pageSize);
        }


        function displayCurrentPage(items) {
            const productsGrid = document.querySelector('.products-grid');
            productsGrid.innerHTML = '';

            let itemCounter= 0;
            items.forEach((item) => {
                // Append the product container to the products grid
                productsGrid.appendChild(createProductCard(false, item, itemCounter, allItems, filteredItems, favouriteItems, window.config.preOrderIconUrl, vocabulary, translations_categories, currency, window.config.changeFavouritesStateUrl, show_quantities, window.config.addToCatalogUrl, getCookie('csrftoken'), window.config.cartUrl, window.config.isAuthenticated, window.config.shopPageUrl, false));
                itemCounter+=1;
            });
        }

        function applyFilters() {
           const nameFilterValue = document.getElementById('contains-in-name').value.toLowerCase();
           const [from, to] = getParsed(fromSlider, toSlider);
           let itemsss = JSON.parse(JSON.stringify(allItems));
           filteredItems = itemsss.filter(item => {
                let isMatch = (category === "All" || (subcat[category] !== undefined ? subcat[category].concat(category).includes(item.category) : item.category === category)) &&
                              item.price <= to &&
                              item.price >= from &&
                    (item.product_name.toLowerCase().includes(nameFilterValue) || item.name.toLowerCase().includes(nameFilterValue))&&
                              (baseFilters.length === 0 || baseFilters.includes(item.material));

                if (!isMatch) {
                    return false;
                }
                let isCollectionMatch = collection_catalog === "All" || item.collection === collection_catalog;

                if(!isCollectionMatch){
                     return false;
                }
                let orderedPlatings = {};
                let hasPlatingMatch = false;

                // Check for plating matches
                if (platingFilters.length > 0) {
                    platingFilters.forEach(platingFilter => {
                        if (item.platings.hasOwnProperty(platingFilter)) {
                            orderedPlatings[platingFilter] = item.platings[platingFilter];
                            hasPlatingMatch = true;
                        }
                    });
                    Object.keys(item.platings).forEach(plating => {
                        if (!orderedPlatings.hasOwnProperty(plating)) {
                            orderedPlatings[plating] = item.platings[plating];
                        }
                    });
                } else {
                    orderedPlatings = item.platings;

                    hasPlatingMatch = true;
                }

                // Process stones and sizes
                let finalPlatings = {};
                Object.keys(orderedPlatings).forEach(plating => {
                    let stones = orderedPlatings[plating].stones;

                    let orderedStones = {};
                    let matchedStones = {};
                    let allStones = {};
                    let hasStoneMatch = false;

                    if (stoneFilters.length > 0) {
                        stoneFilters.forEach(stoneFilter => {
                            if (stones.hasOwnProperty(stoneFilter)) {
                                matchedStones[stoneFilter] = stones[stoneFilter];
                                hasStoneMatch = true;
                            }
                        });

                    } else {
                        allStones = stones;
                        hasStoneMatch = true;
                    }
                    orderedStones = { ...matchedStones, ...allStones};
                    // Reorder and filter sizes within stones
                    let finalStones = {};
                    Object.keys(orderedStones).forEach(stoneKey => {
                        let sizes = orderedStones[stoneKey].sizes;
                        let orderedSizes = {};
                        let hasSizeMatch = false;

                        if (sizeFilters.length > 0) {
                            sizeFilters.forEach(sizeFilter => {
                                if (sizes.hasOwnProperty(sizeFilter)) {
                                    orderedSizes[sizeFilter] = sizes[sizeFilter];
                                    hasSizeMatch = true;
                                }
                            });
                            Object.keys(sizes).forEach(sizeKey => {
                                if (!orderedSizes.hasOwnProperty(sizeKey)) {
                                    orderedSizes[sizeKey] = sizes[sizeKey];
                                }
                            });
                        } else {
                            orderedSizes = sizes;
                            hasSizeMatch = true;
                        }

                        if (hasSizeMatch) {

                            finalStones[stoneKey] = { ...orderedStones[stoneKey], sizes: orderedSizes };
                        }
                    });

                    if (hasStoneMatch && Object.keys(finalStones).length > 0) {
                        finalPlatings[plating] = { stones: finalStones };
                    }
                });

                if (hasPlatingMatch && Object.keys(finalPlatings).length > 0) {
                    item.platings = finalPlatings;
                } else {
                    return false;
                }

                return true;
           });

            const priorityProductIds = new Set(['63338', '61272', '62242', '63542', '32348', '12307', '23073', '61198', '63271', '62145', '32428', '63279', '32400', '12399', 'KS013R70', '22074', 'KS013RG70', 'KS013R40', 'KS013RG40', 'KS013RG55', 'KS013G70', 'KS013R90', 'KS013G90', 'KS013G40', 'KS013G55', 'KS013RG90', 'KS013R55', '41206', '32387', '23093', '23092', '32389', '23094', '12339', '32388', '12341', '12342', '11362', '61186', '63265', '63262', '63263', '63264', '62130', '62133', '63339', '61273', '62243', '21018', 'S24019', '22071', '62060', '22700', '22148', '22702', '62042', '22285', '21002', '22110', '22000', '62057', '22086', '22973', '62066', '62075', '22698', '22975', '22394', '22722', '22654', '22715', '62062', '22186', '22697', '22687', '22254', '62067', '22312', '22707', '22315', '22142', '22695', '22139', '22097', '62080', '22194', '22442', '62078', '22126', '21001', '21008', '22446', '22288', '22146', '22113', '22343', '22012', '22077', '22341', '22970', '22319', '22646', '21009', '22201', '22708', '22630', '62124', '21004', '22132', '21013', '22971', '22204', '22974', '22688', '62079', '63274', '62148', '61200', '62272', '63358', '61300', '61068', '23088', '12280', '63347', '62261', '41122', '23181', '12457', '63351', '22847', '32298', 'S24016', 'S24015', '22921', '22922', '32297', 'S24014', 'S24013', '41156', '22980', '12210', '12066', '12050', '32375', '12331', '23042', '12393', '12392', '23118', '63273', '62147', '11110', '62258', '23173', '62259', '62173', '23170', '23169', '23171', '22740', '62257', '23168', '23172', '62256', '23166', '62255', '23174', '32241', '11989', '22801', '59100', '12113', '63260', '22890', '32233', '11957', '32234', '11956', '32402', '41168', '22916', '12157', '12298', '32342', '41036', '22841', '23003', '22116', '63529', '63296', '62164', '61210', '22786', '32239', '11972', '12391', '61292', '63346', '62260', '32099', '12233', '22996', '41225', '23192', '12466', '22331', '61270', '62239', '11397', '32319', '12256', '32384', '62152', '22792', '11982', '41189', '23104', '12372', '12446', '23200', '12476', '32430', '22389', '11523', '63540', '61267', '63336', '61268', '62237', '11671', '22594', '32293', '41200', '23086', '32372', '12328', '12326', '57004', '58013', '22686', '11792', '62137', '32311', '22981', '63266', '58055', '32291', '12185', '12187', '22931', '32290', '12186', '41203', '32379', '23090', '12338', '12023', '22821', 'KS014G40', 'KS002', 'KS003', 'KS014R40', '57143', 'KS014RG40', '11850', '11844', '11854', '11846', '11837', '11852', '11830', '11848', '11833', '11831', '11847', '11840', '11841', '11845', '11855', '11832', '11836', '11851', '11853', '11838', '11839', '11835', '11843', '11834', '11842', '11849', '23186', '12459', '22892', '12115', '62125', '62126', '63305', '63303', '63306', '23052', '61112', '61138', '62081', '41205', '12160', '22917', '12227', '22993', '12451', '56900', 'S24003', 'S24002', 'S24001', '22572', '32356', '41211', '32307', '12225', '12378', '32226', '23011', '12251', '12475', '32160', '11613', '12335', '63268', '61188', '62132', '63525', '63531', '61225', '62180', '63320', '12302', '32346', '41204', '23063', '12284', '22918', '32288', '12169', 'S24017', '39102', 'S24011', '12293', '12243', '22965', '63252', '63215', '63222', '63253', '61179', '62117', '61125', '63218', '61180', '62115', '62116', '61124', '61154', '41000', '41004', '11945', '11703', '32224', '39104', '63290', '63216', '11329', '11471', '11640', '22699', '11808', '12417', '32354', '23039', '62107', '23177', '12453', '11328', '61177', '11073', '32003', '11030', '22073', '11171', '22913', '12153', '12007', '22156', '22155', '61178', '22815', '41193', '22983', '12229', '23095', '12345', '22112', '11076', '41201', '23087', '32373', '12330', '12136', '63280', '61193', '22105', '61185', '63520', 'V61185', '63259', '12267', '23024', '41207', 'K0003G', 'K0002R', 'K0001R', 'K0002G', 'K0003R', 'K0001G', '12278', '32333', '41198', '32034', '22758', '11910', '32315', '63528', '62136', 'V63528', '61191', '62135', '61190', '23026', '12269', '12270', '32336', '63225', '32248', '12079', '41065', '12032', '41064', '22834', '63301', '61215', '41186', '23097', '12340', '32371', '32313', '22976', '12207', '61290', '63353', '11330', '11148', '22164', '22295', '32404', '32403', '32361', '32405', '32357', '32358', '32376', '32360', '32377', '32359', '23091', '22729', '11924', '22805', '11996', '63299', '61212', '61317', '32396', '12370', '23117', '62143', '61197', '59101', '11947', '22069', '22774', '61143', '62084', '58016', '63548', '63343', '12425', '23146', '12052', '22851', '23071', '41210', '11740', '22623', '32332', '12277', '32327', 'S24004', '22606', 'S24005', '23043', '23152', '12432', '12276', '23037', '12264', '41166', '23020', '32328', '12263', '11062', '41190', '41226', '12472', '23199', '63349', '62263', '63317', '62178', '61222', '41175', '23046', '22779', '11953', '32194', '63325', '61229', '22400', '32167', '22451', '11605', '41110', '11570', '58045', '58046', '11571', '11590', '11879', '11743', '22617', '11701', '32426', '32321', '12279', '23016', '12257', '58006', '63313', '61218', '62175', '63315', '12259', '23018', '22796', '11986', '22934', '61313', '63319', '62179', '61224', '23131', '62285', '61316', '23001', '12245', '32314', '12433', '32415', '23153', '32320', '32424', '23193', '12467', '12230', '22991', '62123', '12253', '23013', '61307', '11540', '22399', '61192', '62138', '41001', '61118', '41172', 'S24010', '22590', '11670', '23045', '12321', '23004', '32362', '22672', '11757', '23124', '41217', '22861', '12077', '63276', '41151', '41164', '23081', '41165', '32316', '23014', '12254', '63297', '32044', '58066', '41182', '12289', '63254', '63256', '62119', '61182', '62118', '62120', '32325', '32324', '32326', '41196', '32416', '12434', '23154', '11998', '22807', '61289', '41136', '11793', '41177', '23057', '23044', '12282', '12292', '12116', '11692', '23145', '12424', '63270', '63210', '63211', '62144', '61109', '11077', '11951', '32270', '22885', '22777', '62278', '63309', '61203', '63331', '61256', '62233', '23180', '12456', '63328', '61242', '62213', '62197', '22817', '23126', '41202', '32386', '12329', '23085', '32374', '32427', '32399', '12025', '22832', '11200', '32057', '23159', '12439', '23096', '22206', '32353', '23069', '63342', '12426', '23147', '22998', '23022', '23023', '41214', '63357', '62271', '61299', '32251', '22845', '12049', '61199', '62146', '63231', '61135', '58048', '61148', '62089', '23116', '12390', '12419', '23144', '11973', '22787', '32406', '23141', '32249', '63547', '12262', '32323', '62284', '61315', '12226', '22985', '32308', '22987', '22731', '11882', '11883', '32026', '11337', '22304', '22896', '12119', '61284', '11025', '22066', '63545', '12320', '23076', '22364', '22363', '12395', '63519', '32158', '11615', 'KS015', 'KS004', 'KS001', '41216', '23028', '23027', '12288', '41208', '23098', '12373', '23058', '41161', '41163', '41162', '22158', '12396', '11861', '63352', '11942', '22771', '22770', '63247', '12297', '32341', '11922', '22764', '12287', '23068', '32186', '11133', '22145', '63251', '62113', '61176', '22793', '11983', '22966', '11010', '58052', '12367', '32294', '63356', '62268', '61296', '61312', '63355', '62266', '61294', '62188', '61251', '31000', '31001', '63258', '62121', '62122', '61184', '61183', '12221', '22988', '32304', '32306', '12224', '63332', '62234', '61255', '63539', '32302', '32414', '11078', '63284', '22096', '11056', '61278', '62250', '32181', '23189', '12463', '32022', '63295', '61319', '62212', '63329', '63537', '12435', '32417', '23155', '23196', '12471', '62254', '63362', '61280', '32253', '22866', '31003', '22183', '41051', '62168', '63302', '61282', '11744', '22647', '11745', '12305', 'S24008', 'S24009', '11616', '12158', '12021', '22819', '11575', '11816', '11873', '12281', '22925', '12180', '11512', '22379', '12261', '32322', '23100', '12375', '32391', '63291', '63267', '63524', '61187', '62131', '63278', '61201', '63275', '23007', '12247', '41191', '32049', '12403', '32401', '23109', '12265', '23021', '63314', '62176', '61219', '12480', '23203', '12234', '32312', '22997', '23080', '12308', '32363', '11074', '32033', '22111', '11138', '11137', '11897', '58064', '32331', '62209', '22937', '63241', '61136', '63287', '12268', '23025', '12209', '61302', '63360', '62274', '12332', '62215', '61263', '41167', '12266', '12206', '12193', '41159', '11534', '61142', '62083', '11825', '12012', '12011', '32212', '12010', '11826', '12252', '23012', '62264', '61293', '22759', '11974', '11911', '12427', '23148', '11210', '22199', '12197', '32300', '61232', '41169', '23158', '58050', '12438', '12449', '63238', '63239', '61153', '63527', '63522', '23075', '12380', '32410', '23132', '61126', '41195', '63348', '62262', '12273', '23149', '12428', '12316', '23074', '11619', '11618', '32162', '22559', '12248', '23008', '63250', '63249', '12429', '22928', '22929', '12304', '23078', '62104', '63246', '61168', '12322', '63530', '62167', '61213', '32292', '12188', '22938', '11898', '22747', '58060', '22979', '32030', '11749', '22651', '11993', '22802', '63285', '62157', '12171', '22982', '63341', '61279', '62251', '63300', '63298', '61211', '62165', '12042', '22872', '12126', '22091', '11024', '41187', '23162', '23049', '32232', '32247', '12034', '12404', '23142', '41209', '32006', '32005', '23099', '12374', '11273', '32393', '12377', '23102', '12406', '23019', '12260', '63345', '62225', '32225', '61252', '23031', '23041', '12271', '61214', '61241', '12133', '12181', '41185', '41171', '63340', '63543', '62246', '63293', '22207', '32252', '12313', '23151', '12431', '32272', '22895', '22396', '11536', '11230', 'S24018', '12242', '22999', '11819', '22756', '11908', '11894', '32343', '12299', '32301', '12205', '32411', '23040', '32408', '32279', '22604', '11685', '22846', '32116', '11395', '12051', '32246', '62281', '61309', '12004', '22813', '32296', '62270', '63550', '61298', '62200', '57141', '32008', '12384', '11022', '63283', '23083', '12324', '32378', '12478', '12443', '63312', '61195', '62141', '63248', '61171', '62109', '12045', '22871', '22694', '41178', '12454', '23178', '32014', '23107', '12415', '12002', '61202', '12319', '32286', '12154', '11769', '23188', '41224', '12462', '23184', '61144', '62085', '23056', '61204', '41212', '22776', '22070', '12448', '12386', '22936', '61231', '23089', '23082', '12369', '11788', '32200', '12194', '63318', '61223', '62224', '41213', '32334', '32344', '12300', '22897', '12120', '32274', '11858', '61283', '32228', '22750', '11903', '41173', '63359', '62273', '61301', '11410', '63344', '12095', '32250', '41199', '61260', '11182', '62231', '61205', '12134', '63316', '61221', '62223', '32317', '23140', '12309', '22728', '11881', '63549', '62134', '61189', '63526', '62071', '63521', '22911', '12150', '22412', '62108', '22417', '61318', '11804', '62150', '12203', '58061', '22960', '12190', '12290', '11714', '11875', '11713', '61167', '62102', '32287', '23047', '32050', '32222', '32105', 'KS012R40', 'KS012G55', 'KS012R55', '11353', 'KS012G40', 'KS012RG55', 'KS012RG40', '11765', '11667', '61196', '63269', '62142', '62192', '63272', '23070', '12294', '61308', '62280', '41160', '23115', '41215', '32425', '12469', '23195', '41227', '23201', '12477', '63277', '62191', '63330', '62228', '61257', '12468', '23194', '22203', '21014', '32091', '61150', '62090', '22837', '11123', '61147', '32295', '32380', '23119', '12291', '12336', '23002', '58019', '62235', '61208', '58054', '32173', '12076', '58056', '63308', '61217', '12161', '22781', '41219', '23160', '32397', '32351', '12303', '63029', '61092', '11902', '22749', '63361', '61303', '62275', '23143', '12418', '11610', '11815', '32257', '12093', '22870', '63234', '23157', '12437', '32407', '23135', '32117', '41180', '41170', '63546', '63282', '62171', '41184', '41179', '57017', '32429', '32318', '12255', '23015', '11984', '22794', '12094', '58001', '62204', '61239', '23017', '12258', '22188', '11548', '12333', '23182', '41223', '58068', '41181', '12460', '23187', '23036', '11126', '12275', '12394', '62248', '61276', '62287', '62227', '61254', '23150', '12430', '62183', '9209', '9206', '9205', '63304', '12402', '32245', '12473', '11677', '22599', '32394', '12413', '61269', '62238', '11777', '41133', '61237', '12314', '12312', '61266', '12447', '32421', '23176', '12452', '11134', '32043', '32345', '12301', '23179', '12455', '12445', '22235', '11246', '32382', '12420', '11212', '61115', '41174', '11483', '61265', '23130', '62201', '61240', '62211', '32413', '11772', '61151', '62092', '32335', '32275', '12240', '62279', '63551', '61306', '11236', '12239', '32001', '11997', '22806', '22733', 'S24012', '22926', '12182', '23005', '41197', '12146', '22907', '32281', '11824', '32221', '58067', '22791', '11981', '23072', '41134', '62149', '23032', '11347', '23030', '32164', '32088', '11321', '22754', '21015', '62139', '12053', '63310', '11441', '22035', '12208', '59103', '61305', '62277', '32299', '62158', '23029', '22933', '62199', '61235', '11899', '23191', '12465', '22831', 'K0004', '23050', '62151', '62103', '61164', '62267', '61295', '11388', '58065', '41188', '63354', '22778', '11952', '61314', '62283', '12436', '23156', '61304', '62276', '23067', '12285', '32340', '22732', '11884', '62082', '61139', '23112', '32409', '41218', '23105', '12400', '12440', '62170', '12237', '23164', '32392', '23101', '12376', '12295', '11990', '22294', '63538', '22783', '32364', '58047', '62162', '22329', '32109', '11058', '32017', '61281', '22967', '12244', '61127', '12069', '11143', '32433', '61275', '63544', '62245', '61264', '62214', '23183', '12201', '11999', '22628', '12235', '12423', '32207', '32422', '23061', '63311', '22406', '62247', '32349', '12474', '12017', '22067', '12334', '12274', '32330', '62106', '61172', '61100', '62105', '62177', '23033', '12272', '32337', '61165', '62210', '32423', '12458', '23185', '32431', '11809', '23175', '12450', '23053', '62252', '11723', '23059', '23066', '11976', '11975', '41146', '22798', '32432', '61209', '11704', '11272', '32254', '22388', '11522', '62230', '61259', '41228', '12479', '23202', '63288', '22977', '22964', '12195', '12389', '11859', '11817', '12337', '62206', '22082', '32218', '63552', '62286', '58062', '22330', '61258', '62229', '22927', '21016', '62156', '23190', '12464', '12470', '63535', '61233', '22685', '11791', '58069', '12223', '22984', '23009', '12249', '23114', '23198', '22989', '22994', '12204', '63289', '62072', '12444', '23167', 'V232', '22968', '23010', '12250', '32381', '22972', '58063', '61288', '62169', '62159', '11593', '11216', '22426', '23055', '23138', '12236', '62241', '12414', '61141', '22893', '12145', '41157', '22986', '12220', '11683', '62208', '61206', '23062', '22767', '62190', '23110', '23161', '32184', '23035', '22990', '12421', '32058', '62100', '23163', '32305', '41221', '58058', '12199', '61137', '63541', '23051', '62207', '23064', '23197', '23129', '58049', '22932', '61119', '23106', '21020', '62091', '39100', '11185', '22978', '12044', '32089', '12283', '23084', '23128', '22780', '61271', '12139', '62154', '62244', '61274', '32383', '32352', '32037', '32063', '22258', '62253', '62205', '32284', '32347', '12306', '62249', '61277', '63350', '11954', '62269', '61297', '63534', '12422', '12315', '23048', '62172', '23103', '12379', '62232', '61261', '22992', '12228', '61230', '11028', '12310', '32271', '11725', '11771', '56027', '12311', '58057', '62203', '61238', '61286', '23133', '32310', '11948', '22775', '12461', '32163', '61285', '11752', '12231', '11742', '11032', '32338', '61310', '32165', '62087', '58053', '23123', '22076', '61287', '11318', '61102', '61194', '62140', '23060', '62288', '58059', '62282', 'S24006', '61060', '12411', '11095', '61311', '12241', '41194', '62265', '11724', '23000', '12196', '23065', '32390', '23054', '32278', '62160', '12159', '61166', '62155', '32398']);
            const defaultPlatingOrder = ["Rhodium", "Gold", "Rosegold"];

            if (platingFilters.length === 0) {
                // When no plating filter is applied, sort by plating priority first, then by price.
                filteredItems.sort((a, b) => {
                    const platingIndexA = defaultPlatingOrder.findIndex(plating =>
                        Object.keys(a.platings).includes(plating));
                    const platingIndexB = defaultPlatingOrder.findIndex(plating =>
                        Object.keys(b.platings).includes(plating));

                    // If plating priority is equal, sort by price.
                    if (platingIndexA === platingIndexB) {
                        return a.price - b.price;
                    }
                    return (platingIndexA === -1 ? Infinity : platingIndexA) -
                           (platingIndexB === -1 ? Infinity : platingIndexB);
                });

                // Reorder the plating objects in each item.
                filteredItems.forEach(item => {
                    const platingKeys = Object.keys(item.platings);
                    const sortedPlatings = platingKeys.sort((a, b) => {
                        const indexA = defaultPlatingOrder.indexOf(a);
                        const indexB = defaultPlatingOrder.indexOf(b);
                        return (indexA === -1 ? Infinity : indexA) - (indexB === -1 ? Infinity : indexB);
                    });
                    const sortedPlatingObject = {};
                    sortedPlatings.forEach(key => {
                        sortedPlatingObject[key] = item.platings[key];
                    });
                    item.platings = sortedPlatingObject;
                });
            } else {
                // When plating filters are active, simply sort by price.
                filteredItems.sort((a, b) => a.price - b.price);
            }
            // --- End of your sorting code ---

            // Now, give priority to products from priorityProductIds
            // Assume you have populated the priorityProductIds set with your ~1500 product IDs.
            const priorityItems = filteredItems.filter(item => priorityProductIds.has(item.name));
            const nonPriorityItems = filteredItems.filter(item => !priorityProductIds.has(item.name));

            // In each group, enforce ordering by price (or any other criteria you need)
            priorityItems.sort((a, b) => a.price - b.price);
            nonPriorityItems.sort((a, b) => a.price - b.price);

            // Combine the two lists: all priority items first, then the rest.
            filteredItems = [...priorityItems, ...nonPriorityItems];

            if(sizeFilters.length === 0) {
                for (let productName in filteredItems) {
                    for (let platingName in filteredItems[productName].platings) {
                        for (let stoneName in filteredItems[productName].platings[platingName].stones) {
                            let stoneEntry = filteredItems[productName].platings[platingName].stones[stoneName];
                            if (stoneEntry.sizes) {
                                stoneEntry.sizes = orderSizes(stoneEntry.sizes);
                            }
                        }
                    }
                }
            }
           if (filteredItems.length === 0) {
               filteredItems.push(vocabulary["No items found"]);
           }
           else{
               filteredItems.forEach(item => {
                    let first_plating = Object.values(item.platings)[0];
                    let first_stone = Object.values(first_plating.stones)[0];
                    item.preview_image = first_stone['image'];
               });
           }


           currentPage = 1;
           total_pages = Math.ceil(filteredItems.length / itemsPerPage);
           constructCrystals(filteredItems, stoneFilters, window.config.crystalImgsFolder);
           changePage(1);
        }

        function order(array) {
            // Establishing the order of platings
            const defaultPlatingOrder = ["Rhodium", "Gold", "Rosegold"];

            // Grouping elements by coverage
            const grouped = defaultPlatingOrder.map(plating =>
                array.filter(item => Object.keys(item.platings).includes(plating))
            );

            // Function for sorting within a group
            function sortGroup(group) {
                if (order_name === "Name") {
                    group.sort((a, b) => {
                        if (order_type === "asc") {
                            return a.name.localeCompare(b.name);
                        } else if (order_type === "desc") {
                            return b.name.localeCompare(a.name);
                        }
                    });
                } else if (order_name === "Price") {
                    group.sort((a, b) => {
                        if (order_type === "asc") {
                            return parseFloat(a.price) - parseFloat(b.price);
                        } else if (order_type === "desc") {
                            return parseFloat(b.price) - parseFloat(a.price);
                        }
                    });
                }
            }

            // Sort each group
            grouped.forEach(group => sortGroup(group));

            // Combining groups into one array
            return grouped.flat();
        }


        function updatePage() {
            let paginatedItems;
            let found = true;
            if(filteredItems.length === 0){
                order(allItems);
                paginatedItems = paginateItems(allItems, currentPage, itemsPerPage);
            }
            else{
                if(filteredItems[0] === "No items found"){
                    paginatedItems = paginateItems([], currentPage, itemsPerPage);

                    found = false;
                }
                else {
                    order(filteredItems);
                    paginatedItems = paginateItems(filteredItems, currentPage, itemsPerPage);
                }
            }
            const current = document.getElementById('current-page');
            current.innerText = vocabulary["Current page"] + currentPage;
            displayCurrentPage(paginatedItems);
            if(found===false){
                const grid = document.querySelector('.products-grid');
                const span = document.createElement('h2');
                span.textContent = vocabulary["No items found"];
                span.style.gridColumn = "1/-1";
                span.style.textAlign = 'center';
                span.style.color = "#4d4d4d"
                grid.appendChild(span);
            }
        }


        document.getElementById('previous-button').addEventListener('click', function (event){
            event.preventDefault();
            if(currentPage>1){
                currentPage-=1;
                changePage(currentPage);
            }
        });


        document.getElementById('next-button').addEventListener('click', function (event){
            event.preventDefault();
            if(currentPage<total_pages){
                currentPage+=1;
                changePage(currentPage);
            }
        });


        document.getElementById('button-jump-to').addEventListener('click', function (event) {
            event.preventDefault();
            let page_number = Number(document.getElementById('page-number-input').value);
            if(page_number>0 && page_number<=total_pages){
                currentPage = page_number;
                changePage(currentPage);
            }
        });


        document.getElementById('select-items-per-page').addEventListener('change', function (event) {
            itemsPerPage = Number(event.target.value);
            if(filteredItems.length === 0) {
                total_pages = Math.ceil(allItems.length / itemsPerPage);
            }
            else{
                 total_pages = Math.ceil(filteredItems.length / itemsPerPage);
            }
            currentPage = 1;
            changePage(1);
        });


        document.getElementById('select-order').addEventListener('change', function (event) {
            let order = (event.target.value).split(', ');

            order_name = order[0];
            order_type=order[1];
            changePage(1);
        });


        $(document).ready(function(){
            $('.slider').on('input change', function() {
                const container_shows = document.getElementById('value-of-slider-price');
                container_shows.innerText = $(this).val();
            });
        });

        document.querySelectorAll('.quantity-input-dialog').forEach(input => {
            input.addEventListener('input', function() {
                console.log(this.value);
            })
        });


        document.querySelectorAll('.quantity-input-dialog').forEach(input => {
            input.addEventListener('change', function() {
                console.log(this.value);
            })
        });


        document.getElementById('product-card').addEventListener('click', async (event) => {
            const heartIconContainer = event.target.closest('.mobile-heart-container');
            if (!heartIconContainer) return;

            const item = JSON.parse(heartIconContainer.getAttribute('data-item-name')); // Assumes each heartIconContainer has `data-item-name`

            const favouriteItem = favouriteItems.find(item_fav => item_fav.name === item.name); // Assuming `item.name` is the name of your current item
            const isFavBefore = Boolean(favouriteItem); // Converts the result to a boolean

            // Stop the event from propagating to other elements
            event.stopPropagation();
            try {
                // Replace `yourItemId` with the actual item ID or any identifier you use
                const response = await fetch(window.config.changeFavouritesStateUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),

                        // Include other headers as needed, like authorization tokens
                    },
                    body: JSON.stringify({item: JSON.stringify(item), "alreadyFavourite": isFavBefore ? "true":"false"}),
                });

                if (!response.ok) throw new Error('Network response was not ok.');

                // Assuming the backend responds with the updated favorite status
                const data = await response.json();
                const isFavourite = data.isFavourite === "true";
                const itemToAddOrRemove = JSON.parse(data.item); // Assuming this is an object {name_id: "someId", ...}
                removeTooltip();
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
                    `<div class="favourites-mobile-container"><span class="mobile-favourites-btn">` + vocabulary["Remove from favorites"] + `<i class="rts" data-size="24" data-color="#000000"><svg xmlns="http://www.w3.org/2000/svg" class="card-fav-icon-yes" viewBox="0 0 28 28" width="24" height="24"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z"></path></svg></i> </span></div>` :
                    `<div class="favourites-mobile-container"><span class="mobile-favourites-btn">` + vocabulary["Add to favorites"] + `<i class="rts" data-size="24" data-color="#000000"><svg xmlns="http://www.w3.org/2000/svg" class="card-fav-icon-no" viewBox="0 0 28 28" width="24" height="24"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z"></path></svg></i> </span></div>`;
            } catch (error) {
                console.error('Error updating favorites:', error);
            }
        });

    })
    .catch(error => {
        console.error("Ошибка при динамическом импорте:", error);
    });