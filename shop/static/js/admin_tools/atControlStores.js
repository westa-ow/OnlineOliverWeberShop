const createAddressModal = document.getElementById('create-store-modal');
const editAddressModal = document.getElementById('edit-store-modal');
const createAddressBtn = document.getElementById('create-store');
const modalOverlay = document.getElementById('modal-overlay');
const newAddressInput = document.getElementById('new-address');
const addressSuggestionsCreate = document.getElementById('address-suggestions-create');
const editAddressInput = document.getElementById('edit-address');
const addressSuggestionsEdit = document.getElementById('address-suggestions-edit');
const listMessageContainer = document.getElementById('list-message-container');
const loadStoresButton = document.getElementById('load-stores');
const createStoreForm = document.getElementById('create-store-form');
const editStoreForm = document.getElementById('edit-store-form');
const createStatus = document.getElementById('create-status');
const editStatus = document.getElementById('edit-status');
const storesTableBody = document.querySelector('#stores-table tbody');

const API_ROOT   = document.querySelector('meta[name="api-root"]').getAttribute('content');


function showModal(modal, form, suggestionElement) {
    modal.classList.remove('hidden');
    modalOverlay.classList.remove('hidden');
    document.body.classList.add('modal-open');
    form.reset();
    suggestionElement.innerHTML = '';
}
function hideModal() {
    createAddressModal.classList.add('hidden');
    editAddressModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
    document.body.classList.remove('modal-open');
}
modalOverlay.addEventListener('click', hideModal);
createAddressBtn.addEventListener('click',()=> showModal(createAddressModal, createStoreForm, addressSuggestionsCreate));


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

newAddressInput.addEventListener('input', async () => {
    const query = newAddressInput.value.trim();
    if (query.length > 2) {
        const suggestions = await getAddressSuggestions(query);
        showSuggestions(newAddressInput, addressSuggestionsCreate, suggestions);
    } else {
        addressSuggestionsCreate.innerHTML = '';
    }
});

editAddressInput.addEventListener('input', async () => {
    const query = editAddressInput.value.trim();
    if (query.length > 2) {
        const suggestions = await getAddressSuggestions(query);
        showSuggestions(editAddressInput, addressSuggestionsEdit, suggestions);
    } else {
        addressSuggestionsEdit.innerHTML = '';
    }
});

createStoreForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const address = newAddressInput.value;
    let url = API_ROOT + "stores/"
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ address: address }),
    })
    .then(response =>{
        console.log(response);
       if (response.ok) {
            newAddressInput.value = '';
            addressSuggestionsCreate.innerHTML = '';
            loadStores();
       } else {
            addressSuggestionsCreate.innerHTML = '';
       }
    })
    .catch(console.error);


});

editStoreForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const id = editStoreForm.getAttribute('data-id');
    const address = editAddressInput.value;
    let url = API_ROOT + `stores/${id}/`
    const response = await fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ address: address }),
    });
    const data = await response.json();
    if (response.ok) {
        alert(vocabulary["Store address with ID"] +  ` ${id} ` + vocabulary["was successfully updated"]);
        loadStores();
        hideModal();
    } else {
        alert(vocabulary["Store address update error"] + `: ${data.address ? data.address[0] : data.error || vocabulary['Unknown error']}`);
        hideModal();
    }
});

async function loadStores() {
    listMessageContainer.textContent = vocabulary['Loading...'];
    try {
        let url = API_ROOT + "stores/"
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            storesTableBody.innerHTML = '';
            data.forEach(store => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${store.id}</td>
                    <td>${store.address}</td>
                    <td>${store.latitude}</td>
                    <td>${store.longitude}</td>
                    <td>
                        <button class="action-btn">⋮</button>
                    </td>
                `;
                row.querySelector('.action-btn').addEventListener('click', function (event) {
                    event.stopPropagation();

                    const existingMenu = document.querySelector('.action-menu');
                    if (existingMenu) existingMenu.remove();

                    const menu = document.createElement('div');
                    menu.classList.add('action-menu');
                    menu.innerHTML = `
                        <button class="update-btn" data-id=${store.id}>${vocabulary["Update"]}</button>
                        <button class="delete-btn" data-id=${store.id}>${vocabulary["Delete"]}</button>
                    `;
                    document.body.appendChild(menu);

                    menu.style.top = `${event.clientY}px`;
                    menu.style.left = `${event.clientX}px`;


                    document.addEventListener('click', () => {
                        if (menu.parentNode) menu.remove();
                    }, { once: true });
                    const update_btn = menu.querySelector('.update-btn');
                    const delete_btn = menu.querySelector('.delete-btn');
                    update_btn.addEventListener('click', () => {
                        let id=  update_btn.getAttribute('data-id');
                        editStoreForm.setAttribute('data-id', id);
                        showModal(editAddressModal,editStoreForm, addressSuggestionsEdit);
                        menu.remove();
                    });

                    delete_btn.addEventListener('click', () => {
                        const confirmation = window.confirm("Are you sure you want to delete this store?");
                        let id=  delete_btn.getAttribute('data-id');
                        if (confirmation) {
                            let url = API_ROOT + `stores/${id}/`
                            fetch(url, { method: 'DELETE', headers: { 'Content-Type': 'application/json','X-CSRFToken': getCookie('csrftoken') } })
                                .then(() => loadStores())
                                .catch(console.error);
                            menu.remove();
                        } else {
                            menu.remove();
                        }
                    });
                });
                storesTableBody.appendChild(row);
            });
            listMessageContainer.textContent = "";
        } else {
            listMessageContainer.textContent = vocabulary['Error loading stores.'];
        }
    } catch (error) {
        listMessageContainer.textContent = vocabulary['Network error when loading stores.'];
    }
}
window.addEventListener('scroll', () => {
  const existingMenu = document.querySelector('.action-menu');
  if (existingMenu) existingMenu.remove();
});


loadStores();
loadStoresButton.addEventListener('click', loadStores);


