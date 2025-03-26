function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function updatePlatings(selectedPlating, stoneSelect, sizeSelect, image, maxQuantity, show_quantities, vocabulary,single_product_address, address, copy_address){
    const firstStone = selectedPlating ? Object.values(selectedPlating.stones || {})[0] : null;

    while (stoneSelect.firstChild) {
        stoneSelect.removeChild(stoneSelect.firstChild);
    }
    fulfilDropdown(stoneSelect, selectedPlating.stones, vocabulary);
    return updateStones(firstStone, sizeSelect, image, maxQuantity, show_quantities, vocabulary,single_product_address, address, copy_address);
}
function updateStones(selectedStone, sizeSelect, image, maxQuantity, show_quantities, vocabulary,single_product_address, address, copy_address){

    const firstSizeKey = selectedStone ? Object.keys(selectedStone.sizes || {})[0] : null;
    const withSizes = !!firstSizeKey;
    const firstSizeQuantity = withSizes ? selectedStone.sizes[firstSizeKey].quantity : selectedStone.quantity;
    if (selectedStone?.image) {
        image.src = selectedStone.image; // Update the image src
    }

    if(selectedStone?.real_name){
        let adres = single_product_address.replace("REPLACE", selectedStone.real_name)
        address.href = adres;
        copy_address.setAttribute("data-link", adres);
    }

    while (sizeSelect.firstChild) {
        sizeSelect.removeChild(sizeSelect.firstChild);
    }
    if(withSizes) {
        fulfilDropdown(sizeSelect, selectedStone.sizes, vocabulary);
        return updateSizes(firstSizeQuantity, maxQuantity, show_quantities, vocabulary);
    }
    else{
         if(show_quantities) {
            maxQuantity.innerText = `${vocabulary['In stock']}: `+firstSizeQuantity;
        }
        else{
            if (firstSizeQuantity<=5){
                maxQuantity.innerText = `${vocabulary['Less than 5 pieces left!']}`
            }
            else if (firstSizeQuantity === 0){
                maxQuantity.innerText = `${vocabulary['This item is only available for pre-order!']}`;
            }
            else{
                maxQuantity.innerText = ``
            }
        }
    }
}
function updateSizes(sizeQuantity, maxQuantity, show_quantities, vocabulary){
     if(show_quantities) {
        maxQuantity.innerText = `${vocabulary['In stock']}: `+sizeQuantity;
    }
    else{
        if (sizeQuantity<=5){
            maxQuantity.innerText = `${vocabulary['Less than 5 pieces left!']}`;
        }
        else if (sizeQuantity === 0){
            maxQuantity.innerText = `${vocabulary['This item is only available for pre-order!']}`;
        }
        else{
            maxQuantity.innerText = ``
        }
    }
    return Number(sizeQuantity);
}

function fulfilDropdown(dropdown, array, vocabulary){
    if(array) {
        (Object.keys(array)).forEach(element => {
            let option = document.createElement('option');
            option.innerText = vocabulary[element] ? vocabulary[element]: element;
            option.value = element;
            dropdown.add(option);
        });
    }
}

function closeDialogWithAnimation(dialog, isCarousel) {
    dialog.classList.remove('show');
    dialog.offsetHeight;
    // Waiting for the animation to complete
    dialog.addEventListener(
        'transitionend',
        () => {
            if (dialog.open) {
                dialog.close(); // We only close it if it's still open
            }
        },
        { once: true } // Let's make sure that the listener is removed after triggering
    );
    if(!isCarousel) {
        currentPlating = "";
    }
}
function bindGlobalClickEvent(dialog) {
    document.addEventListener(
        'click',
        (event) => {
            // Check if the click is inside the dialog box
            const rect = dialog.getBoundingClientRect();
            const isInDialog =
                rect.top <= event.clientY &&
                event.clientY <= rect.top + rect.height &&
                rect.left <= event.clientX &&
                event.clientX <= rect.left + rect.width;

            // Exclude clicks on SELECT or other interactive elements inside the dialog box
            if (
                isInDialog ||
                event.target.closest('select') || // For select and option
                event.target.closest('input') || // For input
                event.target.closest('textarea') // For textarea
            ) {
                return;
            }

            if (dialog.open) {
                document.body.style.overflow = ''; // Allow page scrolling
                closeDialogWithAnimation(dialog, false); // Closing the dialog
            }
        },
        true // Use capture to handle the event before surfacing
    );
}

function dialogCommonSetup(dialog, image_url, card_content){

    const close_dialog = document.createElement('div');
    const icon_close = document.createElement('i');
    icon_close.classList.add('fa-solid', 'fa-close');
    close_dialog.appendChild(icon_close);
    close_dialog.addEventListener('click',()=>{
       document.body.style.overflow = '';
       closeDialogWithAnimation(dialog, false);
    });

    close_dialog.classList.add('close-card');
    card_content.appendChild(close_dialog);

}

