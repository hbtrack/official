# START HERE: HB Track Documentação Canônica

## O que é este repositório?

**HB Track** é um sistema de gestão técnica para handebol: controle de atletas, treinamentos, competições, saúde e análise de desempenho.

**Esta camada canônica** é a porta única de entrada. Todas respostas técnicas devem referenciar: (a) um doc aqui ou em paths relacionados, e (b) evidência (código, `schema.sql`, `openapi.json`, `parity_report.json`, ADR).

---

## 6 Perguntas Fundamentais

1. **O que governa as decisões neste projeto?**  
   → Leia: [01_AUTHORITY_SSOT.md](C:/HB TRACK/docs/_canon/01_AUTHORITY_SSOT.md)  
   → Evidência: [001-ADR-TRAIN-ssot-precedencia.md](C:/HB TRACK/docs/ADR/001-ADR-TRAIN-ssot-precedencia.md)

2. **Quero fazer X, por onde começo?**  
   → Leia: [02_CONTEXT_MAP.md](C:/HB TRACK/docs/_canon/02_CONTEXT_MAP.md)  
   → Encontre sua intenção e siga o fluxo recomendado

3. **Qual é o passo-a-passo para tarefa Y?**  
   → Leia: [03_WORKFLOWS.md](C:/HB TRACK/docs/_canon/03_WORKFLOWS.md)  
   → Workflows operacionais com checklists

4. **Quais são as restrições, constraints e invariantes do sistema?**  
   → Leia: [INVARIANTS_TRAINING](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)  
   → Evidência: `schema.sql`, ADRs em [arquitetura](C:/HB TRACK/docs/ADR/)

5. **Como estão os arquivos gerados (schema, API, reports)?**  
   → Leia: [04_SOURCES_GENERATED.md](C:/HB TRACK/docs/_canon/04_SOURCES_GENERATED.md)  
   → Evidência: [gerados](C:/HB TRACK/docs/_generated/)

6. **Qual protocolo devo seguir para adicionar features/fixes?**  
   → Leia: [INVARIANTS_AGENT_PROTOCOL.md](C:/HB TRACK/docs/_ai/INVARIANTS_AGENT_PROTOCOL.md)  
   → Referência: [EXEC_TASK_ADR_MODELS_001.md](C:/HB TRACK/docs/execution_tasks/EXEC_TASK_ADR_MODELS_001.md)

---

## Regra de Ouro

> Qualquer resposta técnica deve citar:  
> **(a) um documento canônico** (este ou referências),  
> **(b) uma evidência** (código, schema.sql, openapi.json, parity_report.json ou ADR).

---

## Mapa Rápido de Pastas

```
docs/
  _canon/          ← Você está aqui (camada de entrada)
  _ai/             ← Protocolos de agentes, guardrails
  _generated/      ← Outputs de tools (schema.sql, openapi.json, etc)
  ADR/             ← Decisões arquiteturais (001-013)
  execution_tasks/ ← EXEC_TASK para workflows
  references/      ← exit_codes.md, model_requirements_guide.md
  02_modulos/      ← Modelos e invariantes por domínio
  00_product/      ← PRD e documentação de produto
```

---

## Próximos Passos Recomendados

1. Se é sua **primeira vez**, leia [02_CONTEXT_MAP.md](C:/HB TRACK/docs/_canon/02_CONTEXT_MAP.md) para entender fluxos
2. Se precisa **fazer algo imediatamente**, vá direto para [03_WORKFLOWS.md](C:/HB TRACK/docs/_canon/03_WORKFLOWS.md)
3. Se tem dúvida sobre **o quê confiar**, consulte [01_AUTHORITY_SSOT.md](C:/HB TRACK/docs/_canon/01_AUTHORITY_SSOT.md)
4. Se precisa **entender uma decisão**, busque no [_INDEX_ADR.md](C:/HB TRACK/docs/ADR/_INDEX_ADR.md)

---

*Última atualização: 2026*
