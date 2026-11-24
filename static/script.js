// ==========================================================================
// Local Worker Booking — Interactions
// Sticky navbar, scroll-reveal, button ripple, magnetic hover, mobile menu
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {

  /* ---------------------- Sticky navbar shrink/shadow --------------------- */
  var navbar = document.querySelector('.navbar');
  if (navbar) {
    var onScroll = function () {
      if (window.scrollY > 12) navbar.classList.add('is-scrolled');
      else navbar.classList.remove('is-scrolled');
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------ Mobile menu ------------------------------ */
  var navToggle = document.querySelector('.nav-toggle');
  if (navToggle && navbar) {
    navToggle.addEventListener('click', function () {
      var isOpen = navbar.classList.toggle('mobile-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
    document.querySelectorAll('.nav-links a').forEach(function (link) {
      link.addEventListener('click', function () {
        navbar.classList.remove('mobile-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ------------------------------ Scroll reveal ---------------------------- */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* -------------------------------- Button ripple -------------------------------- */
  document.querySelectorAll('.btn-ripple').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      var rect = btn.getBoundingClientRect();
      var ripple = document.createElement('span');
      var size = Math.max(rect.width, rect.height) * 1.2;
      ripple.className = 'ripple';
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      btn.appendChild(ripple);
      setTimeout(function () { ripple.remove(); }, 650);
    });
  });

  /* ------------------------------- Magnetic hover ------------------------------- */
  var magnetics = document.querySelectorAll('.magnetic');
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    magnetics.forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;
        el.style.transform = 'translate(' + (x * 0.18) + 'px,' + (y * 0.28) + 'px)';
      });
      el.addEventListener('mouseleave', function () {
        el.style.transform = 'translate(0,0)';
      });
    });
  }

  /* -------------------------- Dispatch bar -> search redirect -------------------------- */
  var dispatchForm = document.querySelector('[data-dispatch-form]');
  if (dispatchForm) {
    dispatchForm.addEventListener('submit', function (e) {
      var input = dispatchForm.querySelector('input[name="search"]');
      if (!input || !input.value.trim()) {
        e.preventDefault();
        input && input.focus();
      }
    });
  }

  /* ------------------------- Rotating placeholder text ------------------------- */
  var rotateInput = document.querySelector('[data-rotate-placeholder]');
  if (rotateInput) {
    var words = ['Electrician', 'Plumber', 'Carpenter', 'Painter', 'AC Repair', 'Cleaning'];
    var i = 0;
    setInterval(function () {
      i = (i + 1) % words.length;
      rotateInput.setAttribute('placeholder', 'Search "' + words[i] + '" near you');
    }, 2200);
  }

  /* --------------------------------- Lucide icons --------------------------------- */
  if (window.lucide) { window.lucide.createIcons(); }
});

// ==========================================================================
// PHASE 2 — Homepage flagship interactions
// ==========================================================================
document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------- Nav sliding active indicator ------------------------- */
  var navLinksWrap = document.querySelector('.nav-links');
  var navIndicator = document.querySelector('.nav-indicator');
  if (navLinksWrap && navIndicator) {
    var placeIndicator = function (el) {
      if (!el) { navIndicator.style.opacity = 0; return; }
      var wrapRect = navLinksWrap.getBoundingClientRect();
      var rect = el.getBoundingClientRect();
      navIndicator.style.width = rect.width + 'px';
      navIndicator.style.transform = 'translateX(' + (rect.left - wrapRect.left) + 'px)';
      navIndicator.style.opacity = 1;
    };
    var activeLink = navLinksWrap.querySelector('a.active');
    requestAnimationFrame(function () { placeIndicator(activeLink); });
    navLinksWrap.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('mouseenter', function () { placeIndicator(link); });
    });
    navLinksWrap.addEventListener('mouseleave', function () { placeIndicator(activeLink); });
    window.addEventListener('resize', function () { placeIndicator(navLinksWrap.querySelector('a:hover') || activeLink); });
  }

  /* ------------------------------- Mesh parallax on mouse ------------------------------- */
  var heroSection = document.querySelector('.hero');
  var meshBlobs = document.querySelectorAll('.hero .mesh-blob');
  if (heroSection && meshBlobs.length && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    heroSection.addEventListener('mousemove', function (e) {
      var rect = heroSection.getBoundingClientRect();
      var relX = (e.clientX - rect.left) / rect.width - 0.5;
      var relY = (e.clientY - rect.top) / rect.height - 0.5;
      meshBlobs.forEach(function (blob, i) {
        var strength = (i + 1) * 14;
        blob.style.transform = 'translate(' + (relX * strength) + 'px,' + (relY * strength) + 'px)';
      });
    });
    heroSection.addEventListener('mouseleave', function () {
      meshBlobs.forEach(function (blob) { blob.style.transform = 'translate(0,0)'; });
    });
  }

  /* ---------------------------------- Particle field ---------------------------------- */
  var particleField = document.querySelector('.particle-field');
  if (particleField) {
    var count = window.innerWidth < 720 ? 10 : 22;
    for (var p = 0; p < count; p++) {
      var dot = document.createElement('span');
      dot.className = 'particle';
      var size = 2 + Math.random() * 3;
      dot.style.width = size + 'px';
      dot.style.height = size + 'px';
      dot.style.left = Math.random() * 100 + '%';
      dot.style.top = 40 + Math.random() * 55 + '%';
      dot.style.animationDuration = (8 + Math.random() * 10) + 's';
      dot.style.animationDelay = (Math.random() * 8) + 's';
      particleField.appendChild(dot);
    }
  }

  /* ------------------------------- Animated stat counters ------------------------------- */
  var counters = document.querySelectorAll('[data-counter]');
  if (counters.length && 'IntersectionObserver' in window) {
    var counterIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseFloat(el.getAttribute('data-counter'));
        var suffix = el.getAttribute('data-suffix') || '';
        var decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals'), 10) : 0;
        var duration = 1400;
        var startTime = null;
        var step = function (ts) {
          if (!startTime) startTime = ts;
          var progress = Math.min((ts - startTime) / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 3);
          var value = target * eased;
          el.textContent = value.toFixed(decimals) + suffix;
          if (progress < 1) requestAnimationFrame(step);
          else el.textContent = target.toFixed(decimals) + suffix;
        };
        requestAnimationFrame(step);
        counterIO.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { counterIO.observe(el); });
  }

  /* ----------------------------------- Testimonial carousel ----------------------------------- */
  var track = document.querySelector('[data-testimonial-track]');
  if (track) {
    var slides = track.querySelectorAll('.testimonial-card');
    var dotsWrap = document.querySelector('[data-testimonial-dots]');
    var perView = window.innerWidth <= 720 ? 1 : (window.innerWidth <= 1080 ? 2 : 3);
    var maxIndex = Math.max(0, slides.length - perView);
    var current = 0;

    var renderDots = function () {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      for (var i = 0; i <= maxIndex; i++) {
        var b = document.createElement('button');
        if (i === current) b.classList.add('active');
        b.addEventListener('click', function (idx) { return function () { goTo(idx); }; }(i));
        dotsWrap.appendChild(b);
      }
    };
    var goTo = function (index) {
      current = Math.max(0, Math.min(index, maxIndex));
      var slideWidth = slides[0].getBoundingClientRect().width + 24;
      track.style.transform = 'translateX(-' + (current * slideWidth) + 'px)';
      renderDots();
    };
    renderDots();
    var autoRotate = setInterval(function () {
      goTo(current + 1 > maxIndex ? 0 : current + 1);
    }, 4500);
    track.closest('.testimonial-track-wrap').addEventListener('mouseenter', function () { clearInterval(autoRotate); });
    window.addEventListener('resize', function () {
      perView = window.innerWidth <= 720 ? 1 : (window.innerWidth <= 1080 ? 2 : 3);
      maxIndex = Math.max(0, slides.length - perView);
      goTo(Math.min(current, maxIndex));
    });
  }

  /* --------------------------------------- FAQ accordion --------------------------------------- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var question = item.querySelector('.faq-question');
    var answer = item.querySelector('.faq-answer');
    question.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      item.closest('.faq-list').querySelectorAll('.faq-item').forEach(function (other) {
        other.classList.remove('open');
        other.querySelector('.faq-answer').style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  /* -------------------------------------- Newsletter fake submit -------------------------------------- */
  var newsletterForm = document.querySelector('[data-newsletter-form]');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var label = newsletterForm.querySelector('[data-newsletter-label]');
      var input = newsletterForm.querySelector('input');
      if (label) label.textContent = 'Subscribed ✓';
      if (input) input.value = '';
      setTimeout(function () { if (label) label.textContent = 'Subscribe'; }, 2600);
    });
  }
});

