document.addEventListener("DOMContentLoaded", (event) => {
  console.log("DOM fully loaded and parsed");
  setCurrentLanguage();
});
function getStaticUrls() {
  const metaTag = document.querySelector('meta[name="static-urls"]');
  if (metaTag) {
    try {
      return JSON.parse(metaTag.getAttribute("content"));
    } catch (e) {
      console.error("Ошибка при парсинге конфигурации static-urls", e);
    }
  }
  return null;
}
function updateBackgroundImage(selectElement) {
    let imageUrl = '';
    const staticUrls = getStaticUrls();
    if (!staticUrls) {
      console.error("Не удалось загрузить конфигурацию staticUrls");
      return;
    }
    console.log(selectElement.value);
    switch (selectElement.value) {
      case 'gb':
        imageUrl = staticUrls.uk; // UK flag
        break;
      case 'de':
        imageUrl = staticUrls.de; // DE flag
        break;
      case 'it':
        imageUrl = staticUrls.it; // IT flag
        break;
      case 'es':
        imageUrl = staticUrls.es; // SP flag
        break;
      case 'ru':
        imageUrl = staticUrls.ru; // RU flag
        break;
      default:
        imageUrl = staticUrls.uk; // UK flag by default
        break;
    }
    selectElement.style.backgroundImage = `url('${imageUrl}')`;
}

// Function for changing URLs based on selected language
function changeLanguageURL(selectedLang) {
    const newPathname = window.location.pathname.replace(/^\/[a-z]{2}/, '');
    window.location.href = window.location.origin + '/' + selectedLang + newPathname + window.location.search;
}

// Function for setting the initial language based on URL
function setCurrentLanguage() {
    const path = window.location.pathname;
    const langMatch = path.match(/^\/(gb|de|it|es|ru)/);
    const currentLang = langMatch ? langMatch[1] : 'gb'; // By default 'gb'
    const selectElement = document.getElementById('languageSelect');
    selectElement.value = currentLang; // Set the current language in select
    updateBackgroundImage(selectElement); // Background image update
}


document.getElementById('languageSelect').addEventListener('change', function(event) {
    updateBackgroundImage(this);
    if (event.isTrusted) {
        changeLanguageURL(this.value);
    }
});