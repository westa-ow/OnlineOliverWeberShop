(function () {
  const origCreate = document.createElement.bind(document);

  document.createElement = function(tagName) {
    const el = origCreate(tagName);

    if (String(tagName).toLowerCase() === 'script') {
      const proto = HTMLScriptElement.prototype;
      const desc  = Object.getOwnPropertyDescriptor(proto, 'src');

      Object.defineProperty(el, 'src', {
        configurable: true,
        enumerable:   true,
        get() {
          return desc.get.call(this);
        },
        set(value) {
          if (typeof value === 'string') {
            // 1) Протокол-независимый URL: //t.contentsquare.net/… → https://t.contentsquare.net/…
            if (value.startsWith('//t.contentsquare.net/')) {
              value = 'https:' + value;
            }
            // 2) Прямой HTTP: http://t.contentsquare.net/… → https://…
            else if (value.startsWith('http://t.contentsquare.net/')) {
              value = value.replace(/^http:/, 'https:');
            }
          }
          desc.set.call(this, value);
        }
      });
    }

    return el;
  };
})();
