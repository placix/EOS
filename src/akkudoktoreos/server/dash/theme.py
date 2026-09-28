"""EOSdash shell styling and small interaction helpers for MonsterUI."""

from fasthtml.common import Script, Style

EOSDASH_STYLES = Style(
    """
    *, *::before, *::after { box-sizing: border-box; }
    html, body { min-height: 100%; }
    body { margin: 0; overflow-x: hidden; }
    .eos-shell { min-height: 100vh; background: hsl(var(--background)); color: hsl(var(--foreground)); }
    .eos-header {
        position: sticky; top: 0; z-index: 50; background: hsl(var(--card) / .97);
        border-bottom: 1px solid hsl(var(--border)); backdrop-filter: blur(8px);
    }
    .eos-header-row {
        width: 100%; max-width: 100rem; min-height: 4.25rem; margin: 0 auto; padding: .5rem 1.25rem;
        display: flex; align-items: center; gap: 1.25rem;
    }
    .eos-brand {
        flex: 0 0 auto; display: flex; align-items: center; gap: .65rem;
    }
    .eos-brand img { width: 2.25rem; height: 2.25rem; object-fit: contain; }
    .eos-brand-name { font-size: 1.05rem; font-weight: 700; }
    .eos-brand-subtitle { color: hsl(var(--muted-foreground)); font-size: .75rem; }
    .eos-nav-panel { flex: 1 1 auto; min-width: 0; display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
    .eos-nav { display: flex !important; align-items: center; gap: .25rem; padding: 0; }
    .eos-nav li { margin: 0; }
    .eos-nav-link {
        display: flex !important; align-items: center; gap: .5rem; white-space: nowrap;
        border-radius: .375rem; padding: .55rem .7rem !important;
    }
    .eos-nav-link:hover, .eos-nav-link.uk-active {
        color: hsl(var(--primary)); background: hsl(var(--primary) / .10);
    }
    .eos-header-tools { flex: 0 0 auto; min-width: 9.5rem; }
    .eos-header-tools > div, .eos-header-tools uk-theme-switcher { display: block; width: 100%; min-width: 0; }
    .eos-main { min-height: calc(100vh - 4.25rem); }
    .eos-topbar {
        width: 100%; max-width: 100rem; min-height: 3.5rem; margin: 0 auto; display: flex;
        align-items: center; justify-content: space-between; padding: .55rem 1.25rem;
        background: hsl(var(--background));
        border-bottom: 1px solid hsl(var(--border));
    }
    .eos-content {
        width: 100%; max-width: 100rem; min-width: 0; margin: 0 auto; padding: 1.25rem;
        overflow-wrap: anywhere;
    }
    .eos-content > * { min-width: 0; }
    .eos-content img { max-width: 100%; height: auto; }
    .eos-loading-overlay {
        position: fixed; inset: 0; z-index: 45; display: grid; place-items: center;
        background: hsl(var(--background) / .58); backdrop-filter: blur(1px);
        opacity: 0; visibility: hidden; pointer-events: none;
        transition: opacity .14s ease, visibility 0s linear .14s;
    }
    .eos-loading-overlay.htmx-request {
        opacity: 1; visibility: visible; pointer-events: auto;
        transition-delay: .08s, 0s;
    }
    .eos-loading-spinner { color: #15803d; }
    .eos-loading-spinner.uk-spinner > * > * { stroke-width: 2; }
    @media (prefers-reduced-motion: reduce) {
        .eos-loading-spinner.uk-spinner > *,
        .eos-loading-spinner.uk-spinner > * > * { animation-duration: 2.4s; }
    }
    .eos-footer { padding: 0 1.25rem 1.25rem; color: hsl(var(--muted-foreground)); font-size: .8125rem; }
    .eos-footer-links { display: grid !important; grid-template-columns: repeat(4, auto); gap: .75rem 1.5rem; }
    .eos-footer-links > * { margin: 0; min-width: 0; }
    .eos-footer-status { display: flex; align-items: center; gap: .45rem; min-height: 1.5rem; }
    .eos-footer-status-dot { width: .5rem; height: .5rem; border-radius: 50%; flex: 0 0 auto; }
    .eos-footer-status-dot.is-online { background: #22c55e; }
    .eos-footer-status-dot.is-offline { background: #ef4444; }
    .eos-footer-status-link { color: inherit; overflow-wrap: anywhere; }
    .eos-page-heading { font-size: 1.25rem; font-weight: 650; margin: 0; }
    .eos-status-dot { width: .55rem; height: .55rem; border-radius: 999px; background: #22c55e; display: inline-block; }
    .eos-section { border: 1px solid hsl(var(--border)); border-radius: .4rem; background: hsl(var(--card)); }
    .eos-section > summary { padding: .9rem 1rem; }
    .eos-section[open] > summary { border-bottom: 1px solid hsl(var(--border)); }
    .eos-section > div { padding: 1rem; }
    .eos-toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem; }
    .eos-config-readonly-toggle { display: flex; align-items: center; gap: .625rem; }
    .eos-config-readonly-toggle > input { flex: 0 0 auto; margin: 0; }
    .eos-admin-action-summary { display: grid; gap: .75rem; min-width: 0; }
    .eos-admin-action-row {
        display: grid; grid-template-columns: 1.25rem 11rem minmax(0, 36rem);
        align-items: center; gap: .75rem; min-width: 0;
    }
    .eos-admin-action-row > uk-icon { display: inline-flex; justify-content: center; }
    .eos-admin-action-button { width: 11rem; min-width: 11rem; justify-content: center; white-space: nowrap; }
    .eos-admin-action-control { width: 100%; min-width: 0; margin: 0; }
    .eos-admin-action-copy { color: hsl(var(--muted-foreground)); overflow-wrap: anywhere; }
    .eos-admin-filename { display: grid; grid-template-columns: auto minmax(9rem, 1fr) auto; align-items: center; gap: .4rem; }
    .eos-admin-file-tag { width: 100%; min-width: 0; }
    .eos-admin-action-status:empty { display: none; }
    .eos-admin-action-description { margin-top: .75rem; color: hsl(var(--muted-foreground)); }
    .eos-json-editor { min-height: 32rem; resize: vertical; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.55; tab-size: 2; }
    .eos-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)); gap: .75rem; }
    summary { cursor: pointer; }
    details > summary { list-style: none; }
    details > summary::-webkit-details-marker { display: none; }
    @media (max-width: 900px) {
        .eos-header-row { padding: .5rem .875rem; justify-content: space-between; position: relative; }
        .eos-nav-panel {
            display: none; position: absolute; top: 100%; left: 0; right: 0; align-items: stretch;
            padding: .75rem .875rem; background: hsl(var(--card)); border-bottom: 1px solid hsl(var(--border));
            box-shadow: 0 12px 28px rgb(0 0 0 / .14);
        }
        .eos-nav-panel.eos-open { display: block; }
        .eos-nav { display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .25rem; }
        .eos-nav-link { width: 100%; }
        .eos-header-tools { width: 100%; margin-top: .75rem; padding-top: .75rem; border-top: 1px solid hsl(var(--border)); }
        .eos-topbar { padding: .55rem .875rem; }
        .eos-content { padding: .875rem; }
        .eos-footer { padding: 0 .875rem .875rem; }
        .eos-footer-links { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .eos-admin-action-row { grid-template-columns: 1.25rem minmax(0, 1fr); align-items: start; }
        .eos-admin-action-button { width: 100%; min-width: 0; }
        .eos-admin-action-control { grid-column: 2; }
        .eos-admin-filename { grid-template-columns: auto minmax(0, 1fr) auto; }
    }
    @media (min-width: 901px) { .eos-mobile-only { display: none !important; } }
    """
)


