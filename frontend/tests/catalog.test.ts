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
    assert.equal(
      record.source.reviewedAt,
      null,
      'Draft content must not claim completed source verification',
    );
    assert.ok(record.relatedIds.length >= 3);
    for (const related of record.relatedIds) {
      assert.ok(ids.has(related));
      assert.notEqual(related, record.id);
    }
  }
});
for (const item of cases)
  test(`demo scenario: ${item.id}`, () => {
    const answer = classifyQuestion(records, item.question);
    assert.equal(answer.status, item.expectedStatus);
    if (item.expectedServiceId)
      assert.equal(answer.services[0]?.id, item.expectedServiceId);
  });
