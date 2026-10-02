import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('GET /especialidades tem rota e export Xano correspondentes', () => {
  assertApiContract('GET', '/especialidades', 'api/sorriso_acesso/especialidades_GET.xs');
});