EOSDASH_SCRIPT = Script(
    """
    (() => {
      const isDark = () => document.documentElement.classList.contains('dark');
      window.eosTheme = { isDark };

      const closeMenu = () => document.querySelector('.eos-nav-panel')?.classList.remove('eos-open');

      document.addEventListener('click', (event) => {
        if (event.target.closest('[data-eos-menu-toggle]')) {
          document.querySelector('.eos-nav-panel')?.classList.toggle('eos-open');
        }
        const nav = event.target.closest('.eos-nav-link');
        if (nav) {
          document.querySelectorAll('.eos-nav-link').forEach((item) => item.classList.remove('uk-active'));
          nav.classList.add('uk-active');
          const heading = document.querySelector('[data-eos-page-title]');
          if (heading) heading.textContent = nav.dataset.pageTitle || nav.textContent.trim();
          closeMenu();
        }
      });

      const validateJson = (editor) => {
        const message = document.querySelector('[data-json-error]');
        try {
          JSON.parse(editor.value);
          editor.setCustomValidity('');
          editor.removeAttribute('aria-invalid');
          if (message) {
            message.textContent = '';
            message.hidden = true;
          }
          return true;
        } catch (error) {
          editor.setCustomValidity(error.message);
          editor.setAttribute('aria-invalid', 'true');
          if (message) {
            message.textContent = `Invalid JSON: ${error.message}`;
            message.hidden = false;
          }
          return false;
        }
      };

      document.addEventListener('input', (event) => {
        if (event.target.matches('[data-json-editor]')) validateJson(event.target);
      });
      document.addEventListener('keydown', (event) => {
        const editor = event.target.closest?.('[data-json-editor]');
        if (!editor) return;
        if (event.key === 'Tab') {
          event.preventDefault();
          const start = editor.selectionStart;
          editor.setRangeText('  ', start, editor.selectionEnd, 'end');
          editor.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
          event.preventDefault();
          if (validateJson(editor)) editor.form?.requestSubmit();
          else editor.reportValidity();
        }
      });
      document.addEventListener('submit', (event) => {
        const editor = event.target.querySelector?.('[data-json-editor]');
        if (editor && !validateJson(editor)) {
          event.preventDefault();
          editor.reportValidity();
        }
      });

      document.addEventListener('htmx:beforeSwap', (event) => {
        const form = event.detail.requestConfig?.elt?.closest?.('[data-eos-upload-form]');
        if (!form || !event.detail.shouldSwap) return;

        const modal = form.closest('[data-uk-modal]');
        form.reset();
        if (modal && window.UIkit?.modal) window.UIkit.modal(modal).hide();
      });

      let dark = isDark();
      new MutationObserver(() => {
        const next = isDark();
        if (next === dark) return;
        dark = next;
        const active = document.querySelector('.eos-nav-link.uk-active');
        if (active && window.htmx) window.htmx.trigger(active, 'click');
      }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    })();
    """
)
