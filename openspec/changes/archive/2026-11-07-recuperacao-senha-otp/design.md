# Design

O Streamlit mantém apenas a etapa, o identificador opaco da operação e o e-mail durante o fluxo. OTP, senha e confirmação não são persistidos após o processamento.

O Xano usa `recuperacao_senha` para controlar prazo, tentativas, validação e uso. A solicitação responde de forma neutra e envia o OTP pelo endpoint SendGrid configurado no ambiente. A troca atualiza o campo `password` da Conta de Acesso e invalida a operação.
