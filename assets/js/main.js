// Iron-Art — main script
// Vanilla, no dependencies. Handles: mobile nav, scroll fade-in, gallery lightbox.

(function () {
  'use strict';

  document.documentElement.classList.add('js');

  // ---------- Mobile navigation ----------
  const toggle = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');

  if (toggle && mobileNav) {
    toggle.addEventListener('click', function () {
      const open = mobileNav.classList.toggle('is-open');
      toggle.classList.toggle('is-active', open);
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('nav-open', open);
    });

    // Submenu toggles inside mobile nav
    mobileNav.querySelectorAll('.has-sub > span').forEach(function (sp) {
      sp.addEventListener('click', function (e) {
        e.stopPropagation();
        sp.parentElement.classList.toggle('is-open');
      });
    });

    // Close on link click
    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mobileNav.classList.remove('is-open');
        toggle.classList.remove('is-active');
        document.body.classList.remove('nav-open');
      });
    });
  }

  // ---------- Reveal on scroll ----------
  const targets = document.querySelectorAll('.fade-up');
  if ('IntersectionObserver' in window && targets.length) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('is-visible'); });
  }

  // ---------- Lightbox ----------
  const galleryLinks = Array.from(document.querySelectorAll('.gallery a[href]'));
  if (galleryLinks.length) {
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML =
      '<button class="lb-close" aria-label="Zamknij"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>' +
      '<button class="lb-prev" aria-label="Poprzednie"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button>' +
      '<button class="lb-next" aria-label="Następne"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button>' +
      '<img alt="">' +
      '<div class="lb-counter"></div>';
    document.body.appendChild(lb);

    const lbImg = lb.querySelector('img');
    const lbCounter = lb.querySelector('.lb-counter');
    let current = -1;

    function show(i) {
      if (i < 0) i = galleryLinks.length - 1;
      if (i >= galleryLinks.length) i = 0;
      current = i;
      const link = galleryLinks[i];
      lbImg.src = link.getAttribute('href');
      lbImg.alt = link.querySelector('img')?.alt || '';
      lbCounter.textContent = (i + 1) + ' / ' + galleryLinks.length;
      lb.classList.add('is-open');
      document.body.classList.add('nav-open');
    }
    function hide() {
      lb.classList.remove('is-open');
      document.body.classList.remove('nav-open');
      lbImg.src = '';
    }

    galleryLinks.forEach(function (a, i) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        show(i);
      });
    });

    lb.querySelector('.lb-close').addEventListener('click', hide);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) hide(); });

    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') hide();
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }
})();
