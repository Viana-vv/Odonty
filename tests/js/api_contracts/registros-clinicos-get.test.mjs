import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract, assertClientContract, root } from './helpers.mjs';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

test('cliente declara GET /registros-clinicos', () => {
  assertClientContract('GET', '/registros-clinicos', 'listar_registros_clinicos');
  const source = assertApiContract('GET', '/registros-clinicos', 'api/sorriso_acesso/registros_clinicos_GET.xs');
  assert.match(source, /field_name = "conta_acesso_id"/);
  assert.match(source, /field_value = \$auth\.id/);
  assert.match(source, /\$db\.registro_clinico\.liberado_paciente == true/);
  assert.match(source, /auth = "conta_acesso"/);
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

test('GET /registros-clinicos retorna retificações vinculadas aos itens autorizados', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs'), 'utf8');
  assert.match(source, /db\.query registro_clinico_retificacao/);
  assert.match(source, /registro_clinico_id == \$registro\.id/);
  assert.match(source, /retificacoes: \$retificacoes/);
  assert.match(source, /justificativa/);
  assert.match(source, /criada_em/);
});

test('GET /registros-clinicos não consulta retificações para paciente sem liberação', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs'), 'utf8');
  const guarda = /\(\$solicitante\.perfis\|intersect:\["paciente"\]\|count\) == 0 \|\| \$registro\.liberado_paciente == true/;
  assert.match(source, guarda);
  assert.ok(source.indexOf('if (($solicitante.perfis|intersect:["paciente"]|count) == 0') < source.indexOf('db.query registro_clinico_retificacao'));
  assert.match(source, /var \$retificacoes \{ value = \[\] \}/);
});
