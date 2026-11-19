import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Bookmark,
  Search,
  SlidersHorizontal,
  X,
  LoaderCircle,
  Columns3,
} from 'lucide-react';
import { usePortal } from '../App';
import { portalApi } from '../api/client';
import type { Service } from '../domain/types';
import { copy as t, topics } from '../locales/pt-BR';
import {
  Breadcrumb,
  OfficialLink,
  SearchForm,
  ServiceCard,
} from '../components';

export function Catalog() {
  const [params, setParams] = useSearchParams();
  const query = params.get('q') ?? '';
  const topic = topics.some((item) => item.id === params.get('tema'))
    ? params.get('tema')!
    : 'all';
  const savedOnly = params.get('salvos') === '1';
  const { services, savedIds } = usePortal();
  const [results, setResults] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparisonOpen, setComparisonOpen] = useState(false);
  const [selectionNotice, setSelectionNotice] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    portalApi
      .search(query, topic, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) setResults(result.items);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [query, topic, retry]);
  const visible = results.filter(
    (service) => !savedOnly || savedIds.includes(service.id),
  );
  const selected = selectedIds
    .map((id) => services.find((service) => service.id === id))
    .filter((service) => service !== undefined);
  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value && value !== 'all') next.set(key, value);
    else next.delete(key);
    setParams(next);
  }
  function toggleComparison(id: string) {
    setSelectionNotice('');
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((selectedId) => selectedId !== id));
      setComparisonOpen(false);
    } else if (selectedIds.length < 3) setSelectedIds([...selectedIds, id]);
    else setSelectionNotice(t.compareLimit);
  }
  return (
    <div className="container page-space">
      <Breadcrumb items={[{ label: savedOnly ? t.saved : t.services }]} />
      <div className="page-heading">
        <p className="eyebrow">{t.project}</p>
        <h1>{savedOnly ? t.saved : t.searchTitle}</h1>
        <p>{t.searchDescription}</p>
      </div>
      <SearchForm
        key={query}
        initialValue={query}
        compact
        onSearch={(value) => updateParam('q', value.trim())}
      />
      <div className="catalog-layout">
        <aside className="filter-sidebar">
          <h2>
            <SlidersHorizontal size={17} />
            {t.topicsLabel}
          </h2>
          <div className="topic-filters">
            {[{ id: 'all', label: t.allTopics }, ...topics].map((item) => (
              <button
                key={item.id}
                type="button"
                aria-pressed={topic === item.id}
                onClick={() => updateParam('tema', item.id)}
              >
                {item.label}
                <span>
                  {item.id === 'all'
                    ? services.length
                    : services.filter((service) => service.topic === item.id)
                        .length}
                </span>
              </button>
            ))}
          </div>
          <label className="saved-filter">
            <input
              type="checkbox"
              checked={savedOnly}
              onChange={(event) =>
                updateParam('salvos', event.target.checked ? '1' : '')
              }
            />
            {t.savedOnly}
          </label>
          <div className="filter-hint">
            <Columns3 size={21} />
            <p>{t.compareHint}</p>
          </div>
        </aside>
        <section
          className="catalog-results"
          aria-label={t.services}
          aria-busy={loading}
        >
          <div className="results-toolbar">
            <p role="status">
              {loading ? (
                t.loading
              ) : error ? (
                t.requestError
              ) : (
                <>
                  <strong>{visible.length}</strong>{' '}
                  {visible.length === 1 ? t.result : t.results}
                  {query && <span> · “{query}”</span>}
                </>
              )}
            </p>
            {(query || topic !== 'all') && (
              <button
                className="text-button"
                onClick={() => setParams(savedOnly ? { salvos: '1' } : {})}
              >
                {t.resetFilters}
              </button>
            )}
          </div>
          {loading ? (
            <div className="empty-state">
              <LoaderCircle className="spinner" />
            </div>
          ) : error ? (
            <div className="empty-state" role="alert">
              <h2>{t.requestError}</h2>
              <button
                className="button button-outline"
                onClick={() => setRetry(retry + 1)}
              >
                {t.retry}
              </button>
            </div>
          ) : visible.length ? (
            <div className="service-grid catalog-grid">
              {visible.map((service) => (
                <ServiceCard
                  key={service.id}
                  service={service}
                  selected={selectedIds.includes(service.id)}
                  onCompare={() => toggleComparison(service.id)}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              {savedOnly ? <Bookmark size={37} /> : <Search size={37} />}
              <h2>{savedOnly && !savedIds.length ? t.noSaved : t.noResults}</h2>
              <p>
                {savedOnly && !savedIds.length
                  ? t.noSavedDescription
                  : t.noResultsDescription}
              </p>
              <Link
                className="button button-outline"
                to={savedOnly ? '/servicos' : '/assistente'}
              >
                {savedOnly ? t.viewAll : t.startConversation}
              </Link>
            </div>
          )}
        </section>
      </div>
      {selected.length > 0 && (
        <div className="comparison-dock">
          <div>
            <Columns3 size={20} />
            <span>
              <strong>{selected.length}</strong> {t.compareSelected}
            </span>
          </div>
          <div>
            <button
              className="text-button"
              onClick={() => {
                setSelectedIds([]);
                setComparisonOpen(false);
                setSelectionNotice('');
              }}
            >
              {t.removeSelection}
            </button>
            <button
              className="button button-dark"
              disabled={selected.length < 2}
              onClick={() => setComparisonOpen(!comparisonOpen)}
            >
              {comparisonOpen ? t.close : t.comparison}
            </button>
          </div>
        </div>
      )}
      {selectionNotice && (
        <p className="form-error" role="status">
          {selectionNotice}
        </p>
      )}
      {comparisonOpen && selected.length >= 2 && (
        <section className="comparison-section" aria-label={t.comparison}>
          <div className="section-heading">
            <h2>{t.comparison}</h2>
            <button
              className="icon-button"
              aria-label={t.close}
              onClick={() => setComparisonOpen(false)}
            >
              <X size={19} />
            </button>
          </div>
          <div className="comparison-scroll">
            <table>
              <caption className="sr-only">{t.comparison}</caption>
              <thead>
                <tr>
                  <th scope="col">{t.compareField}</th>
                  {selected.map((service) => (
                    <th scope="col" key={service.id}>
                      <Link to={`/servicos/${service.id}`}>
                        {service.title}
                      </Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">{t.scope}</th>
                  {selected.map((service) => (
                    <td key={service.id}>{service.summary}</td>
                  ))}
                </tr>
                <tr>
                  <th scope="row">{t.agency}</th>
                  {selected.map((service) => (
                    <td key={service.id}>{service.agency}</td>
                  ))}
                </tr>
                <tr>
                  <th scope="row">{t.channel}</th>
                  {selected.map((service) => (
                    <td key={service.id}>{t.channels[service.channel]}</td>
                  ))}
                </tr>
                <tr>
                  <th scope="row">{t.source}</th>
                  {selected.map((service) => (
                    <td key={service.id}>
                      <OfficialLink service={service} small />
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      )}
      <p className="page-data-note">{t.demoNotice}</p>
    </div>
  );
}
