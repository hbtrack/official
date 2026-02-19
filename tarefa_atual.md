Nível,Path Correto,Requisito do Contrato
Root,_reports/,Root único e inegociável para auditoria e casos.
Auditoria,_reports/audit/<RUN_ID>/,Localização de execução de cada ciclo de gates.
Metadados,_reports/audit/<RUN_ID>/summary.json,Arquivo obrigatório de consolidação do status global.
Contexto,_reports/audit/<RUN_ID>/context.json,Arquivo obrigatório com Git Hash e variáveis de ambiente.
Gates,_reports/audit/<RUN_ID>/checks/<GATE_ID>/,Pasta individual para cada teste executado.

Falta de result.json:No contrato, cada gate MUST produzir um result.json individual.

Sincronia de Governança: O script check_audit_pack.py foi desenhado para validar a estrutura em _reports/. Se os dados estiverem em outro local, o Arquiteto emitirá um Exit 4 (BLOCKED_INPUT) por não encontrar as provas físicas.

**MUST** ATUALIZAR `_reports/audit/CORRECTIVE_ACTION_v2.0.md`, o documento de referência histórica de governança.

Backups temporários dentro da pasta de audit violam a limpeza do Evidence Pack.

Manual Canónico v1.0, seção 2.1 afirma categoricamente: "Root canônico: _reports/". Não existe menção a docs/_generated/ como repositório de evidências.

O uso do Python 3.14.2 é uma violação de segurança e estabilidade. copilot-instructions.md v1.2, Seção 1 define "Runtime: Python 3.8" como Hard Rule.