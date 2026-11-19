import demoServices from '../../../data/services.demo.json';
import type { Answer, ResponseMode, SearchResult, Service } from '../domain/types';
import { classifyQuestion, searchServices } from '../domain/search';
import { copy } from '../locales/pt-BR';
import { decodeCatalog, decodeSearch, decodeAnswer } from '../domain/contracts';

const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '');
export const isDemoMode = !baseUrl;
const records = decodeCatalog({ items: demoServices });
async function request(path: string, options?: RequestInit): Promise<unknown> {
  const response = await fetch(`${baseUrl}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers }, signal: AbortSignal.timeout(12000) });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<unknown>;
}
export const portalApi = {
  async listServices(): Promise<Service[]> {
    if (isDemoMode) return records;
    return decodeCatalog(await request('/services'));
  },
  async search(query: string, topic: string): Promise<SearchResult> {
    if (isDemoMode) return { items: searchServices(records, query, topic), query };
    return decodeSearch(await request(`/services?${new URLSearchParams({ query, topic })}`));
  },
  async ask(question: string, mode: ResponseMode): Promise<Answer> {
    if (!isDemoMode) return decodeAnswer(await request('/assistant/query', { method: 'POST', body: JSON.stringify({ question, mode }) }));
    const result = classifyQuestion(records, question);
    return { ...result, mode, message: result.status === 'empty' ? copy.emptyQuestion : copy[result.status] };
  },
};
