import { test } from 'node:test';
import assert from 'node:assert/strict';
import { searchServices, classifyQuestion } from '../src/domain/search.ts';

const records = [
  {
    id: 'cpf',
    topic: 'documents',
    title: 'Consultar CPF',
    summary: 'Cadastro de pessoas físicas',
    keywords: ['cpf', 'documento'],
  },
  {
    id: 'cin',
    topic: 'documents',
    title: 'Carteira de Identidade Nacional',
    summary: 'Conhecer a identidade',
    keywords: ['cin', 'identidade', 'documento'],
  },
  {
    id: 'social',
    topic: 'social',
    title: 'Cadastro Único',
    summary: 'Cadastro social',
    keywords: ['cadunico', 'cadastro unico'],
  },
];

test('matches accents and case and ranks exact titles first', () => {
  assert.equal(searchServices(records, 'CADASTRO ÚNICO')[0]?.id, 'social');
  assert.equal(searchServices(records, 'cadunico')[0]?.id, 'social');
});
test('filters by topic and returns no match rather than unrelated advice', () => {
  assert.deepEqual(searchServices(records, 'cpf', 'social'), []);
  assert.deepEqual(searchServices(records, 'astronomia'), []);
});
test('distinguishes empty, ambiguous, matched, and unsupported questions', () => {
  assert.equal(classifyQuestion(records, '   ').status, 'empty');
  assert.equal(classifyQuestion(records, 'documento').status, 'ambiguous');
  assert.equal(
    classifyQuestion(records, 'Como consultar meu CPF?').status,
    'matched',
  );
  assert.equal(
    classifyQuestion(records, 'qual a previsão do tempo?').status,
    'unsupported',
  );
});
test('requires a meaningful term and does not match a keyword substring', () => {
  assert.equal(classifyQuestion(records, 'e o meu?').status, 'unsupported');
  assert.deepEqual(searchServices(records, 'socialista'), []);
});
