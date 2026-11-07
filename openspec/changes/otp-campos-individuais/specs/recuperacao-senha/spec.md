## MODIFIED Requirements

### Requirement: Entrada visual do OTP

Na etapa de validação, o sistema SHALL apresentar seis campos quadrados individuais, alinhados horizontalmente, para um OTP numérico de seis dígitos.

#### Scenario: Digitação sequencial
- **WHEN** a pessoa informa um dígito válido em um campo
- **THEN** o sistema aceita somente o dígito e move o foco para o próximo campo disponível

#### Scenario: Exclusão com backspace
- **WHEN** a pessoa pressiona Backspace em um campo vazio
- **THEN** o sistema move o foco para o campo anterior para permitir sua exclusão

#### Scenario: Colagem do código completo
- **WHEN** a pessoa cola seis dígitos em qualquer campo
- **THEN** o sistema distribui os dígitos nos seis campos na ordem original

#### Scenario: Validação preservada
- **WHEN** os seis campos estão preenchidos e a pessoa solicita a validação
- **THEN** o frontend concatena os campos sem separadores e envia o código ao endpoint OTP existente

#### Scenario: Responsividade
- **WHEN** a tela é exibida em desktop, tablet ou dispositivo móvel
- **THEN** os seis campos permanecem proporcionais, dentro da largura do formulário, sem rolagem horizontal ou corte

### Requirement: Mensagem de recuperação por e-mail

O sistema SHALL enviar o OTP com uma versão HTML visualmente estruturada, código destacado e imagem da marca, além de uma versão texto simples para clientes que não renderizam HTML. O código, a expiração e as instruções SHALL permanecer coerentes entre as versões.

#### Scenario: Cliente de e-mail com HTML
- **WHEN** o provedor entrega a mensagem a um cliente que renderiza HTML
- **THEN** a pessoa visualiza a identidade Sorriso+, o código em destaque e as orientações de expiração e uso único

#### Scenario: Cliente de e-mail sem HTML
- **WHEN** o cliente de e-mail não renderiza HTML
- **THEN** a pessoa recebe o código e as orientações em texto simples
