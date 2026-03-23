# HB Track — Modelo de Identidade, Autorização e RBAC
> Fonte: `_archive/gaps.md` (análise arquitetural de identidade) | Versão: 1.0.0 | 2026-03-19
> Documento de apoio humano, não canônico e não soberano. Serve para estudo e ideação; não substitui `docs/_canon/` nem `docs/hbtrack/modulos/identity_access/`.

---

## Regra de uso

Este documento resume hipóteses e modelos úteis para evolução de identidade e autorização.
Qualquer implementação de permissão, role, bundle ou política de acesso deve se ancorar
nos artefatos canônicos ativos do módulo `identity_access` e nas ADRs aprovadas.

Referência canônica atual: `docs/_canon/SYSTEM_SCOPE.md §4`, `docs/_canon/decisions/ADR-008-authz-strategy.md` e `docs/hbtrack/modulos/identity_access/PERMISSIONS_IDENTITY_ACCESS.md`.

---

## Modelo arquitetural

```
Canonical Actor  →  Role Template  →  Permission Bundles  →  Scope Bindings  →  Policy Engine
```

| Camada | Propósito | Quem usa |
|--------|-----------|----------|
| **Ator Canônico** | Linguagem de negócio, UX, personas, jornadas | Product, design, discovery |
| **Role Template** | Perfil provisionável e auditável | Admins, onboarding, auditoria |
| **Permission Bundles** | Capacidades reutilizáveis por domínio | Engenharia, composição de roles |
| **Scope Bindings** | Clube, equipe, temporada — onde o acesso se aplica | Sistema de autorização |
| **Policy Engine** | Restrições contextuais ABAC | Segurança, compliance |

**Regra arquitetural:** `ator canônico ≠ role ≠ bundle`. Misturar essas camadas gera rigidez
e explosão combinatória de perfis. O role existe para governança; o bundle é a menor unidade
de autorização reutilizável; o ator existe para produto.

---

## 1. Atores Canônicos

### 1.1 Plataforma

| # | Ator | Responsabilidade | Escopo |
|---|------|-----------------|--------|
| 1 | **Platform Super Admin** | Operar plataforma global; administrar tenants; feature flags; suporte auditado | Multi-tenant global |
| 2 | **Tenant Admin** | Administrar usuários; atribuir roles; configurar equipes, temporadas e módulos | Clube, federação ou liga |

### 1.2 Gestão esportiva

| # | Ator | Responsabilidade | Escopo |
|---|------|-----------------|--------|
| 3 | **Executive Stakeholder** | Consumir informação executiva consolidada; acompanhar performance institucional | Organização ou grupo |
| 4 | **Sporting Director** | Gestão esportiva; elenco; evolução de atletas; inteligência de mercado | Clube ou programa esportivo |
| 5 | **Technical Coordinator** | Coordenar metodologia; alinhar base e profissional; supervisionar staff | Uma ou várias categorias |

### 1.3 Comissão técnica

| # | Ator | Responsabilidade |
|---|------|-----------------|
| 6 | **Head Coach** | Comandar treino e jogo; decidir plano técnico-tático; consumir análise |
| 7 | **Assistant Coach** | Apoiar preparação; revisar vídeo; colaborar em scouting e operação |
| 8 | **Performance Analyst** | Produzir análise técnico-tática; operar scouting; construir relatórios |
| 9 | **Video Analyst** | Organizar vídeo; tagging; gerar clips e playlists; manter biblioteca |
| 10 | **Opponent Scout** | Analisar adversários; identificar padrões; preparar dossiês pré-jogo |
| 11 | **Goalkeeper Coach** | Análise específica de goleiros; relatórios e recortes dedicados |

### 1.4 Performance, saúde e disponibilidade

| # | Ator | Responsabilidade |
|---|------|-----------------|
| 12 | **Strength & Conditioning Coach** | Controlar carga; ajustar volume/intensidade; acompanhar readiness |
| 13 | **Performance Scientist** | Modelagem física; análise longitudinal; calibração de métricas |
| 14 | **Physiotherapist** | Conduzir reabilitação; gerenciar restrições funcionais; retorno ao jogo |
| 15 | **Team Doctor** | Emitir aptidão; registrar diagnóstico; gerir camada clínica formal |
| 16 | **Nutritionist** | Acompanhar nutrição esportiva; correlacionar rotina alimentar e performance |

### 1.5 Operacional e competitivo

