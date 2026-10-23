import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract } from './helpers.mjs';
import { root } from './helpers.mjs';

test('cliente declara POST /registros-clinicos', () => {
  assertClientContract('POST', '/registros-clinicos', 'registrar_clinico');
});

test('POST /registros-clinicos restringe Paciente ao escopo do Profissional no Xano', () => {
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/registros_clinicos_POST.xs'), 'utf8');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /function\.run sorriso_validar_sessao/);
  assert.match(source, /db\.query consulta \{[\s\S]*?\$db\.consulta\.paciente_id == \$paciente\.id && \$db\.consulta\.profissional_id == \$profissional\.id/);
  assert.match(source, /if \(\$consulta_escopo == null\)/);
});
