## Context

O Prontuário atual é composto por `prontuario_paciente` e Registros Clínicos textuais. A tela deriva os Pacientes de `GET /consultas` e `GET /registros-clinicos`, por isso omite um Paciente sem atendimento ou evolução. Os dados cadastrais existem parcialmente na tabela de Pacientes, enquanto endereço, seções clínicas estruturadas, prescrições, documentos e odontograma ainda não têm contrato.

## Goals / Non-Goals

**Goals:**

- Expor uma leitura agregada autorizada por Paciente.
- Organizar todas as seções solicitadas com dados reais ou estado vazio.
- Reutilizar Procedimentos, Exames e Registros Clínicos existentes sem duplicar fontes.
- Garantir autorização no Xano, visibilidade por perfil e histórico versionado.
- Permitir evolução incremental dos registros legados textuais.

**Non-Goals:**

- Diagnóstico automático, inteligência artificial ou integração externa.
- Uso de dados clínicos reais.
- URLs públicas permanentes para imagens/documentos.
- Acesso clínico para Recepcionista ou Administrador por padrão.

## Decisions

1. **Endpoint agregado por Paciente.** O Xano fornecerá `GET /prontuarios/{paciente_id}` como entrada principal da tela. A resposta terá `paciente`, `prontuario`, `anamnese`, `historico_odontologico`, `odontograma`, `exame_clinico`, `diagnosticos`, `plano_tratamento`, `procedimentos`, `exames`, `prescricoes`, `evolucoes` e `documentos`. Cada coleção vazia será válida.

2. **Seções clínicas em entidades próprias.** Os dados estruturados serão armazenados em tabela de seção/versionamento, com tipo de seção, conteúdo validado, Paciente/Prontuário, Consulta opcional, Profissional, liberação e data. O contrato separará as seções na resposta, preservando histórico sem sobrescrever versões anteriores.

3. **Arquivos protegidos.** Documentos e imagens serão representados por metadados e referência privada. A listagem não retornará URL pública; downloads, quando implementados, exigirão autenticação e escopo.

4. **Autorização por perfil.** Profissional ativo acessará apenas Pacientes no escopo de atendimento; Paciente somente o próprio conteúdo liberado; Administrador e Recepcionista não receberão conteúdo clínico. O frontend não será mecanismo de segurança.

5. **Compatibilidade legada.** Registros textuais já existentes continuarão aparecendo na seção Evolução Clínica. Novos registros poderão preencher campos estruturados, sem apagar o campo legado.

6. **Odontograma sem conteúdo fabricado.** A interface exibirá a representação dos dentes apenas quando o Xano devolver itens. Sem itens, mostrará estado vazio; não haverá dentes, diagnósticos ou marcações inventados.

## Risks / Trade-offs

- [Escopo amplo] → dividir o código por tabelas, APIs, cliente, tela e testes, mantendo uma única change e integração final.
- [Resposta agregada conter dados demais] → aplicar projeção no Xano por perfil e retornar somente campos autorizados.
- [Dados legados não estruturados] → exibir em Evolução Clínica e não tentar inferir diagnósticos, alergias ou odontograma a partir de texto.
- [Arquivos clínicos] → armazenar somente referência privada e testar sem arquivos reais.
- [Sintaxe Xano variar entre ambientes] → validar export, contratos estáticos e fluxos sem rede antes de qualquer integração externa.