| # | Ator | Responsabilidade |
|---|------|-----------------|
| 17 | **Match Operator** | Operar jogo ao vivo; registrar cronologia e eventos |
| 18 | **Competition Official** | Validar/homologar registros oficiais; conformidade operacional da partida |
| 19 | **Referee-Linked Official** | Consultar evidências e registros autorizados; camada homologatória |

### 1.6 Ecossistema, mídia e distribuição

| # | Ator | Responsabilidade |
|---|------|-----------------|
| 20 | **Federation Operator** | Operar competição; consolidar estatística oficial; publicar dados institucionais |
| 21 | **League Admin** | Governar competição profissional; homologar publicação; portais e produtos digitais |
| 22 | **Media Operator** | Consumir e publicar estatísticas públicas; operar widgets, overlays e highlights |
| 23 | **External Partner** | Consumir dados ou conteúdo explicitamente compartilhado (broadcaster, patrocinador) |

### 1.7 Atletas

| # | Ator | Responsabilidade | Escopo |
|---|------|-----------------|--------|
| 24 | **Athlete** | Consumir feedback; responder wellness; acompanhar agenda e material compartilhado | Exclusivamente seus próprios dados |
| 25 | **Academy Athlete Guardian Proxy** | Acompanhar agenda e informações permitidas de atleta de base | Apenas dados autorizados pelo clube |

---

## 2. Permission Bundles

Bundles são a unidade principal de composição de roles. Cada bundle representa um conjunto
coerente de capacidades em um domínio.

### 2.1 Administração e governança

| Bundle | Capacidades |
|--------|------------|
| `platform_admin_bundle` | Gerenciar tenants; feature flags; licenças; suporte auditado; configuração global |
| `tenant_admin_bundle` | Gerenciar usuários do tenant; atribuir roles; configurar equipes, temporadas e módulos |
| `audit_and_compliance_bundle` | Visualizar logs; trilha de auditoria; revisar exportações sensíveis; acessos críticos |

### 2.2 Identidade e organização

| Bundle | Capacidades |
|--------|------------|
| `organization_management_bundle` | Criar/editar organização; unidades, categorias, equipes; calendários e temporadas |
| `user_access_management_bundle` | Convidar usuários; ativar/desativar acesso; vincular escopos; atribuir templates de role |
| `master_data_management_bundle` | Manter cadastro de atletas, staff, competições, jogos, arenas, elenco por temporada |

### 2.3 Treino e operação técnica

| Bundle | Capacidades |
|--------|------------|
| `training_plan_view_bundle` | Visualizar sessões, agenda, microciclos e objetivos de treino |
| `training_plan_manage_bundle` | Criar/editar microciclos, sessões, objetivos e observações técnicas |
| `session_execution_bundle` | Registrar presença, execução, comentários operacionais; vínculo planejado vs realizado |

### 2.4 Vídeo

| Bundle | Capacidades |
|--------|------------|
| `video_library_view_bundle` | Acessar biblioteca de vídeo; pesquisar jogos, treinos, clips e playlists |
| `video_library_manage_bundle` | Subir vídeos; organizar acervo; classificar ativos; gerenciar metadados |
| `video_tagging_bundle` | Marcar eventos; criar clips; usar templates de tagging; comentar lances |
| `video_playlist_bundle` | Montar playlists; compartilhar material interno; preparar reuniões de vídeo |
| `video_publish_internal_bundle` | Publicar material para staff e atletas dentro do tenant |
| `video_publish_public_bundle` | Liberar vídeos/clips publicáveis; aprovar assets públicos |

### 2.5 Scouting e análise técnica

| Bundle | Capacidades |
|--------|------------|
| `live_scouting_bundle` | Operar scouting ao vivo; registrar eventos em tempo real; corrigir timeline durante o jogo |
| `technical_scouting_bundle` | Classificar ações ofensivas, defensivas, transições e eventos especiais de handebol |
| `opponent_intelligence_view_bundle` | Consumir dossiês de adversário; acessar análise comparativa |
| `opponent_intelligence_manage_bundle` | Criar dossiês; editar observações; montar análise de adversário; consolidar padrões |
| `goalkeeper_analysis_bundle` | Analisar goleiros; mapas de arremesso; relatórios específicos; tendências de finalização |

### 2.6 Analytics e relatórios

