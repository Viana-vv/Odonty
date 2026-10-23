import test from 'node:test';
import assert from 'node:assert/strict';
import { assertApiContract } from './helpers.mjs';

test('GET /profissionais possui rota e export administrativo protegido', () => {
  const source = assertApiContract('GET', '/profissionais', 'api/sorriso_acesso/profissionais_GET.xs');
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /administrador.*recepcionista/);
  assert.match(source, /especialidade_id/);
  assert.doesNotMatch(source, /conta_acesso_id|cpf|conteudo_clinico/);
});
