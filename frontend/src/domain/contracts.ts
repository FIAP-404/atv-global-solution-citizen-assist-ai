import type { Answer, SearchResult, Service } from './types.ts';

const object = (value: unknown): value is Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0;
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.every(text);
function safeUrl(value: unknown): boolean {
  if (!text(value)) return false;
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password; } catch { return false; }
}
function isService(value: unknown): value is Service {
  if (!object(value) || !object(value.source)) return false;
  return ['id', 'title', 'summary', 'agency', 'audience', 'limitations'].every(key => text(value[key])) &&
    ['documents', 'work', 'social'].includes(String(value.topic)) &&
    ['digital', 'in-person', 'mixed'].includes(String(value.channel)) &&
    ['keywords', 'steps', 'preparation', 'relatedIds'].every(key => strings(value[key])) &&
    text(value.source.title) && safeUrl(value.source.url) &&
    (value.source.reviewedAt === null || (text(value.source.reviewedAt) && /^\d{4}-\d{2}-\d{2}$/.test(value.source.reviewedAt) && Number.isFinite(Date.parse(value.source.reviewedAt))));
}
function serviceList(value: unknown): Service[] {
  if (!Array.isArray(value) || !value.every(isService) || new Set(value.map(service => service.id)).size !== value.length) throw new Error('Invalid service list response');
  return value;
}
export function decodeCatalog(value: unknown): Service[] {
  if (!object(value)) throw new Error('Invalid catalog response');
  return serviceList(value.items);
}
export function decodeSearch(value: unknown): SearchResult {
  if (!object(value) || typeof value.query !== 'string') throw new Error('Invalid search response');
  return { items: serviceList(value.items), query: value.query };
}
export function decodeAnswer(value: unknown): Answer {
  if (!object(value) || !text(value.message) || !['empty', 'ambiguous', 'matched', 'unsupported'].includes(String(value.status)) || !['direct', 'steps'].includes(String(value.mode))) throw new Error('Invalid assistant response');
  const services = serviceList(value.services);
  if ((value.status === 'matched' && services.length !== 1) ||
    (value.status === 'ambiguous' && (services.length < 2 || services.length > 3)) ||
    ((value.status === 'empty' || value.status === 'unsupported') && services.length !== 0)) throw new Error('Invalid assistant result cardinality');
  return { status: value.status as Answer['status'], message: value.message, services, mode: value.mode as Answer['mode'] };
}
