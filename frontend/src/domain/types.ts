export type TopicId = 'documents' | 'work' | 'social';
export interface Service {
  id: string;
  topic: TopicId;
  title: string;
  summary: string;
  keywords: string[];
  agency: string;
  channel: 'digital' | 'in-person' | 'mixed';
  source: { title: string; url: string; reviewedAt: string | null };
  audience: string;
  steps: string[];
  preparation: string[];
  limitations: string;
  relatedIds: string[];
}
export interface SearchResult {
  items: Service[];
  query: string;
}
export interface Answer {
  status: 'empty' | 'ambiguous' | 'matched' | 'unsupported';
  message: string;
  services: Service[];
  mode: 'direct' | 'steps';
}
export type ResponseMode = Answer['mode'];