| Bundle | Capacidades |
|--------|------------|
| `analytics_basic_view_bundle` | Visualizar dashboards básicos; métricas de jogo, equipe e atleta |
| `analytics_advanced_view_bundle` | Análises contextuais; comparação por lineup; filtros avançados; benchmarks internos |
| `analytics_authoring_bundle` | Criar dashboards; definir indicadores customizados; construir relatórios analíticos |
| `reporting_view_bundle` | Consultar relatórios; baixar versões autorizadas |
| `reporting_manage_bundle` | Gerar relatórios; editar templates; programar distribuição interna |

### 2.7 Performance física (V2)

| Bundle | Capacidades |
|--------|------------|
| `tracking_view_bundle` | Visualizar tracking, deslocamentos, mapas de calor e carga externa |
| `tracking_manage_bundle` | Configurar coleta; validar ingestão; recalibrar ou consolidar dados autorizados |
| `readiness_view_bundle` | Visualizar prontidão esportiva, disponibilidade e risco funcional resumido |
| `readiness_manage_bundle` | Registrar wellness; ajustar thresholds; validar readiness; configurar alertas |
| `load_management_bundle` | Acompanhar volume, intensidade, carga aguda/crônica; planejado vs realizado |
| `performance_science_bundle` | Análises longitudinais; modelos de risco; calibração de zonas; estudos por posição |

### 2.8 Saúde, recuperação e medicina (V2)

| Bundle | Capacidades | Nota |
|--------|------------|------|
| `medical_summary_view_bundle` | Visualizar status funcional resumido; restrições esportivas; aptidão geral | Não inclui diagnóstico detalhado |
| `medical_record_view_bundle` | Visualizar prontuário clínico detalhado | Acesso auditado |
| `medical_record_manage_bundle` | Criar/editar prontuário; laudos; diagnósticos; liberações; histórico clínico | Acesso auditado + logging reforçado |
| `rehab_management_bundle` | Plano de reabilitação; evolução funcional; retorno progressivo; observações terapêuticas | |
| `availability_decision_support_bundle` | Emitir status esportivo (apto/restrito/indisponível); integrar saúde e performance | |

### 2.9 Competição, oficialização e mídia (V2/V3)

| Bundle | Capacidades |
|--------|------------|
| `competition_management_bundle` | Criar competição; fases; jogos; tabela; parâmetros institucionais |
| `official_match_validation_bundle` | Validar cronologia oficial; revisar inconsistências; homologar dados da partida |
| `official_stats_publish_bundle` | Publicar estatísticas oficiais; liberar leaderboards e rankings |
| `media_feed_access_bundle` | Consumir feeds públicos ou institucionais; widgets, overlays e live stats autorizados |
| `media_operations_bundle` | Operar publicação para mídia; highlights públicos; portais; ativos digitais de competição |

### 2.10 Atleta e self-service

| Bundle | Capacidades |
|--------|------------|
| `athlete_self_service_bundle` | Agenda; wellness; materiais compartilhados; métricas pessoais; feedback individual |
| `athlete_development_view_bundle` | Visualizar plano de desenvolvimento; metas individuais; clips e relatórios atribuídos |

### 2.11 Exportação e compartilhamento

| Bundle | Capacidades |
|--------|------------|
| `data_export_basic_bundle` | Exportar relatórios e dados não sensíveis |
| `data_export_sensitive_bundle` | Exportar dados sensíveis sob política reforçada |
| `external_sharing_bundle` | Compartilhar conteúdo com usuários externos autorizados |

---

## 3. Role Templates

Roles são compostos por bundles e atribuídos a usuários como ponto de partida.
Variações por tenant são resolvidas por adição/remoção de bundles — nunca por criação de novos roles.

### 3.1 Plataforma e administração

| Role | Ator | Bundles | Restrições |
|------|------|---------|-----------|
| `PLATFORM_SUPER_ADMIN` | Platform Super Admin | `platform_admin_bundle`, `audit_and_compliance_bundle` | Sem acesso clínico detalhado por default |
| `TENANT_ADMIN` | Tenant Admin | `tenant_admin_bundle`, `organization_management_bundle`, `user_access_management_bundle`, `master_data_management_bundle`, `reporting_view_bundle` | Sem acesso médico detalhado; sem homologação oficial |

### 3.2 Executivos e gerenciais

