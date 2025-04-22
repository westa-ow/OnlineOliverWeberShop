function getPrivacyPolicyConfig() {
  const meta = document.querySelector('meta[name="privacyPolicyUrl"]');
  return meta
    ? { privacyPolicyUrl: meta.content }
    : {};
}

function getHotJarId() {
  const meta = document.querySelector('meta[name="HOTJARID"]');
  return meta
    ? { HOTJAR_ID: meta.content }
    : {};
}

function enableHotjar() {
  (function (c, s, q, u, a, r, e) {
    c.hj = c.hj || function () {
      (c.hj.q = c.hj.q || []).push(arguments)
    };
    c._hjSettings = {hjid: a};
    r = s.getElementsByTagName('head')[0];
    e = s.createElement('script');
    e.async = true;
    e.src = q + c._hjSettings.hjid + u;
    r.appendChild(e);
  })(window, document, 'https://static.hj.contentsquare.net/c/csq-', '.js', window.config.HOTJAR_ID);
}
window.addEventListener("load", function(){
      window.config = {
        ...(window.config || {}),
        ...getPrivacyPolicyConfig(),
        ...getHotJarId(),
      };
      window.cookieconsent.initialise({
        palette: {
          popup: { background: "#000" },
          button: { background: "#f1d600" }
        },
        theme: "classic",
        type: "opt-in",           // включаем режим Accept/Decline
        cookie: {
          name: "cookie_consent_status",  // имя куки
          expiryDays: 365,                // хранить выбор 365 дней
          path: "/"                       // доступно на всём сайте
        },
        content: {
          message: vocabulary["We use cookies to personalize content and improve your browsing experience. By continuing, you accept our cookie policy."],
          allow: vocabulary["Accept"],
          deny: vocabulary["Decline"],
          link: vocabulary["Privacy Policy"],
          href: window.config.privacyPolicyUrl
        },
        onInitialise: function(status) {
          if (status === 'allow') {
            enableHotjar();
          }
        },
        onStatusChange: function(status, chosenBefore) {
          if (status === 'allow') {
            enableHotjar();
          }
        }
      });
});