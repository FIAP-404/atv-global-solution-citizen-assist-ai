import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  LockKeyhole,
  Check,
  CircleDashed,
  ExternalLink,
} from 'lucide-react';
import { usePortal } from '../App';
import { isDemoMode } from '../api/client';
import { Breadcrumb, AssistantBanner } from '../components';
import { copy as t } from '../locales/pt-BR';

export function About() {
  const { clearSaved } = usePortal();
  const [cleared, setCleared] = useState(false);
  return (
    <div className="container page-space">
      <Breadcrumb items={[{ label: t.about }]} />
      <section className="about-intro">
        <p className="eyebrow">{t.aboutEyebrow}</p>
        <h1>{t.aboutTitle}</h1>
        <p>{t.aboutLead}</p>
        <span className="outline-tag">{t.academic} · Grupo 404</span>
      </section>
      <div className="about-body">
        <section>
          <h2>{t.aboutMissionTitle}</h2>
          <p>{t.aboutMission}</p>
        </section>
        <section>
          <h2>{t.aboutDesignTitle}</h2>
          <p>{t.aboutDesign}</p>
          <div className="about-references">
            <a href="https://www.gov.br/pt-br" target="_blank" rel="noreferrer">
              {t.govPortal}
              <ExternalLink size={14} />
            </a>
            <a href="https://www.gov.br/ds/" target="_blank" rel="noreferrer">
              {t.designSystem}
              <ExternalLink size={14} />
            </a>
          </div>
        </section>
        <div className="scope-grid">
          <section>
            <h2>{t.aboutScopeTitle}</h2>
            <ul>
              {t.aboutScope.map((item) => (
                <li key={item}>
                  <Check size={17} />
                  {item}
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h2>{t.aboutPendingTitle}</h2>
            <ul>
              {t.aboutPending.map((item) => (
                <li key={item}>
                  <CircleDashed size={17} />
                  {item}
                </li>
              ))}
            </ul>
          </section>
        </div>
        <section className="privacy-section">
          <LockKeyhole size={26} />
          <div>
            <h2>{t.privacyTitle}</h2>
            <p>{t.privacyDescription}</p>
            <button
              className="button button-outline"
              onClick={() => {
                clearSaved();
                setCleared(true);
              }}
            >
              {t.clearSaved}
            </button>
            {cleared && <p role="status">{t.privacyCleared}</p>}
          </div>
        </section>
        <section className="about-content-note">
          <ShieldCheck size={24} />
          <div>
            <h2>{t.review}</h2>
            <p>{t.sourceNotice}</p>
            {isDemoMode && <p>{t.backendNotice}</p>}
            <Link className="text-link" to="/servicos">
              {t.viewAll}
            </Link>
          </div>
        </section>
      </div>
      <AssistantBanner />
    </div>
  );
}
