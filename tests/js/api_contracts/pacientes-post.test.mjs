import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /pacientes tem rota e export Xano correspondentes', () => {
  assertApiContract('POST', '/pacientes', 'api/sorriso_acesso/pacientes_POST.xs');
});
