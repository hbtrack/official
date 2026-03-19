# HB Track — Perfis de Usuário e Modelo de Permissões
> Fonte: `_archive/chat.md` (seção 3) | Versão: 1.0.0 | 2026-03-18
> SSOT para decisões de `identity_access`, `permissions` e RBAC de qualquer módulo.

---

## Modelo de autorização

**Fórmula:** `permissão = papel + ação + recurso + escopo + contexto`

Não basta "ser treinador" — é preciso definir:
- treinador de qual equipe, em qual temporada, com quais módulos habilitados
- com qual nível de escrita, leitura, exportação e compartilhamento

**Implementação em 4 níveis:**
1. **Role catalog** — catálogo fixo de perfis base do produto
2. **Permission bundles** — pacotes de permissão por módulo e ação
3. **Scope binding** — vínculo com equipe, competição, categoria, atleta, temporada
4. **Policy engine** — regras ABAC para dados sensíveis e contexto de acesso

---

## Ações padronizadas

`visualizar | criar | editar | excluir | homologar | publicar | exportar | compartilhar | aprovar | administrar`

---

## Classificação de sensibilidade de dados

| Nível | Tipo | Exemplos |
|---|---|---|
| 1 — Público | Estatísticas oficiais, calendário público, rankings divulgáveis | Live stats publicados, tabela de classificação |
| 2 — Interno operacional | Treinos, vídeo interno, relatórios técnicos, workflows de staff | Sessão de treino, playlist interna |
| 3 — Competitivo confidencial | Scouting de adversário, relatórios estratégicos, avaliações individuais | Dossiê pré-jogo, análise tática interna |
| 4 — Sensível pessoal | Dados biométricos, wellness, tracking individual, histórico funcional | Carga aguda, wellness diário |
| 5 — Sensível regulado | Diagnóstico médico, documentos clínicos, exames, dados com exigência legal | Laudo médico, prontuário clínico |

**Cada nível impõe:** autenticação, autorização, criptografia, mascaramento, auditoria e exportação progressivamente mais restritos.

---

## Os 20 perfis canônicos

### Grupo 1 — Plataforma

**Super Admin** (interno HB Track)
- Gerencia tenants, módulos, contratos e licenças. Observabilidade global.
- ⚠️ Não acessa por padrão: dados médicos, vídeo privado, relatórios estratégicos de cliente.
- Regra: acesso a conteúdo sensível de cliente deve ser just-in-time, auditado e aprovado.

**Tenant Admin** (clube / federação / liga)
- Cria usuários, atribui perfis, configura equipes/temporadas/branding.
- ⚠️ Não altera registros médicos clínicos. Não homologa dados oficiais (salvo duplo perfil).

---

### Grupo 2 — Gestão executiva

**Diretor Executivo / C-Level**
- Dashboards estratégicos consolidados, KPIs, comparativos de temporada.
- Acesso predominantemente leitura. Não vê prontuário médico nem scouting sigiloso.

**Diretor Esportivo**
- Evolução do elenco, scouting interno/externo, benchmarking, recrutamento.
- Acesso médico: visão resumida e funcional apenas (não clínica detalhada).

---

### Grupo 3 — Comissão técnica

**Head Coach / Treinador Principal**
- Jogos, treinos, vídeos, relatórios, microciclos, match center, disponibilidade esportiva.
- Vê: "atleta apto / restrito / indisponível + motivo funcional".
- ⚠️ Não vê diagnóstico médico sensível nem informação contratual sigilosa.

**Assistant Coach / Auxiliar Técnico**
- Revisão de vídeo, scouting, planejamento colaborativo. Escopo menor que Head Coach.
- Não aprova relatórios finais. Não altera configurações críticas.

**Analista de Desempenho**
- Templates de scouting, tagging ao vivo, tracking, dashboards técnicos, relatórios pós-jogo, dossiês.
- Permissão alta no domínio analítico; não no administrativo.

**Analista de Vídeo**
- Ingestão, tagging, clipping, playlists, catálogo audiovisual.
- Acesso parcial a métricas (somente para contextualizar).

**Scout**
- Padrões do adversário, opponent intelligence, tendências individuais/coletivas.
- ⚠️ Não acessa dados médicos do próprio elenco nem planejamento interno.

---

### Grupo 4 — Performance e saúde

**Preparador Físico**
- Carga aguda/crônica, prontidão, fadiga, retorno progressivo, alertas de sobrecarga.
- Acesso: tracking detalhado + readiness + restrições esportivas.
- ⚠️ Não vê prontuário clínico completo.

**Fisiologista / Performance Scientist**
- Modelagem de carga, benchmarks, zonas/limiares, prevenção de lesão.
- Datasets avançados de tracking e readiness. Em orgs menores: papel unificado com preparador.

**Fisioterapeuta**
- Evolução de recuperação, restrições, protocolos de retorno, intervenções.
- Dados clínico-funcionais + tracking de reabilitação + vídeos de recuperação.
- ⚠️ Não divulga dados médicos a perfis não autorizados.

**Médico**
- Diagnósticos, aptidão médica, restrições, exames, histórico clínico, liberação/veto.
- Nível máximo de acesso médico no seu escopo.
- ⚠️ Todo acesso médico: fortemente auditado com trilha completa.

**Nutricionista**
- Planos alimentares esportivos, indicadores de performance, restrições alimentares.
- Acesso restrito a informações físicas e de rotina necessárias ao seu domínio.

---

### Grupo 5 — Desenvolvimento e base

