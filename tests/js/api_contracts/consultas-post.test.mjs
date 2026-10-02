import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara POST /consultas', () => {
  assertClientContract('POST', '/consultas', 'agendar_consulta');
});
