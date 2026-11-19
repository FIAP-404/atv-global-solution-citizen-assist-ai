import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { MessageCircle, Plus, Send, Check, ShieldCheck, RefreshCw, LoaderCircle, CircleHelp, BookOpen, UserRound, Sparkles } from 'lucide-react';
import { portalApi, isDemoMode } from '../api/client';
import type { Answer, ResponseMode } from '../domain/types';
import { copy as t } from '../locales/pt-BR';
import { Breadcrumb, OfficialLink } from '../components';

interface Turn { id: number; question: string; answer: Answer; }
export function Assistant() {
  const [params] = useSearchParams();
  const [question, setQuestion] = useState(params.get('q') ?? '');
  const [mode, setMode] = useState<ResponseMode>('direct');
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const endRef = useRef<HTMLDivElement>(null);
  const mounted = useRef(true);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);
  useEffect(() => { if (turns.length) endRef.current?.scrollIntoView({ block: 'nearest' }); }, [turns.length]);
  useEffect(() => { if (!busy && turns.length) inputRef.current?.focus({ preventScroll: true }); }, [busy, turns.length]);
  async function submit(value: string) {
    if (busy) return;
    if (!value.trim()) { setError(t.emptyQuestion); inputRef.current?.focus(); return; }
    if (value.length > 500) { setError(t.longQuestion); return; }
    setBusy(true); setError('');
    try { const answer = await portalApi.ask(value.trim(), mode); if (mounted.current) { setTurns(previous => [...previous, { id: Date.now(), question: value.trim(), answer }]); setQuestion(''); } }
    catch { if (mounted.current) setError(t.requestError); }
    finally { if (mounted.current) setBusy(false); }
  }
  return <div className="container page-space assistant-page"><Breadcrumb items={[{ label: t.assistant }]} /><div className="page-heading"><p className="eyebrow">{t.assistantEyebrow}</p><h1>{t.assistantTitle}</h1><p>{t.assistantDescription}</p></div><div className="chat-layout"><aside className="chat-sidebar"><div className="assistant-avatar"><MessageCircle size={28} strokeWidth={1.6} /><Plus size={12} /></div><h2>{t.assistantSidebarTitle}</h2><p>{t.assistantSidebarText}</p><ul>{t.assistantBenefits.map(text => <li key={text}><Check size={15} />{text}</li>)}</ul><fieldset className="response-mode"><legend>{t.assistantMode}</legend><label><input type="radio" name="response-mode" checked={mode === 'direct'} onChange={() => setMode('direct')} /><span>{t.direct}</span></label><label><input type="radio" name="response-mode" checked={mode === 'steps'} onChange={() => setMode('steps')} /><span>{t.steps}</span></label></fieldset><button className="button button-outline new-chat" disabled={busy || turns.length === 0} onClick={() => { setTurns([]); setQuestion(''); setError(''); inputRef.current?.focus(); }}><RefreshCw size={15} />{t.newConversation}</button><div className="chat-privacy"><ShieldCheck size={17} /><p>{t.sourceSafety}</p></div></aside>
    <section className="chat-panel" aria-label={t.assistant}><div className="chat-panel-header"><div><MessageCircle size={18} /><strong>{t.project}</strong></div>{isDemoMode && <span className="status-pill">{t.demo}</span>}</div><div className={`chat-messages${!turns.length ? ' is-empty' : ''}`} aria-live="polite" aria-busy={busy}>
      {!turns.length && <div className="chat-welcome"><span className="welcome-icon"><Sparkles size={27} strokeWidth={1.4} /></span><h2>{t.assistantWelcome}</h2><p>{t.assistantWelcomeText}</p><div className="question-suggestions">{t.suggestions.map(suggestion => <button type="button" key={suggestion} disabled={busy} onClick={() => submit(suggestion)}><MessageCircle size={15} />{suggestion}</button>)}</div></div>}
      {turns.map(turn => <div className="chat-turn" key={turn.id}><div className="user-message"><span><UserRound size={14} />{t.yourQuestion}</span><p>{turn.question}</p></div><div className="assistant-message"><span className="message-author"><span className="mini-avatar"><MessageCircle size={13} /></span>{t.answerAuthor}<small>{turn.answer.mode === 'direct' ? t.direct : t.steps}</small></span><p>{turn.answer.message}</p>{turn.answer.status === 'matched' && turn.answer.services[0] && <><p>{turn.answer.services[0].summary}</p>{turn.answer.mode === 'steps' && <ol>{turn.answer.services[0].steps.map(step => <li key={step}>{step}</li>)}</ol>}<p className="answer-limitation">{turn.answer.services[0].limitations}</p><div className="answer-source"><BookOpen size={15} /><OfficialLink service={turn.answer.services[0]} small /></div></>}
      {turn.answer.services.length > 0 && <div className="answer-services">{turn.answer.services.map(service => <Link key={service.id} to={`/servicos/${service.id}`}><CircleHelp size={16} /><span>{service.title}</span></Link>)}</div>}{turn.answer.status === 'unsupported' && <Link className="text-link" to="/servicos">{t.viewAll}</Link>}</div></div>)}
      {busy && <p className="thinking" role="status"><LoaderCircle size={16} className="spinner" />{t.thinking}</p>}<div ref={endRef} />
    </div><form className="chat-composer" onSubmit={event => { event.preventDefault(); void submit(question); }}><div><label className="sr-only" htmlFor="citizen-question">{t.questionLabel}</label><textarea id="citizen-question" ref={inputRef} value={question} rows={2} maxLength={500} placeholder={t.questionPlaceholder} disabled={busy} onChange={event => setQuestion(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void submit(question); } }} /><button className="send-button" type="submit" disabled={busy} aria-label={t.send}><Send size={19} /></button></div>{error && <p className="form-error" role="alert">{error}</p>}<p className="composer-note">{isDemoMode ? t.assistantDisclaimer : t.sourceSafety}</p></form></section></div></div>;
}
