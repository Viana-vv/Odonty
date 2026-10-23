## Why

A Visão geral de Administração exibe indicadores genéricos sem refletir a agenda atual da clínica. Um resumo baseado nos contratos REST existentes permite acompanhar o dia e os cadastros ativos sem criar rotas nem expor informações clínicas.

## What Changes

- Substituir os indicadores indisponíveis do painel administrativo por totais de Consultas de hoje, atendimentos realizados, Pacientes ativos e próxima Consulta.
- Exibir até cinco Consultas do dia em ordem de horário, com apenas os dados administrativos necessários.
- Reutilizar `GET /consultas` e `GET /agenda/opcoes`, com mensagens para respostas vazias e falhas.
- Aplicar a referência visual `02-visao-geral.png` e manter os atalhos já funcionais e autorizados.

Fora do escopo: criar ou alterar contratos, endpoints, permissões ou sessão; alterar o painel da Recepção ou do Profissional; incluir informações clínicas ou outros dados de Paciente.

## Capabilities

### New Capabilities

- `interface-painel-administrativo`: resumo administrativo da clínica na Visão geral, derivado de dados dos contratos existentes.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: renderização administrativa em `sorrisomais/paginas_equipe.py` e testes da interface sem rede.
- API: consumo dos métodos existentes `ClienteXano.listar_consultas` e `ClienteXano.listar_opcoes_agenda`; nenhum contrato alterado.
- Xano e sessão: nenhuma alteração.