function showTooltip(event, message) {
    const existingTooltip = document.querySelector('.custom-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }

    // Checking to see if there is an open dialog
    const dialog = document.querySelector('dialog[open]');
    const container = dialog || document.body;

    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = message;
    tooltip.style.position = 'absolute';

    if (dialog) {
        // Calculate coordinates relative to the dialog
        const rect = dialog.getBoundingClientRect();
        const offsetY = dialog.scrollTop || 0; // Take into account possible scrolling inside the dialog box
        tooltip.style.left = `${event.clientX - rect.left + 10}px`;
        tooltip.style.top = `${event.clientY - rect.top + 10 + offsetY}px`; // Account for offset and scrolling
    } else {
        // If the tooltip is added to document.body
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
    }

    container.appendChild(tooltip);

    // Moving the tooltip with the cursor
    event.target.addEventListener('mousemove', (e) => {
        if (dialog) {
            const rect = dialog.getBoundingClientRect();
            const offsetY = dialog.scrollTop || 0; // Consider scrolling inside the dialog
            tooltip.style.left = `${e.clientX - rect.left + 10}px`;
            tooltip.style.top = `${e.clientY - rect.top + 10 + offsetY}px`;
        } else {
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY + 10}px`;
        }
    });

    // Remove the tooltip when the mouse exits
    event.target.addEventListener('mouseleave', () => {
        tooltip.remove();
    });
}
function removeTooltip(){
    const existingTooltip = document.querySelector('.custom-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
}

let currentPlating = "";
currentPlating = "";
function generateDialogContent(id, items_array, currency, show_quantities, add_to_cart_url, vocabulary, cookie, checkout_url, isFavourite, user_auth, single_product_url, allItems, favouriteItems, pre_order_img_src, change_fav_state_url, translations_categories, isCheckout){
    let quantity_max = 1;
    document.body.style.overflow = 'hidden';
    const item = items_array.find(item => item.name === id);

    if (!item) {
        console.error('Item not found');
        return;
    }

    const firstPlatingKey = Object.keys(item.platings)[0];
    const firstPlating = item.platings[firstPlatingKey];

    // Get the first stone in the first plating
    const firstStoneKey = firstPlating && Object.keys(firstPlating.stones)[0];
    const firstStone = firstPlating ? firstPlating.stones[firstStoneKey] : null;

    // Get the first size in the first stone
    const firstSizeKey = firstStone && Object.keys(firstStone.sizes)[0];
    const firstSizeQuantity = firstStone ? firstStone.sizes[firstSizeKey] ? firstStone.sizes[firstSizeKey].quantity: null : null;


    const dialog = document.getElementById('product-card');
    const image = document.createElement('img');
    image.classList.add('zoom-image');
    bindGlobalClickEvent(dialog);
    dialog.innerHTML = '';

    const card = document.createElement('div');
    card.classList.add('card-main-body');

    const card_content = document.createElement('div');
    card_content.classList.add('card-content');

    let imagePath = '';
    let single_product_address = "";

    if (firstStone) {
        imagePath = firstStone.image || '';
        single_product_address = single_product_url.replace('REPLACE', firstStone.real_name);
        quantity_max = Object.keys(firstStone.sizes || {}).length === 0 ? firstStone.quantity : firstSizeQuantity;
    }

    image.src = imagePath;
    image.width = `400`;
    image.height = `400`;
    image.classList.add('img-card');
    const image_container = document.createElement('div');
    image_container.classList.add('image-container');
    image_container.appendChild(image);

    const div_container = document.createElement('div');
    if (window.matchMedia("(min-width: 769px)").matches) {
        setupZoom(image_container, image, vocabulary);
    }

    div_container.appendChild(image_container);
    card_content.appendChild(div_container);

    dialogCommonSetup(dialog, imagePath, card_content);


    const secondColumn = document.createElement('div');
    secondColumn.classList.add('second-column');

    let parts = item.product_name.split(" ");
    // Remove the last word
    let last_word = parts.pop();
    // Join the remaining parts to form the full phrase
    let full_phrase = parts.join(" ");
    const nameSpan = document.createElement('h2');
    nameSpan.textContent = vocabulary[full_phrase] ? vocabulary[full_phrase] + " " + last_word : item.product_name;
    secondColumn.appendChild(nameSpan);

    const product_pages_container = document.createElement('div');
    product_pages_container.classList.add('product-pages-container');

    const address_page = document.createElement('a');
    address_page.classList.add('address-page');
    address_page.setAttribute('href', single_product_address);
    address_page.textContent = "Info ";
    const address_page_i = document.createElement('i');
    address_page_i.classList.add('fa-solid', 'fa-circle-info')
    address_page.appendChild(address_page_i);


    const copy_address_page = document.createElement('span')
    copy_address_page.classList.add('copy-address-page');
    copy_address_page.setAttribute('data-link', single_product_address);
    copy_address_page.textContent = `${vocabulary["Copy link"]} `; // Начальный текст кнопки
    const copy_address_page_i = document.createElement('i');
    copy_address_page_i.classList.add('fa-solid', 'fa-link')
    copy_address_page.appendChild(copy_address_page_i);

    copy_address_page.addEventListener('click', () => {
        // Get the reference from the data-attribute
        const link = copy_address_page.getAttribute('data-link');
        // Using API for copying to clipboard
        navigator.clipboard.writeText(link)
            .then(() => {
                const originalText = copy_address_page.textContent; // Keeping the original text
                copy_address_page.textContent = `${vocabulary["Copied!"]} `;
                copy_address_page.appendChild(copy_address_page_i); // Restore the icon

                // Return the original text after 2 seconds
                setTimeout(() => {
                    copy_address_page.textContent = originalText;
                    copy_address_page.appendChild(copy_address_page_i); // Restore the icon
                }, 2000);
            })
            .catch(err => {
                console.error('Copying error: ', err);
            });
    });

    product_pages_container.appendChild(address_page);
    product_pages_container.appendChild(copy_address_page);
    secondColumn.appendChild(product_pages_container);

    const numberSpan = document.createElement('h4');
    numberSpan.textContent = `${item.name}`;
    secondColumn.appendChild(numberSpan);


    if (window.matchMedia("(max-width: 769px)").matches && user_auth === "True") {
        // Code to run if the viewport width is less than 798px
        const heartIconContainer = document.createElement('div');
        heartIconContainer.className = 'mobile-heart-container';
        heartIconContainer.setAttribute('data-item-name', JSON.stringify(item));
        heartIconContainer.innerHTML = isFavourite ?
        `<div class="favourites-mobile-container"><span class="mobile-favourites-btn"> ${vocabulary["Remove from favorites"]} <i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:#000000;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i> </span></div>` :
        `<div class="favourites-mobile-container"><span class="mobile-favourites-btn"> ${vocabulary["Add to favorites"]} <i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i> </span></div>`; // Example with FontAwesome
        secondColumn.appendChild(heartIconContainer);
    }

    const priceSpan = document.createElement('div');
    priceSpan.classList.add('price-element');
    priceSpan.textContent = currency+`${item.price}`;
    secondColumn.appendChild(priceSpan);

    const quantitySpan = document.createElement('div');
    if(show_quantities) {
        if( quantity_max === 0) {
            quantitySpan.textContent = `${vocabulary['This item is only available for pre-order!']}`;
        }
        else{
            quantitySpan.textContent = `${vocabulary['In stock']}: ${quantity_max}`;
        }
    }
    else{
        if (quantity_max<=5){
            quantitySpan.textContent = `${vocabulary['Less than 5 pieces left!']}`;
        }
        if(quantity_max === 0){
            quantitySpan.textContent = `${vocabulary['This item is only available for pre-order!']}`;
        }
    }
    quantitySpan.classList.add('maximum-span');

    const platingLabel = document.createElement('span');
    platingLabel.innerText = `${vocabulary['Plating Material']}`;
    platingLabel.classList.add('card-dropdown-label');
    const platingsSelect = document.createElement('select');
    platingsSelect.classList.add('card-dropdown');
    fulfilDropdown(platingsSelect, item.platings, vocabulary);
    secondColumn.appendChild(platingLabel);
    secondColumn.appendChild(platingsSelect);

    const stoneLabel = document.createElement('span');
    stoneLabel.innerText = `${vocabulary['Stone color']}`;
    stoneLabel.classList.add('card-dropdown-label');
    const stoneSelect = document.createElement('select');
    stoneSelect.classList.add('card-dropdown');
    fulfilDropdown(stoneSelect, firstPlating.stones, vocabulary);
    secondColumn.appendChild(stoneLabel);
    secondColumn.appendChild(stoneSelect);

    const sizeLabel = document.createElement('span');
    sizeLabel.innerText = `${vocabulary['Size']}`;
    sizeLabel.classList.add('card-dropdown-label');
    const sizeSelect = document.createElement('select');
    sizeSelect.classList.add('card-dropdown');
    if(Object.keys(firstStone.sizes).length>0) {
        fulfilDropdown(sizeSelect, firstStone.sizes, vocabulary);
        secondColumn.appendChild(sizeLabel);
        secondColumn.appendChild(sizeSelect);
    }
    const inputQuantity = document.createElement('input');

    platingsSelect.addEventListener('change', (event) => {
        const selectedPlatingKey = event.target.value;
        currentPlating = selectedPlatingKey;

        const selectedPlating = item.platings[selectedPlatingKey];
        inputQuantity.value = '1';
        quantity_max = updatePlatings(selectedPlating, stoneSelect, sizeSelect, image, quantitySpan, show_quantities, vocabulary,single_product_url, address_page, copy_address_page);

        updateCarouselImages(selectedPlatingKey, allItems);
    });

    stoneSelect.addEventListener('change', (event) => {
        const selectedStoneKey = event.target.value;
        const selectedPlatingKey = platingsSelect.value;
        const selectedPlating = item.platings[selectedPlatingKey];
        const selectedStone = selectedPlating && selectedPlating.stones ? selectedPlating.stones[selectedStoneKey] : null;
        inputQuantity.value = '1';
        quantity_max = updateStones(selectedStone, sizeSelect, image, quantitySpan, show_quantities,vocabulary, single_product_url, address_page, copy_address_page);

    });

    sizeSelect.addEventListener('change', (event) => {
        const selectedSizeKey = event.target.value;
        const selectedPlatingKey = platingsSelect.value;
        const selectedPlating = item.platings[selectedPlatingKey];
        const selectedStoneKey = stoneSelect.value;
        const selectedSizeQuantity = selectedPlating.stones[selectedStoneKey].sizes[selectedSizeKey].quantity;
        inputQuantity.value = '1';
        quantity_max = updateSizes(selectedSizeQuantity, quantitySpan, show_quantities, vocabulary);

    });

    const dimensions_container = document.createElement('div');
    dimensions_container.classList.add('dimensions-container');

    if(item.product_width) {
        const product_width_div = document.createElement('div');
        const product_width_label = document.createElement('span');
        product_width_label.classList.add('card-dropdown-label');
        product_width_label.innerText = `${vocabulary['Product width']}`;
        const product_width_value = document.createElement('span');
        product_width_value.innerText = `${item.product_width} cm`;
        product_width_div.appendChild(product_width_label);
        product_width_div.appendChild(product_width_value);

        dimensions_container.appendChild(product_width_div);
    }

    if(item.product_height) {
        const product_height_div = document.createElement('div');
        const product_height_label = document.createElement('span');
        product_height_label.classList.add('card-dropdown-label');
        product_height_label.innerText = `${vocabulary["Product height"]}`;
        const product_height_value = document.createElement('span');
        product_height_value.innerText = `${item.product_height} cm`;
        product_height_div.appendChild(product_height_label);
        product_height_div.appendChild(product_height_value);

        dimensions_container.appendChild(product_height_div);
    }

    secondColumn.appendChild(dimensions_container);

    if(item.chain_length) {
        const chain_length_container = document.createElement('div');
        chain_length_container.classList.add('chain-dimensions-container');
        const product_chain_length_label = document.createElement('span');
        product_chain_length_label.classList.add('card-dropdown-label');
        product_chain_length_label.innerText = `${vocabulary['Chain length']}`;
        const product_chain_length_value = document.createElement('span');
        product_chain_length_value.innerText = `${item.chain_length} cm`;

        chain_length_container.appendChild(product_chain_length_label);
        chain_length_container.appendChild(product_chain_length_value);

        secondColumn.appendChild(chain_length_container);
    }

    const bottom_part = document.createElement('div');
    bottom_part.classList.add('bottom-card-part');

    const counter = document.createElement('div');
    counter.classList.add('counter-container');

    const button_minus = document.createElement('button');
    button_minus.innerText = '-';
    button_minus.classList.add('minus-button-dialog');

    inputQuantity.type = 'number';
    inputQuantity.style.textAlign = 'center';
    inputQuantity.value = 1;
    inputQuantity.classList.add('quantity-input-dialog');
    inputQuantity.min = '1';

    inputQuantity.addEventListener('input', function() {
        if(!item.pre_order) {
            if (inputQuantity.value > quantity_max || inputQuantity.value < 1) {
                if (inputQuantity.value > quantity_max) {
                    inputQuantity.value = quantity_max;
                } else {
                    inputQuantity.value = 1;
                }
                alert(`${vocabulary['Quantity number has to be less than or equal to quantity number in stock or and be greater than 0']}`);
            }
        }
        else{
            if (inputQuantity.value > 20 || inputQuantity.value < 1) {
                if (inputQuantity.value > 20) {
                    inputQuantity.value = 20;
                } else {
                    inputQuantity.value = 1;
                }
                alert(`${vocabulary['Maximum items for pre-order is 20, minimum is 1']}`);
            }
        }
    });

    button_minus.addEventListener('click', () => {
        if(inputQuantity.value > 1)
            inputQuantity.value -= 1;
    });
    const button_plus = document.createElement('button');
    button_plus.innerText = '+';
    button_plus.classList.add('plus-button-dialog');
    button_plus.addEventListener('click', () => {
        if(!item.pre_order) {
            if (inputQuantity.value < quantity_max) {
                let currentValue = Number(inputQuantity.value === "" ? 1 : inputQuantity.value);
                inputQuantity.value = currentValue + 1;
            }
        }
        else{
            if (inputQuantity.value < 20) {
                let currentValue = Number(inputQuantity.value === "" ? 1 : inputQuantity.value);
                inputQuantity.value = currentValue + 1;
            }
        }
    });
    counter.appendChild(button_minus);
    counter.appendChild(inputQuantity);
    counter.appendChild(button_plus);



    const add_to_cart = document.createElement('button');
    add_to_cart.type = 'submit';
    add_to_cart.classList.add('add-to-cart-dialog');
    add_to_cart.addEventListener('click', function() {
        add_to_cart_func(item, platingsSelect.value, stoneSelect.value, sizeSelect.value, Number(inputQuantity.value), add_to_cart, dialog, currency, add_to_cart_url, vocabulary, cookie, checkout_url, isCheckout);
    });
    const icon_cart = document.createElement('i');
    icon_cart.classList.add('fa-solid', 'fa-cart-shopping');
    add_to_cart.appendChild(icon_cart);
    const text_add_to_cart = document.createElement('span');
    text_add_to_cart.innerText = `${vocabulary['Add to cart']}`;
    add_to_cart.appendChild(icon_cart);
    add_to_cart.appendChild(text_add_to_cart);
    bottom_part.appendChild(counter);
    bottom_part.appendChild(quantitySpan);
    bottom_part.appendChild(add_to_cart);
    secondColumn.appendChild(bottom_part);

    card_content.appendChild(secondColumn);
    card.appendChild(card_content);

    const product_name = item.groupName;
    const groupIds = productGroups[product_name] || [];
    if (!groupIds || !Array.isArray(groupIds)) {
        console.error('Group not found or invalid');
    }
    const groupItems = groupIds.filter(groupId => groupId !== id);

    if (groupItems.length !== 0 && isCheckout!==true) {

        const card_bottom_content = document.createElement('div');
        card_bottom_content.classList.add('card-bottom-content');

        generateBottomPart(card_bottom_content, groupItems, items_array, currency, show_quantities, add_to_cart_url, vocabulary, cookie, checkout_url, isFavourite, user_auth, single_product_url, allItems, favouriteItems, pre_order_img_src, change_fav_state_url, translations_categories);

        card.appendChild(card_bottom_content);
    }
    dialog.appendChild(card);
    if (!currentPlating) {
        currentPlating = firstPlatingKey || "Rhodium"; // Default plating

        updateCarouselImages(currentPlating, allItems);
    }
    else{
        updateCarouselImages(currentPlating, allItems);
    }
    // Force reflow before animation
    dialog.classList.add('show');
    dialog.offsetHeight;
    // Show modal
    dialog.showModal();

}

function updateCarouselImages(selectedPlatingKey, allItems) {
    // Get all products in the feed
    const carouselItems = document.querySelectorAll('.card-carousel-item');

    carouselItems.forEach((carouselItem) => {
        const itemId = carouselItem.getAttribute('data-item-id'); // product ID
        const item = allItems.find(product => product.name === itemId); // Search for product

        if (item && item.platings[selectedPlatingKey]) { // If the item has this coverage
            const firstStone = Object.values(item.platings[selectedPlatingKey].stones)[0]; // Take the first stone
            if (firstStone) {
                const imageElement = carouselItem.querySelector('img'); // Find the picture in the card
                imageElement.src = firstStone.image; // Changing the image
            }
        }
    });
}

function generateBottomPart(card_bottom_content, groupItems, items_array, currency, show_quantities, add_to_cart_url, vocabulary, cookie, checkout_url, isFavourite, user_auth, single_product_url, allItems, favouriteItems, pre_order_img_src, change_fav_state_url, translations_categories){
    const bottom_title = document.createElement('div');
    bottom_title.classList.add('card-bottom-title');
    bottom_title.textContent = `${vocabulary['Similar products']}`;

    const itemListElements = groupItems
        .map((groupId, index) => {
            const groupItem = allItems.find(item => item.name === groupId);
            if (!groupItem) return null;

            return createProductCard(
                true, // isCarousel
                groupItem,
                index, // itemCounter
                allItems,
                items_array,
                favouriteItems,
                pre_order_img_src,
                vocabulary,
                translations_categories,
                currency,
                change_fav_state_url,
                show_quantities,
                add_to_cart_url,
                cookie,
                checkout_url,
                user_auth,
                single_product_url,
                false
            );
        })
        .filter(Boolean); // Remove elements equal to null

    // If the array is empty, exit the function
    if (itemListElements.length === 0) {
        return;
    }

    // Create a container for the carousel
    const card_carousel = document.createElement('div');
    card_carousel.classList.add('card-carousel-view');

    // Create navigation buttons
    const prevButton = document.createElement('button');
    prevButton.id = 'prev-btn-card';
    prevButton.className = 'prev-btn-card';
    prevButton.innerHTML = `
        <svg viewBox="0 0 512 512" width="20" title="chevron-circle-left">
            <path d="M256 504C119 504 8 393 8 256S119 8 256 8s248 111 248 248-111 248-248 248zM142.1 273l135.5 135.5c9.4 9.4 24.6 9.4 33.9 0l17-17c9.4-9.4 9.4-24.6 0-33.9L226.9 256l101.6-101.6c9.4-9.4 9.4-24.6 0-33.9l-17-17c-9.4-9.4-24.6-9.4-33.9 0L142.1 239c-9.4 9.4-9.4 24.6 0 34z" />
        </svg>
    `;

    const nextButton = document.createElement('button');
    nextButton.id = 'next-btn-card';
    nextButton.className = 'next-btn-card';
    nextButton.innerHTML = `
        <svg viewBox="0 0 512 512" width="20" title="chevron-circle-right">
            <path d="M256 8c137 0 248 111 248 248S393 504 256 504 8 393 8 256 119 8 256 8zm113.9 231L234.4 103.5c-9.4-9.4-24.6-9.4-33.9 0l-17 17c-9.4 9.4-9.4 24.6 0 33.9L285.1 256 183.5 357.6c-9.4 9.4-9.4 24.6 0 33.9l17 17c-9.4 9.4 24.6 9.4 33.9 0L369.9 273c9.4-9.4 9.4-24.6 0-34z" />
        </svg>
    `;

    // Create a container for carousel elements
    const itemListContainer = document.createElement('div');
    itemListContainer.id = 'item-list-card';
    itemListContainer.className = 'item-list-card';

    // Add carousel elements to the container
    itemListElements.forEach(element => {
        itemListContainer.appendChild(element);
    });

    // Assembling the carousel
    card_carousel.appendChild(prevButton);
    card_carousel.appendChild(itemListContainer);
    card_carousel.appendChild(nextButton);

    // Add the carousel to the DOM (for example, to a specific container)

    card_bottom_content.appendChild(bottom_title);
    card_bottom_content.appendChild(card_carousel);

    setTimeout(() => {
        const list_card = document.getElementById('item-list-card'); // Elements container
        const prev = document.getElementById('prev-btn-card'); // Button "Previous"
        const next = document.getElementById('next-btn-card'); // Button "Next"


        if (list_card && list_card.firstElementChild) {

            // Calculate the width of one element
            const itemWidth = 115; // Take the width of the first element
            // Handlers for buttons
            prev.addEventListener('click', () => {
                list_card.scrollLeft -= itemWidth; // Scroll left
            });

            next.addEventListener('click', () => {
                list_card.scrollLeft += itemWidth; // Right scroll
            });
        } else {
            console.error("List card or its children are not ready!");
        }
    }, 100); // Delay for waiting for the animation to complete
}

function add_to_cart_func(item, plating, stone, size, quantity, add_button, dialog, currency, add_to_cart_url, vocabulary, cookie, checkout_url, isCheckout){
    let doc;
    if( size === "" ){
         doc = item.platings[plating].stones[stone].real_name;
    }
    else{
         doc = item.platings[plating].stones[stone].sizes[size].real_name;
    }
    add_button.textContent = `${vocabulary['Processing']}...`;
    add_button.style.backgroundColor = "#7894a6";
    add_button.disabled = true;

    fetch(add_to_cart_url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': cookie,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'document': doc, 'quantity': quantity})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            trackAddToCart(data.product.name, data.product.product_name, data.sum, currency==="$"? "USD":"EUR");
            closeDialogWithAnimation(dialog, false);
            if(!isCheckout) {
                setTimeout(() => {

                    activate_success_card(data.product, data.quantity, data.cart_size, data.subtotal, currency, vocabulary, checkout_url);
                }, 0);
            }
            else{
                window.location.reload();
            }


        } else {
            alert(`${vocabulary['An error occured']}: ` + data.error);
            closeDialogWithAnimation(dialog, false);
        }
    });
}

