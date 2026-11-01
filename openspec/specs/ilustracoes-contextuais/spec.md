# ilustracoes-contextuais Specification

## Purpose

Definir a identidade visual Sorriso+ com mascotes contextuais transparentes, composição responsiva, marca consistente e navegação com rolagem independente.

## Requirements

### Requirement: Recursos transparentes preservados
O sistema SHALL disponibilizar 16 mascotes tratados com transparência real em assets/mascotes-tratados, preservando os arquivos de origem e sem simular transparência por CSS.

#### Scenario: Carregar ilustração contextual
- **WHEN** uma interface renderiza uma ilustração
- **THEN** ela utiliza o PNG tratado correspondente ao contexto e mantém proporções e acessórios visíveis.

### Requirement: Composição responsiva
O sistema SHALL apresentar banners com fundo verde-menta, ondas, cantos arredondados, texto e personagem integrados, reutilizando um componente comum.

#### Scenario: Desktop
- **WHEN** um banner aparece em resolução desktop
- **THEN** o texto fica à esquerda e a arte à direita, sem sobreposição.

#### Scenario: Celular
- **WHEN** o espaço horizontal é reduzido
- **THEN** a arte passa para baixo do texto, sem rolagem horizontal.

### Requirement: Integração seletiva
O sistema SHALL associar os mascotes às funcionalidades existentes sem criar relatórios ou configurações para justificar uso das imagens.

#### Scenario: Estados da Agenda
- **WHEN** a Agenda está vazia, apresenta erro ou confirma uma operação
- **THEN** a arte contextual acompanha a mensagem funcional existente e os controles continuam operantes.

### Requirement: Marca atual compartilhada
O sistema SHALL usar a assinatura Sorriso+ com o mascote transparente atual no login da equipe, no menu e na área do Paciente, sem carregar a imagem antiga com fundo quadrado.

#### Scenario: Abrir login ou área autenticada
- **WHEN** a marca é apresentada
- **THEN** o mesmo componente de assinatura mostra o mascote atual e o nome da clínica.

### Requirement: Menu fixo com rolagem própria
O sistema SHALL manter o menu preso à janela em desktop, reservando sua largura no layout e permitindo rolagem vertical independente.

#### Scenario: Rolar o conteúdo
- **WHEN** a Visão geral ou a lista de Pacientes é rolada
- **THEN** o menu mantém a posição na janela.

#### Scenario: Rolar o menu
- **WHEN** a altura da janela não comporta todos os itens do menu
- **THEN** o menu permite alcançar os últimos itens com sua própria rolagem, sem alterar a rolagem do conteúdo e sem propagá-la ao chegar ao limite.
