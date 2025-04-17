document.querySelectorAll('.catalog-card').forEach(card => {
  card.style.cursor = 'pointer';
  card.addEventListener('click', () => {
    window.open(card.dataset.url, '_blank', 'noopener');
  });
});

document.querySelectorAll('.download-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();

    fetch(btn.href)
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.blob();
      })
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = btn.dataset.filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(blobUrl);
      })
      .catch(err => console.error('Download error:', err));
  });
});