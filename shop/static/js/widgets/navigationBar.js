function getMetaContent(name) {
  const meta = document.querySelector(`meta[name="${name}"]`);
  return meta ? meta.getAttribute("content") : "";
}

const currency = getMetaContent("currency");
let isCheckout = false;

document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("collections-toggle");
  const menu = document.getElementById("collections-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      menu.style.display = menu.style.display === "flex" ? "none" : "flex";
    });
    // Closing a menu when clicking outside of it
    document.addEventListener("click", function (e) {
      if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = "none";
      }
    });
  }

  window.addEventListener('scroll', function () {
    let toolbar = document.querySelector('.toolbar');
    if (toolbar) {
      if (window.pageYOffset > 50) {
        toolbar.classList.remove('large');
        toolbar.classList.add('small');
      } else {
        toolbar.classList.remove('small');
        toolbar.classList.add('large');
      }
    }
  });

  document.querySelectorAll('.close_cross').forEach(button =>
    button.addEventListener('click', function () {
      let accPanel = document.getElementById('side_acc_wrap');
      let overlay = document.getElementById('overlay');
      let searchPanel = document.getElementById('side_search_wrap');
      let menuPanel = document.getElementById('side_menu_wrap');

      if (accPanel) accPanel.classList.remove('open');
      if (searchPanel) searchPanel.classList.remove('open');
      if (menuPanel) menuPanel.classList.remove('open');
      if (overlay) overlay.style.display = 'none';
      closeDropdownSearch();
    })
  );

  const searchBtnMobile = document.getElementById('searchBtnMobile');
  const searchBtn = document.getElementById('searchBtn');
  if (searchBtnMobile) searchBtnMobile.addEventListener('click', searchPanelPopUp);
  if (searchBtn) searchBtn.addEventListener('click', searchPanelPopUp);


  const overlay = document.getElementById('overlay');
  if (overlay) {
    overlay.addEventListener('click', function () {
      const cartPanel = document.getElementById('cartPanel');
      const accPanel = document.getElementById('side_acc_wrap');
      const searchPanel = document.getElementById('side_search_wrap');
      const menuPanel = document.getElementById('side_menu_wrap');
      if (cartPanel) cartPanel.classList.remove('open');
      if (accPanel) accPanel.classList.remove('open');
      if (searchPanel) searchPanel.classList.remove('open');
      if (menuPanel) menuPanel.classList.remove('open');
      closeDropdownSearch();
      this.style.display = 'none';
    });
  }
});


function closeDropdownSearch() {
  const inputSearch = document.getElementById('input-search');
  if (inputSearch) inputSearch.value = "";
  const dropdown = document.getElementById('dropdown');
  if (dropdown) dropdown.innerHTML = '';
}


function searchPanelPopUp() {
  const searchPanel = document.getElementById('side_search_wrap');
  const overlay = document.getElementById('overlay');

  if (searchPanel) {
    if (searchPanel.classList.contains('open')) {
      searchPanel.classList.remove('open');
      if (overlay) overlay.style.display = 'none';
    } else {
      searchPanel.classList.add('open');
      if (overlay) overlay.style.display = 'block';
    }
  }
}

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

document.getElementById('cartBtnMobile')?.addEventListener('click', miniCartPanel);
document.getElementById('cartBtn')?.addEventListener('click', miniCartPanel);

