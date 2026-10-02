import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara POST /registros-clinicos', () => {
  assertClientContract('POST', '/registros-clinicos', 'registrar_clinico');
});
