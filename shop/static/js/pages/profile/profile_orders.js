let products = [];
let orders = window.config.orders;
let currencies =  window.config.currencies;
let b2b_can_pay = window.config.b2b_can_pay;
document.addEventListener("DOMContentLoaded", function() {
    products = window.config.products;
});

document.querySelectorAll('.i-menu-points').forEach(button => {
    button.addEventListener('click', (event) => {
        event.stopPropagation();
        const contextMenu = document.getElementById('contextMenu');
        contextMenu.style.display = 'block';
        contextMenu.style.left = `${event.pageX - 100}px`;
        contextMenu.style.top = `${event.pageY}px`;
        let orderId = button.getAttribute('data-order-id');
        let current_order = orders.filter(item => item.order_id === parseInt(orderId))[0];

        if(b2b_can_pay){
        if (current_order.payment_type === 'BANK TRANSFER' && current_order.paid_sum !== current_order.sum ){
            document.getElementById('payForOrder').style.display = 'block';
        } else {
            document.getElementById('payForOrder').style.display = 'none';
        }}

        // Function to hide the context menu
        function hideContextMenu() {
            contextMenu.style.display = 'none';
        }

        // Close the menu when clicking outside of it
        document.addEventListener('click', hideContextMenu, { once: true });

        // Set up the menu actions
        document.getElementById('downloadCsv').onclick = function() {
            let address = window.config.downloadCsvDummyUrl;
            address = address.replace('BIG', orderId);
            window.location.href = address;
        };
        document.getElementById('downloadPdfWImg').addEventListener('click', function() {
              let dialog = document.getElementById('wait-please-dialog');
              dialog.style.display="block";
              dialog.showModal();
              let address = window.config.downloadPdfWImgsDummyUrl;
              address = address.replace('BIG', orderId);
              window.location.href = address;
              // Set a timeout to close the dialog after 3 seconds
              setTimeout(function() {
                  dialog.close();   // Redirect to the download URL after closing the dialog
                  dialog.style.display="none";
              }, 3000);

        });
        document.getElementById('downloadPdfWithoutImg').onclick = function() {
            let address = window.config.downloadPdfWithoutImgsDummyUrl;
            address = address.replace('BIG', orderId);
            window.location.href = address;
        };
        if (b2b_can_pay) {
            document.getElementById('payForOrder').onclick = function () {
                const modal = document.getElementById('custom-modal');
                const overlay = document.getElementById('custom-modal-overlay');
                let orderPaidSum = current_order.paid_sum ? current_order.paid_sum.toString() : 0;
                const orderPrice = current_order.sum;
                let max_sum_to_pay = orderPrice - orderPaidSum;

                // Set the price in the text field
                document.getElementById('order-price').innerText = `${current_order.currency === "Euro" ? "€" : "$"}${max_sum_to_pay.toFixed(2)}`;

                document.getElementById('amount-input').max = max_sum_to_pay;

                document.getElementById('amount-input').max = max_sum_to_pay;

                // Show modal window and overlay
                modal.style.display = 'block';
                overlay.style.display = 'block';

                // Disable page scrolling
                document.body.style.overflow = 'hidden';

                document.getElementById('pay-button').onclick = function () {
                    const amount = parseFloat(document.getElementById('amount-input').value.toString().replace(',', '.'));
                    console.log(amount);
                    if (isNaN(amount) || amount <= 0) {
                        alert(vocabulary["Please enter a valid amount."]);
                        return;
                    }
                    // Вызов функции оплаты
                    pay_for_order(amount, current_order);   // ADD HERE THE ADDRESS_DICT PARSER, WHICH SHOULD BE CREATED BY YOURSELF
                };
            };
        }
    });
});