**Coordenador de Base**
- Categorias inferiores, evolução longitudinal, transição para categorias superiores.
- Sem acesso ao profissional (salvo delegação). Sem acesso médico detalhado.

---

### Grupo 6 — Atleta e operação de jogo

**Atleta**
- Próprio portal: agenda, clipes compartilhados, indicadores pessoais liberados, wellness, metas.
- ⚠️ Acessa apenas seus dados. Não vê dados de colegas nem scouting confidencial.

**Operador de Jogo / Staff de Mesa**
- Registro de eventos ao vivo, validação de cronologia, match center, súmulas.
- Interface rápida com permissões estreitas e focadas na operação do evento.

---

### Grupo 7 — Competição e institucional

**Árbitro / Delegado / Oficial de Competição**
- Dados oficiais da partida, homologação, documentos e evidências do jogo.
- ⚠️ Não acessa inteligência interna do clube, dados médicos nem material privado.

**Federação / Liga Admin**
- Competições, fases, regras, homologação, live stats oficiais, distribuição de dados oficiais.
- Acessa dados agregados e oficiais sob sua governança.
- ⚠️ Não acessa medicina interna de clubes nem relatórios estratégicos privados.

---

### Grupo 8 — Mídia e parceiros externos

**Operador de Mídia / Broadcast**
- Feed de live stats, widgets, overlays, assets autorizados, highlights publicáveis.
- Apenas dados liberados para mídia e vídeos marcados como publicáveis.

**Jornalista / Parceiro Externo**
- Portal público: estatísticas oficiais, calendário, rankings, clips públicos.
- Nenhum acesso a conteúdo interno ou sensível.

**Gestor Comercial / Patrocinador**
- Painéis de audiência, uso de mídia, métricas de ativação.
- Sempre agregado; sem conteúdo competitivo sensível.

---

## Matriz resumida por macrodomínio

| Perfil | Op. esportiva | Vídeo | Analytics | Perf. física | Médico | Competição | Mídia | Admin |
|---|---|---|---|---|---|---|---|---|
| Super Admin | limitado/auditado | limitado | limitado | limitado | muito restrito | limitado | limitado | total plataforma |
| Tenant Admin | médio | baixo | médio | baixo | nenhum padrão | médio | baixo | alto tenant |
| Diretor Executivo | leitura | baixo | alto executivo | resumo | resumo | baixo | baixo | baixo |
| Diretor Esportivo | alto | médio | alto | resumo | resumo funcional | baixo | baixo | médio |
| Head Coach | alto | alto | alto | médio funcional | restrito | baixo | baixo | baixo |
| Auxiliar Técnico | alto | alto | médio | médio | restrito | baixo | baixo | baixo |
| Analista de Desempenho | alto | alto | muito alto | médio | restrito | baixo | baixo | baixo |
| Analista de Vídeo | médio | total escopo | baixo | nenhum | nenhum | nenhum | nenhum | nenhum |
| Scout | médio | médio adversário | médio comparativo | nenhum | nenhum | nenhum | nenhum | nenhum |
| Preparador Físico | médio | baixo | alto físico | muito alto | baixo | baixo | baixo | baixo |
| Fisiologista | médio | baixo | alto físico | muito alto | médio | nenhum | nenhum | nenhum |
| Fisioterapeuta | médio | médio reab. | médio reab. | alto | alto funcional | baixo | baixo | baixo |
| Médico | médio | baixo | médio clínico | médio | muito alto | baixo | baixo | baixo |
| Nutricionista | baixo | nenhum | baixo | médio | baixo | nenhum | nenhum | nenhum |
| Coord. de Base | médio base | médio base | médio base | médio base | nenhum | nenhum | nenhum | baixo |
| Atleta | próprio | próprio | próprio | próprio resumido | próprio resumido | nenhum | nenhum | nenhum |
| Operador de Jogo | baixo operacional | nenhum | nenhum | nenhum | nenhum | médio oficial | nenhum | nenhum |
| Árbitro / Oficial | nenhum | nenhum | nenhum | nenhum | nenhum | alto oficial | nenhum | nenhum |
| Federação / Liga Admin | médio oficial | baixo | alto oficial | nenhum | nenhum | muito alto | médio | alto institucional |
| Operador de Mídia | nenhum | médio publicável | médio público | nenhum | nenhum | médio oficial | alto | nenhum |
| Jornalista / Externo | nenhum | nenhum | público | nenhum | nenhum | público | público | nenhum |

---

## Políticas ABAC obrigatórias

Estas regras devem existir no policy engine desde o início:

- Médico acessa registro médico somente se vinculado ao atleta ou equipe
- Treinador vê restrição funcional, nunca laudo clínico
- Atleta acessa apenas relatórios explicitamente compartilhados com ele
- Mídia consome apenas estatística homologada e publicada
- Exportação de dados biométricos exige política específica habilitada
- Acesso fora de horário/país pode exigir step-up authentication
- Ações de homologação oficial exigem dupla confirmação
- Acesso de suporte do fornecedor deve expirar automaticamente

---

## Exemplo técnico de perfil completo

```yaml
role: HEAD_COACH
permissions:
  - view_match
  - edit_training_plan
  - view_video
  - view_team_readiness
scope:
  club: "A"
  team: "adulto_masculino"
  season: "2026"
policies:
  - deny: medical_diagnosis_details
  - allow: athlete_status_functional_summary
```

---

## Referência completa

Documento de origem: [`_archive/chat.md`](../../_archive/chat.md) (seção 3)
Módulo responsável: `identity_access` (MODULE_REGISTRY.yaml)
