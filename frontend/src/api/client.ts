import demoServices from '../../../data/services.demo.json';
import type {
  Answer,
  ResponseMode,
  SearchResult,
  Service,
} from '../domain/types';
import { classifyQuestion, searchServices } from '../domain/search';
import { copy } from '../locales/pt-BR';
import { decodeCatalog, decodeSearch, decodeAnswer } from '../domain/contracts';
import { fetchJson } from './http';

const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '');
export const isDemoMode = !baseUrl;
const records = decodeCatalog({ items: demoServices });
const request = (path: string, options?: RequestInit) =>
  fetchJson(`${baseUrl}${path}`, options);
export const portalApi = {
  async listServices(signal?: AbortSignal): Promise<Service[]> {
    if (isDemoMode) return records;
    return decodeCatalog(await request('/services', { signal }));
  },
  async search(
    query: string,
    topic: string,
    signal?: AbortSignal,
  ): Promise<SearchResult> {
    if (isDemoMode)
      return { items: searchServices(records, query, topic), query };
    return decodeSearch(
      await request(`/services?${new URLSearchParams({ query, topic })}`, {
        signal,
      }),
    );
  },
  async ask(
    question: string,
    mode: ResponseMode,
    signal?: AbortSignal,
  ): Promise<Answer> {
    if (!isDemoMode)
      return decodeAnswer(
        await request('/assistant/query', {
          method: 'POST',
          body: JSON.stringify({ question, mode }),
          signal,
        }),
      );
    const result = classifyQuestion(records, question);
    return {
      ...result,
      mode,
      message:
        result.status === 'empty' ? copy.emptyQuestion : copy[result.status],
    };
  },
};
