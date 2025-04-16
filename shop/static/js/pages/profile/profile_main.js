function getProfileOrdersConfig() {
    const metaTag = document.querySelector('meta[name="profile-config"]');
    if (metaTag) {
      try {
        const content = metaTag.getAttribute("content").replaceAll("'", '"');
        return JSON.parse(content);
      } catch (err) {
        console.error("Ошибка при парсинге meta tag config:", err);
      }
    } else {
      console.error('Meta tag с именем "config" не найден');
    }
    return {};
}
function getScriptConfig() {
    const configScript = document.getElementById('config-data');
    if (configScript) {
      try {
        return JSON.parse(configScript.textContent);
      } catch (err) {
        console.error("Ошибка при парсинге config-data из script:", err);
      }
    } else {
      console.error('Элемент с id "config-data" не найден');
    }
    return {};
}
function getMergedConfig() {
    const metaConfig = getProfileOrdersConfig();
    const scriptConfig = getScriptConfig();
    return { ...metaConfig, ...scriptConfig };
}

window.config = getMergedConfig();