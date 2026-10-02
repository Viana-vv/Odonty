import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara GET /disponibilidades', () => {
  assertClientContract('GET', '/disponibilidades', 'listar_disponibilidades');
});