| Role | Bundles | Restrições |
|------|---------|-----------|
| `EXECUTIVE_VIEWER` | `analytics_basic_view_bundle`, `reporting_view_bundle` | Leitura apenas; sem clínico |
| `SPORTING_DIRECTOR` | `analytics_basic_view_bundle`, `analytics_advanced_view_bundle`, `reporting_view_bundle`, `opponent_intelligence_view_bundle`, `goalkeeper_analysis_bundle`, `medical_summary_view_bundle`, `athlete_development_view_bundle` | Sem prontuário clínico detalhado |
| `TECHNICAL_COORDINATOR` | `training_plan_view_bundle`, `training_plan_manage_bundle`, `analytics_basic_view_bundle`, `reporting_view_bundle`, `athlete_development_view_bundle`, `opponent_intelligence_view_bundle` | Escopo: múltiplas equipes/categorias |

### 3.3 Comissão técnica

| Role | Bundles padrão | Restrições |
|------|---------------|-----------|
| `HEAD_COACH` | `training_plan_view_bundle`, `training_plan_manage_bundle`, `session_execution_bundle`, `video_library_view_bundle`, `video_playlist_bundle`, `technical_scouting_bundle`, `opponent_intelligence_view_bundle`, `analytics_basic_view_bundle`, `reporting_view_bundle`, `readiness_view_bundle`, `medical_summary_view_bundle`, `goalkeeper_analysis_bundle` | Sem `medical_record_*`; sem exportação sensível |
| `ASSISTANT_COACH` | `training_plan_view_bundle`, `session_execution_bundle`, `video_library_view_bundle`, `video_tagging_bundle`, `video_playlist_bundle`, `technical_scouting_bundle`, `opponent_intelligence_view_bundle`, `analytics_basic_view_bundle`, `readiness_view_bundle` | Geralmente sem aprovação plena |
| `PERFORMANCE_ANALYST` | `video_library_view_bundle`, `video_library_manage_bundle`, `video_tagging_bundle`, `video_playlist_bundle`, `live_scouting_bundle`, `technical_scouting_bundle`, `opponent_intelligence_view_bundle`, `opponent_intelligence_manage_bundle`, `analytics_basic_view_bundle`, `analytics_advanced_view_bundle`, `analytics_authoring_bundle`, `reporting_view_bundle`, `reporting_manage_bundle`, `goalkeeper_analysis_bundle` | Sem acesso médico detalhado |
| `VIDEO_ANALYST` | `video_library_view_bundle`, `video_library_manage_bundle`, `video_tagging_bundle`, `video_playlist_bundle`, `video_publish_internal_bundle`, `reporting_view_bundle` | Sem saúde/medicina; analytics limitado |
| `OPPONENT_SCOUT` | `video_library_view_bundle`, `video_tagging_bundle`, `opponent_intelligence_view_bundle`, `opponent_intelligence_manage_bundle`, `analytics_basic_view_bundle`, `reporting_view_bundle`, `reporting_manage_bundle` | Sem dados médicos; sem gestão administrativa |
| `GOALKEEPER_COACH` | `video_library_view_bundle`, `video_playlist_bundle`, `goalkeeper_analysis_bundle`, `analytics_basic_view_bundle`, `reporting_view_bundle`, `opponent_intelligence_view_bundle` | Escopo: goleiros do time + finalizadores adversários |

### 3.4 Performance e saúde (V2)

| Role | Bundles padrão | Restrições |
|------|---------------|-----------|
| `STRENGTH_AND_CONDITIONING_COACH` | `training_plan_view_bundle`, `session_execution_bundle`, `tracking_view_bundle`, `readiness_view_bundle`, `readiness_manage_bundle`, `load_management_bundle`, `medical_summary_view_bundle`, `availability_decision_support_bundle`, `reporting_view_bundle` | Sem prontuário clínico detalhado |
| `PERFORMANCE_SCIENTIST` | `tracking_view_bundle`, `tracking_manage_bundle`, `readiness_view_bundle`, `load_management_bundle`, `performance_science_bundle`, `analytics_advanced_view_bundle`, `analytics_authoring_bundle`, `reporting_view_bundle`, `reporting_manage_bundle` | Visão clínica apenas resumida |
| `PHYSIOTHERAPIST` | `medical_summary_view_bundle`, `rehab_management_bundle`, `availability_decision_support_bundle`, `tracking_view_bundle`, `readiness_view_bundle`, `reporting_view_bundle` | Opcional por tenant: `medical_record_view_bundle` (auditado por atleta) |
| `TEAM_DOCTOR` | `medical_summary_view_bundle`, `medical_record_view_bundle`, `medical_record_manage_bundle`, `availability_decision_support_bundle`, `tracking_view_bundle`, `readiness_view_bundle`, `reporting_view_bundle` | Exportação sensível controlada; logging reforçado |
| `NUTRITIONIST` | `athlete_development_view_bundle`, `medical_summary_view_bundle`, `reporting_view_bundle` | Sem prontuário clínico completo; `readiness_view_bundle` opcional |

