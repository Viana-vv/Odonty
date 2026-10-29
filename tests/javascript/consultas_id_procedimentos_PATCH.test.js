const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const arquivo = path.resolve(__dirname, '../../backend/xano/api/sorriso_acesso/consultas_id_procedimentos_consulta_procedimento_id_realizacao_PATCH.xs');
const fonte = fs.readFileSync(arquivo, 'utf8');

test('PATCH permite somente a transição planejado para realizado', () => {
  assert.match(fonte, /verb=PATCH/);
  assert.match(fonte, /auth = "conta_acesso"/);
  assert.match(fonte, /function\.run sorriso_validar_sessao/);
  assert.match(fonte, /situacao != "planejado"/);
  assert.match(fonte, /situacao: "realizado"/);
  assert.match(fonte, /realizado_por_profissional_id: \$profissional_autenticado\.id/);
  assert.match(fonte, /realizado_em: now/);
});

test('PATCH preserva os valores de planejamento', () => {
  const edicao = fonte.match(/db\.edit consulta_procedimento\s*\{[\s\S]*?\n\s*\}/)?.[0] ?? '';
  assert.match(edicao, /situacao: "realizado"/);
  assert.match(edicao, /realizado_por_profissional_id/);
  assert.match(edicao, /realizado_em/);
  assert.doesNotMatch(edicao, /(?:^|[\s,{])profissional_id:/);
  assert.doesNotMatch(edicao, /(?:^|[\s,{])criado_em:/);
});
