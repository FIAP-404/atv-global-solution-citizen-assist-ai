interface Searchable {
  id: string;
  topic: string;
  title: string;
  summary: string;
  keywords: string[];
}
const ignoredWords = new Set([
  'a',
  'o',
  'os',
  'as',
  'e',
  'de',
  'do',
  'da',
  'dos',
  'das',
  'em',
  'no',
  'na',
  'um',
  'uma',
  'meu',
  'minha',
  'como',
  'para',
  'por',
  'que',
  'qual',
  'quais',
  'eu',
  'se',
  'ao',
  'com',
  'faco',
  'posso',
  'preciso',
  'quero',
  'onde',
  'sobre',
]);
const normalize = (value: string) =>
  value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
const words = (value: string) =>
  normalize(value)
    .split(' ')
    .filter((word) => word.length > 1 && !ignoredWords.has(word));

function rank<T extends Searchable>(
  records: T[],
  query: string,
  topic = 'all',
) {
  const terms = [...new Set(words(query))];
  return records
    .filter((record) => topic === 'all' || record.topic === topic)
    .map((record) => {
      const titleWords = new Set(words(record.title));
      const keywordWords = new Set(record.keywords.flatMap(words));
      const summaryWords = new Set(words(record.summary));
      const score = terms.reduce(
        (total, term) =>
          total +
          (titleWords.has(term)
            ? 4
            : keywordWords.has(term)
              ? 3
              : summaryWords.has(term)
                ? 1
                : 0),
        0,
      );
      return {
        record,
        score: score + (normalize(record.title) === normalize(query) ? 20 : 0),
      };
    })
    .filter((item) => !query.trim() || item.score > 0)
    .sort((first, second) => second.score - first.score);
}
export function searchServices<T extends Searchable>(
  records: T[],
  query: string,
  topic = 'all',
): T[] {
  return rank(records, query, topic).map((item) => item.record);
}
export function classifyQuestion<T extends Searchable>(
  records: T[],
  question: string,
): {
  status: 'empty' | 'ambiguous' | 'matched' | 'unsupported';
  services: T[];
} {
  if (!question.trim()) return { status: 'empty', services: [] };
  const ranked = rank(records, question);
  if (!ranked.length) return { status: 'unsupported', services: [] };
  const best = ranked[0];
  const closeMatches = ranked.filter((item) => item.score >= best.score * 0.8);
  return {
    status: closeMatches.length > 1 ? 'ambiguous' : 'matched',
    services: closeMatches.slice(0, 3).map((item) => item.record),
  };
}
