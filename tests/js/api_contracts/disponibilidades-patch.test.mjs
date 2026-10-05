import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara PATCH /disponibilidades/{id}', () => {
  assertClientContract('PATCH', '/disponibilidades/{disponibilidade_id}', 'atualizar_disponibilidade');
});
