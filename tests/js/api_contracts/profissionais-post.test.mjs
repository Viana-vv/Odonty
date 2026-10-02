import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /profissionais tem rota e export Xano correspondentes', () => {
  assertApiContract('POST', '/profissionais', 'api/sorriso_acesso/profissionais_POST.xs');
});