function activate_success_card(item, quantity, cart_count, subtotalValue, currency, vocabulary, checkout_url){
    const dialog = document.getElementById('product-card-success');

    bindGlobalClickEvent(dialog);
    dialog.innerHTML = '';
    const card_content = document.createElement('div');
    card_content.classList.add('success-card-content');
    const image = document.createElement('img');

    image.src = item.image_url;
    image.width = `400`;
    image.height = `400`;
    image.classList.add('img-card');
    card_content.appendChild(image);

    dialogCommonSetup(dialog, item.image_url, card_content);

    //Column with text information and everything about added to cart product
    const secondColumn = document.createElement('div');
    secondColumn.classList.add('second-column');

    //Add information about added the product and about the cart
    informationSuccessSetup(secondColumn, item, quantity, cart_count, subtotalValue, currency, vocabulary);

    //Add buttons to continue shopping or to procceed to checkout
    manageButtonsSuccessSetup(dialog, secondColumn, vocabulary, checkout_url);

    card_content.appendChild(secondColumn);
    dialog.appendChild(card_content);

    let dialogMain = document.getElementById('product-card');
    dialogMain.addEventListener(
        'transitionend',
        () => {
            if (!dialog.open) {
                dialog.classList.add('show');
                dialog.offsetHeight;
                // Показываем модальное окно
                dialog.showModal();
            }
        },
        { once: true } // Let's make sure that the listener is removed after triggering
    );

}

function activate_success_card_shop(item, quantity, cart_count, subtotalValue, currency, vocabulary, checkout_url){
    const dialog = document.getElementById('product-card-success');

    bindGlobalClickEvent(dialog);
    dialog.innerHTML = '';
    const card_content = document.createElement('div');
    card_content.classList.add('success-card-content');
    const image = document.createElement('img');

    image.src = item.image_url;
    image.width = `400`;
    image.height = `400`;
    image.classList.add('img-card');
    card_content.appendChild(image);

    dialogCommonSetup(dialog, item.image_url, card_content);

    //Column with text information and everything about added to cart product
    const secondColumn = document.createElement('div');
    secondColumn.classList.add('second-column');

    //Add information about added the product and about the cart
    informationSuccessSetup(secondColumn, item, quantity, cart_count, subtotalValue, currency, vocabulary);

    //Add buttons to continue shopping or to procceed to checkout
    manageButtonsSuccessSetup(dialog, secondColumn, vocabulary, checkout_url);

    card_content.appendChild(secondColumn);
    dialog.appendChild(card_content);

    if (!dialog.open) {
        dialog.classList.add('show');
        dialog.offsetHeight;
        // Показываем модальное окно
        dialog.showModal();
    }

    console.log("IT WORKDS FINE here2");
}


