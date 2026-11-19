import { test } from 'node:test';
import assert from 'node:assert/strict';
import records from '../../data/services.demo.json' with { type: 'json' };
import { decodeCatalog, decodeSearch, decodeAnswer } from '../src/domain/contracts.ts';

test('accepts the documented catalog and search response', () => {
  assert.equal(decodeCatalog({ items: records }).length, 15);
  assert.equal(decodeSearch({ items: records, query: 'cpf' }).query, 'cpf');
});
test('rejects malformed successful responses before React receives them', () => {
  assert.throws(() => decodeCatalog({}));
  assert.throws(() => decodeSearch({}));
  assert.throws(() => decodeAnswer({}));
  assert.throws(() => decodeCatalog({ items: [{ ...records[0], steps: null }] }));
});
test('rejects unsafe reference URLs and duplicate catalog IDs', () => {
  assert.throws(() => decodeCatalog({ items: [{ ...records[0], source: { ...records[0].source, url: 'javascript:alert(1)' } }] }));
  assert.throws(() => decodeCatalog({ items: [records[0], records[0]] }));
});
test('enforces assistant result cardinality and response mode', () => {
  assert.throws(() => decodeAnswer({ status: 'matched', message: 'Found', services: [], mode: 'direct' }));
  assert.throws(() => decodeAnswer({ status: 'unsupported', message: 'Missing', services: [records[0]], mode: 'direct' }));
  assert.throws(() => decodeAnswer({ status: 'matched', message: 'Found', services: [records[0]], mode: 'invented' }));
  assert.equal(decodeAnswer({ status: 'matched', message: 'Found', services: [records[0]], mode: 'steps' }).services[0].id, 'cpf');
});
