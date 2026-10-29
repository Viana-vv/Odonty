import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { assertClientContract } from './helpers.mjs';
import { root } from './helpers.mjs';

test('cliente declara GET /consultas', () => {
  assertClientContract('GET', '/consultas', 'listar_consultas');
  const source = readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso/consultas_GET.xs'), 'utf8');
  assert.match(source, /paciente_nome/);
  assert.match(source, /profissional_nome/);
  assert.match(source, /procedimento_vinculado_nome/);
  assert.doesNotMatch(source, /eval\s*=\s*\{[^}]*format_timestamp/s);
  assert.match(source, /var \$inicio_iso \{ value = \$consulta\.inicio_em\|format_timestamp:"c":"UTC" \}/);
  assert.match(source, /var \$fim_iso \{ value = \$consulta\.fim_em\|format_timestamp:"c":"UTC" \}/);
  assert.match(source, /db\.query consulta \{/);
  assert.match(source, /db\.get paciente \{/);
  assert.match(source, /db\.get profissional \{/);
  const pacienteBranchStart = source.indexOf('if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {', source.indexOf('var $fim_iso'));
  const pacienteBranchEnd = source.indexOf('\n          else {', pacienteBranchStart);
  assert.notEqual(pacienteBranchStart, -1, 'deve existir um ramo próprio para o perfil Paciente');
  assert.notEqual(pacienteBranchEnd, -1);
  const pacienteBranch = source.slice(pacienteBranchStart, pacienteBranchEnd);
  assert.match(pacienteBranch, /profissional_nome:/);
  assert.doesNotMatch(pacienteBranch, /procedimento|disponibilidade_id|paciente_nome|telefone|cpf|conteudo_clinico/i);
  assert.match(source, /procedimento_vinculado_nome/); // resposta completa da equipe permanece
  const consultaBase = source.match(/db\.query consulta \{([\s\S]*?)\} as \$consultas/)[1];
  assert.doesNotMatch(consultaBase, /\bwhere\s*=/);
  assert.match(source, /if \(\$incluir_consulta\)/);
  assert.doesNotMatch(source, /conteudo_clinico|telefone|cpf/);
});
