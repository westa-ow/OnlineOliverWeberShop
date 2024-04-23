function constructFilters(items){
    constructCrystals(items);
    constructPlatings(items);
    constructBases(items);
}

function constructCrystals(items) {
    let uniqueStones = new Set();
    items.forEach(document => {
        Object.values(document.platings).forEach(plating => {
            Object.keys(plating.stones).forEach(stoneCategory => {
                uniqueStones.add(stoneCategory);
            });
        });
    });
    createCrystalElements('crystals', Array.from(uniqueStones), 'crystal');
}

function constructPlatings(items) {
    let uniquePlatings = new Set();
    items.forEach(document => {
        Object.keys(document.platings).forEach(plating => {
            uniquePlatings.add(plating);
        });
    });
    createFilterElements('platings', Array.from(uniquePlatings), 'plating');
}

function constructBases(items) {
    let all_bases = items.reduce((accumulator, document) => {
        if (!accumulator.includes(document.material)) {
            accumulator.push(document.material);
        }
        return accumulator;
    }, []);
    createFilterElements('bases', all_bases, 'base');
}

function createFilterElements(containerClass, itemsArray, prefix) {
    const container = document.querySelector(`.${containerClass}`);
    container.innerHTML = ''; // Clear existing content

    itemsArray.forEach((item, index) => {
        const itemId = `${prefix}${index + 1}`;
        const checkboxId = `checkbox${prefix.toUpperCase()}${index + 1}`;

        // Create div for each item
        const itemDiv = document.createElement('div');
        itemDiv.id = itemId;

        // Create checkbox input for each item
        const checkbox = document.createElement('input');
        checkbox.className = `${prefix}-checkbox`;
        checkbox.type = 'checkbox';
        checkbox.id = checkboxId;
        checkbox.name = checkboxId;
        checkbox.value = item;

        // Create label for each checkbox
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.htmlFor = checkboxId;
        label.textContent = item;

        // Append checkbox and label to itemDiv
        itemDiv.appendChild(checkbox);
        itemDiv.appendChild(label);

        // Append itemDiv to container
        container.appendChild(itemDiv);
    });
}

function createCrystalElements(containerClass, itemsArray, prefix) {
    const container = document.querySelector(`.${containerClass}`);
    container.innerHTML = ''; // Clear existing content

    // Create select element
    const select = document.createElement('select');
    select.className = `${prefix}-select`;
    select.id = `${prefix}-select`;

    // Add a default option
    const defaultOption = document.createElement('option');
    defaultOption.textContent = 'All';
    defaultOption.value = '';
    select.appendChild(defaultOption);

    // Create option for each item
    itemsArray.forEach((item, index) => {
        const option = document.createElement('option');
        option.value = item;
        option.textContent = item;
        select.appendChild(option);
    });

    // Append select to container
    container.appendChild(select);
}