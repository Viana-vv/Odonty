import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract, assertClientContract } from './helpers.mjs';

test('cliente declara GET /registros-clinicos', () => {
  assertClientContract('GET', '/registros-clinicos', 'listar_registros_clinicos');
  const source = assertApiContract(
    'GET', '/registros-clinicos', 'api/sorriso_acesso/registros_clinicos_GET.xs',
  );
  assert.match(source, /field_name = "conta_acesso_id"/);
  assert.match(source, /field_value = \$auth\.id/);
  assert.match(source, /\$db\.registro_clinico\.liberado_paciente == true/);
  assert.match(source, /auth = "conta_acesso"/);
});