function informationSuccessSetup(column, item, actual_quantity, cart_count, cartSubtotal, currency, vocabulary){
    const addedText = document.createElement('h4');
    addedText.classList.add('added-text');
    addedText.innerHTML = `<i class='fa-solid fa-check'></i> `+`${vocabulary['Product successfully added to your shopping cart']}`;
    column.appendChild(addedText);
    const nameSpan = document.createElement('h3');
    nameSpan.textContent = `${vocabulary[item.category]} ${item.product_name}`;
    column.appendChild(nameSpan);

    const numberSpan = document.createElement('h4');
    numberSpan.textContent = `${item.name}`;
    column.appendChild(numberSpan);

    const priceSpan = document.createElement('div');
    priceSpan.textContent = currency + `${item.price.toFixed(2)}`;
    column.appendChild(priceSpan);

    const platingSpan = document.createElement('spanSucc');
    platingSpan.innerHTML= `<strong>${vocabulary['Plating Material']}: </strong>` + `${vocabulary[item.plating]?vocabulary[item.plating]:item.plating}`;
    column.appendChild(platingSpan);
    const crystalSpan = document.createElement('spanSucc');
    crystalSpan.innerHTML = `<strong>${vocabulary['Crystal color']}: </strong> ` +`${vocabulary[item.stone]?vocabulary[item.stone]:item.stone}`;
    column.appendChild(crystalSpan);
    const baseSpan = document.createElement('spanSucc');
    baseSpan.innerHTML =`<strong>${vocabulary['Base material']}: </strong> ` + `${vocabulary[item.material]?vocabulary[item.material]:item.material}`;
    column.appendChild(baseSpan);

    const quantitySpan = document.createElement('spanSucc');
    quantitySpan.innerHTML = `<strong>${vocabulary['Quantity']}: </strong> ` + `${actual_quantity}`;
    quantitySpan.style.marginBottom = '20px';
    column.appendChild(quantitySpan);

    const items_count = document.createElement('spanSucc');
    items_count.textContent = `${vocabulary['Number of items in your cart']}: ${cart_count}`;
    column.appendChild(items_count);

    const subtotal = document.createElement('spanSucc');
    subtotal.innerHTML =`<strong>${vocabulary['Subtotal']}: </strong>`+ currency + `${cartSubtotal}`;
    subtotal.style.marginBottom = '20px';
    column.appendChild(subtotal);
}

function manageButtonsSuccessSetup(dialog, column, vocabulary, checkout_url){
    const container_for_success_buttons = document.createElement('div');
    container_for_success_buttons.classList.add('container-for-success-buttons');
    const continue_shopping = document.createElement('button');
    continue_shopping.classList.add('button-continue-shopping');
    continue_shopping.textContent = `${vocabulary['Continue shopping']}`;
    container_for_success_buttons.appendChild(continue_shopping);

    continue_shopping.addEventListener('click', ()=>{
        document.body.style.overflow = '';
        closeDialogWithAnimation(dialog, false);
    });

    const proceed_to_checkout = document.createElement('a');
    proceed_to_checkout.textContent = `${vocabulary['Proceed to checkout']}`;
    proceed_to_checkout.classList.add('button-proceed-to-checkout');
    proceed_to_checkout.href = `${checkout_url}`;

    container_for_success_buttons.appendChild(proceed_to_checkout);
    column.appendChild(container_for_success_buttons);
}


function setupZoom(image_container, image, vocabulary){
    const magnifier = document.createElement('div');
    magnifier.classList.add('magnifier');

    const buttonMagnifier = document.createElement('button');
    buttonMagnifier.classList.add('toggle-zoom-button');

    const magnifier_icon = document.createElement('i');
    magnifier_icon.classList.add('fa-solid', 'fa-magnifying-glass')

    const zoomSettings = document.createElement('div');
    zoomSettings.classList.add('zoom-settings');
    zoomSettings.style.display = 'none'; // Скрываем настройки по умолчанию

    // Добавляем ползунок для изменения уровня зума
    const zoom_container = document.createElement('div');
    zoom_container.classList.add('zoom-slider-container');
    const zoomLabel = document.createElement('span');
    zoomLabel.innerText = 'Zoom 1x ';
    zoomLabel.id = "zoom-multiplier";

    const zoomSlider = document.createElement('input');
    zoomSlider.type = 'range';
    zoomSlider.classList.add('zoom-slider');
    zoomSlider.min = '1'; // Minimal scale
    zoomSlider.max = '4'; // Maximum scale
    zoomSlider.step = '0.1'; // Step change
    zoomSlider.value = '1'; // Default value

    zoom_container.appendChild(zoomSlider);
    zoom_container.appendChild(zoomLabel);

    zoomSettings.appendChild(zoom_container);

    buttonMagnifier.addEventListener('mouseenter', (event) =>{
        showTooltip(event, isZoomEnabled ?  vocabulary['Turn off the magnifying glass'] : vocabulary['Turn on the magnifying glass'])
    });
    buttonMagnifier.addEventListener('click', () => {
       removeTooltip();
    });
    // Update the visibility of the zoom settings
    const updateZoomSettingsVisibility = () => {
        zoomSettings.style.display = isZoomEnabled ? 'block' : 'none';
    };

    // Add an event for changing the slider value
    zoomSlider.addEventListener('input', () => {
        const zoomLevel = parseFloat(zoomSlider.value);
        document.getElementById('zoom-multiplier').innerText = `Zoom ${zoomLevel}x`;
    // Updating the magnifying glass scale
        magnifier.style.backgroundSize = `${image.width * zoomLevel}px ${image.height * zoomLevel}px`;

    });


    buttonMagnifier.appendChild(magnifier_icon);


    image_container.appendChild(magnifier);
    const magnifier_settings_container = document.createElement('div');
    magnifier_settings_container.classList.add('magnifier-settings');


    magnifier_settings_container.appendChild(zoomSettings);
    magnifier_settings_container.appendChild(buttonMagnifier);

    image_container.appendChild(magnifier_settings_container);

    let isZoomEnabled = true;

    // Update button status
    const updateButtonState = () => {
        if (isZoomEnabled) {
            buttonMagnifier.classList.add('active');
        } else {
            buttonMagnifier.classList.remove('active');
        }
    };

    // Handler for switching the status of the magnifying glass
    buttonMagnifier.addEventListener('click', () => {
        isZoomEnabled = !isZoomEnabled;
        updateButtonState();
        magnifier.style.display = 'none';
        updateZoomSettingsVisibility();
    });

    // Show magnifying glass when pointing
    image_container.addEventListener('mousemove', (e) => {
        let zoomLevel = parseFloat(zoomSlider.value);
        if (!isZoomEnabled) return;

        // Get bounding rectangles for container and image
        const containerRect = image_container.getBoundingClientRect();
        const imageRect = image.getBoundingClientRect();

        // Check if the cursor is over the image
        if (e.clientX < imageRect.left || e.clientX > imageRect.right ||
            e.clientY < imageRect.top  || e.clientY > imageRect.bottom) {
            magnifier.style.display = 'none';
            return;
        }

        // Calculate relative coordinates within the image
        const x = e.clientX - imageRect.left;
        const y = e.clientY - imageRect.top;

        // Show the magnifier
        magnifier.style.display = 'block';

        // Position the magnifier relative to the container
        // (CSS transform centers it automatically)
        magnifier.style.left = `${e.clientX - containerRect.left}px`;
        magnifier.style.top = `${e.clientY - containerRect.top}px`;

        // Set the background image and its size/position
        magnifier.style.backgroundImage = `url(${image.src})`;
        magnifier.style.backgroundSize = `${imageRect.width * zoomLevel}px ${imageRect.height * zoomLevel}px`;
        magnifier.style.backgroundPosition = `-${(x * zoomLevel - magnifier.offsetWidth / 2)}px -${(y * zoomLevel - magnifier.offsetHeight / 2)}px`;
    });

    // Hide the magnifying glass if the mouse is out of the image
    image_container.addEventListener('mouseleave', () => {
        magnifier.style.display = 'none';
    });


    // Set the initial state of the button
    updateButtonState();
    updateZoomSettingsVisibility();
}


