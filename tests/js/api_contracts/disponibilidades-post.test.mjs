import test from 'node:test';
import { assertClientContract } from './helpers.mjs';

test('cliente declara POST /disponibilidades', () => {
  assertClientContract('POST', '/disponibilidades', 'criar_disponibilidade');
});
