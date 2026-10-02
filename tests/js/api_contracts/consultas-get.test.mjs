import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara GET /consultas', () => {
  assertClientContract('GET', '/consultas', 'listar_consultas');
});
