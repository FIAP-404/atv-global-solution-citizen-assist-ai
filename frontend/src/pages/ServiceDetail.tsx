import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Bookmark,
  Printer,
  Link as LinkIcon,
  CircleCheck,
  Info,
  Clock3,
  ShieldCheck,
  MessageCircle,
} from 'lucide-react';
import { NotFound, usePortal } from '../App';
import type { Service } from '../domain/types';
import {
  Breadcrumb,
  OfficialLink,
  ServiceCard,
  topicIcons,
} from '../components';
import { copy as t, topics } from '../locales/pt-BR';

export function ServiceDetail() {
  const { id } = useParams();
  const { services } = usePortal();
  const service = services.find((item) => item.id === id);
  return service ? (
    <DetailBody key={service.id} service={service} />
  ) : (
    <NotFound />
  );
}
function DetailBody({ service }: { service: Service }) {
  const { services, savedIds, toggleSaved } = usePortal();
  const [checked, setChecked] = useState<number[]>([]);
  const [copyStatus, setCopyStatus] = useState('');
  const topic = topics.find((item) => item.id === service.topic)!;
  const TopicIcon = topicIcons[service.topic];
  const related = service.relatedIds
    .map((id) => services.find((item) => item.id === id))
    .filter((item) => item !== undefined);
  const saved = savedIds.includes(service.id);
  async function copyLink() {
    try {
      await navigator.clipboard.writeText(location.href);
      setCopyStatus(t.copied);
    } catch {
      setCopyStatus(t.copyError);
    }
  }
  return (
    <div className="container page-space">
      <Breadcrumb
        items={[
          { label: t.services, to: '/servicos' },
          { label: topic.shortLabel, to: `/servicos?tema=${topic.id}` },
          { label: service.title },
        ]}
      />
      <div className="detail-title">
        <div>
          <p className="eyebrow">{t.detailEyebrow}</p>
          <div className="detail-topic">
            <TopicIcon size={17} />
            {topic.label}
          </div>
          <h1>{service.title}</h1>
          <p className="detail-summary">{service.summary}</p>
          <div className="detail-meta">
            <span>
              <ShieldCheck size={15} />
              {service.agency}
            </span>
            <span>
              <Clock3 size={15} />
              {t.channels[service.channel]}
            </span>
          </div>
        </div>
        <div className="detail-tools">
          <button
            className={`icon-button${saved ? ' is-saved' : ''}`}
            aria-label={saved ? t.unsave : t.save}
            aria-pressed={saved}
            onClick={() => toggleSaved(service.id)}
          >
            <Bookmark size={20} fill={saved ? 'currentColor' : 'none'} />
          </button>
          <button
            className="icon-button"
            aria-label={t.print}
            onClick={() => window.print()}
          >
            <Printer size={20} />
          </button>
          <button
            className="icon-button"
            aria-label={t.copyLink}
            onClick={copyLink}
          >
            <LinkIcon size={20} />
          </button>
        </div>
      </div>
      {copyStatus && (
        <p role="status" className="inline-notice">
          {copyStatus}
        </p>
      )}
      <div className="detail-layout">
        <article className="detail-body">
          <section>
            <h2>{t.overview}</h2>
            <p>{service.summary}</p>
          </section>
          <section>
            <h2>{t.audience}</h2>
            <p>{service.audience}</p>
          </section>
          <section>
            <h2>{t.nextSteps}</h2>
            <ol className="steps-list">
              {service.steps.map((step, index) => (
                <li key={step}>
                  <span className="step-number">{index + 1}</span>
                  <p>{step}</p>
                </li>
              ))}
            </ol>
          </section>
          <section className="preparation">
            <h2>{t.preparation}</h2>
            <p>{t.preparationDescription}</p>
            <div className="checklist">
              {service.preparation.map((item, index) => (
                <label key={item}>
                  <input
                    type="checkbox"
                    checked={checked.includes(index)}
                    onChange={(event) =>
                      setChecked(
                        event.target.checked
                          ? [...checked, index]
                          : checked.filter((value) => value !== index),
                      )
                    }
                  />
                  <span>{item}</span>
                </label>
              ))}
            </div>
            <div className="checklist-progress">
              <progress
                max={service.preparation.length}
                value={checked.length}
                aria-label={t.preparationProgress}
              />
              <span aria-live="polite">
                {checked.length}/{service.preparation.length}{' '}
                {t.preparationProgress}
              </span>
            </div>
          </section>
          <section className="limitations">
            <Info size={22} />
            <div>
              <h2>{t.limitations}</h2>
              <p>{service.limitations}</p>
            </div>
          </section>
        </article>
        <aside className="source-sidebar">
          <div className="official-card">
            <div className="source-mark">
              <ShieldCheck size={23} />
            </div>
            <p className="eyebrow">{t.officialReference}</p>
            <h2>{t.sourceTitle}</h2>
            <p>{t.sourceDescription}</p>
            <OfficialLink service={service} />
            <div className="source-reference">
              <span>{t.source}</span>
              <OfficialLink service={service} small />
            </div>
            <p
              className={`review-status${service.source.reviewedAt ? ' reviewed' : ''}`}
            >
              <CircleCheck size={16} />
              {service.source.reviewedAt
                ? `${t.reviewedOn} ${new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' }).format(new Date(service.source.reviewedAt))}`
                : t.notReviewed}
            </p>
          </div>
          <div className="detail-help">
            <MessageCircle size={21} />
            <h3>{t.assistantSidebarTitle}</h3>
            <p>{t.assistantSidebarText}</p>
            <Link
              to={`/assistente?q=${encodeURIComponent(service.title)}`}
              className="text-link"
            >
              {t.startConversation}
            </Link>
          </div>
          <p className="small-note">{t.sourceSafety}</p>
        </aside>
      </div>
      {related.length > 0 && (
        <section className="related-section">
          <div className="section-heading">
            <h2>{t.related}</h2>
          </div>
          <div className="service-grid">
            {related.map((item) => (
              <ServiceCard key={item.id} service={item} />
            ))}
          </div>
        </section>
      )}
      <p className="page-data-note">{t.demoNotice}</p>
    </div>
  );
}