// ==========================================================================
// PHASE 3 — Auth, Profile, Post Work / Find Work interactions
// ==========================================================================
document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------------- Flash auto-dismiss ------------------------------- */
  document.querySelectorAll('.flash-msg').forEach(function (msg) {
    var closeBtn = msg.querySelector('.flash-close');
    var dismiss = function () {
      msg.style.animation = 'flashOut .3s ease forwards';
      setTimeout(function () { msg.remove(); }, 300);
    };
    if (closeBtn) closeBtn.addEventListener('click', dismiss);
    setTimeout(dismiss, 5000);
  });

  /* ------------------------------- Password show/hide ------------------------------- */
  document.querySelectorAll('[data-password-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('data-password-toggle'));
      if (!input) return;
      var isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.innerHTML = isHidden
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.5 18.5 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
    });
  });

  /* ------------------------------- Role selection cards ------------------------------- */
  var roleCards = document.querySelectorAll('.role-card');
  if (roleCards.length) {
    var fieldGroups = {
      customer: document.querySelector('[data-field-group="customer"]'),
      worker: document.querySelector('[data-field-group="worker"]'),
      admin: document.querySelector('[data-field-group="admin"]')
    };
    var applyRole = function (role) {
      roleCards.forEach(function (card) {
        var input = card.querySelector('input');
        card.classList.toggle('selected', input.value === role);
      });
      Object.keys(fieldGroups).forEach(function (key) {
        var group = fieldGroups[key];
        if (!group) return;
        group.classList.toggle('open', key === role);
      });
    };
    roleCards.forEach(function (card) {
      card.addEventListener('click', function () {
        var input = card.querySelector('input');
        input.checked = true;
        applyRole(input.value);
      });
    });
    var initialChecked = document.querySelector('.role-card input:checked');
    applyRole(initialChecked ? initialChecked.value : 'customer');
  }

  /* ------------------------------- Chip select (budget / category) ------------------------------- */
  document.querySelectorAll('.chip-select').forEach(function (group) {
    var chips = group.querySelectorAll('.chip-option');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var input = chip.querySelector('input');
        chips.forEach(function (c) { c.classList.remove('selected'); });
        chip.classList.add('selected');
        input.checked = true;
      });
    });
  });

  /* ------------------------------- Dropzone upload preview ------------------------------- */
  document.querySelectorAll('[data-dropzone]').forEach(function (zone) {
    var input = zone.querySelector('input[type="file"]');
    var preview = zone.parentElement.querySelector('[data-dropzone-preview]');
    var previewImg = preview ? preview.querySelector('img') : null;
    var removeBtn = preview ? preview.querySelector('.remove-img') : null;
    var progress = zone.parentElement.querySelector('[data-upload-progress]');
    var progressBar = progress ? progress.querySelector('.upload-progress-bar') : null;

    var showPreview = function (file) {
      if (!file || !file.type.startsWith('image/')) return;
      var reader = new FileReader();
      reader.onload = function (e) {
        if (previewImg) previewImg.src = e.target.result;
        if (preview) preview.classList.add('active');
        zone.style.display = 'none';
        if (progress && progressBar) {
          progress.classList.add('active');
          progressBar.style.width = '0%';
          requestAnimationFrame(function () {
            setTimeout(function () { progressBar.style.width = '100%'; }, 30);
          });
        }
      };
      reader.readAsDataURL(file);
    };

    if (input) {
      input.addEventListener('change', function () {
        if (input.files && input.files[0]) showPreview(input.files[0]);
      });
    }
    ['dragenter', 'dragover'].forEach(function (evt) {
      zone.addEventListener(evt, function (e) { e.preventDefault(); zone.classList.add('drag-over'); });
    });
    ['dragleave', 'drop'].forEach(function (evt) {
      zone.addEventListener(evt, function (e) { e.preventDefault(); zone.classList.remove('drag-over'); });
    });
    zone.addEventListener('drop', function (e) {
      var file = e.dataTransfer.files[0];
      if (file && input) {
        var dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        showPreview(file);
      }
    });
    if (removeBtn) {
      removeBtn.addEventListener('click', function () {
        if (input) input.value = '';
        if (preview) preview.classList.remove('active');
        if (progress) progress.classList.remove('active');
        zone.style.display = '';
      });
    }
  });

  /* ------------------------------- Multi-step form (Post Work) ------------------------------- */
  var stepperWrap = document.querySelector('[data-stepper]');
  if (stepperWrap) {
    var steps = document.querySelectorAll('.form-step');
    var stepperItems = document.querySelectorAll('.stepper-item');
    var current = 0;

    var showStep = function (index) {
      steps.forEach(function (s, i) { s.classList.toggle('active', i === index); });
      stepperItems.forEach(function (item, i) {
        item.classList.toggle('active', i === index);
        item.classList.toggle('done', i < index);
      });
      current = index;
    };
    showStep(0);

    document.querySelectorAll('[data-step-next]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var requiredFields = steps[current].querySelectorAll('[required]');
        var valid = true;
        requiredFields.forEach(function (field) {
          if (!field.value.trim()) {
            valid = false;
            var wrap = field.closest('.field-float') || field.closest('.field');
            if (wrap) {
              wrap.classList.add('invalid');
              setTimeout(function () { wrap.classList.remove('invalid'); }, 500);
            }
          }
        });
        if (valid && current < steps.length - 1) showStep(current + 1);
      });
    });
    document.querySelectorAll('[data-step-back]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (current > 0) showStep(current - 1);
      });
    });
  }

  /* ------------------------------- Submit button loading state ------------------------------- */
  document.querySelectorAll('form[data-loading-submit]').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.classList.add('is-loading');
    });
  });

  /* ------------------------------- Floating select label fix ------------------------------- */
  document.querySelectorAll('.field-float select').forEach(function (select) {
    var label = select.parentElement.querySelector('label');
    var sync = function () {
      if (label) label.classList.toggle('filled', !!select.value);
    };
    select.addEventListener('change', sync);
    sync();
  });
});

