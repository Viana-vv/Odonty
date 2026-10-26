## Why

O objetivo do projeto inclui registrar Exames relacionados ao acompanhamento de Pacientes, mas a instância Xano versionada não possui tabela, endpoints REST ou tela para essa capacidade. Sem esse fluxo, Profissionais não conseguem registrar solicitações e resultados e Pacientes não conseguem consultar resultados liberados.

## What Changes

- Criar no Xano a entidade Exame com vínculo ao Paciente, vínculo opcional à Consulta, Profissional solicitante, tipo, datas, resultado, observações e situação prevista no modelo de domínio.
- Criar rotas REST autenticadas para solicitar, listar conforme o escopo do Profissional ou do próprio Paciente e avançar a situação até resultado disponível.
- Criar uma tela Streamlit responsiva para Profissionais registrarem Exames e para Pacientes consultarem somente os próprios Exames com resultado disponível.
- Preservar histórico e validar no Xano autorização, vínculo Paciente–Consulta–Profissional e ordem temporal das situações.
- Não incluir anexos nesta change. O plano gratuito atual não oferece armazenamento privado de arquivos; não será gravado arquivo nem emitido URL pública. A referência de arquivo permanece sem valor.

Fora do escopo: upload/visualização de arquivos, edição ou exclusão de Exames com resultado disponível, novas modalidades de armazenamento e acesso administrativo a resultados clínicos.

## Capabilities

### New Capabilities

- `exames`: solicitação, acompanhamento e consulta autorizada de Exames vinculados ao Paciente e opcionalmente à Consulta.

### Modified Capabilities

Nenhuma.

## Impact

- Xano: nova tabela e endpoints REST versionados com autorização por perfil e relacionamento clínico.
- Streamlit: novo módulo de tela, integrado à navegação pelo principal depois da implementação isolada.
- Testes: contratos REST isolados em Python e JavaScript, sem rede nos testes unitários; integração real somente em ambiente Xano temporário.
- Referência visual: composição mais próxima de Prontuário individual e Nova evolução do kit Sorriso Mais.
- Segurança: nenhum arquivo clínico ou link público será armazenado ou retornado.
