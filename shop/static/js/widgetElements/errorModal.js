document.addEventListener("DOMContentLoaded", function() {
    const script = document.getElementById("error-data");
    if (!script) return;

    let raw;
    try {
      raw = JSON.parse(script.textContent);
    } catch (e) {
      console.error("Failed to parse error-data JSON:", e);
      return;
    }
    const msgs = [];
    if (Array.isArray(raw) && raw.every(item => typeof item === "string")) {
      msgs.push(...raw);
    }

    else if (Array.isArray(raw) && raw.every(item => item && item.message)) {
      raw.forEach(item => msgs.push(item.message));
    }
    else if (raw && typeof raw === "object" && !Array.isArray(raw)) {
      Object.values(raw).forEach(arr => {
        if (Array.isArray(arr)) {
          arr.forEach(errObj => {
            if (typeof errObj === "string")           msgs.push(errObj);
            else if (errObj && errObj.message)        msgs.push(errObj.message);
            else console.warn("Unexpected errors format in array:", errObj);
          });
        }
      });
    }
    else if (typeof raw === "string") {
      msgs.push(raw);

    }
    else {
      console.warn("Unexpected errors format:", raw);
    }

    if (msgs.length === 0) return;

    const modal = document.getElementById("errorModal");
    const textNode = document.getElementById("errorText");
    const okBtn = document.getElementById("okButton");
    const closeBtn = modal.querySelector(".close-button");

    textNode.innerHTML = msgs
      .map(s => escapeHtml(s))
      .join("<br>");

    modal.style.display = "block";
    document.body.style.overflow = "hidden";

    function hide() {
      modal.style.display         = "none";
      document.body.style.overflow = "";
    }
    okBtn   .addEventListener("click", hide);
    closeBtn.addEventListener("click", hide);
    window  .addEventListener("click", e => {
      if (e.target === modal) hide();
    });
});

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}