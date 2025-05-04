function getMetaJson(name) {
  const metaTag = document.querySelector(`meta[name="${name}"]`);
  if (metaTag) {
    try {
      if(name==="vocabulary"){
        console.log(metaTag)
      }
      return JSON.parse(metaTag.getAttribute("content"));
    } catch (error) {

      console.error(`Error when parsing meta tag config "${name}":`, error);
    }
  } else {
    console.error(`Meta tag with name "${name}" was not found`);
  }
  return {};
}

const translations_categories = getMetaJson("translations-categories");
const filters_dict = getMetaJson("filters-dict");
const synonyms = getMetaJson("synonyms");
const categories_codes = getMetaJson("categories-codes");
const categories_code_to_name = getMetaJson("categories-code-to-name");
const synonyms_collections = getMetaJson("synonyms-collections");

function getVocabularyData() {
    const el = document.getElementById("vocabulary-data");
    if (el) {
      try {
        return JSON.parse(el.textContent);
      } catch (err) {
        console.error("Error while parsing vocabulary confing:", err);
      }
    } else {
      console.error("Element with id 'vocabulary-data' was not found");
    }
    return {};
  }
const vocabulary_base = getVocabularyData();

function getVocabulary() {
    return Object.assign({}, vocabulary_base, translations_categories, filters_dict);
}

