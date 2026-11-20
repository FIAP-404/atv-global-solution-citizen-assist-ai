import { test } from 'node:test';
import assert from 'node:assert/strict';
import records from '../../data/services.demo.json' with { type: 'json' };
import cases from '../../data/demo-test-cases.json' with { type: 'json' };
import { classifyQuestion } from '../src/domain/search.ts';

test('demo catalog has 15 unique orientations, five per topic, and valid relationships', () => {
  const ids = new Set(records.map((record) => record.id));
  assert.equal(records.length, 15);
  assert.equal(ids.size, 15);
  for (const topic of ['documents', 'work', 'social'])
    assert.equal(records.filter((record) => record.topic === topic).length, 5);
  for (const record of records) {
    assert.equal(new URL(record.source.url).protocol, 'https:');
    assert.ok(
      record.steps.length &&
        record.preparation.length &&
        record.keywords.length,
    );
    assert.match(
      String(record.source.reviewedAt),
      /^\d{4}-\d{2}-\d{2}$/,
      'Every reviewed record must carry its verification date',
    );
    assert.ok(record.relatedIds.length >= 3);
    for (const related of record.relatedIds) {
      assert.ok(ids.has(related));
      assert.notEqual(related, record.id);
    }
  }
});
// The browser fallback search is a simplified offline demo. The full 56-case
// evaluation targets the Python assistant (backend/evaluation.py); here we keep
// the 12 starter scenarios the fallback was designed for.
const fallbackScenarios = new Set([
  'empty', 'unsupported', 'ambiguous', 'work-card', 'registry', 'identity',
  'passport', 'voter', 'fgts', 'unemployment', 'family', 'jobs',
]);
for (const item of cases.filter((c) => fallbackScenarios.has(c.id)))
  test(`demo scenario: ${item.id}`, () => {
    const answer = classifyQuestion(records, item.question);
    assert.equal(answer.status, item.expectedStatus);
    if (item.expectedServiceId)
      assert.equal(answer.services[0]?.id, item.expectedServiceId);
  });
