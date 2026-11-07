## Decisão

O Streamlit usará um fragmento periódico de 20 segundos. O fragmento será executado apenas com uma Conta de Acesso ativa e fora de chaves de edição conhecidas; antes de solicitar um rerun da aplicação, invalidará o cache GET privado. A autorização continuará sendo validada no Xano a cada chamada.

O mecanismo não cria push ou trigger no Xano: ele usa polling controlado pelo frontend, preservando os endpoints existentes e o botão de atualização manual.