document.querySelectorAll('.show-content').forEach(button => {
    button.addEventListener('click', () => {
         let orderId = button.getAttribute('data-order-id');
         let orderRow = document.getElementById('content-' + orderId);
         let table = orderRow.closest('table');
         let rowIndex = orderRow.rowIndex;
         let nextRow = table.rows[rowIndex + 1];
         const order_currency = currencies[orderId];

         if (nextRow && nextRow.classList.contains('nested-table-row')) {

            let nestedTableContainer = nextRow.querySelector('.nested-table-container');
            // Access nestedTable directly from nestedTableContainer if it's already in the DOM
            if (nestedTableContainer.classList.contains('expanded')) {
                nestedTableContainer.classList.remove('expanded');
                document.getElementById('show-button-' + orderId).innerText = vocabulary["Show details"];

                // Start the collapsing animation by setting max-height to 0
                nestedTableContainer.style.maxHeight = '0'; // Trigger the collapsing animation

                nestedTableContainer.addEventListener('transitionend', function onCollapse() {
                    // Remove event listener to avoid memory leaks
                    nestedTableContainer.removeEventListener('transitionend', onCollapse);

                    let deleteAfterCollapse = function() {
                        const rowToDelete = table.rows[rowIndex + 1]; // Assuming this is the row you want to delete
                        rowToDelete.style.transition = 'margin-top 0.05s ease';
                        rowToDelete.style.marginTop = `-${rowToDelete.offsetHeight}px`; // Animate the row out of view

                        // Wait for the margin-top transition to complete before deleting the row
                        setTimeout(() => {
                            requestAnimationFrame(() => {
                                table.deleteRow(rowIndex + 1);
                            });
                        }, 0); // This duration should match the CSS transition duration
                    };

                    // Execute the deletion with visual transition
                    deleteAfterCollapse();
                });
            } else {
                nestedTableContainer.classList.add('expanded');
                // Since nestedTable exists, recalculate contentHeight based on its current state
                let contentHeight = nestedTableContainer.scrollHeight + 'px';
                requestAnimationFrame(() => {
                    nestedTableContainer.style.maxHeight = contentHeight;
                });
                document.getElementById('show-button-' + orderId).innerText = vocabulary["Hide details"];
            }

        } else {
            // This is the section where you're adding the nested table for the first time
            document.getElementById('show-button-' + orderId).innerText = vocabulary["Hide details"];

            let nestedTableRow = table.insertRow(rowIndex + 1);
            nestedTableRow.classList.add('nested-table-row');

            let indentCell = nestedTableRow.insertCell(0);
            indentCell.classList.add('td-outer');

            let nestedTableCell = nestedTableRow.insertCell(1);
            nestedTableCell.colSpan = 5;

            let nestedTableContainer = document.createElement('div');
            nestedTableContainer.classList.add('nested-table-container'); // Initially not expanded

            let nestedTable = document.createElement('table');
            nestedTable.classList.add('nested-table');
            let Name = vocabulary["Name"];
            let Image = vocabulary["Image"];
            let Description = vocabulary["Description"];
            let Price = vocabulary["Price"];
            let Quantity = vocabulary["Quantity"];
            let Summary = vocabulary["Summary"];
            let In_stock = vocabulary["In stock"];
            let nestedTableContent = `
                <tr>
                    <th>${Name}</th>
                    <th>${Image}</th>
                    <th>${Description}</th>
                    <th>${Price}</th>
                    <th>${Quantity}</th>
                    <th>${Summary}</th>
                    <th>${In_stock}</th>
                </tr>`;
            let intId = parseInt(orderId);
            products[intId].forEach(function(product) {
                let mark = `&#10003`;
                if(product.in_stock === false){
                    mark = `&#x2717`;
                }
                nestedTableContent += `
                    <tr>
                        <td>${product.name}</td>
                        <td class="image-cell"> <img alt="Product image" src="${product.image_url}" width="50" height="50"> </td>
                        <td>${product.description}</td>
                        <td>${order_currency}${(product.price).toFixed(2)}</td>
                        <td>${product.quantity}</td>
                        <td>${order_currency}${(product.quantity * product.price).toFixed(1)}</td>
                        <td class="mark-cell"  ><span >${mark};</span></td>
                    </tr>`;
            });
            nestedTable.innerHTML = nestedTableContent;
            nestedTableContainer.appendChild(nestedTable);
            nestedTableCell.appendChild(nestedTableContainer);

            // At this point, nestedTable is fully prepared, so we should measure the scrollHeight of nestedTableContainer
            // Make sure to append nestedTableContainer to the document before measuring
            let contentHeight = "0px";
            // Make sure the nestedTableContainer is part of the document
            if (nestedTableContainer.scrollHeight) {
                contentHeight = nestedTableContainer.scrollHeight + "px";
            }

            // Apply the dynamic max-height and trigger the animation
            requestAnimationFrame(() => {
                nestedTableContainer.style.maxHeight = "0"; // Reset to start the transition
                // Allow the browser to register the reset
                requestAnimationFrame(() => {
                    nestedTableContainer.style.maxHeight = contentHeight; // Expand
                    nestedTableContainer.classList.add('expanded'); // Mark as expanded
                });
            });

            document.getElementById('show-button-' + orderId).innerText = vocabulary["Hide details"];
        }
    });
});

document.getElementById('close-modal').onclick = function() {
    closeModal();
};

// Closing a window when clicking on an overlay
document.getElementById('custom-modal-overlay').onclick = function() {
    closeModal();
};

function closeModal() {
    const modal = document.getElementById('custom-modal');
    const overlay = document.getElementById('custom-modal-overlay');

    // Hiding modal window and overlay
    modal.style.display = 'none';
    overlay.style.display = 'none';

    // Enable page scrolling
    document.body.style.overflow = '';
}


function pay_for_order(amount, current_order) {

    if (amount < 0 || amount > current_order['sum'] || amount > (current_order['sum']-current_order['paid_sum']) ){
        alert(vocabulary["Invalid amount"]);
        return;
    }

    current_order['sum'] = amount
    const csrfToken = getCookie('csrftoken');

    fetch(window.config.partialPaymentUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(current_order)
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            const stripe = Stripe(`${window.config.stripePublicKey}`);
            stripe.redirectToCheckout({ sessionId: data.id })
                .then(function (result) {
                    if (result.error) {
                        console.error('Error redirecting to Stripe checkout:', result.error.message);
                    }
                });
        } else {
            console.error('Error creating checkout session:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => closeModal());
}