function createProductCard(isCarousel, item, itemCounter, allItems, filteredItems, favouriteItems, pre_order_img_src, vocabulary, translations_categories, currency, change_fav_state_url, show_quantities, add_to_cart_url, cookie, checkout_url, user_auth, single_product_url, isCheckout){

    const favouriteItem = favouriteItems.find(item_fav => item_fav.name === item.name); // Assuming `item.name` is the name of your current item
    // Check if the item was found in the favourites
    const itemIsFavourite = Boolean(favouriteItem);

    const productContainer = document.createElement('div');
    productContainer.className = isCarousel ? 'card-carousel-item' : 'product-container';
    productContainer.setAttribute('data-item-id', item.name);
    productContainer.id = `product-${item.name}`;
    productContainer.setAttribute('data-id', itemCounter);

    productContainer.addEventListener('click', () => {
        const targetItems = (filteredItems.length === 0 || filteredItems[0] === "No items found")
            ? allItems
            : filteredItems;
        generateDialogContent(
            `${item.name}`,
            targetItems,
            currency,
            show_quantities,
            add_to_cart_url,
            vocabulary,
            cookie,
            checkout_url,
            itemIsFavourite,
            user_auth,
            single_product_url,
            allItems,
            favouriteItems,
            pre_order_img_src,
            change_fav_state_url,
            translations_categories,
            isCheckout
        );
        if (isCarousel) {
            // Automatically select the current coverage in a new card
            const observer = new MutationObserver((mutations, obs) => {
                const platingDropdown = document.querySelector('.card-dropdown');
                if (platingDropdown) {
                    // Checking if the item has current coverage
                    if (!item.platings[currentPlating]) {
                        console.warn(`Coverage ${currentPlating} was not found for item ${item.name}, select the first available one.`);
                        currentPlating = Object.keys(item.platings)[0] || "Gold"; // If there are no platings available, take Gold
                    }

                    platingDropdown.value = currentPlating;
                    platingDropdown.dispatchEvent(new Event('change'));

                    obs.disconnect(); // Stopping the observation
                }
            });

            const dialog = document.getElementById('product-card');
            observer.observe(dialog, { childList: true, subtree: true });
        }
    });

    // Create the image section
    const imgSection = document.createElement('div');
    imgSection.className = isCarousel ? 'card-img-section' : 'img-section';

    const div_pre_order_icon = document.createElement('div');
    const pre_order_icon = document.createElement('img');
    pre_order_icon.className = 'icon-pre-order';
    pre_order_icon.src = pre_order_img_src;
    div_pre_order_icon.appendChild(pre_order_icon);

    const imgWrapper = document.createElement('div');
    imgWrapper.className = isCarousel ? 'card-img-wrapper' : 'img-wrapper';
    const img = document.createElement('img');
    img.classList.add(isCarousel ? "card-carousel-image" : "normal-image");
    img.src = item.preview_image;
    img.style.borderRadius = '10px';

    const iconContainer = document.createElement('div');
    iconContainer.className = 'icon-container';

    const heartIconContainer = document.createElement('div');
    heartIconContainer.className = 'heart-icon-container';
     // Converts the result to a boolean

    heartIconContainer.innerHTML = itemIsFavourite ?
    `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:#000000;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i>` :
    `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i>`; // Example with FontAwesome

    // Adding your new icon
    const newIconContainer = document.createElement('div');
    newIconContainer.className = 'new-icon-container';
    newIconContainer.innerHTML = `<i class="rts" data-size="24" data-color="#000000" style="width: 26px; height: 26px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M21.46,26H6.54C4,26,4,23.86,4,22.46V2H24V22.46C24,23.86,24,26,21.46,26Z" style="fill:none;stroke:#000000;stroke-miterlimit:10;stroke-width:2px"></path><path d="M10,8v.78c0,2.68,1.8,4.88,4,4.88s4-2.19,4-4.88V8" style="fill:none;stroke:#000000;stroke-miterlimit:10;stroke-width:2px"></path></svg></i>`;


    heartIconContainer.addEventListener('mouseenter', (event) => {

        const favouriteItem = favouriteItems.find(item_fav => item_fav.name === item.name); // Assuming `item.name` is the name of your current item
        const isFavBefore = Boolean(favouriteItem); // Converts the result to a boolean
        let message_fav = isFavBefore ? vocabulary["Remove from favorites"] : vocabulary["Add to favorites"];

        showTooltip(event, message_fav);
    });

    heartIconContainer.addEventListener('click', async (event) => {
        const favouriteItem = favouriteItems.find(item_fav => item_fav.name === item.name); // Assuming `item.name` is the name of your current item
        const isFavBefore = Boolean(favouriteItem); // Converts the result to a boolean

        // Stop the event from propagating to other elements
        event.stopPropagation();
        try {
            const response = await fetch(change_fav_state_url, {
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
                `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:#000000;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i>` :
                `<i class="rts" data-size="24" data-color="#000000" style="width: 24px; height: 24px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" style="width: 24px; height: 24px;"><path d="M14.05,6.72C8.17.2,2.57,7.54,3.67,11.76,5.56,19,14.05,23.57,14.05,23.57s7.74-4.16,10.39-11.81C25.86,7.64,20.24.13,14.05,6.72Z" style="fill:none;stroke:#000000;stroke-linecap:round;stroke-linejoin:round;stroke-width:2px"></path></svg></i>`;
        } catch (error) {
            console.error('Error updating favorites:', error);
        }
    });
    // Add event listeners for the new icon
    newIconContainer.addEventListener('mouseenter', (event) => showTooltip(event, vocabulary["Add to cart"]));

    // Append both icon containers to the iconContainer
    iconContainer.appendChild(newIconContainer);
    iconContainer.appendChild(heartIconContainer);

    // Finally, append the iconContainer to the imgWrapper or imgSection
    imgWrapper.appendChild(img);
    if (window.matchMedia("(min-width: 769px)").matches && user_auth === "True") {
        imgWrapper.appendChild(iconContainer);
    }
    // Append the imgWrapper to the imgSection
    imgSection.appendChild(imgWrapper);

    if (item.pre_order){
        imgSection.appendChild(div_pre_order_icon);
        div_pre_order_icon.addEventListener('mouseenter', (event) => {
            showTooltip(event, vocabulary["This item is only available for pre-order"]);
        });
    }
    // Create the info section
    const infoSection = document.createElement('div');
    infoSection.className = 'info-section';
    const nameSpan = document.createElement('span');
    nameSpan.className = isCarousel ? 'carousel-price' : 'info-name';

    let parts = item.product_name.split(" ");
    // Remove the last word
    let last_word = parts.pop();
    // Join the remaining parts to form the full phrase
    let full_phrase = parts.join(" ");
    nameSpan.textContent = translations_categories[full_phrase] ? translations_categories[full_phrase]+ " " + last_word : item.product_name;
    const priceSpan = document.createElement('span');
    priceSpan.className = isCarousel ? 'carousel-price' : 'info-price';
    priceSpan.textContent = currency + `${item.price}`;
    infoSection.appendChild(nameSpan);
    infoSection.appendChild(document.createElement('br'));
    infoSection.appendChild(priceSpan);

    // Assemble the product container
    productContainer.appendChild(imgSection);
    productContainer.appendChild(infoSection);

    return productContainer;
}

function trackAddToCart(productId, productName, productPrice, currency) {
  cbq('track', 'AddToCart', {
    content_ids: [productId],
    content_name: productName,
    value: productPrice,
    currency: currency
  });
}

let productGroups = { 'Rosalie': ['63338', '61272', '62242', '63542'], 'Vishap': ['32348', '12307', '23073'], 'Royal': ['61198', '63271', '62145'], 'Gallantry': ['32428'], 'Vulcan': ['63279'], 'Pacify': ['32400', '12399'], 'Medium': ['KS013R70', '22074', 'KS013RG70', 'KS013R40', 'KS013RG40', 'KS013RG55', 'KS013G70', 'KS013R90', 'KS013G90', 'KS013G40', 'KS013G55', 'KS013RG90', 'KS013R55'], 'Mati': ['41206', '32387', '23093', '23092', '32389', '23094', '12339', '32388', '12341', '12342'], 'Cat': ['11362'], 'Smooth': ['61186', '63265', '63262', '63263', '63264', '62130', '62133'], 'Camille': ['63339', '61273', '62243'], 'Drop': ['21018', 'S24019'], 'earring': ['22071', '62060', '22700', '22148', '22702', '62042', '22285', '21002', '22110', '22000', '62057', '22086', '22973', '62066', '62075', '22698', '22975', '22394', '22722', '22654', '22715', '62062', '22186', '22697', '22687', '22254', '62067', '22312', '22707', '22315', '22142', '22695', '22139', '22097', '62080', '22194', '22442', '62078', '22126', '21001', '21008', '22446', '22288', '22146', '22113', '22343', '22012', '22077', '22341', '22970', '22319', '22646', '21009', '22201', '22708', '22630', '62124', '21004', '22132', '21013', '22971', '22204', '22974', '22688', '62079'], 'Augusta': ['63274', '62148', '61200'], 'Glee': ['62272', '63358', '61300'], 'Nice': ['61068'], 'Charlotte': ['23088', '12280'], 'Spirit': ['63347', '62261'], 'Duo': ['41122'], 'Praise': ['23181', '12457'], 'Iris': ['63351'], 'Pearl': ['22847', '32298', 'S24016', 'S24015', '22921', '22922', '32297', 'S24014', 'S24013', '41156', '22980', '12210', '12066', '12050'], 'Nymph': ['32375', '12331', '23042'], 'Bohemia': ['12393', '12392', '23118'], 'Juventa': ['63273', '62147'], 'Florita': ['11110'], 'Earring': ['62258', '23173', '62259', '62173', '23170', '23169', '23171', '22740', '62257', '23168', '23172', '62256', '23166', '62255', '23174'], 'Clavis': ['32241', '11989', '22801'], 'Row': ['59100'], 'Legend': ['12113', '63260', '22890'], 'Little': ['32233', '11957', '32234', '11956'], 'Pleasure': ['32402'], 'Lithuanian': ['41168'], 'Boost': ['22916', '12157'], 'Hebo': ['12298', '32342'], 'Real': ['41036'], 'Breathe': ['22841'], 'Hop': ['23003'], 'Find': ['22116'], 'Splendor': ['63529', '63296', '62164', '61210'], 'Joy': ['22786', '32239', '11972'], 'Outspoken': ['12391'], 'Velvet': ['61292', '63346', '62260'], 'Close': ['32099'], 'Bro': ['12233', '22996'], 'Luster': ['41225', '23192', '12466'], 'Fun': ['22331'], 'Felicity': ['61270', '62239'], 'Eternal': ['11397', '32319', '12256'], 'Artemis': ['32384', '62152'], 'Corazina': ['22792', '11982'], 'Jik': ['41189'], 'Leaves': ['23104', '12372'], 'Tropics': ['12446'], 'Lofty': ['23200', '12476', '32430'], 'Reach': ['22389', '11523'], 'Ginkgo': ['63540', '61267', '63336', '61268', '62237'], 'Life': ['11671', '22594', '32293'], 'Anima': ['41200', '23086', '32372', '12328'], 'Emotions': ['12326'], 'Luxury': ['57004'], 'Leaf': ['58013', '22686', '11792'], 'Hang': ['62137'], 'Fence': ['32311'], 'Stick': ['22981'], 'Edge': ['63266'], 'Chara': ['58055'], 'FS': ['32291', '12185', '12187', '22931', '32290', '12186'], 'Lion': ['41203', '32379', '23090', '12338'], 'Joice': ['12023', '22821'], 'Chain': ['KS014G40', 'KS002', 'KS003', 'KS014R40', '57143', 'KS014RG40'], 'Initial': ['11850', '11844', '11854', '11846', '11837', '11852', '11830', '11848', '11833', '11831', '11847', '11840', '11841', '11845', '11855', '11832', '11836', '11851', '11853', '11838', '11839', '11835', '11843', '11834', '11842', '11849'], 'Mellow': ['23186', '12459'], 'Me': ['22892', '12115'], 'Legit': ['62125', '62126'], 'Zephyr': ['63305', '63303', '63306'], 'Amanor': ['23052'], 'Clear': ['61112'], 'Triumph': ['61138', '62081'], 'Eye': ['41205'], 'Point': ['12160', '22917'], 'Loop': ['12227', '22993'], 'Respect': ['12451'], 'it': ['56900'], 'Chaton': ['S24003', 'S24002', 'S24001'], 'Twice': ['22572'], 'Attitude': ['32356'], 'Boxy': ['41211'], 'Undo': ['32307', '12225'], 'Entitlement': ['12378'], 'Top': ['32226', '23011', '12251'], 'Junction Cross': ['12475'], 'Couple': ['32160', '11613'], 'Poly': ['12335'], 'Sunshine': ['63268', '61188', '62132', '63525'], 'Spotlight': ['63531', '61225', '62180', '63320'], 'Neptune': ['12302', '32346'], 'BlueEye': ['41204'], 'Anthosai': ['23063', '12284'], 'Own': ['22918', '32288', '12169'], 'Butterfly': ['S24017', '39102', 'S24011'], 'Statement': ['12293'], 'Sound': ['12243', '22965'], 'Brilliance': ['63252', '63215', '63222', '63253', '61179', '62117', '61125', '63218', '61180', '62115', '62116', '61124', '61154'], 'Horizon': ['41000', '41004'], 'Moon': ['11945'], 'Love': ['11703', '32224', '39104'], 'Eternita': ['63290'], 'Simple': ['63216', '11329', '11471', '11640'], 'Doggy': ['22699', '11808'], 'Kindness': ['12417', '32354', '23039'], 'Better': ['62107'], 'Halfmoon': ['23177', '12453'], 'Believe': ['11328', '61177'], 'Meriva': ['11073'], 'Fleur': ['32003', '11030', '22073', '11171'], 'Flourish': ['22913', '12153'], 'Double': ['12007', '22156', '22155', '61178', '22815'], 'Anahita': ['41193'], 'Way': ['22983', '12229'], 'Carmen': ['23095', '12345'], 'Bright': ['22112', '11076'], 'Turtle': ['41201', '23087', '32373', '12330', '12136'], 'Lauma': ['63280'], 'Compass': ['61193'], 'Classic': ['22105', '61185', '63520', 'V61185', '63259'], 'Wake': ['12267', '23024'], 'Exquisite': ['41207'], 'back': ['K0003G', 'K0002R', 'K0001R', 'K0002G', 'K0003R', 'K0001G'], 'Helios': ['12278', '32333'], 'Character': ['41198'], 'Tennis': ['32034', '22758', '11910'], 'Hold': ['32315'], 'Best': ['63528', '62136', 'V63528', '61191', '62135', '61190'], 'Passion': ['23026', '12269', '12270'], 'Fujin': ['32336'], 'Jolie': ['63225'], 'Princess': ['32248', '12079', '41065', '12032', '41064', '22834'], 'Quartet': ['63301', '61215'], 'Shahapet': ['41186'], 'Butterflower': ['23097', '12340'], 'Moxie': ['32371'], 'Origin': ['32313', '22976', '12207'], 'Apricus': ['61290'], 'Coleus Green': ['63353'], 'More': ['11330', '11148', '22164', '22295'], 'Blossom': ['32404', '32403', '32361', '32405', '32357', '32358', '32376', '32360', '32377', '32359'], 'Chandelier': ['23091'], 'Young': ['22729', '11924'], 'Torre': ['22805', '11996'], 'Prism': ['63299', '61212'], 'Mercy': ['61317'], 'Ameretat': ['32396', '12370', '23117'], 'Vote': ['62143', '61197'], 'Flower': ['59101', '11947', '22069', '22774'], 'Sunly': ['61143', '62084'], 'Monte': ['58016'], 'Polaris': ['63548'], 'Defiy': ['63343'], 'Freeze': ['12425', '23146'], 'Secret': ['12052', '22851'], 'Earth': ['23071'], 'Prerogative': ['41210'], 'Uno': ['11740', '22623'], 'Tane': ['32332', '12277'], 'Temple': ['32327'], 'Cube': ['S24004', '22606', 'S24005'], 'Pomona': ['23043'], 'Aura': ['23152', '12432'], 'Taboo': ['12276', '23037'], 'Romantic': ['12264', '41166', '23020', '32328', '12263'], 'Rings': ['11062'], 'Emesh': ['41190'], 'Meed': ['41226', '12472', '23199'], 'Cheer': ['63349', '62263'], 'Serendipity': ['63317', '62178', '61222'], 'Umay': ['41175'], 'Horae': ['23046'], 'Orbit': ['22779', '11953'], 'Port': ['32194'], 'Zest': ['63325', '61229'], 'Mini': ['22400'], 'Gaudí': ['32167', '22451', '11605', '41110', '11570', '58045', '58046', '11571', '11590', '11879', '11743'], 'Flor': ['22617', '11701'], 'Hallow': ['32426'], 'Away': ['32321', '12279', '23016', '12257'], 'Libella': ['58006'], 'Morningstar': ['63313', '61218', '62175'], 'MamaKuka': ['63315'], 'Scene': ['12259', '23018'], 'Goccina': ['22796', '11986'], 'Care': ['22934'], 'Lien': ['61313'], 'Windrose': ['63319', '62179', '61224'], 'Signature': ['23131'], 'Saint': ['62285', '61316'], 'Fire': ['23001', '12245', '32314'], 'Meadow': ['12433', '32415', '23153'], 'Tainted': ['32320'], 'Gerbera': ['32424', '23193', '12467'], 'Into': ['12230', '22991'], 'Courage': ['62123', '12253', '23013'], 'Fairy': ['61307'], 'Anchor': ['11540', '22399'], 'Virtue': ['61192', '62138'], 'Solitaire': ['41001', '61118'], 'Hermione': ['41172'], 'Star': ['S24010'], 'Power': ['22590', '11670'], 'Ukulan': ['23045', '12321'], 'Bowy': ['23004'], 'Dryad': ['32362'], 'Great': ['22672', '11757'], 'Cuore': ['23124', '41217'], 'Upside': ['22861', '12077'], 'Hathor': ['63276'], 'Twist': ['41151'], 'Change': ['41164', '23081', '41165', '32316', '23014', '12254'], 'Venus': ['63297'], 'Weave': ['32044'], 'Leafy': ['58066'], 'Indra': ['41182'], 'Damu': ['12289'], 'Solitär': ['63254', '63256', '62119', '61182', '62118', '62120'], 'Deja Vu': ['32325', '32324', '32326'], 'Nariphon': ['41196'], 'Prosper': ['32416', '12434', '23154', '11998', '22807'], 'Meliora': ['61289'], 'Skyline': ['41136', '11793'], 'Feronia': ['41177', '23057'], 'Silvanus': ['23044', '12282'], 'You': ['12292', '12116'], 'Vitae': ['11692'], 'Chance': ['23145', '12424'], 'Pure': ['63270', '63210', '63211', '62144', '61109'], 'Expression': ['11077'], 'Orient': ['11951', '32270', '22885', '22777'], 'Papilio': ['62278'], 'Ritual': ['63309'], 'Hemera': ['61203'], 'Dauntless': ['63331', '61256', '62233'], 'Miracle': ['23180', '12456'], 'Mystique': ['63328', '61242', '62213'], 'Chasca': ['62197'], 'Voila': ['22817'], 'Marshmallow': ['23126'], 'Rabbit': ['41202', '32386', '12329', '23085', '32374'], 'Kudos': ['32427'], 'Moment': ['32399'], 'Bun': ['12025', '22832'], 'Prestige': ['11200', '32057'], 'Asterlove': ['23159', '12439'], 'Utopia': ['23096'], 'large': ['22206'], 'Soriso': ['32353', '23069'], 'Sanctuary': ['63342'], 'Symphony': ['12426', '23147'], 'Up': ['22998'], 'Good': ['23022', '23023'], 'Rapunzel': ['41214'], 'Fantasia': ['63357', '62271', '61299'], 'Flow': ['32251', '22845', '12049'], 'RoyalDrop': ['61199', '62146'], 'Foursquare': ['63231', '61135'], 'Fiorellino': ['58048'], 'Pear': ['61148', '62089'], 'Flexibility': ['23116', '12390'], 'Heartbeat': ['12419', '23144'], 'Tree': ['11973', '22787'], 'Nexus': ['32406', '23141'], 'MyHeart': ['32249'], 'Saiph': ['63547'], 'Freak': ['12262', '32323'], 'Sinless': ['62284', '61315'], 'Beautify': ['12226', '22985', '32308', '22987'], 'Extase': ['22731', '11882', '11883'], 'Down': ['32026'], 'Villa': ['11337', '22304'], 'There': ['22896', '12119'], 'Deify': ['61284'], 'Diamond': ['11025', '22066'], 'Maria': ['63545'], 'Arista': ['12320'], 'Waterfall': ['23076'], 'Brilli': ['22364', '22363'], 'Alma': ['12395'], 'Tres': ['63519'], 'Fond': ['32158', '11615'], 'chain': ['KS015', 'KS004', 'KS001'], 'Oblong': ['41216'], 'Jump': ['23028', '23027'], 'Freedom': ['12288', '41208', '23098', '12373'], 'Romana': ['23058'], 'Links': ['41161', '41163', '41162'], 'Fiesta': ['22158'], 'Open': ['12396', '11861'], 'Blush': ['63352'], 'Music': ['11942', '22771', '22770'], 'Why': ['63247'], 'Metsaema': ['12297', '32341'], 'Timeless': ['11922', '22764'], 'Lucina': ['12287', '23068'], 'Soon': ['32186', '11133', '22145'], 'Distinct': ['63251', '62113', '61176'], 'Lunina': ['22793', '11983'], 'Triple Love': ['22966'], 'white': ['11010'], 'Whorl': ['58052'], 'ApamNapat': ['12367'], 'Lover': ['32294'], 'Posh': ['63356', '62268', '61296'], 'Cara': ['61312'], 'Azalea': ['63355', '62266', '61294'], 'DreamCatcher': ['62188', '61251'], 'Dance': ['31000', '31001'], 'Genuine': ['63258', '62121', '62122', '61184', '61183'], 'Wispy': ['12221', '22988', '32304', '32306', '12224'], 'Soul': ['63332', '62234', '61255', '63539'], 'Like': ['32302'], 'Eddy': ['32414'], 'Composition': ['11078'], 'Cleopatra': ['63284'], 'Single': ['22096', '11056'], 'Synthia': ['61278', '62250'], 'Kiss': ['32181'], 'Botany': ['23189', '12463'], 'Divide': ['32022'], 'Maia': ['63295'], 'Sheer': ['61319'], 'Guardian': ['62212', '63329', '63537'], 'Florescence': ['12435', '32417', '23155'], 'Smash': ['23196', '12471'], 'Maya': ['62254', '63362', '61280'], 'Precioso': ['32253', '22866'], 'Grey': ['31003'], 'Pearly': ['22183', '41051'], 'Karma': ['62168', '63302', '61282'], 'Coqui': ['11744', '22647', '11745'], 'Viridios': ['12305'], 'Heart': ['S24008', 'S24009', '11616', '12158'], 'Glory': ['12021', '22819'], 'Sagrada': ['11575', '11816', '11873'], 'Demeter': ['12281'], 'Focus': ['22925', '12180'], 'Giant': ['11512', '22379'], 'Esteem': ['12261', '32322'], 'Libertá': ['23100', '12375', '32391'], 'Loving': ['63291'], 'Water': ['63267', '63524', '61187', '62131'], 'Halo': ['63278', '61201'], 'Dryads': ['63275'], 'Wishful': ['23007', '12247'], 'Agni': ['41191'], 'Link': ['32049'], 'Theatrical': ['12403', '32401', '23109'], 'Rush': ['12265', '23021'], 'Crescent': ['63314', '62176', '61219'], 'Cushy': ['12480', '23203'], 'Target': ['12234', '32312', '22997'], 'Oceanides': ['23080', '12308', '32363'], 'Starfish': ['11074', '32033', '22111', '11138', '11137', '11897'], 'Freesia': ['58064'], 'Mix Tape': ['32331'], 'Furrin': ['62209'], 'Clamp': ['22937'], 'Wheely': ['63241', '61136'], 'Pontus': ['63287'], 'Run': ['12268', '23025'], 'Core': ['12209'], 'Lush': ['61302', '63360', '62274'], 'Plutos': ['12332'], 'Dashing': ['62215', '61263'], 'Medeina': ['41167'], 'Again': ['12266', '12206'], 'Drive': ['12193', '41159'], 'Favour': ['11534'], 'Catch': ['61142', '62083'], 'Gaudi': ['11825', '12012', '12011', '32212', '12010', '11826'], 'Reason': ['12252', '23012'], 'Dream': ['62264', '61293'], 'Delite': ['22759', '11974', '11911'], 'Pik': ['12427', '23148'], 'Rain': ['11210', '22199'], 'Smitten': ['12197', '32300'], 'PachaMama': ['61232'], 'Cronus': ['41169'], 'Nobly': ['23158', '58050', '12438'], 'Luminous': ['12449'], 'Relate': ['63238'], 'Step': ['63239', '61153', '63527', '63522'], 'Diana': ['23075'], 'Right': ['12380', '32410', '23132'], 'Tender': ['61126'], 'Meliae': ['41195'], 'Satin': ['63348', '62262'], 'Mix': ['12273'], 'Unique': ['23149', '12428'], 'Varuna': ['12316', '23074'], 'Lucent': ['11619', '11618', '32162', '22559'], 'River': ['12248', '23008'], 'Imperial': ['63250', '63249'], 'Twilight': ['12429'], 'Enter': ['22928', '22929'], 'Miara': ['12304', '23078'], 'Duchesse': ['62104', '63246', '61168'], 'Roma': ['12322'], 'Mariposa': ['63530', '62167', '61213'], 'Glint': ['32292', '12188', '22938'], 'Hero': ['11898', '22747'], 'Carpel': ['58060'], 'Tell': ['22979'], 'Less': ['32030'], 'Style': ['11749', '22651'], 'Concept': ['11993', '22802'], 'Pluto': ['63285'], 'Atlas': ['62157'], 'Keylove': ['12171'], 'Sense': ['22982'], 'Oasis': ['63341', '61279', '62251'], 'Blessing': ['63300'], 'Anito': ['63298', '61211', '62165'], 'Breath': ['12042'], 'Alegra': ['22872', '12126'], 'Full Heart': ['22091', '11024'], 'Terra': ['41187'], 'Finest': ['23162'], 'Mihr': ['23049'], 'Blinky': ['32232'], 'Stunning': ['32247', '12034'], 'Show': ['12404', '23142'], 'Trust': ['41209', '32006', '32005', '23099', '12374', '11273'], 'Delight': ['32393', '12377', '23102'], 'Idea': ['12406'], 'Prayer': ['23019', '12260'], 'Fame': ['63345', '62225', '32225', '61252'], 'People': ['23031', '23041', '12271'], 'Triad': ['61214', '61241'], 'Grid': ['12133'], 'Daydream': ['12181'], 'Penghou': ['41185'], 'Kodama': ['41171'], 'Caroline': ['63340', '63543', '62246'], 'Vesta': ['63293'], 'XL': ['22207'], 'Loco': ['32252', '12313'], 'Sweets': ['23151', '12431'], 'Learn': ['32272', '22895'], 'Coast': ['22396', '11536'], 'Cameo': ['11230'], 'Viola': ['S24018'], 'Panorama': ['12242', '22999'], 'Edelweiss': ['11819'], 'Expand': ['22756', '11908'], 'Merge': ['11894'], 'Pixie': ['32343', '12299'], 'Say': ['32301', '12205'], 'Towards': ['32411', '23040'], 'Tolerance': ['32408'], 'Treat': ['32279'], 'Just': ['22604', '11685'], 'Rainbow': ['22846', '32116', '11395', '12051', '32246'], 'Vow': ['62281', '61309'], 'United': ['12004', '22813'], 'Connected': ['32296'], 'Lobelia': ['62270', '63550', '61298'], 'Asterie': ['62200'], 'Ring': ['57141'], 'Choice': ['32008', '12384'], 'Tropfen': ['11022'], 'Libya': ['63283'], 'Izanami': ['23083', '12324', '32378'], 'Renown': ['12478'], 'Cherry': ['12443'], 'Belladonna': ['63312'], 'Achive': ['61195', '62141'], 'Baia': ['63248', '61171', '62109'], 'Speak': ['12045', '22871'], 'Kingly': ['22694'], 'Rakapila': ['41178'], 'Astral': ['12454', '23178'], 'Universe': ['32014', '23107', '12415'], 'Message': ['12002'], 'Elissa': ['61202'], 'ZigZag': ['12319'], 'Closer': ['32286', '12154'], 'Closed': ['11769'], 'Aglow': ['23188', '41224', '12462'], 'Icy': ['23184'], 'Newy': ['61144', '62085'], 'Persephone': ['23056', '61204'], 'Jasmine': ['41212'], 'Sweet': ['22776', '22070'], 'Ardour': ['12448'], 'Eccentric': ['12386'], 'Nightsky': ['22936'], 'Enchanted': ['61231'], 'Suadela': ['23089'], 'Mayari': ['23082', '12369'], 'Dangle': ['11788', '32200'], 'TwoCats': ['12194'], 'Windfall': ['63318', '61223', '62224'], 'Tiana': ['41213'], 'Fish': ['32334'], 'Amaterasu': ['32344', '12300'], 'Call': ['22897', '12120', '32274'], 'Doubleheart': ['11858'], 'Cherish': ['61283'], 'Relax': ['32228', '22750', '11903'], 'Cybele': ['41173'], 'Lilith': ['63359', '62273', '61301'], 'Planet': ['11410'], 'Promise': ['63344'], 'Treasure': ['12095', '32250'], 'Esostre': ['41199'], 'Ladybug': ['61260', '11182', '62231'], 'Muse': ['61205'], 'Titanic': ['12134'], 'Palmtree': ['63316', '61221', '62223'], 'Shadow': ['32317'], 'Sinann': ['23140', '12309'], 'Peak': ['22728', '11881'], 'Saiph small': ['63549'], 'Benefit': ['62134', '61189', '63526'], 'Comfort': ['62071', '63521'], 'Cloud': ['22911', '12150'], 'Turn': ['22412'], 'Unica': ['62108'], 'Dual': ['22417'], 'Gentle': ['61318'], 'External': ['11804'], 'Diez': ['62150'], 'Prezzy': ['12203'], 'Twig': ['58061'], 'Beam': ['22960', '12190'], 'Sarruma': ['12290'], 'Art': ['11714', '11875', '11713'], 'Reina': ['61167', '62102'], 'Radio': ['32287'], 'Nereids': ['23047'], 'Plain': ['32050', '32222'], 'Fine': ['32105', 'KS012R40', 'KS012G55', 'KS012R55', '11353', 'KS012G40', 'KS012RG55', 'KS012RG40'], 'Luna': ['11765'], 'Bone': ['11667'], 'Balance': ['61196', '63269', '62142'], 'MamaZara': ['62192'], 'Lempo': ['63272'], 'Peace': ['23070', '12294'], 'Koli': ['61308', '62280'], 'Select': ['41160'], 'Loyal': ['23115'], 'Ariel': ['41215'], 'Wintertime': ['32425', '12469', '23195'], 'Luxe': ['41227', '23201', '12477'], 'Minerva': ['63277'], 'MamaCocha': ['62191'], 'Liberty': ['63330', '62228', '61257'], 'Maple': ['12468', '23194'], 'Place': ['22203'], '36': ['21014'], 'South': ['32091'], 'Inner': ['61150', '62090'], 'Now': ['22837'], 'True': ['11123', '61147', '32295'], 'Asclepius': ['32380'], 'Low': ['23119'], 'MonaLisa': ['12291'], 'Silent': ['12336'], 'Decorate': ['23002'], 'Rose': ['58019'], 'Horseshoe': ['62235', '61208'], 'Lilium': ['58054'], 'Next': ['32173'], 'Touch': ['12076'], 'Skimmer': ['58056'], 'Polestar': ['63308', '61217'], 'Pearling': ['12161'], 'Sail': ['22781'], 'Joker': ['41219', '23160'], 'Repose': ['32397'], 'Apam': ['32351', '12303'], 'Infinity': ['63029', '61092'], 'Develop': ['11902', '22749'], 'Purity': ['63361', '61303', '62275'], 'Affection': ['23143', '12418'], 'Number': ['11610'], 'Vida': ['11815', '32257', '12093', '22870'], 'Contact': ['63234'], 'Edellove': ['23157', '12437'], 'Perk': ['32407', '23135'], 'Flex': ['32117'], 'Tapio': ['41180'], 'Hama': ['41170'], 'Capella': ['63546'], 'Hesper': ['63282'], 'Serenity': ['62171'], 'Sheaf': ['41184'], 'Bhumi': ['41179'], 'Pen': ['57017'], 'Dignity': ['32429'], 'Moonlight': ['32318', '12255', '23015'], 'Farfallina': ['11984', '22794'], 'My': ['12094'], 'Flowers': ['58001'], 'Safeguard': ['62204', '61239'], 'Really': ['23017', '12258'], 'Diva': ['22188'], 'Class': ['11548'], 'Celum': ['12333'], 'Sleet': ['23182', '41223', '58068'], 'Quadrat': ['41181'], 'Secure': ['12460', '23187'], 'Beat': ['23036', '11126', '12275'], 'Purpose': ['12394'], 'Dahlia': ['62248', '61276'], 'Oasis long': ['62287'], 'Pensive': ['62227', '61254'], 'Luminary': ['23150', '12430'], 'AnnaPerenna': ['62183'], '12cm': ['9209', '9206', '9205'], 'Bliss': ['63304'], 'Pursue': ['12402'], 'Surround': ['32245'], 'Junction Simple': ['12473'], 'Pack': ['11677', '22599'], 'Respire': ['32394', '12413'], 'Finesse': ['61269', '62238'], 'Divers': ['11777'], 'Extra': ['41133'], 'Volturn': ['61237'], 'Aranyani': ['12314'], 'Kurozome': ['12312'], 'Family': ['61266'], 'Papillon': ['12447', '32421'], 'Dualism': ['23176', '12452'], 'Precious': ['11134', '32043'], 'Barsamin': ['32345', '12301'], 'Esoteric': ['23179', '12455'], 'Honeybee': ['12445'], 'Hidden': ['22235', '11246'], 'Odysseus': ['32382'], 'Cupid': ['12420'], 'Pleased': ['11212'], 'Signs': ['61115'], 'Visayan': ['41174'], 'Always': ['11483'], 'Mummy': ['61265'], 'Excuse': ['23130'], 'Azure': ['62201', '61240', '62211'], 'Gracious': ['32413'], 'Amo': ['11772'], 'State': ['61151', '62092'], 'Nantosuelta': ['32335'], 'Coco': ['32275'], 'Accept': ['12240'], 'Flutter': ['62279', '63551', '61306'], 'CRY': ['11236'], 'Tune': ['12239'], 'Inside': ['32001'], 'Shine': ['11997', '22806', '22733'], 'Violet': ['S24012'], 'Shore': ['22926', '12182'], 'Blind': ['23005'], 'Faunus': ['41197'], 'Company': ['12146', '22907', '32281'], 'Sun': ['11824', '32221'], 'Hail': ['58067'], 'Stellina': ['22791', '11981'], 'earrings': ['23072'], 'Private': ['41134'], 'HulaHoop': ['62149'], 'Deja': ['23032'], 'Pluma': ['11347'], 'Crossing': ['23030'], 'Local': ['32164'], 'Rank': ['32088', '11321'], 'Complex': ['22754'], 'Wurfel': ['21015'], 'Day': ['62139'], 'Sunrise': ['12053'], 'Marguerite': ['63310'], 'Pend': ['11441', '22035'], 'Spring': ['12208'], 'Wind': ['59103'], 'Ivory': ['61305', '62277'], 'Donor': ['32299'], 'Favonius': ['62158'], 'Dropping': ['23029'], 'Solar': ['22933'], 'Tendresse': ['62199', '61235'], 'Shimmer': ['11899'], 'Wildflower': ['23191', '12465'], 'Digi': ['22831'], 'Stopper': ['K0004'], 'Mulan': ['23050'], 'Juno': ['62151'], 'Forever': ['62103', '61164'], 'Hibiscus': ['62267', '61295'], 'Darling': ['11388'], 'Anemone': ['58065'], 'Sansin': ['41188'], 'Calathea Pink': ['63354'], 'Mystery': ['22778', '11952'], 'Heavenly': ['61314', '62283'], 'Edelbloom': ['12436', '23156'], 'Unity': ['61304', '62276'], 'Sublime': ['23067', '12285', '32340'], 'Animation': ['22732', '11884'], 'Success': ['62082', '61139'], 'Freehand': ['23112', '32409', '41218'], 'Volition': ['23105', '12400'], 'Destiny': ['12440'], 'Nifty': ['62170'], 'Endless': ['12237'], 'Vibe': ['23164'], 'Candor': ['32392', '23101', '12376'], 'Caring': ['12295'], 'Split': ['11990'], 'GP': ['22294'], 'Glitz': ['63538'], 'Deli': ['22783'], 'Irpitiga': ['32364'], 'Elephant': ['58047'], 'Selena': ['62162'], 'Brill': ['22329', '32109'], 'Silk': ['11058', '32017'], 'Whisper': ['61281'], 'Drape': ['22967', '12244'], 'Heaven': ['61127'], 'Estar': ['12069'], 'Posess': ['11143'], 'Highness': ['32433'], 'Ruby': ['61275', '63544', '62245'], 'Vogue': ['61264', '62214'], 'Sleet Double': ['23183'], 'Aspect': ['12201'], 'Espira': ['11999'], 'Pin': ['22628'], 'RH': ['12235'], 'Flamme': ['12423'], 'Easy': ['32207'], 'Lagoon': ['32422'], 'Plumnus': ['23061'], 'Nightshade': ['63311'], 'Compo': ['22406'], 'Daphne': ['62247'], 'Tala': ['32349'], 'Junction ': ['12474'], 'Astro': ['12017'], 'Rondo': ['22067'], 'Poseidon': ['12334'], 'Shuffle': ['12274', '32330'], 'Dive': ['62106', '61172'], 'Cross': ['61100'], 'High': ['62105'], 'Rune': ['62177'], 'Mosaic': ['23033', '12272'], 'Dangun': ['32337'], 'Mom': ['61165'], 'Moira': ['62210'], 'Cozy': ['32423', '12458', '23185'], 'Wealth': ['32431'], 'Pawy': ['11809'], 'Laurels': ['23175', '12450'], 'Gaulish': ['23053'], 'Affinity': ['62252'], 'Sevilla': ['11723'], 'Gaia': ['23059'], 'Baianai': ['23066'], 'Wonder': ['11976', '11975', '41146', '22798'], 'Majesty': ['32432'], 'Semele': ['61209'], 'Second': ['11704'], 'Mixed': ['11272', '32254'], 'Club': ['22388', '11522'], 'Silverpaw': ['62230', '61259'], 'Dusk': ['41228', '12479', '23202'], 'Fortune': ['63288'], 'Cuff Line': ['22977'], 'Under': ['22964', '12195'], 'Helix': ['12389'], 'Vivre': ['11859'], 'Outround': ['11817'], 'Hercules': ['12337'], 'Erinia': ['62206'], 'Small': ['22082'], 'Free': ['32218'], 'Zeal': ['63552', '62286'], 'Sheen': ['58062'], 'Four': ['22330'], 'Silverdog': ['61258', '62229'], 'Limit': ['22927'], 'White': ['21016'], 'Trivia': ['62156'], 'Nectar': ['23190', '12464'], 'Wintertime Skate': ['12470'], 'Soar': ['63535', '61233'], 'Galactic': ['22685', '11791'], 'Heyday': ['58069'], 'Tucky': ['12223', '22984'], 'Perfect': ['23009', '12249'], 'Frank': ['23114'], 'Cypress': ['23198'], 'Trio': ['22989'], 'Plank': ['22994', '12204'], 'Austras': ['63289'], 'Basic': ['62072'], 'Bee': ['12444', '23167'], 'Sterilization': ['V232'], 'Sky': ['22968'], 'Femme': ['23010', '12250'], 'Boreas': ['32381'], 'Flair': ['22972'], 'Bamboo': ['58063'], 'Selene': ['61288'], 'TwinHearts': ['62169'], 'Ossa': ['62159'], 'Knot': ['11593'], 'Soft': ['11216'], 'Gaudí Drac': ['22426'], 'Ceres': ['23055'], 'Soothe': ['23138'], 'Culture': ['12236'], 'Mia': ['62241'], 'Reunite': ['12414'], 'Pace': ['61141'], 'Your': ['22893'], 'Cornetto': ['12145'], 'Spell': ['41157', '22986', '12220'], 'Mind': ['11683'], 'Sylvan': ['62208'], 'Amore': ['61206'], 'Ops': ['23062'], 'Regal': ['22767'], 'Perla': ['62190'], 'Act': ['23110'], 'Ace': ['23161'], 'Label': ['32184'], 'Twisty': ['23035'], 'Day&Night': ['22990'], 'Embrace': ['12421'], 'Between': ['32058'], 'Back': ['62100'], 'Belief': ['23163'], 'Alone': ['32305'], 'Willow': ['41221'], 'Monarch': ['58058'], 'Position': ['12199'], 'Subtle': ['61137'], 'Custody': ['63541'], 'Amihan': ['23051'], 'Grace': ['62207'], 'Bacchus': ['23064'], 'Florid': ['23197'], 'Trance': ['23129'], 'Aroma': ['58049'], 'Lunar': ['22932'], 'Simply': ['61119'], 'Acting': ['23106'], 'Pearl Sissy': ['21020'], 'Glacier': ['62091'], 'Dolphin': ['39100'], 'Sea': ['11185'], 'cuff': ['22978'], 'Heely': ['12044'], 'Hearty': ['32089'], 'Elizabeth': ['12283', '23084'], 'Levity': ['23128'], 'Lovely Pearly': ['22780'], 'Ophelia': ['61271'], 'Flamingo': ['12139'], 'Panacea': ['62154'], 'Sophia': ['62244', '61274'], 'Hecate': ['32383'], 'Ranginui': ['32352'], 'Elements': ['32037'], 'Contessa': ['32063'], 'Dot': ['22258'], 'Spinner': ['62253'], 'Hoopy': ['62205'], 'Raise': ['32284'], 'Gallia': ['32347', '12306'], 'Alice': ['62249', '61277'], 'Crayons': ['63350'], 'Lovely': ['11954'], 'Dewdrop': ['62269', '61297'], 'Essenza': ['63534'], 'Crush': ['12422'], 'Izanagi': ['12315'], 'Liber': ['23048'], 'Chimera': ['62172'], 'Latitude': ['23103', '12379'], 'Silvercat': ['62232', '61261'], 'Emblem': ['22992', '12228'], 'Tinkerbell': ['61230'], 'Blue': ['11028'], 'Adruinna': ['12310'], 'Maybe': ['32271'], 'Owly': ['11725'], 'Fourleaf': ['11771'], 'Bead': ['56027'], 'Oxylus': ['12311'], 'Dragonfly': ['58057'], 'Paradiso': ['62203', '61238'], 'Roots': ['61286'], 'Calm': ['23133'], 'Castle': ['32310'], 'Switch': ['11948', '22775'], 'Kindly': ['12461'], 'Base': ['32163'], 'Slim': ['61285'], 'Sunray': ['11752'], 'Dreamy': ['12231'], 'Symphonie': ['11742'], 'Couture': ['11032'], 'Abu': ['32338'], 'Relish': ['61310'], 'Serial': ['32165'], 'Cielo': ['62087'], 'Peony': ['58053'], 'Lilac': ['23123'], 'Ball': ['22076'], 'Twinkle': ['61287'], 'Aloha': ['11318'], 'Wing': ['61102'], 'Bravo': ['61194', '62140'], 'Troya': ['23060'], 'Rosa': ['62288'], 'Pipit': ['58059'], 'Connection': ['62282'], 'Daisy': ['S24006'], 'Safe': ['61060'], 'Coin': ['12411'], 'Blast': ['11095'], 'Mother': ['61311'], 'Pole': ['12241'], 'Sijou': ['41194'], 'Dream Trio': ['62265'], 'Toro': ['11724'], 'First': ['23000'], 'Mundo': ['12196'], 'Naiades': ['23065'], 'Instant': ['32390'], 'Vayu': ['23054'], 'Trois': ['32278'], 'Faun': ['62160'], 'Unlock': ['12159'], 'Confianza': ['61166'], 'Lily': ['62155'], 'Independence': ['32398']}
