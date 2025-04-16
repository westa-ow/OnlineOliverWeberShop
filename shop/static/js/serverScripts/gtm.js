const metaTag = document.querySelector('meta[name="gtm-config"]');
if (metaTag) {
    window.gtmConfigId = metaTag.getAttribute('content');
} else {
    console.error('Meta tag with name "gtm-config" not found.');
}

window.dataLayer = window.dataLayer || [];
function gtag(){ dataLayer.push(arguments); }
gtag('js', new Date());
gtag('config', window.gtmConfigId);