### 3.5 Operacional e institucional

| Role | Bundles padrão | Restrições |
|------|---------------|-----------|
| `MATCH_OPERATOR` | `live_scouting_bundle`, `technical_scouting_bundle`, `reporting_view_bundle` | Acesso focado em jogo; sem saúde/analytics amplo |
| `COMPETITION_OFFICIAL` | `competition_management_bundle`, `official_match_validation_bundle`, `reporting_view_bundle` | Sem dados privados do clube; sem opponent intelligence interno |
| `FEDERATION_OPERATOR` | `competition_management_bundle`, `official_match_validation_bundle`, `official_stats_publish_bundle`, `media_operations_bundle`, `reporting_view_bundle`, `analytics_basic_view_bundle` | Sem clínico interno; sem scouting estratégico privado |
| `LEAGUE_ADMIN` | `competition_management_bundle`, `official_match_validation_bundle`, `official_stats_publish_bundle`, `media_feed_access_bundle`, `media_operations_bundle`, `analytics_basic_view_bundle`, `reporting_view_bundle` | |
| `MEDIA_OPERATOR` | `media_feed_access_bundle`, `media_operations_bundle`, `video_publish_public_bundle`, `reporting_view_bundle` | Sem acesso interno estratégico; sem dados sensíveis |
| `EXTERNAL_PARTNER_VIEWER` | `reporting_view_bundle`, `media_feed_access_bundle` | Leitura somente; escopo explicitamente compartilhado |

### 3.6 Atletas

| Role | Bundles | Restrições |
|------|---------|-----------|
| `ATHLETE` | `athlete_self_service_bundle`, `athlete_development_view_bundle` | Apenas próprio escopo; sem acesso a colegas |
| `ACADEMY_GUARDIAN_VIEWER` | `athlete_self_service_bundle` | Somente materiais explicitamente liberados; sujeito à política de menor de idade |

---

## 4. Modelo de dados (entidades de implementação)

```
CanonicalActor { id, code, name, description, domain_family }
PermissionBundle { id, code, name, description, sensitivity_level, module_family }
Permission { id, resource, action, condition_schema }
RoleTemplate { id, code, name, canonical_actor_id, description, is_system_default }
RoleBundleAssignment { role_id, bundle_id }
BundlePermissionAssignment { bundle_id, permission_id }
UserRoleBinding { user_id, role_id, scope_type, scope_id, valid_from, valid_to }
PolicyConstraint { id, role_id | bundle_id, policy_type, rule_expression }
```

---

## 5. Regra arquitetural

1. **Roles não são a menor unidade de segurança** — o bundle ou a permissão atômica é.
   O role existe para governança e provisionamento; o bundle é a menor unidade reutilizável.

2. **Variações por tenant via composição** — se um clube precisa de Head Coach com acesso
   a `medical_summary_view_bundle` e outro não, resolve-se com binding de bundle, não com
   um novo role.

3. **Atores canônicos são estáveis** — bundles evoluem moderadamente; roles são templates
   versionáveis por tenant.

4. **Nenhum novo role sem aprovação formal** — ADR + atualização deste documento.

5. **Exportação sensível exige política adicional** — `data_export_sensitive_bundle` nunca
   é atribuído por padrão; requer ativação explícita com logging reforçado.

---

## 6. Exemplo completo

```
Ator canônico: Head Coach
Role formal: HEAD_COACH
Escopo: clube=Pinheiros, equipe=Adulto Masculino, temporada=2026
Bundles: training_plan_manage_bundle + video_library_view_bundle +
         opponent_intelligence_view_bundle + readiness_view_bundle +
         medical_summary_view_bundle
Policies:
  - deny medical_diagnosis_detail
  - allow medical_functional_status_summary
  - deny export_sensitive_biometric_data
```

---

## 7. Referências

Modelo arquitetural: [`docs/_canon/SYSTEM_SCOPE.md §4`](../_canon/SYSTEM_SCOPE.md)
Módulo responsável: `identity_access`
Perfis de usuário: [`docs/guias/USER_PROFILES.md`](USER_PROFILES.md)
Escopo por fase: [`docs/guias/MVP_SCOPE.md`](MVP_SCOPE.md)
