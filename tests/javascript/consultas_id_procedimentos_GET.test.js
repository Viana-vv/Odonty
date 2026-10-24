const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const arquivo = path.resolve(__dirname, '../../backend/xano/api/sorriso_acesso/consultas_id_procedimentos_GET.xs');
const fonte = fs.readFileSync(arquivo, 'utf8');

test('GET lista itens da Consulta autenticada com dados de situação e planejamento', () => {
  assert.match(fonte, /query "consultas\/{id}\/procedimentos" verb=GET/);
  assert.match(fonte, /auth = "conta_acesso"/);
  assert.match(fonte, /function\.run sorriso_validar_sessao/);
  assert.match(fonte, /profissional_autenticado\.id/);
  assert.match(fonte, /situacao.*realizado_por_profissional_id.*realizado_em/);
  assert.match(fonte, /profissional_planejamento_nome/);
  assert.match(fonte, /criado_em/);
});

test('GET não apresenta Consulta fora do escopo', () => {
  assert.match(fonte, /consulta\.profissional_id != \$profissional_autenticado\.id/);
  assert.match(fonte, /HTTP\/1\.1 404 Not Found/);
});
