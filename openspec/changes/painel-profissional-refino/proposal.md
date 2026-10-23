## Por que

O painel do Profissional já consulta as Consultas do dia, mas sua apresentação não acompanha a hierarquia da referência 15 do kit Sorriso Mais e não aproveita o cache diário usado pela Agenda. O refinamento deve melhorar a leitura do dia e manter a mesma autorização, contrato REST e ações já disponíveis.

## O que muda

- Organizar a Visão geral do Profissional com quatro indicadores derivados exclusivamente de `GET /consultas`, uma agenda limitada às cinco próximas linhas visíveis e os atalhos existentes para Agenda e Prontuários.
- Reutilizar a leitura diária em cache por até vinte segundos, sem filtrar ou ampliar no frontend o escopo de Consultas definido pelo Xano.
- Tratar respostas vazias, inválidas, erros de acesso e falhas da API sem expor mensagens técnicas nem conservar dados antigos como atuais.
- Aplicar hierarquia, cartões, lista e comportamento responsivo próximos da referência `15-painel-dentista.png`, preservando os controles funcionais do Streamlit.

Fora do escopo: novos endpoints, alteração do Xano, novas ações de Consulta, novos dados ou métricas que dependam de outra rota, exibição de conteúdo clínico ou mudança em outros perfis.

## Capacidades

### Novas capacidades

- `interface-painel-profissional`: resumo diário do Profissional com Consultas autorizadas, estados seguros e atalhos existentes.

### Capacidades modificadas

Nenhuma.

## Impacto

- Interface Streamlit em `sorrisomais/painel_profissional.py` e estilos compartilhados em `assets/estilos.css`.
- Reutilização da função de cache diária já existente para a Agenda; sem alteração do contrato `GET /consultas` ou da autorização no Xano.
- Testes de interface Python sem rede, com Consultas fictícias; nenhuma dependência ou alteração JavaScript prevista.
