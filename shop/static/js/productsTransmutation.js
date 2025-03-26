const regex = /^[a-zA-Z]{0,2}\d{5}[a-zA-Z]{0,5}$/;
function productsTransmutation(items, price_category, sale, stones, isB2B){

    let products = {};

    items.forEach(item => {
        if(item.Visible === false || item.b2b_only === true && !isB2B){
            return;
        }
        let itemName = item.name;
        let stone = stones[item.stone] !== undefined ? stones[item.stone] : item.stone;
        getNormalizedItemName(itemName, item);

        if (!products[itemName] ) { //&& item.plating && item.stone
                products[itemName] = {
                    name: itemName,
                    groupName: item.product_name,
                    product_name: item.category + " "+ item.product_name,
                    description: item.description,
                    price:calculatePrice(item, price_category, sale),
                    category: item.category,
                    collection: item.hasOwnProperty('collection') ? item.collection : "",
                    pre_order: item.hasOwnProperty('pre_order') ? item.pre_order : false,
                    material: item.material,
                    preview_image: item.image_url,
                    platings: {}
                };
                if (item.product_width) {
                    products[itemName].product_width = item.product_width;
                }

                // Conditionally add product_height if it exists
                if (item.product_height) {
                    products[itemName].product_height = item.product_height;
                }

                // Conditionally add chain_length if it exists
                if (item.chain_length) {
                    products[itemName].chain_length = item.chain_length;
                }
            }
            if (item.plating) {
                // Initialize plating if it doesn't exist.
                if (!products[itemName].platings[item.plating]) {
                    products[itemName].platings[item.plating] = {
                        stones: {},
                    };
                }

                // Proceed only if stone is defined.
                if (stone) {
                    // Initialize the stone if it doesn't exist under the current plating.
                    if (!products[itemName].platings[item.plating].stones[stone]) {
                        products[itemName].platings[item.plating].stones[stone] = {
                            sizes: {},
                            image: item.image_url,
                            real_name: item.name,
                        };

                    }

                    // If size is present, add or update the size and quantity for the stone.
                    if (item.size) {
                        let stoneSizes = products[itemName].platings[item.plating].stones[stone].sizes;
                        if (!stoneSizes[item.size]) {
                                stoneSizes[item.size] = {
                                    'quantity': item.quantity,
                                    'real_name': item.name
                                };

                                // Conditionally add product_width if it exists


                        } else {
                            // Assuming you want to sum quantities for the same size.
                            stoneSizes[item.size].quantity += item.quantity;
                        }
                    } else {
                        // If there's no size, add the quantity directly to the stone.
                        if (!products[itemName].platings[item.plating].stones[stone].quantity) {
                            products[itemName].platings[item.plating].stones[stone].quantity = item.quantity;
                            products[itemName].platings[item.plating].stones[stone].real_name = item.name;
                        } else {
                            products[itemName].platings[item.plating].stones[stone].quantity += item.quantity;
                        }
                    }
                }
            }
    });
    for (let productName in products) {
        for (let platingName in products[productName].platings) {
            for (let stoneName in products[productName].platings[platingName].stones) {
                let stoneEntry = products[productName].platings[platingName].stones[stoneName];
                if (stoneEntry.sizes) {
                    stoneEntry.sizes = orderSizes(stoneEntry.sizes);
                }
            }
        }
    }
    console.log(products);
    return Object.values(products);
}

function orderSizes(sizes) {
    const sizeOrder = ['S', 'M', 'L', 'XL'];
    const orderedSizes = {};
    sizeOrder.forEach(size => {
        if (sizes.hasOwnProperty(size)) {
            orderedSizes[size] = sizes[size];
        }
    });
    // Include other sizes not in the specified order
    Object.keys(sizes).forEach(size => {
        if (!orderedSizes.hasOwnProperty(size)) {
            orderedSizes[size] = sizes[size];
        }
    });
    return orderedSizes;
}

function calculatePrice(item, price_category, sale) {
    return (Number(((price_category === "VK3" ? item.priceVK3 :
             price_category === "GH" ? item.priceGH :
             price_category === "GH_USD" ? item.priceUSD_GH :
             price_category === "Default_USD" ? (item.priceUSD * (1 - sale)) :
             price_category === "Default_High" ? (item.priceVK4 * 1.3) :
             (item.priceVK4 * (1 - sale)))).toFixed(1))).toFixed(2);
}

function getNormalizedItemName(itemName, item){
    itemName = itemName.split(' ')[0];
     if (regex.test(itemName)) {
        let processedName = itemName.match(/^([a-zA-Z]{0,2})(\d{5})/);
         // This includes both the initial letters and the 5 digits
         itemName = processedName[0];
    } else {
        itemName = (item.name).split(' ')[0];
    }
    return itemName;
}