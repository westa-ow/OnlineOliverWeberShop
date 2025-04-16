document.addEventListener("DOMContentLoaded", async function () {
    setupImageCarousel();
});
function setupImageCarousel() {
    let currentIndex = 0;
    const items = document.querySelectorAll('.carousel-item');
    const itemAmount = items.length;

    // Initialize the first item's opacity directly for clarity
    items[0].style.display = "block";
    items[0].style.opacity = 1;

    function cycleItems() {
        const currentItem = items[currentIndex];
        const nextIndex = (currentIndex + 1) % itemAmount;
        const nextItem = items[nextIndex];

        // Fade out the current item by directly setting opacity to 0
        currentItem.style.opacity = 0;
        requestAnimationFrame(() => {
            // This slight delay ensures the browser has time to apply the above styles
            setTimeout(() => {
                currentItem.style.display = "none";
            }, 500);
        });

        // Ensure the next item is positioned but invisible, ready to fade in
        nextItem.style.opacity = 0;
        nextItem.style.display = "block";
        nextItem.classList.add('active');

        // Use requestAnimationFrame to ensure the next frame starts the fade-in
        requestAnimationFrame(() => {
            // This slight delay ensures the browser has time to apply the above styles
            setTimeout(() => {
                nextItem.style.opacity = 1;
            }, 20);
        });

        // Update the currentIndex to the next item
        currentIndex = nextIndex;
    }

    setInterval(cycleItems, 8000); // Adjusted timing for visual clarity
}