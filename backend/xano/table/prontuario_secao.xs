// Seções clínicas versionadas do Prontuário. Nunca excluir ou sobrescrever versões.
table prontuario_secao {
  auth = false
  schema {
    int id
    int prontuario_id {
      table = "prontuario_paciente"
    }
    int paciente_id {
      table = "paciente"
    }
    int profissional_id {
      table = "profissional"
    }
    int? consulta_id? {
      table = "consulta"
    }
    int? secao_original_id? {
      table = "prontuario_secao"
    }
    enum tipo {
      values = [
        "Anamnese"
        "Histórico Odontológico"
        "Exame Clínico"
        "Diagnóstico"
        "Plano de Tratamento"
        "Odontograma"
        "Prescrição"
        "Documento"
      ]
    }
    text conteudo
    text? justificativa_retificacao?
    bool liberado_paciente?=false
    bool concluido?=true
    int versao?=1
    timestamp criado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "prontuario_id", op: "asc"}, {name: "tipo", op: "asc"}, {name: "versao", op: "desc"}]}
    {type: "btree", field: [{name: "paciente_id", op: "asc"}, {name: "profissional_id", op: "asc"}]}
    {type: "btree", field: [{name: "secao_original_id", op: "asc"}, {name: "versao", op: "asc"}]}
  ]
}
