function calculate_final(vat, shipping_value, currency, documents){
     let totalQuantity = 0;
     let totalSum = 0;
     let totalItems = 0;

     documents.forEach(doc => {
        totalItems+=1;
        totalQuantity += doc.quantity;
        totalSum += (doc.quantity * doc.price);
     });

     const quantity_items = totalItems%10===1 ? "item" : "items";
     const totalSumFinal =  totalSum;
     const included_vat = ((totalSumFinal + shipping_value) * vat/100);
     const sum_with_vat = totalSumFinal + shipping_value;//(included_vat + totalSumFinal);
     console.log(included_vat);
     console.log(shipping_value);
     document.querySelector('.final-unique-quantity').innerText =  totalItems + " " + quantity_items;
     document.getElementById('final-sum').innerText = currency + totalSumFinal.toFixed(2);
     const totalEl = document.querySelector('.value-total');
     if (totalEl) {
       totalEl.innerText = currency + sum_with_vat.toFixed(2);
     }
     const taxesEl = document.querySelector('.value-taxes');
     if (taxesEl) {
       taxesEl.innerText = currency + included_vat.toFixed(2);
     }
     const shippingEl = document.querySelector('.value-shipping');
     if (shippingEl) {
       shippingEl.innerText = currency + shipping_value.toFixed(2);
     }
}