import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import {
  Bookmark,
  Contrast,
  Menu,
  X,
  Search,
  ShieldCheck,
  MessageCircle,
  ExternalLink,
  LoaderCircle,
} from 'lucide-react';
import type { Service } from './domain/types';
import { portalApi, isDemoMode } from './api/client';
import { copy as t } from './locales/pt-BR';
import { Home } from './pages/Home';
import { Catalog } from './pages/Catalog';
import { ServiceDetail } from './pages/ServiceDetail';
import { Assistant } from './pages/Assistant';
import { About } from './pages/About';

interface PortalContextValue {
  services: Service[];
  savedIds: string[];
  toggleSaved: (id: string) => void;
  clearSaved: () => void;
}
const PortalContext = createContext<PortalContextValue | null>(null);
export function usePortal() {
  const value = useContext(PortalContext);
  if (!value) throw new Error('Portal provider is missing');
  return value;
}
function readSaved(): string[] {
  try {
    const value: unknown = JSON.parse(
      localStorage.getItem('citizen-assist:saved') ?? '[]',
    );
    return Array.isArray(value)
      ? [...new Set(value.filter((id): id is string => typeof id === 'string'))]
      : [];
  } catch {
    return [];
  }
}
export function NotFound() {
  return (
    <section className="container empty-state page-space">
      <Search size={42} />
      <h1>{t.notFoundTitle}</h1>
      <p>{t.notFoundDescription}</p>
      <Link className="button button-primary" to="/servicos">
        {t.backServices}
      </Link>
    </section>
  );
}
export function App() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [savedIds, setSavedIds] = useState(readSaved);
  const [storageNotice, setStorageNotice] = useState(false);
  const [contrast, setContrast] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [retry, setRetry] = useState(0);
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    portalApi
      .listServices(controller.signal)
      .then((items) => {
        if (!controller.signal.aborted) setServices(items);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [retry]);
  useEffect(() => {
    setMenuOpen(false);
    window.scrollTo(0, 0);
    mainRef.current?.focus({ preventScroll: true });
  }, [location.pathname]);
  function storeSaved(next: string[]) {
    setSavedIds(next);
    try {
      localStorage.setItem('citizen-assist:saved', JSON.stringify(next));
      setStorageNotice(false);
    } catch {
      setStorageNotice(true);
    }
  }
  function toggleSaved(id: string) {
    storeSaved(
      savedIds.includes(id)
        ? savedIds.filter((saved) => saved !== id)
        : [...savedIds, id],
    );
  }
  return (
    <PortalContext.Provider
      value={{
        services,
        savedIds,
        toggleSaved,
        clearSaved: () => storeSaved([]),
      }}
    >
      <div className={`portal-app${contrast ? ' high-contrast' : ''}`}>
        <a
          className="skip-link"
          href="#main-content"
          onClick={(event) => {
            event.preventDefault();
            mainRef.current?.focus();
          }}
        >
          {t.skip}
        </a>
        <div className="academic-bar">
          <div className="container">
            <span>
              {t.academic} <span className="bar-separator">/</span> Global
              Solution 2026.2
            </span>
            <span className="academic-mode">
              {isDemoMode ? t.demo : t.project}
            </span>
          </div>
        </div>
        <header className="site-header">
          <div className="container header-main">
            <Link
              className="brand"
              to="/"
              aria-label={`${t.brand} — ${t.home}`}
            >
              <img src="/fiap-logo.png" width="118" height="32" alt="FIAP" />
              <span className="brand-divider" />
              <span className="brand-name">
                <strong>{t.brand}</strong>
                <span>{t.tagline}</span>
              </span>
            </Link>
            <div className="header-actions">
              <button
                className="icon-button contrast-button"
                type="button"
                aria-label={t.contrast}
                aria-pressed={contrast}
                onClick={() => setContrast(!contrast)}
              >
                <Contrast size={19} />
              </button>
              <Link
                className="saved-link"
                to="/servicos?salvos=1"
                aria-label={`${t.saved}${savedIds.length ? ` ${savedIds.length}` : ''}`}
              >
                <Bookmark size={17} />
                <span>{t.saved}</span>
                {savedIds.length > 0 && (
                  <span className="saved-count">{savedIds.length}</span>
                )}
              </Link>
              <button
                className="icon-button mobile-menu"
                aria-label={menuOpen ? t.close : t.menu}
                aria-expanded={menuOpen}
                aria-controls="main-navigation"
                onClick={() => setMenuOpen(!menuOpen)}
              >
                {menuOpen ? <X /> : <Menu />}
              </button>
            </div>
          </div>
          <div className="nav-border">
            <nav
              id="main-navigation"
              className={`container main-nav${menuOpen ? ' is-open' : ''}`}
              aria-label={t.services}
            >
              <NavLink to="/" end>
                {t.home}
              </NavLink>
              <NavLink to="/servicos">{t.services}</NavLink>
              <NavLink to="/assistente">
                <MessageCircle size={16} />
                {t.assistant}
              </NavLink>
              <NavLink to="/sobre">{t.about}</NavLink>
              <button
                className="mobile-contrast text-button"
                aria-pressed={contrast}
                onClick={() => setContrast(!contrast)}
              >
                <Contrast size={17} />
                {t.contrast}
              </button>
              <span className="nav-caption">{t.national}</span>
            </nav>
          </div>
        </header>
        {storageNotice && (
          <div className="container inline-notice" role="status">
            {t.clearBookmarksNotice}
          </div>
        )}
        <main id="main-content" tabIndex={-1} ref={mainRef}>
          {loading ? (
            <section className="empty-state page-space" role="status">
              <LoaderCircle className="spinner" size={28} />
              <p>{t.loading}</p>
            </section>
          ) : error ? (
            <section className="container empty-state page-space" role="alert">
              <h1>{t.loadError}</h1>
              <button
                className="button button-primary"
                onClick={() => setRetry(retry + 1)}
              >
                {t.retry}
              </button>
            </section>
          ) : (
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/servicos" element={<Catalog />} />
              <Route path="/servicos/:id" element={<ServiceDetail />} />
              <Route path="/assistente" element={<Assistant />} />
              <Route path="/sobre" element={<About />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          )}
        </main>
        <footer className="site-footer">
          <div className="container footer-main">
            <div className="footer-brand">
              <img
                src="/fiap-logo-white.png"
                width="100"
                height="34"
                alt="FIAP"
              />
              <h2>
                {t.footerTitle}
                <br />
                <span>{t.footerHighlight}</span>
              </h2>
              <p>{t.footerAcademic}</p>
            </div>
            <div>
              <h3>{t.footerLinks}</h3>
              <Link to="/servicos">{t.services}</Link>
              <Link to="/assistente">{t.assistant}</Link>
              <Link to="/sobre">{t.about}</Link>
            </div>
            <div>
              <h3>{t.footerSources}</h3>
              <a
                href="https://www.gov.br/pt-br"
                target="_blank"
                rel="noreferrer"
              >
                {t.govPortal}
                <ExternalLink size={12} />
              </a>
              <a href="https://www.gov.br/ds/" target="_blank" rel="noreferrer">
                {t.designSystem}
                <ExternalLink size={12} />
              </a>
              <a
                href="https://github.com/FIAP-404/atv-global-solution-citizen-assist-ai"
                target="_blank"
                rel="noreferrer"
              >
                {t.repository}
                <ExternalLink size={12} />
              </a>
            </div>
          </div>
          <div className="container footer-bottom">
            <span>{t.footerMeta}</span>
            <span>
              <ShieldCheck size={14} />
              {t.lastUpdate}
            </span>
          </div>
        </footer>
      </div>
    </PortalContext.Provider>
  );
}
