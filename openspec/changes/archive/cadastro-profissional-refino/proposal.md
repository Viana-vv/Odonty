## Por quê

O modal administrativo de cadastro de Profissional está funcional, mas sua hierarquia e distribuição dos campos não acompanham a referência visual aprovada 10 do kit Sorriso Mais. O refinamento melhora leitura e uso em telas amplas e estreitas sem alterar o cadastro existente.

## O que muda

- Reorganizar visualmente o formulário no modal existente, aproximando-o da referência 10.
- Destacar o nome em largura total, agrupar campos em colunas em telas amplas e manter ações no rodapé.
- Adaptar modal e campos para rolagem e coluna única em telas estreitas.
- Preservar validações, estados, mensagens, autorização e chamadas REST atuais.

## O que não muda

- Não alterar os endpoints existentes `GET /especialidades` e `POST /profissionais` nem seus contratos.
- Não alterar regras de autorização ou criação: o Xano continua validando Administrador e criando Profissional e Conta de Acesso atomicamente no POST atual.
- Não criar listagem ou gestão de Profissionais, nem alterar outras páginas.

## Capacidade

### Capacidades modificadas
- `cadastro-profissional`: aprimorar apresentação responsiva do modal sem mudança do comportamento funcional.

## Impacto

- Interface em `sorrisomais/paginas_equipe.py` e estilos compartilhados em `assets/estilos.css`.
- Referência visual: `sorriso-mais-kit-recriacao/sorriso-mais-kit-recriacao/referencias-telas/10-novo-profissional.png` (fora desta cópia de trabalho).
- Testes de interface existentes; contratos da API permanecem inalterados.
