import test from 'node:test';
import assert from 'node:assert/strict';
import { assertApiContract, assertClientContract } from './helpers.mjs';

test('GET /procedimentos permite equipe administrativa e consulta somente catálogo ativo', () => {
  const source = assertApiContract('GET', '/procedimentos', 'api/sorriso_acesso/procedimentos_GET.xs');
  assertClientContract('GET', '/procedimentos', 'listar_procedimentos');
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /administrador.*recepcionista/);
  assert.match(source, /\$db.procedimento.ativo == true/);
  assert.match(source, /output = \["id", "nome"\]/);
  assert.match(source, /Cache-Control: no-store/);
  assert.match(source, /history = false/);
  assert.doesNotMatch(source, /db.query (paciente|profissional)/);
});
