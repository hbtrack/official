"""Seed exercise_tags with complete handball taxonomy

Revision ID: 0052
Revises: 0051
Create Date: 2026-01-22

Insere taxonomia hierárquica de tags para exercícios de handebol.
12 categorias top-level com filhos e sub-filhos.

Características:
- UUIDs determinísticos (uuid5) para referência futura
- is_active=True e approved_at=NOW() para todas
- ON CONFLICT (name) DO NOTHING para idempotência
- display_order sequencial por nível

Categorias EXCLUÍDAS (viram campos estruturados):
- Relação Numérica → campos players_attack, players_defense
- Capacidades Físicas → campo de texto ou enum
- Intensidade e Carga → já existe intensity_target em sessões
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from uuid import uuid5, UUID, NAMESPACE_DNS
from datetime import datetime

revision: str = '0052'
down_revision: Union[str, None] = '0051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Namespace para gerar UUIDs determinísticos
NAMESPACE = UUID('a1b2c3d4-e5f6-7890-abcd-ef1234567890')


def gen_uuid(name: str) -> str:
    """Gera UUID determinístico baseado no nome."""
    return str(uuid5(NAMESPACE, name))


def upgrade() -> None:
    """Insere taxonomia completa de tags de exercícios."""

    # Timestamp para approved_at
    now = datetime.utcnow().isoformat()

    # ==========================================================================
    # DEFINIÇÃO DA TAXONOMIA
    # Formato: (name, parent_name, display_order, description)
    # parent_name=None indica tag raiz
    # ==========================================================================

    tags = [
        # ======================================================================
        # A. FASE DO JOGO
        # ======================================================================
        ("Fase do Jogo", None, 1, "Momento do jogo (ataque, defesa, transições)"),
        ("Ataque Posicional", "Fase do Jogo", 1, "Ataque organizado contra defesa montada"),
        ("Transição Ofensiva", "Fase do Jogo", 2, "Passagem de defesa para ataque"),
        ("Contra-ataque", "Fase do Jogo", 3, "Ataque rápido em superioridade numérica"),
        ("Segunda Onda", "Fase do Jogo", 4, "Continuação do contra-ataque com apoio"),
        ("Transição Defensiva", "Fase do Jogo", 5, "Passagem de ataque para defesa"),
        ("Retorno Defensivo", "Fase do Jogo", 6, "Balanço e recuperação defensiva"),
        ("Defesa Organizada", "Fase do Jogo", 7, "Defesa posicional montada"),

        # ======================================================================
        # B. OBJETIVO PEDAGÓGICO
        # ======================================================================
        ("Objetivo Pedagógico", None, 2, "Foco de aprendizagem do exercício"),
        ("Técnica", "Objetivo Pedagógico", 1, "Aprimoramento de gestos técnicos"),
        ("Tática Individual", "Objetivo Pedagógico", 2, "Tomada de decisão individual"),
        ("Tática Coletiva", "Objetivo Pedagógico", 3, "Coordenação de grupo"),
        ("Tomada de Decisão", "Objetivo Pedagógico", 4, "Leitura de jogo e escolhas"),
        ("Condicionamento Integrado", "Objetivo Pedagógico", 5, "Físico integrado ao técnico-tático"),
        ("Aquecimento", "Objetivo Pedagógico", 6, "Ativação e preparação"),
        ("Recuperação", "Objetivo Pedagógico", 7, "Regenerativo e volta à calma"),
        ("Avaliação", "Objetivo Pedagógico", 8, "Testes e diagnósticos"),

        # ======================================================================
        # C. FUNDAMENTOS TÉCNICOS
        # ======================================================================
        ("Fundamentos Técnicos", None, 3, "Gestos técnicos do handebol"),

        # C.1 Passe
        ("Passe", "Fundamentos Técnicos", 1, "Tipos de passe"),
        ("Passe de Ombro", "Passe", 1, "Passe clássico de ombro"),
        ("Passe Picado", "Passe", 2, "Passe com quique no solo"),
        ("Passe Por Cima", "Passe", 3, "Passe por cima do defensor"),
        ("Passe Longo", "Passe", 4, "Passe de longa distância"),
        ("Passe Sob Pressão", "Passe", 5, "Passe em situação de marcação"),

        # C.2 Recepção
        ("Recepção", "Fundamentos Técnicos", 2, "Tipos de recepção"),
        ("Recepção em Movimento", "Recepção", 1, "Recepção durante deslocamento"),
        ("Recepção Sob Contato", "Recepção", 2, "Recepção com oposição física"),
        ("Recepção em Salto", "Recepção", 3, "Recepção aérea"),

        # C.3 Drible
        ("Drible", "Fundamentos Técnicos", 3, "Condução de bola"),
        ("Drible de Progressão", "Drible", 1, "Drible para avançar"),
        ("Drible de Proteção", "Drible", 2, "Drible protegendo a bola"),
        ("Mudança de Direção", "Drible", 3, "Drible com mudança de direção"),

        # C.4 Finta
        ("Finta", "Fundamentos Técnicos", 4, "Fintas e enganos"),
        ("Finta de Corpo", "Finta", 1, "Engano com movimento corporal"),
        ("Finta de Braço", "Finta", 2, "Engano com movimento de braço"),
        ("Finta de Velocidade", "Finta", 3, "Mudança de ritmo"),
        ("Finta de Direção", "Finta", 4, "Mudança de trajetória"),

        # C.5 Arremesso
        ("Arremesso", "Fundamentos Técnicos", 5, "Finalizações"),
        ("Arremesso em Apoio", "Arremesso", 1, "Arremesso com pés no solo"),
        ("Arremesso em Salto", "Arremesso", 2, "Arremesso em suspensão"),
        ("Arremesso em Suspensão", "Arremesso", 3, "Arremesso no ponto alto do salto"),
        ("Arremesso com Queda", "Arremesso", 4, "Arremesso com queda lateral"),
        ("Arremesso Rosca", "Arremesso", 5, "Arremesso com efeito"),
        ("Arremesso Vaselina", "Arremesso", 6, "Arremesso por cima do goleiro"),
        ("Arremesso de 7m", "Arremesso", 7, "Cobrança de tiro de 7 metros"),
        ("Arremesso de 9m", "Arremesso", 8, "Arremesso de longa distância"),

        # C.6 Bloqueio Ofensivo
        ("Bloqueio Ofensivo", "Fundamentos Técnicos", 6, "Bloqueio para liberação de companheiro"),

        # C.7 Pivô
        ("Técnica de Pivô", "Fundamentos Técnicos", 7, "Fundamentos específicos do pivô"),
        ("Selagem", "Técnica de Pivô", 1, "Bloqueio do defensor"),
        ("Giro de Pivô", "Técnica de Pivô", 2, "Rotação para finalização"),
        ("Recepção em Contato", "Técnica de Pivô", 3, "Receber sob marcação"),
        ("Finalização de Pivô", "Técnica de Pivô", 4, "Arremessos típicos do pivô"),

        # C.8 Contato
        ("Contato", "Fundamentos Técnicos", 8, "Engajamento físico"),
        ("1x1 com Contato", "Contato", 1, "Duelo individual com contato"),
        ("Proteção de Bola", "Contato", 2, "Manter posse sob pressão"),

        # ======================================================================
        # D. PRINCÍPIOS OFENSIVOS
        # ======================================================================
        ("Princípios Ofensivos", None, 4, "Conceitos táticos de ataque"),
        ("Fixar e Soltar", "Princípios Ofensivos", 1, "Atrair defensor e liberar companheiro"),
        ("Criar Superioridade", "Princípios Ofensivos", 2, "Situações de vantagem numérica"),
        ("2x1", "Criar Superioridade", 1, "Superioridade 2 contra 1"),
        ("3x2", "Criar Superioridade", 2, "Superioridade 3 contra 2"),
        ("4x3", "Criar Superioridade", 3, "Superioridade 4 contra 3"),
        ("Continuidade", "Princípios Ofensivos", 3, "Circulação e fluidez de bola"),
        ("Ataque ao Espaço", "Princípios Ofensivos", 4, "Exploração de intervalos"),
        ("Intervalo", "Ataque ao Espaço", 1, "Espaço entre defensores"),
        ("Costas do Defensor", "Ataque ao Espaço", 2, "Movimento nas costas"),
        ("Jogo com Pivô", "Princípios Ofensivos", 5, "Utilização do pivô"),
        ("Alimentação do Pivô", "Jogo com Pivô", 1, "Passes para o pivô"),
        ("Pivô Inside", "Jogo com Pivô", 2, "Pivô entrando por dentro"),
        ("Cruzamentos com Pivô", "Jogo com Pivô", 3, "Trocas envolvendo pivô"),
        ("Cruzamentos", "Princípios Ofensivos", 6, "Trocas de posição"),
        ("Cruzamento Simples", "Cruzamentos", 1, "Troca de duas posições"),
        ("Cruzamento Duplo", "Cruzamentos", 2, "Troca envolvendo três jogadores"),
        ("Cruzamento com Bloqueio", "Cruzamentos", 3, "Troca com bloqueio ofensivo"),
        ("Permutas", "Princípios Ofensivos", 7, "Trocas de posições dinâmicas"),
        ("Largura e Profundidade", "Princípios Ofensivos", 8, "Ocupação de espaços"),
        ("Finalização sob Pressão", "Princípios Ofensivos", 9, "Arremesso em situação de marcação"),

        # ======================================================================
        # E. PRINCÍPIOS DEFENSIVOS
        # ======================================================================
        ("Princípios Defensivos", None, 5, "Conceitos táticos de defesa"),
        ("Contenção", "Princípios Defensivos", 1, "Atraso do atacante"),
        ("Cobertura", "Princípios Defensivos", 2, "Apoio ao companheiro"),
        ("Dobra", "Princípios Defensivos", 3, "Ajuda defensiva 2x1"),
        ("Flutuação", "Princípios Defensivos", 4, "Antecipação de linha de passe"),
        ("Linha de Passe", "Princípios Defensivos", 5, "Controle de corredores"),
        ("Fechar Linha", "Linha de Passe", 1, "Bloquear corredor de passe"),
        ("Interceptar", "Linha de Passe", 2, "Roubar bola no passe"),
        ("Bloqueio Defensivo", "Princípios Defensivos", 6, "Bloqueio de arremesso"),
        ("Defesa do Pivô", "Princípios Defensivos", 7, "Marcação específica do pivô"),
        ("Defesa Pivô Frente", "Defesa do Pivô", 1, "Marcação pela frente"),
        ("Defesa Pivô Lado", "Defesa do Pivô", 2, "Marcação pelo lado"),
        ("Defesa Pivô Trás", "Defesa do Pivô", 3, "Marcação por trás"),
        ("Negação de Linha", "Defesa do Pivô", 4, "Impedir passe para pivô"),
        ("Balanço Defensivo", "Princípios Defensivos", 8, "Retorno e organização"),
        ("Proteção do Centro", "Princípios Defensivos", 9, "Priorizar zona central"),

        # ======================================================================
        # F. SISTEMAS E ESTRUTURAS
        # ======================================================================
        ("Sistemas e Estruturas", None, 6, "Formações táticas"),

        # F.1 Sistemas Defensivos
        ("Sistemas Defensivos", "Sistemas e Estruturas", 1, "Formações de defesa"),
        ("Defesa 6:0", "Sistemas Defensivos", 1, "Seis jogadores na linha"),
        ("Defesa 5:1", "Sistemas Defensivos", 2, "Cinco na linha, um avançado"),
        ("Defesa 3:2:1", "Sistemas Defensivos", 3, "Três linhas de marcação"),
        ("Defesa 4:2", "Sistemas Defensivos", 4, "Quatro na linha, dois avançados"),
        ("Defesa Mista", "Sistemas Defensivos", 5, "Combinação de individual e zona"),
        ("Defesa Individual", "Sistemas Defensivos", 6, "Marcação homem a homem"),
        ("Pressão Quadra Toda", "Sistemas Defensivos", 7, "Marcação desde o ataque"),
        ("Pressão Meia Quadra", "Sistemas Defensivos", 8, "Pressão a partir do meio"),

        # F.2 Sistemas Ofensivos
        ("Sistemas Ofensivos", "Sistemas e Estruturas", 2, "Formações de ataque"),
        ("Ataque com 2 Pivôs", "Sistemas Ofensivos", 1, "Formação com dois pivôs"),
        ("Ataque 7x6", "Sistemas Ofensivos", 2, "Goleiro-linha em superioridade"),
        ("Ataque 6x7", "Sistemas Ofensivos", 3, "Ataque em inferioridade"),

        # F.3 Bola Parada
        ("Bola Parada", "Sistemas e Estruturas", 3, "Situações de bola parada"),
        ("Tiro Livre", "Bola Parada", 1, "Cobrança de falta"),
        ("Lateral", "Bola Parada", 2, "Cobrança de lateral"),
        ("Saída de Gol", "Bola Parada", 3, "Reposição do goleiro"),
        ("Cobrança de 7m", "Bola Parada", 4, "Penalidade"),
        ("Reposição Rápida", "Bola Parada", 5, "Saída rápida de bola"),

        # ======================================================================
        # G. POSIÇÕES E PAPÉIS
        # ======================================================================
        ("Posições e Papéis", None, 7, "Funções específicas dos jogadores"),
        ("Goleiro", "Posições e Papéis", 1, "Guarda-redes"),
        ("Ponta", "Posições e Papéis", 2, "Jogador de extremidade"),
        ("Ponta Esquerda", "Ponta", 1, "Extremo esquerdo"),
        ("Ponta Direita", "Ponta", 2, "Extremo direito"),
        ("Armador", "Posições e Papéis", 3, "Jogadores de 1ª linha"),
        ("Armador Esquerdo", "Armador", 1, "Lateral esquerdo"),
        ("Armador Central", "Armador", 2, "Central"),
        ("Armador Direito", "Armador", 3, "Lateral direito"),
        ("Pivô", "Posições e Papéis", 4, "Jogador de 6 metros"),
        ("Especialista Defensivo", "Posições e Papéis", 5, "Defensor específico"),
        ("Goleiro-Linha", "Posições e Papéis", 6, "Goleiro jogando na linha"),
        ("Papel Defensivo", "Posições e Papéis", 7, "Funções na defesa"),
        ("1º Defensor", "Papel Defensivo", 1, "Marcador direto"),
        ("2º Defensor", "Papel Defensivo", 2, "Cobertura e ajuda"),

        # ======================================================================
        # H. FORMATO DO EXERCÍCIO
        # ======================================================================
        ("Formato do Exercício", None, 8, "Estrutura metodológica"),

        # H.1 Oposição
        ("Oposição", "Formato do Exercício", 1, "Nível de resistência"),
        ("Sem Oposição", "Oposição", 1, "Exercício sem defensor"),
        ("Oposição Passiva", "Oposição", 2, "Defensor sem reação"),
        ("Oposição Semiativa", "Oposição", 3, "Defensor com reação limitada"),
        ("Oposição Ativa", "Oposição", 4, "Defensor em jogo real"),

        # H.2 Estrutura
        ("Estrutura", "Formato do Exercício", 2, "Tipo de organização"),
        ("Analítico", "Estrutura", 1, "Exercício fragmentado"),
        ("Situacional", "Estrutura", 2, "Simulação de situação de jogo"),
        ("Jogo Reduzido", "Estrutura", 3, "Jogo com regras modificadas"),
        ("Jogo Formal", "Estrutura", 4, "Jogo completo"),
        ("Circuito", "Estrutura", 5, "Estações rotativas"),

        # ======================================================================
        # J. ESPAÇO E ZONA (pulamos I - Relação Numérica)
        # ======================================================================
        ("Espaço e Zona", None, 9, "Áreas da quadra utilizadas"),

        # J.1 Quadra
        ("Área de Quadra", "Espaço e Zona", 1, "Dimensão do espaço"),
        ("Quadra Inteira", "Área de Quadra", 1, "Uso de toda a quadra"),
        ("Meia Quadra", "Área de Quadra", 2, "Metade da quadra"),

        # J.2 Corredores
        ("Corredores", "Espaço e Zona", 2, "Faixas verticais"),
        ("Corredor Central", "Corredores", 1, "Centro da quadra"),
        ("Corredor Meia-Esquerda", "Corredores", 2, "Entre centro e ponta esquerda"),
        ("Corredor Meia-Direita", "Corredores", 3, "Entre centro e ponta direita"),
        ("Corredores Extremos", "Corredores", 4, "Zonas das pontas"),

        # J.3 Zonas
        ("Zonas", "Espaço e Zona", 3, "Áreas específicas"),
        ("Zona de 6m", "Zonas", 1, "Área do gol"),
        ("Zona de 9m", "Zonas", 2, "Linha de tiro livre"),
        ("Zona de Construção", "Zonas", 3, "Área de organização ofensiva"),
        ("Zona de Finalização", "Zonas", 4, "Área de conclusão"),
        ("Zona de Transição", "Zonas", 5, "Corredor de contra-ataque"),

        # ======================================================================
        # K. REGRAS E CONSTRAINTS
        # ======================================================================
        ("Regras e Constraints", None, 10, "Modificações e limitações"),
        ("Toques Limitados", "Regras e Constraints", 1, "Restrição de contatos com bola"),
        ("Tempo de Posse", "Regras e Constraints", 2, "Limite temporal"),
        ("Posse 6 Segundos", "Tempo de Posse", 1, "Finalização em 6s"),
        ("Posse 10 Segundos", "Tempo de Posse", 2, "Finalização em 10s"),
        ("Finalização Obrigatória", "Regras e Constraints", 3, "Deve arremessar"),
        ("Pontuação por Objetivo", "Regras e Constraints", 4, "Gols com valor diferente"),
        ("Regras de Drible", "Regras e Constraints", 5, "Restrições de condução"),
        ("Drible Proibido", "Regras de Drible", 1, "Não pode driblar"),
        ("Drible Obrigatório", "Regras de Drible", 2, "Deve driblar"),
        ("Passe ao Pivô Obrigatório", "Regras e Constraints", 6, "Deve passar ao pivô"),
        ("Cruzamento Obrigatório", "Regras e Constraints", 7, "Deve executar cruzamento"),
        ("Defesa Restrita", "Regras e Constraints", 8, "Limitação da defesa"),
        ("Só Flutuar", "Defesa Restrita", 1, "Defesa apenas flutuando"),
        ("Só Conter", "Defesa Restrita", 2, "Defesa apenas contendo"),

        # ======================================================================
        # N. MATERIAIS (pulamos L e M)
        # ======================================================================
        ("Materiais", None, 11, "Recursos necessários"),
        ("Cones e Barreiras", "Materiais", 1, "Demarcadores e obstáculos"),
        ("Elásticos e Medicine Ball", "Materiais", 2, "Equipamentos de força"),
        ("Coletes", "Materiais", 3, "Identificação de equipes"),
        ("Mini-gols e Alvos", "Materiais", 4, "Objetivos alternativos"),
        ("Cronômetro", "Materiais", 5, "Controle de tempo"),

        # ======================================================================
        # O. CONTEXTO DE USO
        # ======================================================================
        ("Contexto de Uso", None, 12, "Situação de aplicação"),
        ("Iniciação", "Contexto de Uso", 1, "Primeiros passos no esporte"),
        ("Formação", "Contexto de Uso", 2, "Categorias de base"),
        ("Alto Rendimento", "Contexto de Uso", 3, "Competição de elite"),
        ("Pré-jogo", "Contexto de Uso", 4, "Aquecimento antes de partida"),
        ("Pós-jogo", "Contexto de Uso", 5, "Recuperação após partida"),
        ("Reabilitação", "Contexto de Uso", 6, "Retorno progressivo de lesão"),
    ]

    # ==========================================================================
    # INSERÇÃO DAS TAGS
    # ==========================================================================

    # Primeiro, criar todas as tags raiz (parent=None)
    root_tags = [(name, parent, order, desc) for name, parent, order, desc in tags if parent is None]

    for name, _, display_order, description in root_tags:
        tag_uuid = gen_uuid(name)
        op.execute(f"""
            INSERT INTO exercise_tags (id, name, parent_tag_id, display_order, description, is_active, approved_at, created_at)
            VALUES (
                '{tag_uuid}',
                '{name.replace("'", "''")}',
                NULL,
                {display_order},
                '{description.replace("'", "''") if description else ''}',
                true,
                '{now}',
                '{now}'
            )
            ON CONFLICT (name) DO NOTHING;
        """)

    # Depois, criar tags com parent (ordenado para garantir que parents existam)
    child_tags = [(name, parent, order, desc) for name, parent, order, desc in tags if parent is not None]

    # Múltiplas passadas para garantir hierarquia correta
    for _ in range(5):  # Máximo 5 níveis de profundidade
        for name, parent_name, display_order, description in child_tags:
            tag_uuid = gen_uuid(name)
            parent_uuid = gen_uuid(parent_name)
            op.execute(f"""
                INSERT INTO exercise_tags (id, name, parent_tag_id, display_order, description, is_active, approved_at, created_at)
                SELECT
                    '{tag_uuid}',
                    '{name.replace("'", "''")}',
                    '{parent_uuid}',
                    {display_order},
                    '{description.replace("'", "''") if description else ''}',
                    true,
                    '{now}',
                    '{now}'
                WHERE EXISTS (SELECT 1 FROM exercise_tags WHERE id = '{parent_uuid}')
                ON CONFLICT (name) DO NOTHING;
            """)


def downgrade() -> None:
    """Remove tags seedadas (opcional - geralmente não remove seeds)."""
    # Não removemos as tags no downgrade para preservar dados
    # Se necessário, pode-se adicionar:
    # op.execute("DELETE FROM exercise_tags WHERE approved_at IS NOT NULL;")
    pass
