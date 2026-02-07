<!-- STATUS: NEEDS_REVIEW -->

# REGRAS DO SISTEMA (V1.1)

Sumário
- [1. Regras Estruturais](#1-regras-estruturais)
- [2. Regras Operacionais - V1 (Consolidadas)](#2-regras-operacionais---v1-consolidadas)
- [3. Regras de Domínio Esportivo - Definitivas](#3-regras-de-dominio-esportivo---definitivas)
- [4. Visibilidade do Perfil Atleta](#4-visibilidade-do-perfil-atleta)
- [5. Regras de Participação da Atleta - Definitivas](#5-regras-de-participacao-da-atleta---definitivas)
- [6. Regras de Configuração do Banco - V1](#6-regras-de-configuracao-do-banco---v1)
- [6.1 Esquema técnico (temporadas e jogos)](#61-esquema-técnico-temporadas-e-jogos)
- [7. Organização das Regras por Camada de Configuração](#7-organizacao-das-regras-por-camada-de-configuracao)

# Política de Provisionamento

## Regras Operacionais
1. Associação organizacional automática
- Em V1 (clube único), todo novo usuário é automaticamente associado ao clube único, sem exigir seleção de organização no cadastro.

2. Vínculo sazonal na criação
- Staff (Dirigente, Coordenador, Treinador): criar `membership` ativo na temporada corrente. Não requer equipe na criação (R6, R9).
- Atleta: criar `membership` ativo na temporada corrente e `team_registration` automático na Equipe Institucional ou Grupo de Avaliação (R38, R39, RDB10).

3. Gating de operação (sem bloquear cadastro)
- Usuários sem escopo operacional (equipe competitiva ou responsabilidade) “aparecem” no sistema, mas:
  - Atleta: não participa de jogos/treinos até ter `team_registration` na equipe competitiva vigente e dados críticos (RG/CPF, posição defensiva) completos (RD13, RP10).
  - Treinador: não consegue operar ações de equipe até ser definido como responsável em uma equipe (RF7).
  - Coordenador/Dirigente: operam de imediato pelo papel e membership criado.
- Atleta e usuários sem escopo mantêm acesso conforme R42 (leitura do próprio histórico; sem dados coletivos).

4. Auditoria e integridade
- Todas as criações de usuário e vínculos automáticos são auditadas (R31–R32, RDB5).
- Soft delete permanece obrigatório nas tabelas de domínio (RDB4).
- Categorias da atleta permanecem derivadas por temporada (RD1–RD2) e não são gravadas no perfil global.

## Efeitos Práticos
- Cadastro de usuário completo sem escolher equipe/organização.
- O sistema garante os vínculos mínimos nos bastidores (auto-org e Equipe Institucional).
- Você coloca o usuário em equipe/organização competitiva depois, sem violar as regras.

# Regras de Cadastro do Sistema (compatível com REGRAS_SISTEMAS.md V1.1)

Objetivo
- Permitir cadastrar usuários (Atleta, Treinador, Coordenador, Dirigente) com ficha completa, sem exigir equipe no momento do cadastro, mantendo 100% de conformidade com o RAG.
- Garantir que o usuário “apareça” no sistema após o cadastro e que vínculos mínimos sejam criados automaticamente, sem bloquear a criação.
- Postergar a definição de equipe competitiva para depois do cadastro, com histórico e auditoria preservados.

Referências canônicas
- RF1 (cadeia de criação), R2/R42 (usuário e vínculo), R33 (regra de ouro), R34 (clube único na V1), R38–R39 (atleta e equipe), RDB10 (team_registrations não sobrepostas), RD1–RD2 (idade/categoria por temporada), RD13 (goleira), R31–R32/RDB5 (auditoria), RDB4 (soft delete), RDB3 (temporal em UTC), RF18 (rascunhos).

Glossário
- Organização: único clube na V1 (R34).
- Temporada corrente: temporada cuja data atual está entre `start_date` e `end_date`.
- Equipe Institucional/Grupo de Avaliação: equipe técnica para atividades sem equipe competitiva (R39).
- Membership: vínculo pessoa+papel+clube+temporada (R6, R9).
- Team registration: participação temporal da atleta na equipe na temporada (RDB10).

## 1) Hierarquia e quem pode cadastrar quem (RF1)
- Dirigente cadastra Coordenadores.
- Coordenador cadastra Treinadores.
- Treinador cadastra Atletas.
- Observações:
  - O Super Administrador é único e seedado (R3, RDB6); não é cadastrado via fluxo comum.
  - A criação gera automaticamente o papel correspondente (RF1) e o vínculo mínimo (ver Seção 3).

## 2) Regras gerais de usuário e login (R2, R42)
- Usuário exige e-mail único, normalizado e verificado para login.
- Senha obrigatória na criação, com política mínima (8+ caracteres, complexidade configurável).
- Sem vínculo ativo, usuário não opera (R42); após cadastro, “aparece” no sistema com escopo conforme o papel:
  - Atleta: leitura do próprio histórico pessoal; sem interação coletiva.
  - Treinador: sem acesso a equipes até ser vinculado como responsável (RF7).
  - Coordenador/Dirigente: acesso operacional/administrativo imediato.

## 3) Vínculos automáticos na criação (removendo bloqueios no cadastro)
Para não bloquear cadastro por falta de equipe, o backend cria vínculos mínimos automaticamente:

- Associação organizacional automática (R2, R34):
  - Todo novo usuário é associado ao clube único da V1 no momento do cadastro.

- Membership sazonal (R6, R9):
  - Ao criar um usuário, criar `membership` ativo na temporada corrente:
    - Staff (Dirigente/Coordenador/Treinador): `membership` ativo sem equipe na criação (papel exclusivo por pessoa; R7).
    - Atleta: `membership` ativo + `team_registration` automático na Equipe Institucional/Grupo de Avaliação (R38, R39).
  - Se não houver temporada ativa, usar a planejada mais próxima (RF4/RDB14). Se inexistente, bloquear com alerta crítico para o Dirigente criar a temporada seed (RF4, RDB14).

- Team registration automático da atleta (R38, R39, RDB10):
  - Criar uma linha vigente de `team_registration` na Equipe Institucional com `start_at = now()`.
  - Ao mover para equipe competitiva:
    - Encerrar a linha vigente (setar `end_at`) e criar nova linha para a equipe competitiva.
    - Garantir que períodos não se sobreponham para a mesma pessoa+equipe+temporada (RDB10).

- Auditoria obrigatória (R31–R32, RDB5):
  - Registre a criação do usuário e todos os vínculos automáticos: quem (actor_id), quando, ação (`user_create`, `membership_create`, `team_registration_create`), contexto, old/new.

## 4) Ficha de cadastro por papel: campos e validações

### 4.1 Atleta (ficha completa)
- Obrigatórios no backend/API:
  - `athlete_name`: 3–100; trim
  - `birth_date`: data válida
  - `athlete_rg`: formato e unicidade
  - `athlete_cpf`: dígitos válidos e unicidade
  - `athlete_phone`: normalização e validação
  - `main_defensive_position_id`: FK defensiva
  - Condicional RD13 (goleira): se `main_defensive_position_id = 5`, `main_offensive_position_id` deve ser NULL (bloqueio); tempo/estatísticas de linha bloqueadas para goleira
- Opcionais:
  - `athlete_nickname` (≤50)
  - `shirt_number` (1–99)
  - `secondary_defensive_position_id` (FK)
  - `main_offensive_position_id` (FK condicional)
  - `secondary_offensive_position_id` (FK)
  - `athlete_email` (opcional na ficha; não concede login) com índice único parcial case-insensitive quando preenchido
  - Responsáveis e escolaridade: `guardian_name` (3–100), `guardian_phone`, `schooling_id` (FK)
  - Endereço: `zip_code` (CEP), `street`, `neighborhood`, `city`, `state` (UF), `address_number`, `address_complement`
  - `athlete_photo` upload até 5MB; URL derivada no GET
- Derivados/automáticos:
  - `registered_at`: setado pelo servidor
  - `created_at`, `updated_at`: UTC; trigger atualiza `updated_at`
  - `athlete_age`: não persistir; calculado no GET
  - `athlete_age_at_registration`: INT calculado por trigger (diff `registered_at` vs `birth_date`)
  - `category_id`: derivado pela idade no início da temporada e fixado no contexto sazonal (não no perfil global; RD1–RD2)

### 4.2 Treinador
- Obrigatórios:
  - `name`, `email` (login), `password`
- Derivados/automáticos:
  - `membership` sazonal ativo (sem equipe)
- Operação:
  - Só acessa equipes onde for definido responsável (RF7); troca auditável.

### 4.3 Coordenador
- Obrigatórios:
  - `name`, `email` (login), `password`
- Derivados/automáticos:
  - `membership` sazonal ativo
- Operação:
  - Acesso operacional amplo (R26); pode criar treinos/jogos/estatísticas (RF9), reabrir/excluir logicamente jogos (RF15), encerrar participações (RF17).

### 4.4 Dirigente
- Obrigatórios:
  - `name`, `email` (login), `password`
- Derivados/automáticos:
  - `membership` sazonal ativo
- Operação:
  - Acesso administrativo total; pode criar temporadas, equipes, trocar treinador responsável, etc.

### 4.5 Super Administrador (seed)
- Criado no seed inicial com índice parcial único (RDB6); não removível e imutável (R3).
- Autoridade máxima; ignora travas operacionais, mas tudo é auditado (R3, R31–R32).

## 5) Regras de validação por camada

### 5.1 Backend
- Bloqueios e alertas:
  - Não bloqueie a criação por falta de equipe; crie vínculos mínimos (Seção 3).
  - Bloqueie ações operacionais quando faltar integridade estrutural (RF20): ex. atleta sem RG/CPF, goleira com ofensiva definida, sem team_registration vigente na equipe competitiva.
- Derivações:
  - Categoria por temporada (RD1–RD2) no momento de ativação da atleta na temporada e a cada consulta contextual.
- Estados esportivos:
  - Estado inicial “ativa”; mudanças auditáveis; “dispensada” encerra automaticamente participações vigentes (R13 Complemento).
- Regras de goleira (RD13):
  - Bloquear `main_offensive_position_id` para goleira; bloquear tempo/estatísticas de linha; goleiro-linha (RD22) só para atletas de linha.
- Rascunhos:
  - Permitir salvar rascunhos sem efeito operacional (RF18), visíveis para comissão técnica (RF22), com janela de desfazer/editar (RF27).

### 5.2 Banco de Dados (Neon Postgres/SQL)
- PKs UUID com `gen_random_uuid()` (RDB1–RDB2).
- Temporal em UTC (`timestamptz`) (RDB3).
- Soft delete em tabelas de domínio: `deleted_at` + `deleted_reason`; triggers bloqueiam DELETE físico (RDB4).
- Auditoria append-only: `audit_logs` com INSERT-only; triggers/rotinas para ações críticas (RDB5, R31–R32, R35).
- Índices e constraints:
  - Unicidade de e-mail em `users`: índice único `lower(email)`.
  - Unicidade de e-mail opcional em `athletes`: índice único parcial `lower(email)` `WHERE email IS NOT NULL`.
  - `shirt_number` CHECK 1–99.
  - FKs: posições defensivas/ofensivas, escolaridade, categorias (lookup com PK integer permitido pela allowlist de RDB2.1).
- Triggers:
  - `updated_at` BEFORE UPDATE.
  - `athlete_age_at_registration` ON INSERT/UPDATE (somente quando `registered_at`/`birth_date` mudam).
  - Jogos finalizados bloqueiam UPDATE; reabertura altera `status=em_revisao` com auditoria (RDB13, RF15).

### 5.3 Front-end
- Não pedir equipe no cadastro de usuário.
- Validar campos conforme ficha; aplicar RD13 (ex.: esconder/ofuscar campo ofensivo quando defensivo=Goleira).
- Exibir categoria calculada (somente leitura) e pendências operacionais (ex.: “mover para equipe competitiva”, “definir treinador responsável”).
- Notificações críticas bloqueiam ação até leitura/confirm (RF24).
- Operação offline suportada em jogos com sincronização posterior (RF25).

## 6) Regras de vinculação posterior (após cadastro)
- Atleta:
  - Mover para equipe competitiva cria nova `team_registration` e encerra a institucional; sem sobreposição temporal (RDB10).
  - Estatísticas e histórico preservados após troca (RD87).
- Treinador:
  - Definição como responsável pela equipe (RF7), auditável; não altera histórico passado.
- Coordenador e Dirigente:
  - Já operacionais; podem criar temporadas, equipes, etc.

## 7) Gating de operação (quando cada item passa a ser exigido)
- Cadastro (aparecer no sistema): apenas campos obrigatórios do papel + vínculos mínimos automáticos (Seção 3).
- Operar em equipe:
  - Atleta: `RG`, `CPF`, `main_defensive_position_id` válidos; RD13 aplicado; `team_registration` vigente na equipe competitiva.
  - Treinador: deve estar definido como responsável na equipe (RF7).
- Ação crítica (qualquer papel): auditoria obrigatória (R31–R32).
- Temporada encerrada: edições só via ação administrativa auditada (R37).

## 8) Exceções e falhas controladas
- Sem temporada ativa:
  - Se existir temporada planejada futura, criar `membership` com `start_at` na virada; bloquear operações até início (RF5/6.1.1).
  - Se não existir temporada, bloquear cadastro com mensagem para Dirigente criar a temporada seed (RDB14).
- Sem Equipe Institucional configurada:
  - Bloquear criação de atleta com mensagem para criar a equipe institucional (R39).
- Conflito de edição simultânea:
  - Registrar conflito, bloquear sobrescrita, exigir decisão autorizada com auditoria (R41).

## 9) Eventos de auditoria mínimos (ação -> descrição)
- `user_create`: criação de usuário (person+user).
- `membership_create`: criação de vínculo sazonal.
- `team_registration_create`: criação de participação em equipe.
- `team_registration_close`: encerramento de participação.
- `user_provision_auto_link`: vínculos automáticos na criação.
- `role_change`/`membership_reactivate`: transições de papel/vínculo.
- `athlete_state_change`: mudança de estado da atleta (R13).
- `game_finalize` / `game_reopen` / `game_soft_delete`: fluxo de jogo (RF15/RDB13).
- `stat_correction`: correções com `admin_note` (R23–R24, RDB12).

## 10) Checklist de implementação
- Backend:
  - POST /users: cria usuário + vínculos automáticos (organizacional, sazonal; atleta -> equipe institucional).
  - POST /teams/{team_id}/registrations: movimenta atletas entre equipes (encerra anterior, cria nova).
  - POST /teams/{team_id}/set-coach: define treinador responsável (RF7).
  - GET /athletes/{id}: deriva idade e categoria por temporada; retorna `photo_url`.
- DB:
  - Triggers `updated_at`, `age_at_registration`, bloqueio de `games.status=finalizado`.
  - `audit_logs` append-only, índices únicos, FKs e CHECKs.
  - Soft delete nas tabelas de domínio.
- Front:
  - Tela de cadastro sem campo de equipe; mostra pendências para operação.
  - Aplicar RD13 condicional na UI.

Regra-síntese (Cadastro)
- Cadastre com ficha completa sem equipe; o sistema cria vínculos mínimos automaticamente (clube, temporada, e para atleta, Equipe Institucional), garantindo que o usuário apareça no sistema sem operar fora de vínculo. A operação em equipes competitivas ocorre depois, com histórico, auditoria e integridade preservados.

## 1. Regras Estruturais

R1. Pessoa  
Pessoa representa o indivíduo real e é independente de função esportiva.

R2. Usuário  
Usuário representa acesso ao sistema. Apenas o Super Administrador pode existir sem vínculo organizacional.

R3. Super Administrador  
Existe exatamente um Super Administrador estrutural, vitalício, imutável e não removível. Possui autoridade máxima e pode ignorar travas operacionais; toda ação crítica é auditada.

R4. Papéis do sistema  
Papéis organizacionais válidos: Dirigente, Coordenador, Treinador, Atleta.

R5. Papéis não acumuláveis  
Uma pessoa não pode ter múltiplos papéis ativos simultaneamente. Mudanças de papel exigem encerramento de vínculo e criação de novo, sem sobreposição temporal.

R6. Vínculo organizacional  
Toda atuação no sistema ocorre por meio de vínculo entre pessoa, papel, clube e temporada.

R7. Vínculo ativo e exclusividade  
Regra geral: uma pessoa possui apenas um vínculo ativo. Exceção: atleta pode ter múltiplos vínculos ativos simultâneos em equipes diferentes, desde que as competições permitam. Papéis Dirigente, Coordenador e Treinador são exclusivos.  
Observação: para atleta, múltiplos vínculos por temporada são realizados via team_registrations (ver RDB10).

R8. Temporada obrigatória  
Todo vínculo ativo deve estar associado a uma temporada.

R9. Encerramento de vínculo  
Encerramento é manual, solicitado pelo usuário e validado pelo Coordenador (ou Dirigente quando exigido). O encerramento automático ocorre apenas no fim da vigência/temporada quando não há renovação.

R10. Encerramento automático de temporada  
Ao final da temporada o sistema encerra automaticamente todos os vínculos ativos, impedindo extensão temporal ou reativação retroativa.

R11. Histórico imutável  
Vínculos encerrados jamais são apagados ou alterados retroativamente.

R12. Atleta como papel permanente  
Atleta é papel permanente no histórico: uma pessoa nunca deixa de ser atleta no histórico, embora não possa acumular papéis simultaneamente.

R13. Estados operacionais da atleta  
Estados válidos: ativa, lesionada, dispensada. Estado não equivale a encerramento de vínculo, exceto em "dispensada".  
Complemento V1.1: Ao mudar para “dispensada”, o sistema encerra imediatamente todas as participações em equipes (team_registrations) ativas da temporada, mantendo o membership de atleta da temporada para histórico/consulta. Reativações criam novas linhas em team_registrations (novo UUID) a partir da data de reativação, sem reabrir registros encerrados.

R14. Impacto dos estados  
- Ativa: participa de tudo.  
- Lesionada (atualização V1.1): participa normalmente de jogos e treinos; estatísticas (de jogo e de treino) entram nos agregados; o sistema exibe alertas e visibilidade específica; pode receber comunicação específica.  
- Dispensada: aparece apenas em histórico; não entra em estatísticas; não recebe comunicação operacional.

R15. Categorias globais  
Categorias são globais e definidas exclusivamente por idade.

R16. Regra etária obrigatória  
A atleta pode atuar na sua categoria ou em categorias acima, nunca em categorias abaixo.

R17. Múltiplas equipes  
A participação da atleta em equipes é temporal, vinculada à temporada, e pode ser encerrada antes do término por decisão administrativa auditável.

R18. Treinos  
Treinos são eventos operacionais, editáveis dentro dos limites do sistema (R40), históricos e usados para carga, presença e análise.

R19. Jogos  
Jogos são eventos oficiais e, após finalizados, são imutáveis como evento; alterações só ocorrem por reabertura (RF15).

R20. Estatísticas primárias  
Estatísticas primárias estão sempre vinculadas a um jogo.

R21. Estatísticas agregadas  
Estatísticas agregadas são derivadas e recalculáveis; nunca são fonte primária.

R22. Métricas de treino  
Dados de treino são métricas operacionais (carga, PSE, assiduidade) e não substituem estatísticas primárias de jogo.

R23. Correção permitida com justificativa  
Correções em estatísticas são permitidas somente com justificativa obrigatória, identificação do responsável e data/hora.

R24. Preservação do dado anterior  
O dado corrigido substitui o anterior para fins operacionais; o valor anterior é preservado apenas para auditoria, sem efeito analítico.

R25. Permissões por papel  
Permissões são definidas por papel e aplicadas via vínculo.

R26. Escopo implícito  
- Treinador: acesso apenas às suas equipes.  
- Coordenador: acesso total a dados operacionais e esportivos.  
- Dirigente: acesso administrativo.  
- Atleta: acesso restrito aos próprios dados.

R27. Troca de função  
Não existe troca direta de papel.

R28. Transição obrigatória  
O vínculo atual é encerrado, um novo vínculo é criado, sem sobreposição temporal.

R29. Exclusão lógica  
Nenhuma entidade relevante é apagada fisicamente.

R30. Reativação de vínculo  
Vínculos podem ser reativados desde que não violem exclusividade, não alterem histórico passado e passem a valer somente a partir da data de reativação.

R31. Ações críticas auditáveis  
São obrigatoriamente auditadas: correção de estatística, encerramento de vínculo, reativação de vínculo, exclusão lógica de jogo, mudança de estado de atleta.

R32. Log obrigatório  
Todo evento crítico deve registrar quem, quando, o quê e contexto.

R33. Regra de ouro do sistema  
Nada acontece fora de um vínculo. Nada relevante é apagado. Nada histórico é sobrescrito sem rastro.

R34. Clube único na V1  
Existe exatamente um clube no sistema na V1; não há suporte a múltiplos clubes.

R35. Imutabilidade dos logs  
Logs de auditoria são absolutamente imutáveis, não podendo ser alterados ou removidos, nem pelo Super Administrador.

R36. Autoridade de correção de estatísticas  
Correções de estatísticas podem ser realizadas por qualquer papel durante temporada ativa, obedecendo R23 e R24. Após encerramento da temporada, apenas Coordenador e Dirigente, via ação administrativa auditada.

R37. Edição após encerramento da temporada  
Após o encerramento da temporada, qualquer edição de dados operacionais ou esportivos só pode ocorrer por ação administrativa auditada, sem reabertura temporal.

R38. Obrigatoriedade de equipe para atleta  
A atleta não pode existir em uma temporada sem estar vinculada a pelo menos uma equipe (competitiva ou institucional, ver R39). Criação ou reativação de vínculo de atleta exige associação imediata a uma equipe.

R39. Atividades sem equipe competitiva  
Atividades sem equipe (avaliações, testes, captação) devem ser vinculadas à Equipe Institucional ou Grupo de Avaliação.

R40. Limite temporal de edição de treinos  
O autor tem 10 minutos para correções rápidas. Após esse prazo, até 24 horas, qualquer edição exige aprovação ou perfil de nível superior. Após 24 horas, o registro é somente leitura, exceto por ação administrativa auditada.

R41. Resolução de conflitos de edição  
Em conflito simultâneo de edição, o sistema registra o conflito, bloqueia a sobrescrita automática e exige decisão explícita de usuário autorizado, com auditoria.

R42. Modo somente leitura sem vínculo  
Usuários sem vínculo ativo não podem operar no sistema. Atletas mantêm acesso somente leitura ao próprio histórico pessoal e estatísticas individuais, sem interação nem dados coletivos.

R43. Hierarquia formal  
1. Dirigente (Super Administrador) > 2. Coordenador > 3. Treinador/Staff > 4. Atleta.

## 2. Regras Operacionais — V1 (Consolidadas)

RF1. Cadeia hierárquica de criação de pessoas e usuários  
- Dirigentes criam coordenadores.  
- Coordenadores criam treinadores.  
- Treinadores criam atletas.  
A criação gera automaticamente o papel correspondente.

RF2. Identidade baseada em papel  
Pessoas só existem no sistema se identificadas como dirigente, coordenador, treinador ou atleta.

RF3. Usuário sem vínculo ativo  
Usuários (exceto Super Administrador) não podem operar no sistema sem vínculo ativo; atletas mantêm acesso somente leitura ao próprio histórico (ver R42).

RF4. Criação de temporadas  
Dirigentes, coordenadores e treinadores podem criar temporadas, inclusive futuras.

RF5. Encerramento de temporada  
Nenhuma temporada pode ser encerrada manualmente após iniciada; o encerramento ocorre de forma automática ao fim do período anual.  
Sub-regras V1.1:  
- RF5.1 Cancelamento antes do início: Permitido apenas se a temporada não possuir dados vinculados (equipes, jogos, treinos, convocações, participações, etc.). Havendo dados, é obrigatório mover/encerrar esses registros antes do cancelamento. Tudo é auditado.  
- RF5.2 Interrupção após início (força maior): Não há encerramento manual. A temporada recebe o estado operacional “Interrompida” a partir da data do evento; o sistema bloqueia criação/edição de novos eventos e cancela automaticamente jogos futuros. A end_date permanece inalterada. Tudo é auditado.

RF6. Criação de equipes  
Dirigentes e coordenadores podem criar equipes. Equipes podem existir temporariamente sem atletas vinculadas.

RF7. Alteração de treinador responsável pela equipe  
A troca pode ser feita por dirigente ou coordenador, é auditável e não altera histórico passado.

RF8. Encerramento de equipes  
Equipes encerradas deixam de operar, permanecem em histórico e não participam de relatórios ativos.

RF9. Criação de registros esportivos  
Jogos, treinos e estatísticas podem ser criados por coordenadores e treinadores.

RF10. Registro de presença em treinos  
Podem registrar presença: dirigentes, coordenadores e treinadores.

RF11. Convocação e recusa de atleta  
Atletas podem recusar convocações; a recusa exige justificativa registrada; a convocação permanece no histórico com status atualizado.

RF12. Edição de treinos  
Segue R40.

RF13. Conflito de edição  
Segue R41.

RF14. Finalização de jogos  
Jogos podem ser finalizados por dirigentes, coordenadores e treinadores.

RF15. Reabertura e exclusão lógica de jogos (atualização V1.1)  
Reabertura é permitida apenas pelo Coordenador e sempre via ação administrativa auditada. Ao reabrir, o mesmo registro do jogo retorna ao status “Em Revisão” (sem criação de nova versão/snapshot). As estatísticas deixam de alimentar dashboards até a nova finalização. Exclusão lógica de jogo pode ser feita por Coordenador ou Dirigente, sempre auditada.

RF16. Alteração do estado da atleta  
O estado (ativa, lesionada, dispensada) pode ser alterado por dirigentes, coordenadores e treinadores; toda alteração é auditável.

RF17. Encerramento manual de vínculos e participações  
Coordenadores e treinadores podem encerrar participações de atletas em equipes. Encerramento de vínculos de treinadores ou coordenadores exige aprovação explícita do dirigente.

RF18. Salvamento de rascunhos  
O sistema permite salvar registros incompletos como rascunho; rascunhos não produzem efeitos operacionais nem analíticos.

RF19. Violação de regras  
Quando uma regra é violada, o sistema alerta o usuário, permite salvar quando não estrutural e exige correção antes da efetivação.

RF20. Prioridade operacional  
O sistema prioriza alertas e orientação ao usuário; bloqueios só ocorrem quando a integridade estrutural está em risco.

RF21. Regra suprema de decisão  
Em conflito entre usabilidade e integridade dos dados, a integridade sempre prevalece. Regras automáticas do sistema sempre se sobrepõem à ação humana.

RF22. Visibilidade de rascunhos  
Registros em rascunho são visíveis para toda a comissão técnica, não apenas para quem criou.

RF23. Duplicação de registros  
O sistema permite duplicar treinos, jogos e equipes, sempre gerando um novo registro independente.

RF24. Notificações obrigatórias  
Notificações críticas do sistema bloqueiam ações até serem lidas e confirmadas pelo usuário.

RF25. Operação offline  
O sistema permite registro offline durante jogos, com sincronização posterior, preservando ordem temporal e integridade dos dados.

RF26. Versionamento visível  
Alterações relevantes exibem versionamento visível (antes/depois), além do log técnico interno.

RF27. Janela de desfazer/editar  
O usuário que realizou a ação pode editar ou desfazer por até 10 minutos. Após esse prazo, o registro é travado e apenas um superior hierárquico pode alterar, sempre com auditoria. Para treinos, aplicar também R40; para jogos, aplicar RF15.

RF28. Comentários e anotações livres  
O sistema permite comentários/anotações livres em jogos, treinos e atletas; esses comentários não alteram dados estatísticos.

RF29. Atualização de relatórios e dashboards  
Relatórios e dashboards refletem dados com atraso controlado, somente após validação dos registros.

RF30. Alertas automáticos  
O sistema possui alertas automáticos para inconsistências de dados e riscos esportivos (ex.: excesso de carga, acúmulo disciplinar).

RF31. Prioridade entre regras  
Em qualquer conflito entre regra esportiva e regra operacional, a regra esportiva sempre prevalece automaticamente.

## 3. Regras de Domínio Esportivo — Definitivas

RD1. Cálculo de idade esportiva  
A idade da atleta é determinada pela idade no início da temporada; essa idade é referência oficial para toda a temporada.

RD2. Fixação de categoria na temporada  
A categoria da atleta é definida no início da temporada e permanece inalterada até o fim da mesma.

RD3. Atuação em categorias superiores  
A atleta pode atuar em categorias acima da sua, sem limite, desde que esteja vinculada às equipes correspondentes.

RD4. Participação em jogos  
A atleta só pode participar de um jogo se estiver na convocação/lista oficial (o mesmo documento de autorização). Vínculo com equipe não implica participação automática.

RD5. Estatísticas individuais  
As estatísticas individuais pertencem exclusivamente à atleta, acumulam ao longo da temporada e da carreira, e não são fragmentadas por equipe ou categoria.

RD6. Substituições e tempo de jogo  
O sistema registra entrada e saída de atletas; esses registros compõem o tempo de participação no jogo.

RD7. Critério de participação oficial  
Participação disciplinar: presença em súmula (banco + quadra). Participação estatística: tempo efetivo em quadra.

RD8. Validação de jogos interrompidos  
Estatísticas só são válidas se o jogo for oficialmente validado; jogos interrompidos e não validados não geram estatísticas.

RD9. Empréstimo/cessão temporária  
A atleta só pode atuar por outra equipe mediante vínculo explícito, ainda que temporário.

RD10. Jogos amistosos  
Jogos amistosos geram estatísticas individuais separadas das estatísticas de jogos oficiais.

RD11. Posições em quadra  
As atletas podem exercer múltiplas posições, variáveis por jogo.

RD12. Mudança de posição durante o jogo  
O sistema registra mudanças de posição ao longo do jogo, preservando a sequência temporal.

RD13. Goleira (atualização V1.1)  
A goleira é exclusiva da posição e não atua como jogadora de linha na temporada nem no jogo; não é contabilizada como atleta de linha para minutagem tática.  
Complemento V1.1: O sistema bloqueia o lançamento de tempo em quadra e estatísticas típicas de atleta de linha para uma goleira. RD22 (goleiro-linha) aplica-se exclusivamente a atletas de linha.

RD14. Capitã  
A função de capitã não é registrada no sistema.

RD15. Convocação  
Uma atleta vinculada à equipe pode não ser convocada para um jogo, sem impacto automático em vínculo ou estado.

RD16. Suspensão e punição (atualização V1.1)  
Suspensão/punição gera impedimento esportivo de participação; o sistema sinaliza "Atleta Irregular" nas telas de escalação e não bloqueia automaticamente a súmula.  
Complemento V1.1: Lançamentos de tempo em quadra e eventos são permitidos, com alerta e flag “Atleta Irregular”. Essas estatísticas contam normalmente nos agregados (temporada/carreira), mantendo a marcação de irregularidade.

RD17. Acúmulo disciplinar  
O sistema controla acúmulo de cartões/faltas e aplica impactos automáticos previstos (ex.: alertas de irregularidade), sem suspensão automática.

RD18. Limite de atletas por jogo  
O sistema valida o limite máximo de 16 atletas relacionadas por jogo; relações acima do limite são bloqueadas.

RD19. Lesão durante o jogo  
Lesão ocorrida em jogo altera imediatamente o estado da atleta a partir do evento, sem reescrever dados anteriores.

RD20. Estatísticas coletivas  
Estatísticas coletivas da equipe são derivadas automaticamente das estatísticas individuais; não existe lançamento manual independente.

RD21. Sistemas defensivos  
O sistema registra sistemas defensivos e suas variações ao longo do jogo.

RD22. Goleiro-linha (atualização V1.1)  
Qualquer atleta de linha pode assumir a função de goleiro-linha, com estatísticas de goleiro; é uma situação tática distinta de substituição comum.  
Complemento V1.1: Aplica-se apenas a atletas de linha. Não se aplica a atletas registradas como goleira na temporada.

RD23. Tiros de 7 metros  
Tiros de 7 metros possuem estatística específica separada.

RD24. Exclusão de 2 minutos  
A exclusão de 2 minutos deve registrar o evento, controlar tempo, gerenciar retorno e refletir impacto numérico em quadra.

RD25. Cartão vermelho  
O cartão vermelho encerra a participação apenas no jogo em que ocorreu.

RD26. Pedidos de tempo (time-out)  
Pedidos de tempo registram o momento e a equipe solicitante.

RD27. Posse de bola  
A posse de bola é inferida pelas ações; não é evento explícito independente.

RD28. Transições ataque-defesa  
Transições ataque-defesa são eventos analisáveis separadamente.

RD29. Erros técnicos  
Erros técnicos são registrados como estatística e geram impacto tático/disciplinar conforme regras definidas.

RD30. Critério de vitória  
Em caso de empate, o sistema suporta prorrogação e tiros de 7 metros decisivos, registrando cada fase como parte do mesmo jogo.

RD31. Duração do jogo  
A duração do jogo é configurável por competição.

RD32. Intervalo  
O intervalo influencia o controle de tempo e eventos.

RD33. Prorrogação  
A prorrogação segue regras próprias por categoria e competição.

RD34. Tiros de 7m decisivos - elegibilidade  
Todas as atletas relacionadas podem cobrar tiros de 7 metros decisivos.

RD35. Tiros de 7m decisivos - registro  
O sistema registra quem cobrou e o resultado, sem impor ordem fixa.

RD36. Substituições durante exclusão  
Durante exclusão de 2 minutos, substituições são permitidas normalmente, respeitando o impacto numérico.

RD37. Retorno da exclusão  
O retorno da atleta excluída ocorre apenas ao término do tempo regulamentar da exclusão.

RD38. Acúmulo de exclusões  
O sistema aplica automaticamente cartão vermelho após três exclusões na mesma partida.

RD39. Faltas ofensivas  
Faltas ofensivas geram impacto tático automático, além do registro estatístico.

RD40. Vantagem  
A aplicação de vantagem é ignorada no modelo.

RD41. Defesas de goleira  
Defesas da goleira são registradas como estatística específica.

RD42. Rebotes  
Rebotes não são registrados no modelo estatístico.

RD43. Contra-ataque  
Contra-ataques são registrados manualmente como evento.

RD44. Assistência  
Assistência possui definição rígida e padronizada no sistema.

RD45. Arremesso bloqueado  
Arremesso bloqueado é ação defensiva separada.

RD46. Bolas perdidas  
Bolas perdidas são registradas por tipo.

RD47. Recuperação de bola  
Recuperação de bola é evento próprio, não inferido automaticamente.

RD48. Faltas defensivas  
Faltas defensivas impactam o controle disciplinar automático, além do registro estatístico.

RD49. Tempo efetivo de jogo  
O sistema calcula tempo efetivo em quadra por atleta, além do tempo corrido.

RD50. Encerramento antecipado do jogo  
O jogo pode ser encerrado antecipadamente conforme regra da competição.

RD51. Tipos de jogo  
O sistema distingue: jogo oficial, jogo amistoso, treino-jogo. Cada tipo possui tratamento estatístico próprio.

RD52. Convivência de jogos  
Jogos oficiais e amistosos podem coexistir na mesma competição.

RD53. Mando de jogo  
O mando de jogo não gera impacto estatístico.

RD54. Local do jogo  
O local do jogo é informativo/formativo, sem impacto em regras.

RD55. Placar por período  
O sistema registra placar parcial por período.

RD56. WO  
Vitória por ausência (WO) é suportada.

RD57. Abandono de jogo  
O sistema suporta registro de abandono de jogo.

RD58. Empate  
Empates são permitidos em competições.

RD59. Controle do relógio  
O relógio para automaticamente em exclusões e pedidos de tempo.

RD60. Tempo efetivo  
O tempo efetivo considera apenas paralisações oficiais.

RD61. Prorrogação e estatísticas  
Estatísticas da prorrogação são separadas do tempo normal.

RD62. Múltiplos jogos no mesmo dia  
A atleta pode atuar em múltiplos jogos no mesmo dia; o sistema permite, emite alerta e monitora carga total, notificando coordenador e treinador.

RD63. Limite diário  
Não existe limite adicional de jogos por dia além da regra de alerta de carga.

RD64. Banco de reservas  
Atleta pode iniciar no banco e não entrar em quadra sem penalidade.

RD65. Ausência não justificada  
Ausência não justificada gera impacto disciplinar.

RD66. Participação no banco  
Estar no banco conta como participação disciplinar oficial.

RD67. Advertência verbal  
Advertência verbal não é registrada.

RD68. Cartão amarelo  
Cartão amarelo não gera impacto automático futuro.

RD69. Duplo amarelo  
Não existe conceito de duplo amarelo.

RD70. Suspensão automática  
Não existe suspensão automática por acúmulo disciplinar.

RD71. Defesa com os pés  
Defesa com os pés da goleira não é estatística separada.

RD72. Saída da goleira  
Saída da goleira da área não é registrada como evento.

RD73. Interceptação defensiva  
Interceptação defensiva é estatística própria.

RD74. Bloqueio defensivo  
Bloqueio defensivo não gera posse automática.

RD75. Defesa de 7m  
Defesa de tiro de 7m é estatística distinta.

RD76. Arremesso após falta  
Arremesso após falta não é tratado como situação especial.

RD77. Contra-ataque  
Arremesso em contra-ataque possui estatística própria.

RD78. Gol contra  
Gol contra é registrado no sistema.

RD79. Gol anulado  
Não existe registro de gol anulado.

RD80. Zona de arremesso  
O local/zona do arremesso é registrado.

RD81. Superioridade/inferioridade numérica  
O sistema registra situações ativas de superioridade/inferioridade numérica.

RD82. Sistema ofensivo  
Mudanças de sistema ofensivo são registradas.

RD83. Jogadas ensaiadas  
Jogadas ensaiadas são identificadas como tal.

RD84. Marcação individual  
Marcação individual é registrada como evento tático.

RD85. Estatísticas em tempo real  
Estatísticas são calculadas em tempo real para Live-Scouting e Logs de Atividade. Relatórios, dashboards e rankings usam dados validados.

RD86. Correções e ranking  
Correções estatísticas afetam rankings automaticamente.

RD87. Estatísticas após troca de equipe  
Estatísticas da atleta permanecem preservadas após troca de equipe.

RD88. Comparação entre temporadas  
Estatísticas são comparáveis entre temporadas diferentes.

RD89. Jogos de referência técnica  
Jogos podem ser marcados como referência técnica.

RD90. Reset disciplinar por temporada  
Penalidades disciplinares são resetadas ao final de cada temporada.

RD91. Ranking coletivo  
O ranking coletivo é definido exclusivamente pelo saldo de gols.

## 4. Visibilidade do Perfil Atleta

1. Dados pessoais (próprios)  
A atleta pode visualizar: nome completo, apelido esportivo, data de nascimento, categoria da temporada, equipes vinculadas, posições registradas, foto (se existir). Não pode editar dados estruturais.

2. Estado esportivo  
A atleta pode visualizar: estado atual, histórico de estados. Não pode alterar o próprio estado nem ver justificativas médicas detalhadas.

3. Dados médicos e sensíveis (LGPD)  
A atleta pode visualizar: status esportivo (apta/inapta), restrições gerais. Não pode visualizar: CID, diagnóstico detalhado, observações médicas internas, notas confidenciais.

4. Treinos  
A atleta pode visualizar: calendário de treinos, presença, carga individual (quando liberado), observações públicas. Não pode visualizar: carga planejada do grupo, avaliações internas, comparativos com outras atletas.

5. Jogos  
A atleta pode visualizar: jogos convocados, jogos não convocados (agenda), resultado final, tempo em quadra, posição exercida, eventos pessoais. Não pode visualizar: anotações táticas, avaliações de outras atletas, decisões internas de escalação.

6. Estatísticas individuais  
A atleta pode visualizar: estatísticas individuais completas, evolução por jogo/temporada, comparativo consigo mesma. Não pode visualizar: ranking completo da equipe, estatísticas de outras atletas (exceto se liberado futuramente).

7. Convocações e comunicação  
A atleta pode: receber convocações, confirmar presença, recusar convocação com justificativa, visualizar comunicados oficiais. Não pode: criar comunicados, responder fora do fluxo previsto.

8. Disciplina  
A atleta pode visualizar: cartões, exclusões, suspensões vigentes, histórico disciplinar pessoal. Não pode visualizar: regras internas de punição, histórico disciplinar de outras atletas.

9. Histórico esportivo  
A atleta pode visualizar: temporadas passadas, equipes anteriores, estatísticas históricas pessoais, mesmo após troca de equipe, mudança de categoria ou fim de temporada.

10. O que a atleta nunca vê  
Dados de outras atletas, relatórios técnicos, dados financeiros, dados médicos detalhados, logs de auditoria, pendências administrativas, rankings estratégicos internos.

Regra-síntese (Atleta)  
A atleta vê tudo que diz respeito a si mesma, nada que exponha outras pessoas e nada que comprometa decisão técnica ou governança.

## 5. Regras de Participação da Atleta — Definitivas

RP1. Definição de participação  
Participação disciplinar é definida pela presença em súmula (banco + quadra). Participação estatística exige tempo efetivo em quadra.

RP2. Convocada sem entrada em quadra  
Atleta convocada que não entra em quadra é participante disciplinar, mas não é participante estatística.

RP3. Convocação obrigatória  
Participação em jogo exige convocação/lista oficial prévia; participação sem convocação é bloqueada pelo sistema.

RP4. Escopo da participação  
A participação da atleta é considerada em jogos, treinos e atividades extras (avaliações, testes, captação).

RP5. Ausência em treino  
Ausência em treino gera carga = 0, impacto negativo no percentual de assiduidade e reflexo nas métricas do período.

RP6. Participação em treino  
Toda participação em treino gera métricas esportivas obrigatórias, incluindo dados objetivos e subjetivos.

RP7. Atleta lesionada  
Atleta lesionada pode participar de treinos adaptados; lesão não implica exclusão automática de atividades.

RP8. Treino adaptado  
Treino adaptado é registrado como tipo específico de participação.

RP9. Atleta dispensada  
Atleta dispensada aparece nos relatórios da temporada e no histórico, mas não participa de novos eventos.

RP10. Validação da participação  
Toda participação registrada deve ser validada pelo Coordenador.

RP11. Contestação de participação  
A atleta pode contestar registros incorretos por solicitação formal ao Coordenador.

RP12. Participação parcial  
Participações parciais exigem registro obrigatório de tempo efetivo.

RP13. Impacto da participação  
A participação impacta estatísticas objetivas, avaliações internas subjetivas e relatórios esportivos/operacionais.

RP14. Múltiplas equipes no mesmo dia  
A atleta pode participar de múltiplas equipes no mesmo dia; o sistema permite, emite alerta e monitora carga total, notificando coordenador e treinador.

RP15. Amistoso vs jogo oficial  
Participações em jogos amistosos e oficiais são registradas normalmente e contam separadamente para estatísticas e índices.

RP16. Atleta suspensa  
Atleta suspensa pode ser relacionada, mas sua participação em quadra é irregular e o sistema sinaliza a irregularidade.

RP17. Alerta por restrição  
A participação é sinalizada como irregular se houver punição disciplinar ativa ou restrição médica ativa.

RP18. Atividade sem equipe  
A atleta pode participar de atividades sem equipe vinculada, desde que associadas à Equipe Institucional/Grupo de Avaliação.

RP19. Dupla natureza do registro  
Toda participação gera registro esportivo e registro administrativo.

RP20. Mudança de equipe  
Ao mudar de equipe, a participação passada permanece vinculada à equipe original, preservando contexto histórico.

Regra-síntese de participação  
A atleta participa quando está presente, com controle, validação e rastreabilidade, sem reescrever o passado e sem perder contexto esportivo.

## 6. Regras de Configuração do Banco - V1

RDB1. SGBD e extensões  
Banco PostgreSQL 17 (Neon) com extensão pgcrypto habilitada para uso de gen_random_uuid().

RDB2. Chaves primárias e nomes  
PKs são UUID com default gen_random_uuid(). Constraints e índices usam nomes semânticos (pk_, fk_, ux_, ix_, ck_, trg_).

RDB2.1. Exceção de PK (allowlist fechada)  
Tabelas técnicas/lookup/sistema que podem usar integer/smallint como PK:
- `roles` (lookup de papéis - R4)
- `categories` (lookup de categorias - R15)
- `permissions` (lookup de permissões)
- `role_permissions` (junction table)
- `alembic_version` (técnica - migrations)

Qualquer tabela fora desta lista é considerada tabela de domínio e DEVE usar UUID com default gen_random_uuid().

RDB3. Timezone e colunas temporais  
Colunas temporais usam timestamptz em UTC; conversão e exibição são responsabilidade da UI.

RDB4. Exclusão lógica  
Tabelas de domínio usam deleted_at + deleted_reason. deleted_reason é obrigatória quando deleted_at não é null. DELETE físico é bloqueado por trigger.

RDB4.1. Exceção de Soft Delete (allowlist fechada)  
Tabelas que NÃO requerem deleted_at/deleted_reason:
- `roles` (lookup imutável)
- `categories` (lookup imutável)
- `permissions` (lookup imutável)
- `role_permissions` (junction table imutável)
- `alembic_version` (técnica - migrations)
- `audit_logs` (excluída por RDB5 - append-only, nunca deletada)

Qualquer tabela fora desta lista é tabela de domínio e DEVE implementar soft delete completo.

RDB5. Auditoria imutável  
audit_logs é append-only: apenas INSERT. UPDATE/DELETE são bloqueados por trigger. Logs registram quem, quando, ação, contexto e old/new.

RDB6. Super Administrador único  
Existe exatamente um Super Administrador. Unicidade garantida por índice parcial único em users (is_superadmin = true); seed inicial cria esse usuário.

RDB7. Papéis e estados  
Papéis são definidos em tabela de roles. Estado da atleta é validado por CHECK e possui histórico dedicado com FK.

RDB8. Temporadas  
Temporadas possuem start_date e end_date com CHECK start_date < end_date. Status "ativa" é derivado por data; sem EXCLUDE no MVP. (obrigação do backend)

RDB9. Vínculos e exclusividade  
membership possui start_at/end_at e índices parciais para garantir 1 vínculo ativo por pessoa (staff) e 1 vínculo ativo por pessoa+temporada (atleta).

RDB10. Múltiplos vínculos de atleta (atualização V1.1)  
team_registrations usa uma linha por período ativo (start_at, end_at) por pessoa+equipe+temporada. Reativações criam novas linhas (novo UUID), sem reabrir a anterior. O backend garante que períodos não se sobreponham para a mesma pessoa+equipe+temporada. Convocações/participações referenciam a linha vigente no momento do evento.

RDB11. Categorias globais  
Categorias são globais com min_age/max_age e CHECK min_age <= max_age. Sem EXCLUDE de sobreposição no MVP.

RDB12. Correções de estatística  
Correções exigem admin_note obrigatório e geram log em audit_logs com old/new, sem versionamento completo.

RDB13. Imutabilidade de jogos e treinos  
Trigger bloqueia UPDATE em jogo finalizado. Reabertura é auditada. Treinos com mais de 24h exigem admin_note para edição.

RDB14. Seed mínimo  
Banco novo deve conter: org única, roles, superadmin e uma temporada. Categorias e equipe são opcionais.

### 6.1 Esquema técnico (temporadas e jogos)

6.1.1 Temporadas — estados, campos e transições  
- Campos adicionais recomendados (além de start_date e end_date):  
  - canceled_at timestamptz NULL (cancelamento pré-início; ver RF5.1)  
  - interrupted_at timestamptz NULL (interrupção pós-início; ver RF5.2)

- Status derivado (não armazenado como enum, exceto sinalizadores não-deriváveis):  
  - planejada: now < start_date AND canceled_at IS NULL  
  - ativa: start_date <= now AND now <= end_date AND interrupted_at IS NULL AND canceled_at IS NULL  
  - interrompida: interrupted_at IS NOT NULL AND canceled_at IS NULL  
  - cancelada: canceled_at IS NOT NULL (somente permitido se não houver dados vinculados; ver RF5.1)  
  - encerrada: now > end_date AND canceled_at IS NULL (independente de interrupção)

- Transições permitidas (sempre auditadas quando não derivadas por data):  
  - planejada -> ativa: automática por data (virada de start_date)  
  - planejada -> cancelada: ação administrativa auditada; pré-condição “sem dados vinculados”  
  - ativa -> interrompida: ação administrativa auditada; na V1 não há retorno para ativa  
  - ativa/interrompida -> encerrada: automática por data (virada de end_date); não há encerramento manual

- Efeitos operacionais por estado:  
  - interrompida: bloqueia criação/edição de novos eventos a partir de interrupted_at; cancela jogos futuros (status “cancelado”/deleted_reason apropriado); vínculos continuam válidos no histórico; dashboards não recebem novos dados dessa temporada após a interrupção.  
  - cancelada: temporada fica inelegível para operação; objetos ligados a ela permanecem em histórico apenas se existirem (idealmente, cancelamento só ocorre sem dados; ver RF5.1); nada produz efeito operacional/analítico.

6.1.2 Jogos — triggers de bloqueio e reabertura  
- Estados de jogo:  
  - rascunho  
  - em_revisao  
  - finalizado

- Trigger de bloqueio (TRG_games_block_update_finalized):  
  - Bloqueia qualquer UPDATE em jogos com status=finalizado.  
  - Exceção: permitir UPDATE que altere exclusivamente o status de finalizado -> em_revisao, quando a ação for do Coordenador/Dirigente, com audit_log obrigatório (acao=game_reopen, actor_id, timestamp, old/new).

- Reabertura (sem snapshot/versão nova, conforme RF15 V1.1):  
  - Operação: set status=em_revisao; registrar audit_log “game_reopen”.  
  - Efeito: estatísticas deixam de alimentar dashboards/rankings até nova finalização (conforme RD85/RF29).  
  - Edits permitidos: enquanto em_revisao, o registro permite atualizações e correções (R23/R24), todas auditadas.

- Nova finalização:  
  - Operação: set status=finalizado; registrar audit_log “game_finalize”; reativar trigger de bloqueio.  
  - Dashboards/rankings passam a refletir o jogo novamente quando finalizado.

- Exclusão lógica:  
  - Operação: set deleted_at + deleted_reason (obrigatório); registrar audit_log “game_soft_delete”; permanece não editável; visível somente em histórico.

## 7. Organização das Regras por Camada de Configuração

Classificação por onde cada regra é configurada/enforced no sistema.

### 7.1 Apenas no DB
- R: R4, R20, R29, R35
- RDB: RDB1, RDB2, RDB3, RDB4, RDB5, RDB6, RDB7, RDB8, RDB9, RDB10, RDB11, RDB12, RDB13, RDB14

### 7.2 DB + Backend
- R: R1, R2, R3, R5, R6, R7, R8, R11, R12, R13, R15, R16, R17, R19, R23, R24, R25, R28, R30, R31, R32, R33, R34, R37, R38, R39
- RF: RF2
- RDB: (removido RDB15 inexistente)

### 7.3 Apenas no Backend
- R: R10, R21, R22, R26, R27, R36, R43
- RF: RF5, RF21, RF31
- RD: RD1, RD2, RD3, RD5, RD7, RD8, RD9, RD10, RD14, RD15, RD18, RD20, RD27, RD30, RD33, RD34, RD38, RD40, RD42, RD49, RD50, RD51, RD52, RD53, RD54, RD58, RD60, RD61, RD63, RD64, RD66, RD67, RD68, RD69, RD70, RD71, RD72, RD74, RD76, RD79, RD86, RD87, RD88, RD90, RD91
- RP: RP1, RP2, RP4, RP5, RP6, RP9, RP13, RP15, RP19, RP20
- Síntese: Regra-síntese de participação

### 7.4 Backend + Frontend
- R: R9, R14, R18, R40, R41, R42
- RF: RF1, RF3, RF4, RF6, RF7, RF8, RF9, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17, RF18, RF19, RF20, RF22, RF23, RF24, RF25, RF26, RF27, RF28, RF29, RF30
- RD: RD4, RD6, RD11, RD12, RD13, RD16, RD17, RD19, RD21, RD22, RD23, RD24, RD25, RD26, RD28, RD29, RD31, RD32, RD35, RD36, RD37, RD39, RD41, RD43, RD44, RD45, RD46, RD47, RD48, RD55, RD56, RD57, RD59, RD62, RD65, RD73, RD75, RD77, RD78, RD80, RD81, RD82, RD83, RD84, RD85, RD89
- RP: RP3, RP7, RP8, RP10, RP11, RP12, RP14, RP16, RP17, RP18
- Visibilidade do Perfil Atleta: itens 1 a 10 e Regra-síntese (Atleta)

### 7.5 Apenas no Front
- Nenhuma