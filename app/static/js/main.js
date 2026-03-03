// Auto dismiss toasts
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => { const b = bootstrap.Toast.getOrCreateInstance(t); b.hide(); }, 3500);
  });

  // Size selection highlight
  document.querySelectorAll('.size-option input[type=radio]').forEach(radio => {
    radio.addEventListener('change', function () {
      document.querySelectorAll('.size-label').forEach(l => l.classList.remove('selected'));
      this.nextElementSibling.classList.add('selected');
    });
    if (radio.checked) radio.nextElementSibling.classList.add('selected');
  });

  // Navbar scroll effect
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.style.boxShadow = window.scrollY > 20 ? '0 2px 20px rgba(0,0,0,.1)' : 'none';
    });
  }
});
