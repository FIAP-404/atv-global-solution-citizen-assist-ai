import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Bookmark,
  IdCard,
  BriefcaseBusiness,
  HeartHandshake,
  ChevronRight,
  MessageCircle,
  ExternalLink,
} from 'lucide-react';
import type { Service } from './domain/types';
import { copy as t, topics } from './locales/pt-BR';
import { usePortal } from './App';

export const topicIcons = {
  documents: IdCard,
  work: BriefcaseBusiness,
  social: HeartHandshake,
};
export function SearchForm({
  initialValue = '',
  compact = false,
  onSearch,
}: {
  initialValue?: string;
  compact?: boolean;
  onSearch?: (query: string) => void;
}) {
  const [value, setValue] = useState(initialValue);
  const navigate = useNavigate();
  return (
    <form
      className={`search-form${compact ? ' compact' : ''}`}
      role="search"
      onSubmit={(event) => {
        event.preventDefault();
        if (onSearch) onSearch(value);
        else navigate(`/servicos?q=${encodeURIComponent(value.trim())}`);
      }}
    >
      <Search aria-hidden="true" size={21} />
      <input
        name="query"
        aria-label={t.searchLabel}
        placeholder={t.searchPlaceholder}
        value={value}
        maxLength={200}
        onChange={(event) => setValue(event.target.value)}
      />
      {value && (
        <button
          className="search-clear"
          type="button"
          aria-label={t.clear}
          onClick={() => setValue('')}
        >
          ×
        </button>
      )}
      <button
        className="button button-primary"
        type="submit"
        aria-label={t.search}
      >
        <span>{t.search}</span>
        <Search className="search-mobile-icon" size={18} />
      </button>
    </form>
  );
}
export function Breadcrumb({
  items,
}: {
  items: { label: string; to?: string }[];
}) {
  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      <Link to="/">{t.home}</Link>
      {items.map((item, index) => (
        <span key={`${item.label}-${index}`}>
          <ChevronRight size={13} />
          {item.to ? (
            <Link to={item.to}>{item.label}</Link>
          ) : (
            <span aria-current="page">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
export function ServiceCard({
  service,
  selected,
  onCompare,
}: {
  service: Service;
  selected?: boolean;
  onCompare?: () => void;
}) {
  const { savedIds, toggleSaved } = usePortal();
  const Icon = topicIcons[service.topic];
  const topic = topics.find((item) => item.id === service.topic)!;
  const saved = savedIds.includes(service.id);
  return (
    <article className="service-card">
      <div className="card-top">
        <span className={`topic-icon ${service.topic}`}>
          <Icon size={22} strokeWidth={1.65} />
        </span>
        <button
          className={`icon-button bookmark-button${saved ? ' is-saved' : ''}`}
          aria-label={`${saved ? t.unsave : t.save}: ${service.title}`}
          aria-pressed={saved}
          onClick={() => toggleSaved(service.id)}
        >
          <Bookmark size={18} fill={saved ? 'currentColor' : 'none'} />
        </button>
      </div>
      <span className="card-category">{topic.label}</span>
      <h3>
        <Link to={`/servicos/${service.id}`}>{service.title}</Link>
      </h3>
      <p>{service.summary}</p>
      <div className="card-bottom">
        <Link to={`/servicos/${service.id}`}>
          {t.readGuidance}
          <ChevronRight size={15} />
        </Link>
        {onCompare && (
          <label className="compare-check">
            <input type="checkbox" checked={selected} onChange={onCompare} />
            {t.compare}
          </label>
        )}
      </div>
    </article>
  );
}
export function AssistantBanner() {
  return (
    <section className="assistant-banner">
      <div className="assistant-banner-symbol">
        <MessageCircle size={31} strokeWidth={1.4} />
        <span>+</span>
      </div>
      <div className="assistant-banner-copy">
        <p className="eyebrow">{t.assistantEyebrow}</p>
        <h2>{t.assistantBannerTitle}</h2>
        <p>{t.assistantBannerDescription}</p>
      </div>
      <Link className="button button-dark" to="/assistente">
        {t.startConversation}
      </Link>
    </section>
  );
}
export function OfficialLink({
  service,
  small = false,
}: {
  service: Service;
  small?: boolean;
}) {
  return (
    <a
      className={small ? 'source-link' : 'button button-primary'}
      href={service.source.url}
      target="_blank"
      rel="noreferrer"
    >
      {small ? service.source.title : t.openOfficial}
      <ExternalLink size={small ? 13 : 16} />
    </a>
  );
}
