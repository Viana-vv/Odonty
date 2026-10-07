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
  assert.match(source, /inicio_em:.*format_timestamp:"c":"UTC"/);
  assert.match(source, /fim_em:.*format_timestamp:"c":"UTC"/);
  assert.doesNotMatch(source, /conteudo_clinico|telefone|cpf/);
});
