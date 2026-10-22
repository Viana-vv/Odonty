import test from 'node:test';
import assert from 'node:assert/strict';
import { assertApiContract, root } from './helpers.mjs';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

test('cliente declara GET /registros-clinicos', () => {
  assertApiContract('GET', '/registros-clinicos', 'api/sorriso_acesso/registros_clinicos_GET.xs');
});

test('GET /registros-clinicos restringe as consultas ao escopo autenticado no Xano', () => {
  const xano = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs'), 'utf8');
  assert.match(xano, /auth = "conta_acesso"/);
  assert.match(xano, /function\.run sorriso_validar_sessao/);
  assert.match(xano, /where = \$db\.registro_clinico\.profissional_id == \$profissional_escopo/);
  assert.match(xano, /where = \$db\.registro_clinico\.paciente_id == \$paciente_escopo && \$db\.registro_clinico\.liberado_paciente == true/);
  assert.match(xano, /\$registro\.paciente_id != \$input\.paciente_id/);
  assert.match(xano, /\$registro\.consulta_id != \$input\.consulta_id/);
  assert.doesNotMatch(xano, /where = [^\r\n]*== null \|\|/);
  assert.match(xano, /history = false/);
});
