## Why

O Prontuário da `main` funciona apenas como uma linha do tempo de Registros Clínicos em texto livre. Ele não apresenta os dados cadastrais do Paciente nem organiza Anamnese, Histórico Odontológico, Exame Clínico, Diagnósticos, Plano de Tratamento, Procedimentos, Exames, Prescrições, Evolução e Documentos em uma visão clínica coerente.

## What Changes

- Criar um contrato agregado e autorizado para consultar o Prontuário completo de um Paciente.
- Incluir no resumo os dados cadastrais autorizados: nome, CPF, nascimento, telefone e endereço quando disponível.
- Criar seções clínicas estruturadas e versionadas para Anamnese, Histórico Odontológico, Exame Clínico, Diagnósticos, Plano de Tratamento, Prescrições e Documentos.
- Integrar no agregado os Procedimentos realizados, Exames e Evoluções já existentes.
- Adicionar suporte estruturado ao Odontograma, sem simular dados ausentes.
- Permitir que Profissional autorizado registre e consulte dados clínicos no próprio escopo; Paciente consulta somente dados liberados; perfis administrativos não recebem conteúdo clínico.
- Exibir estados vazios e falhas por seção sem inventar conteúdo.
- Corrigir a exibição de Pacientes que possuem Prontuário, mas ainda não possuem Consulta ou Registro Clínico.
- Preservar versões, retificações e histórico sem exclusão física.

## Capabilities

### New Capabilities

- `prontuario-completo`: agregado autorizado e seções estruturadas do Prontuário.

### Modified Capabilities

- `interface-prontuario`: substituir a visão somente de Registros Clínicos por uma visão completa, com estados por seção.
- `registro-clinico`: manter compatibilidade com registros textuais históricos e integrar Evolução Clínica estruturada.

## Impact

- Tabelas e endpoints Xano para dados do Prontuário e suas seções.
- Cliente REST Python e tela Streamlit do Prontuário.
- Integração com Pacientes, Consultas, Procedimentos e Exames.
- Testes Python, contratos de API em Python/JavaScript e documentação do domínio.
- Não serão usados dados reais, URLs públicas de arquivos ou conteúdo clínico em logs.
