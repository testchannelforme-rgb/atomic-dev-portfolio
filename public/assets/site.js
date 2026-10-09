(() => {
  'use strict';
  if (!document.querySelector('.hero-art')) return;
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const toggle = document.querySelector('.menu-toggle');
  const mobileNav = document.getElementById('mobile-nav');
  const mobileViewport = window.matchMedia('(max-width: 760px)');

  function closeMenu() {
    mobileNav.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }
  function updateNavigation() {
    toggle.hidden = !mobileViewport.matches;
    closeMenu();
  }
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    mobileNav.hidden = !open;
  });
  mobileNav.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !mobileNav.hidden) {
      closeMenu();
      toggle.focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (!mobileNav.hidden && !event.target.closest('.header')) closeMenu();
  });
  mobileViewport.addEventListener('change', updateNavigation);
  updateNavigation();

  // Content remains visible if JavaScript fails or the user requests less motion.
  let observer;
  function updateReveals() {
    if (observer) observer.disconnect();
    if (motionPreference.matches || !('IntersectionObserver' in window)) {
      document.documentElement.classList.remove('motion-enabled');
      return;
    }
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));
    document.documentElement.classList.add('motion-enabled');
  }
  updateReveals();
  motionPreference.addEventListener('change', updateReveals);

  const line = document.getElementById('reading-line');
  const car = document.getElementById('reading-car');
  const art = document.querySelector('.hero-art');
  let framePending = false;
  function updateProgress() {
    const root = document.documentElement;
    const scroll = Math.max(0, window.scrollY);
    const progress = Math.min(1, scroll / Math.max(1, root.scrollHeight - root.clientHeight));
    line.style.transform = `scaleX(${progress})`;
    car.style.transform = `translateX(${progress * Math.max(0, root.clientWidth - 34)}px)`;
    // A central shape expands toward the app cards as the hero leaves the viewport.
    const expansion = motionPreference.matches ? 0 : Math.min(1, scroll / 520);
    art.style.setProperty('--expansion', String(expansion));
    framePending = false;
  }
  function scheduleProgress() {
    if (!framePending) {
      framePending = true;
      window.requestAnimationFrame(updateProgress);
    }
  }
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress, { passive: true });
  motionPreference.addEventListener('change', scheduleProgress);
  updateProgress();
})();

(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.movable-preview').forEach((preview) => {
    const handle = preview.querySelector('.preview-handle');
    let drag = null;
    function reset() {
      drag = null;
      preview.classList.remove('is-dragging');
      preview.style.setProperty('--move-x', '0px');
      preview.style.setProperty('--move-y', '0px');
      handle.hidden = reduceMotion.matches;
    }
    handle.addEventListener('pointerdown', (event) => {
      if (reduceMotion.matches || event.button !== 0) return;
      drag = { x: event.clientX, y: event.clientY, id: event.pointerId };
      handle.setPointerCapture(event.pointerId);
      preview.classList.add('is-dragging');
    });
    handle.addEventListener('pointermove', (event) => {
      if (!drag || drag.id !== event.pointerId) return;
      const dx = Math.max(-22, Math.min(22, event.clientX - drag.x));
      const dy = Math.max(-15, Math.min(15, event.clientY - drag.y));
      preview.style.setProperty('--move-x', `${dx}px`);
      preview.style.setProperty('--move-y', `${dy}px`);
    });
    handle.addEventListener('pointerup', reset);
    handle.addEventListener('pointercancel', reset);
    handle.addEventListener('lostpointercapture', reset);
    handle.addEventListener('keydown', (event) => {
      if (reduceMotion.matches || !['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)) return;
      event.preventDefault();
      preview.style.setProperty('--move-x', `${event.key === 'ArrowLeft' ? -18 : event.key === 'ArrowRight' ? 18 : 0}px`);
      preview.style.setProperty('--move-y', `${event.key === 'ArrowUp' ? -12 : event.key === 'ArrowDown' ? 12 : 0}px`);
    });
    handle.addEventListener('blur', reset);
    reduceMotion.addEventListener('change', reset);
    reset();
  });

  document.querySelectorAll('button.study-task').forEach((button) => {
    button.addEventListener('click', () => {
      const completed = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(completed));
      const circle = button.querySelector('.task-circle');
      circle.classList.toggle('completed', completed);
      circle.textContent = completed ? '✓' : '';
      const label = button.querySelector('.task-label');
      if (label) label.textContent = completed ? 'Done' : 'To do';
    });
  });
  const budgetToggle = document.querySelector('.budget-toggle');
  budgetToggle?.addEventListener('click', () => {
    const open = budgetToggle.getAttribute('aria-expanded') !== 'true';
    budgetToggle.setAttribute('aria-expanded', String(open));
    document.querySelector('.budget-explanation').hidden = !open;
    budgetToggle.firstChild.textContent = open ? 'Hide the breakdown ' : 'See the breakdown ';
  });

  const dialog = document.querySelector('.screenshot-dialog');
  if (!dialog) return;
  const links = [...document.querySelectorAll('.screenshot-link')];
  const image = dialog.querySelector('.viewer-image');
  const caption = dialog.querySelector('.viewer-caption');
  const count = dialog.querySelector('.viewer-count');
  let index = 0;
  let previousFocus;
  let swipeStart;
  function show(nextIndex) {
    index = (nextIndex + links.length) % links.length;
    const source = new URL(links[index].href, window.location.origin);
    if (source.origin !== window.location.origin || !source.pathname.startsWith('/assets/screenshots/')) return;
    image.src = source.pathname;
    image.alt = links[index].querySelector('img').alt;
    caption.textContent = links[index].dataset.caption;
    count.textContent = `${index + 1} / ${links.length}`;
  }
  document.querySelectorAll('[data-caption]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const selected = links.findIndex((candidate) => candidate.href === link.href);
      if (selected < 0) return;
      event.preventDefault();
      previousFocus = link;
      show(selected);
      dialog.showModal();
      document.body.classList.add('viewer-open');
      dialog.querySelector('.viewer-close').focus();
    });
  });
  dialog.querySelector('.viewer-close').addEventListener('click', () => dialog.close());
  dialog.querySelector('.viewer-prev').addEventListener('click', () => show(index - 1));
  dialog.querySelector('.viewer-next').addEventListener('click', () => show(index + 1));
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(index + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  image.addEventListener('pointerdown', (event) => { swipeStart = { x: event.clientX, y: event.clientY }; });
  image.addEventListener('pointerup', (event) => {
    if (!swipeStart) return;
    const dx = event.clientX - swipeStart.x;
    const dy = event.clientY - swipeStart.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1));
    swipeStart = null;
  });
  image.addEventListener('pointercancel', () => { swipeStart = null; });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('viewer-open');
    previousFocus?.focus();
  });
})();
