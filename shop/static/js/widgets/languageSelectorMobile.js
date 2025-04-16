// Function for changing URLs
function changeLanguageURL(selectedLang) {
    const newPathname = window.location.pathname.replace(/^\/[a-z]{2}/, '');
    window.location.href = window.location.origin + '/' + selectedLang + newPathname + window.location.search;
}

// Function for setting the initial language based on URL
function setMobileCurrentLanguage() {
    const path = window.location.pathname;
    const langMatch = path.match(/^\/(gb|de|it|es|ru)/);
    const currentLang = langMatch ? langMatch[1] : 'gb'; // By default 'gb'
    const selectElement = document.getElementById('languageSelectMobile');
    selectElement.value = currentLang; // Set the current language in select
}

// Initialization on page load
window.onload = function() {
    setMobileCurrentLanguage();
};

document.getElementById('languageSelectMobile').addEventListener('change', function(event) {

    if (event.isTrusted) {
        changeLanguageURL(this.value);
    }
});