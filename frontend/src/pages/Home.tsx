import { Link } from 'react-router-dom';
import { ShieldCheck, CircleHelp, LockKeyhole, ChevronRight } from 'lucide-react';
import { usePortal } from '../App';
import { copy as t, topics } from '../locales/pt-BR';
import { AssistantBanner, SearchForm, ServiceCard, topicIcons } from '../components';

export function Home() {
  const { services } = usePortal();
  const featured = ['cpf', 'work-card', 'social-registry', 'identity', 'unemployment', 'cras'].map(id => services.find(service => service.id === id)).filter(service => service !== undefined);
  const trustIcons = [ShieldCheck, CircleHelp, LockKeyhole];
  return <>
    <section className="hero"><div className="hero-art" aria-hidden="true"><div /><div /><div /><span>+</span><b>404</b></div><div className="container hero-content"><p className="eyebrow">{t.heroEyebrow}</p><h1>{t.heroTitle}<br /><span>{t.heroHighlight}</span></h1><p className="hero-description">{t.heroDescription}</p><SearchForm /><div className="popular-searches"><span>{t.popular}</span>{t.popularQueries.map(query => <Link key={query} to={`/servicos?q=${encodeURIComponent(query)}`}>{query}</Link>)}</div><p className="hero-footnote"><LockKeyhole size={13} />{t.heroFootnote}</p></div></section>
    <section className="container section-space"><div className="section-heading"><div><p className="eyebrow">{t.journeyEyebrow}</p><h2>{t.journeyTitle}</h2><p>{t.journeyDescription}</p></div><span className="section-index">01 / 03</span></div><div className="topic-grid">{topics.map(topic => { const Icon = topicIcons[topic.id]; return <Link className="topic-card" key={topic.id} to={`/servicos?tema=${topic.id}`}><div className="topic-card-top"><Icon size={29} strokeWidth={1.4} /><span>{services.filter(service => service.topic === topic.id).length} {t.guidanceCount}</span></div><h3>{topic.label}</h3><p>{topic.description}</p><span className="topic-card-action">{t.explore}<ChevronRight size={17} /></span></Link>; })}</div></section>
    <section className="highlights-section"><div className="container section-space"><div className="section-heading"><div><h2>{t.highlightsTitle}</h2><p>{t.highlightsDescription}</p></div><Link className="text-link desktop-link" to="/servicos">{t.viewAll}<ChevronRight size={17} /></Link></div><div className="service-grid">{featured.map(service => <ServiceCard key={service.id} service={service} />)}</div><Link className="button button-outline explore-all" to="/servicos">{t.viewAll}</Link></div></section>
    <div className="container section-space"><AssistantBanner /></div>
    <section className="trust-section"><div className="container"><div className="trust-heading"><p className="eyebrow">{t.project}</p><h2>{t.trustTitle}</h2><p>{t.trustDescription}</p><Link className="text-link" to="/sobre">{t.aboutHelp}<ChevronRight size={16} /></Link></div><div className="trust-grid">{t.trustItems.map((item, index) => { const Icon = trustIcons[index]; return <div key={item.title}><Icon size={24} strokeWidth={1.6} /><h3>{item.title}</h3><p>{item.text}</p></div>; })}</div></div></section>
  </>;
}