// ==========================================================================
// PHASE 4 — Dashboard shell interactions
// ==========================================================================
document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------------- Sidebar collapse (desktop) ------------------------------- */
  var dashShell = document.querySelector('[data-dash-shell]');
  var sidebarToggle = document.querySelector('[data-sidebar-toggle]');
  if (dashShell && sidebarToggle) {
    var savedState = null;
    try { savedState = localStorage === undefined ? null : null; } catch (e) { savedState = null; }
    sidebarToggle.addEventListener('click', function () {
      dashShell.classList.toggle('collapsed');
    });
  }

  /* ------------------------------- Sidebar mobile open/close ------------------------------- */
  var mobileToggle = document.querySelector('[data-mobile-sidebar-toggle]');
  if (dashShell && mobileToggle) {
    mobileToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      dashShell.classList.toggle('sidebar-open');
    });
    document.addEventListener('click', function (e) {
      if (dashShell.classList.contains('sidebar-open')) {
        var sidebar = document.querySelector('.dash-sidebar');
        if (sidebar && !sidebar.contains(e.target) && e.target !== mobileToggle) {
          dashShell.classList.remove('sidebar-open');
        }
      }
    });
  }

  /* ------------------------------- Dropdown panels (notifications / profile) ------------------------------- */
  var dropdownWraps = document.querySelectorAll('[data-dropdown-wrap]');
  dropdownWraps.forEach(function (wrap) {
    var trigger = wrap.querySelector('[data-dropdown-trigger]');
    if (!trigger) return;
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var wasOpen = wrap.classList.contains('open');
      dropdownWraps.forEach(function (w) { w.classList.remove('open'); });
      if (!wasOpen) wrap.classList.add('open');
    });
  });
  document.addEventListener('click', function (e) {
    dropdownWraps.forEach(function (wrap) {
      if (!wrap.contains(e.target)) wrap.classList.remove('open');
    });
  });

  /* ------------------------------- Availability toggle (worker dashboard) ------------------------------- */
  document.querySelectorAll('.availability-switch').forEach(function (sw) {
    sw.addEventListener('click', function () {
      sw.classList.toggle('on');
      var label = sw.parentElement.querySelector('[data-availability-label]');
      if (label) label.textContent = sw.classList.contains('on') ? 'Available for jobs' : 'Currently unavailable';
    });
  });

  /* ------------------------------- Reject job ------------------------------- */
  document.querySelectorAll('[data-reject-job]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var jobId = btn.getAttribute('data-reject-job');
      var card = btn.closest('.job-card');
      if (card) {
        card.style.transition = 'opacity .35s ease, transform .35s ease';
        card.style.opacity = '0';
        card.style.transform = 'scale(.95)';
        setTimeout(function () { card.remove(); }, 350);
      }
      if (jobId) {
        var meta = document.querySelector('meta[name="csrf-token"]');
        fetch('/jobs/reject/' + jobId, {
          method: 'GET',
          headers: meta ? { 'X-CSRFToken': meta.getAttribute('content') } : {}
        }).catch(function () {});
      }
    });
  });
});

