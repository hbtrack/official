## PRD: Sistema "Comissão Digital" (HB Track)

### 1. Contexto e Problema

Treinadores de handebol "solo" enfrentam uma sobrecarga de tarefas burocráticas e manuais, como o planejamento de ciclos em planilhas e a edição exaustiva de vídeos. A comunicação via WhatsApp é caótica, resultando na perda de informações táticas cruciais. Além disso, o acompanhamento psicológico e o controle de carga física/mental são frequentemente negligenciados por falta de tempo ou ferramentas acessíveis, o que limita a evolução dos atletas e a performance da equipe.

### 2. Objetivo

Profissionalizar a gestão técnica de equipes de handebol através de uma **Comissão Técnica Virtual**. O foco é automatizar a análise tática (via IA de vídeo) e o suporte psicológico (via IA conversacional), permitindo que o treinador reduza em **50% o tempo gasto com burocracia** e tome decisões baseadas em dados precisos.

### 3. Público-alvo

* **Treinador Principal:** Gestor que planeja, analisa dados de scout e decide a estratégia.
* **Atletas:** Usuários finais que recebem treinos e feedbacks, e interagem com a IA para relatar estado físico e mental.

### 4. Escopo

#### **In (Prioridade Atual)**

* **Planejamento de Ciclos:** Estruturação de Macrociclos, Mesociclos e Microciclos.
* **IA de Vídeo:** Edição automática de clipes e cortes por atleta/lance (Gols, Erros, Defesas).
* **Comunicação Estruturada:** Substituição do WhatsApp por canais de tópicos oficiais e chat conversacional com IA.
* **Inteligência Tática:** Scout em tempo real, sugestão de exercícios e planos de jogo.
* **Saúde Mental:** Coleta de dados de bem-estar via interface de diálogo natural.

#### **Out (Futuro)**

* Transmissão de jogos via streaming.
* Rede Social para treinadores e atletas do clube
* Chat social/aberto entre atletas (foco apenas em comunicação técnica).

### 5. Requisitos Funcionais

1. **Gestão de Ciclos:** Automação e cronograma de Macrociclo, Mesociclo e Microciclo.
2. **Registro de Scout:** Interface rápida para marcação de ações (gols, faltas, defesas, perdas de bola).
3. **Dashboard de Performance:** Geração de gráficos automáticos individuais e coletivos.
4. **Recomendador de Treinos:** Sugestão de exercícios baseada nos erros detectados pelo scout/vídeo.
5. **Plano de Jogo:** Ferramenta estratégica baseada no cruzamento de dados Equipe vs Adversário.
6. **Painel do Atleta:** Hub de visualização de treinos, feedbacks explicados pela IA e feedback de vídeo e evolução técnica/tática/física.
7. **Interface de Diálogo (IA Psicóloga):** Conversa natural com o atleta para extrair humor, estresse, sono e dores (sem formulários).
8. **Perfil Comportamental:** Identificação do perfil psicológico para melhor abordagem do treinador.
9. **Ajuste Dinâmico de Treino:** Alertas ao treinador para reduzir carga em caso de risco de *burnout* ou lesão detectado pela IA.
10. **Motor de Edição IA:** Identificação automática de padrões de movimento em vídeos brutos.
11. **Mural de Avisos com Confirmação:** Protocolo de leitura ativa ("Ciente") para mensagens táticas importantes.
12. **Canais por Tópicos:** Separação de conversas por temas (Tático, Técnico, Saúde Mental).

### 6. Requisitos Não Funcionais

* **UX (Experiência):** Planejamento de microciclo em menos de 5 minutos; interface amigável e esportiva.
* **Disponibilidade:** Módulo de Scout deve funcionar 100% offline com sincronização posterior.
* **Performance:** Registro de lances em menos de 100ms.
* **Segurança:** Conteúdo bruto das conversas íntimas da IA com atletas é restrito (o treinador recebe apenas alertas e resumos de risco).

### 7. Restrições e Gestão de Dados

* **Privacidade (LGPD):** Proteção rigorosa de dados de menores e direito ao esquecimento.
* **Hardware:** Processamento de vídeo em nuvem (servidor) para não sobrecarregar dispositivos móveis.
* **Custo:** Sistema escalável e acessível para equipes de pequeno porte.
* **Retenção de Dados:** Treinador define se dados de atletas desligados são excluídos ou arquivados para futura reativação.

### 8. Métricas de Sucesso

* **Produtividade:** Redução de 50% no tempo de planejamento e edição de vídeo do treinador.
* **Engajamento:** 90% dos atletas interagindo com a IA 3x por semana e 80% visualizando feedbacks de vídeo.
* **Migração:** 100% da comunicação técnica saindo do WhatsApp para o HB Track.
* **Eficiência:** Redução de erros de posicionamento detectados pela IA após os ciclos de feedback.

### 9. Riscos e Suposições

* **Viés da IA:** Risco de interpretação errada de gírias (Solução: Atleta pode contestar alertas).
* **Infraestrutura:** Suposição de que o treinador pode gravar jogos de uma posição elevada (tripé).
* **Resistência:** Atletas podem omitir dados por medo de punição ou preferir o WhatsApp por hábito.