import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara GET /registros-clinicos', () => {
  assertClientContract('GET', '/registros-clinicos', 'listar_registros_clinicos');
});