/* ------------------------------- Client-side table search filter ------------------------------- */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-table-search]').forEach(function (input) {
    var table = document.getElementById(input.getAttribute('data-table-search'));
    if (!table) return;
    input.addEventListener('input', function () {
      var query = input.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(function (row) {
        row.style.display = row.textContent.toLowerCase().indexOf(query) !== -1 ? '' : 'none';
      });
    });
  });
});

// ==========================================================================
// PHASE 5 — Marketplace experience interactions
// ==========================================================================
document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------------- Saved jobs (localStorage) ------------------------------- */
  var SAVED_KEY = 'fixnear_saved_jobs';
  function getCsrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }
  function getSavedIds() {
    try { return JSON.parse(localStorage.getItem(SAVED_KEY)) || []; } catch (e) { return []; }
  }
  function setSavedIds(ids) {
    try { localStorage.setItem(SAVED_KEY, JSON.stringify(ids)); } catch (e) {}
  }
  function isSaved(id) { return getSavedIds().indexOf(String(id)) !== -1; }
  function toggleSaved(id) {
    id = String(id);
    var ids = getSavedIds();
    var idx = ids.indexOf(id);
    if (idx === -1) { ids.push(id); } else { ids.splice(idx, 1); }
    setSavedIds(ids);
    return ids.indexOf(id) !== -1;
  }

  function refreshSaveButtons() {
    document.querySelectorAll('[data-save-job]').forEach(function (btn) {
      var id = btn.getAttribute('data-save-job');
      var saved = isSaved(id);
      btn.classList.toggle('saved', saved);
      if (btn.hasAttribute('aria-pressed')) btn.setAttribute('aria-pressed', String(saved));
    });
  }
  refreshSaveButtons();

  // Sync bookmark state from the server (real, persisted saves) when logged in.
  // Silently does nothing for guests — the fetch just won't return JSON.
  fetch('/api/saved-jobs', { headers: { 'Accept': 'application/json' } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (data && data.saved_ids) {
        setSavedIds(data.saved_ids.map(String));
        refreshSaveButtons();
      }
    })
    .catch(function () {});

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-save-job]');
    if (!btn) return;
    e.preventDefault();
    var id = btn.getAttribute('data-save-job');
    var nowSaved = toggleSaved(id);
    btn.classList.toggle('saved', nowSaved);
    if (btn.hasAttribute('aria-pressed')) btn.setAttribute('aria-pressed', String(nowSaved));
    btn.classList.remove('bump');
    void btn.offsetWidth;
    btn.classList.add('bump');

    // Persist the bookmark server-side (best effort — a guest visitor
    // still gets the instant localStorage-based UI feedback above).
    fetch('/saved-jobs/toggle/' + id, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() }
    }).catch(function () {});

    if (window.location.pathname === '/saved-jobs') {
      setTimeout(function () { window.location.reload(); }, 300);
    }
  });

  /* ------------------------------- Share button ------------------------------- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-share-job]');
    if (!btn) return;
    e.preventDefault();
    var url = btn.getAttribute('data-share-url') || window.location.href;
    var title = btn.getAttribute('data-share-title') || 'Check out this job on FixNear';
    if (navigator.share) {
      navigator.share({ title: title, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () {
        btn.setAttribute('title', 'Link copied!');
        var original = btn.innerHTML;
        setTimeout(function () { btn.setAttribute('title', 'Share'); }, 2000);
      });
    }
  });

  /* ------------------------------- Report job modal ------------------------------- */
  document.querySelectorAll('[data-open-modal]').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      var modal = document.getElementById(trigger.getAttribute('data-open-modal'));
      if (modal) modal.classList.add('open');
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay || e.target.closest('.modal-close')) overlay.classList.remove('open');
    });
  });

  /* ------------------------------- Star picker (write review modal) ------------------------------- */
  document.querySelectorAll('.modal-star-picker').forEach(function (picker) {
    var stars = picker.querySelectorAll('svg');
    stars.forEach(function (star, i) {
      star.addEventListener('click', function () {
        stars.forEach(function (s, j) { s.classList.toggle('filled', j <= i); });
      });
    });
  });

  /* ------------------------------- Inline toast on form submit (frontend-only) ------------------------------- */
  document.querySelectorAll('[data-inline-toast-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var toast = form.parentElement.querySelector('.toast-inline');
      if (toast) {
        toast.classList.add('show');
        setTimeout(function () {
          var overlay = form.closest('.modal-overlay');
          if (overlay) overlay.classList.remove('open');
          toast.classList.remove('show');
          form.reset();
        }, 1800);
      }
    });
  });

  /* ------------------------------- Helpful button ------------------------------- */
  document.querySelectorAll('.helpful-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var countEl = btn.querySelector('[data-helpful-count]');
      var active = btn.classList.toggle('active');
      if (countEl) {
        var count = parseInt(countEl.textContent, 10) || 0;
        countEl.textContent = active ? count + 1 : count - 1;
      }
    });
  });

  /* ------------------------------- Filter chips (Find Work) ------------------------------- */
  document.querySelectorAll('[data-filter-chip-group]').forEach(function (group) {
    var chips = group.querySelectorAll('.filter-chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var input = chip.querySelector('input');
        var isActive = chip.classList.contains('active');
        chips.forEach(function (c) { c.classList.remove('active'); });
        if (!isActive) {
          chip.classList.add('active');
          if (input) input.checked = true;
        } else if (input) {
          input.checked = false;
        }
        var form = chip.closest('form');
        if (form) form.submit();
      });
    });
  });

  /* ------------------------------- Live client-side search (Find Work, Saved Jobs, History) ------------------------------- */
  document.querySelectorAll('[data-live-filter]').forEach(function (input) {
    var targetSelector = input.getAttribute('data-live-filter');
    var emptyMsgId = input.getAttribute('data-live-filter-empty');
    input.addEventListener('input', function () {
      var query = input.value.trim().toLowerCase();
      var cards = document.querySelectorAll(targetSelector);
      var visibleCount = 0;
      cards.forEach(function (card) {
        var match = card.textContent.toLowerCase().indexOf(query) !== -1;
        card.style.display = match ? '' : 'none';
        if (match) visibleCount++;
      });
      if (emptyMsgId) {
        var emptyEl = document.getElementById(emptyMsgId);
        if (emptyEl) emptyEl.style.display = visibleCount === 0 ? '' : 'none';
      }
    });
  });

  /* ------------------------------- Client-side sort (progressive enhancement) ------------------------------- */
  var clientSortSelect = document.querySelector('[data-client-sort]');
  if (clientSortSelect) {
    clientSortSelect.addEventListener('change', function () {
      var grid = document.querySelector(clientSortSelect.getAttribute('data-client-sort'));
      if (!grid) return;
      var cards = Array.prototype.slice.call(grid.children);
      var mode = clientSortSelect.value;
      if (mode === 'budget') {
        cards.sort(function (a, b) { return (parseInt(b.dataset.budgetRank || 0, 10)) - (parseInt(a.dataset.budgetRank || 0, 10)); });
      } else if (mode === 'urgent') {
        cards.sort(function (a, b) { return (b.dataset.urgent === 'true' ? 1 : 0) - (a.dataset.urgent === 'true' ? 1 : 0); });
      } else if (mode === 'match') {
        cards.sort(function (a, b) { return (parseInt(b.dataset.matchScore || 0, 10)) - (parseInt(a.dataset.matchScore || 0, 10)); });
      }
      cards.forEach(function (card) { grid.appendChild(card); });
    });
  }

  /* ------------------------------- Notification mark-all-as-read ------------------------------- */
  var markAllBtn = document.querySelector('[data-mark-all-read]');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', function () {
      document.querySelectorAll('.notif-page-item').forEach(function (item) {
        item.classList.add('is-read');
        var dot = item.querySelector('.unread-dot');
        if (dot) dot.remove();
      });
      markAllBtn.textContent = 'All caught up ✓';
      markAllBtn.disabled = true;

      var meta = document.querySelector('meta[name="csrf-token"]');
      fetch('/notifications/mark-all-read', {
        method: 'POST',
        headers: { 'X-CSRFToken': meta ? meta.getAttribute('content') : '' }
      }).catch(function () {});
    });
  }
  document.querySelectorAll('.notif-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.notif-tab').forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      var filter = tab.getAttribute('data-notif-filter');
      document.querySelectorAll('.notif-page-item').forEach(function (item) {
        if (filter === 'all') { item.style.display = ''; }
        else if (filter === 'unread') { item.style.display = item.classList.contains('is-read') ? 'none' : ''; }
      });
    });
  });

  /* ------------------------------- Chat mock interactions ------------------------------- */
  var chatForm = document.querySelector('[data-chat-send-form]');
  if (chatForm) {
    var chatBody = document.querySelector('[data-chat-body]');
    var chatInput = chatForm.querySelector('input');
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = chatInput.value.trim();
      if (!text) return;
      var row = document.createElement('div');
      row.className = 'bubble-row mine';
      row.innerHTML = '<div class="mini-avatar">Y</div><div><div class="bubble">' +
        text.replace(/</g, '&lt;') + '</div><span class="bubble-time">Just now</span></div>';
      chatBody.appendChild(row);
      chatInput.value = '';
      chatBody.scrollTop = chatBody.scrollHeight;

      var typing = document.createElement('div');
      typing.className = 'bubble-row';
      typing.innerHTML = '<div class="mini-avatar">W</div><div class="typing-indicator"><span></span><span></span><span></span></div>';
      setTimeout(function () {
        chatBody.appendChild(typing);
        chatBody.scrollTop = chatBody.scrollHeight;
        setTimeout(function () {
          typing.remove();
          var reply = document.createElement('div');
          reply.className = 'bubble-row';
          reply.innerHTML = '<div class="mini-avatar">W</div><div><div class="bubble">Got it, thanks for the update!</div><span class="bubble-time">Just now</span></div>';
          chatBody.appendChild(reply);
          chatBody.scrollTop = chatBody.scrollHeight;
        }, 1400);
      }, 500);
    });
  }
  document.querySelectorAll('.chat-list-item').forEach(function (item) {
    item.addEventListener('click', function () {
      document.querySelectorAll('.chat-list-item').forEach(function (i) { i.classList.remove('active'); });
      item.classList.add('active');
      var badge = item.querySelector('.unread-count');
      if (badge) badge.remove();
    });
  });

  /* ------------------------------- Skeleton reveal (Related Jobs on Job Details) ------------------------------- */
  document.querySelectorAll('[data-skeleton-reveal]').forEach(function (wrap) {
    var skeleton = wrap.querySelector('[data-skeleton]');
    var content = wrap.querySelector('[data-skeleton-content]');
    if (!skeleton || !content) return;
    content.style.display = 'none';
    setTimeout(function () {
      skeleton.classList.add('skeleton-fade-out');
      setTimeout(function () {
        skeleton.style.display = 'none';
        content.style.display = '';
      }, 400);
    }, 500);
  });

  /* ------------------------------- Saved Jobs page renderer ------------------------------- */
  window.renderSavedJobs = function renderSavedJobs() {
    var container = document.querySelector('[data-saved-jobs-grid]');
    if (!container || typeof window.FIXNEAR_JOBS === 'undefined') return;
    var savedIds = getSavedIds();
    var jobs = window.FIXNEAR_JOBS.filter(function (j) { return savedIds.indexOf(String(j.id)) !== -1; });
    var emptyState = document.querySelector('[data-saved-empty]');

    if (jobs.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.style.display = '';
      return;
    }
    if (emptyState) emptyState.style.display = 'none';

    container.innerHTML = jobs.map(function (job) {
      var desc = (job.description || '').substring(0, 100);
      return (
        '<div class="job-card reveal is-visible">' +
          '<div class="job-card-img placeholder"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></div>' +
          '<div class="card-fab-row"><button type="button" class="card-fab save-btn saved" data-save-job="' + job.id + '"><svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></button></div>' +
          '<div class="job-card-body">' +
            '<div class="job-card-top"><span class="job-category-tag">' + job.category + '</span>' + (job.budget ? '<span class="job-budget">' + job.budget + '</span>' : '') + '</div>' +
            '<p class="job-desc">' + desc + '</p>' +
            '<div class="job-meta-row"><span>' + job.location + '</span></div>' +
            '<div class="job-card-footer"><div class="job-poster"><span class="mini-avatar">' + job.customer_name.charAt(0).toUpperCase() + '</span>' + job.customer_name + '</div>' +
            '<a href="/job/' + job.id + '" class="btn btn-primary btn-ripple btn-sm">View</a></div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  };
  if (document.querySelector('[data-saved-jobs-grid]')) {
    window.renderSavedJobs();
  }
});
