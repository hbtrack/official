# Seeds do HB Track

Este diretório contém os seeds para popular o banco com **dados de teste** para desenvolvimento.

## 🔧 NOVA ARQUITETURA (Pós Schema Canônico)

**IMPORTANTE**: Dados de configuração (roles, permissions, positions, etc.) agora estão nas **migrations**.
Os seeds servem apenas para dados de **teste e desenvolvimento**.

### Dados nas Migrations ✅
- Roles (dirigente, coordenador, treinador, atleta, membro)
- Permissions (65 permissões do sistema)
- Role_permissions (matriz RBAC completa)
- Positions (ofensivas e defensivas)
- Categories (categorias de idade)
- Schooling_levels (níveis de escolaridade)
- Event system (phases_of_play, advantage_states, event_types)
- Super admin (adm@handballtrack.app)

### Dados nos Seeds 🧪
- Organização de teste
- Atletas de teste
- Outros dados específicos para desenvolvimento

## 📋 Seeds Atuais

1. **seed_test_organization.py**: Organização e temporada de teste
2. **seed_test_athletes.py**: Atletas de teste

## 🚀 Execução

Para executar todos os seeds de teste:

```bash
python run_test_seeds.py
```

Para executar um seed específico:

```bash
python seed_test_organization.py
```

## 📁 Arquivo Antigo

Seeds antigos movidos para `_archived/` (dados agora nas migrations).

## Arquivos de Seed

1. **001_seed_roles.py** - Roles do sistema (R4)
   - dirigente, coordenador, treinador, atleta
   - **Status**: Aplicado pela migração inicial

2. **002_seed_superadmin.py** - Super Administrador único (R3, RDB6)
   - Email: superadmin@seed.local
   - **Status**: Aplicado pela migração inicial

3. **003_seed_categories.py** - Categorias globais (R15, RDB11)
   - SUB12, SUB14, SUB16, SUB18, SUB20, ADULTO
   - **Status**: Aplicado pela migração inicial

4. **004_seed_organization.py** - Organização inicial (R34)
   - Clube HB Tracking (clube único da V1)
   - Vinculado ao superadmin

## Como Executar

### Executar seeds individuais:

```bash
# Organization (único que precisa ser executado manualmente)
python backend/db/seeds/004_seed_organization.py
```

### Executar todos os seeds:

```bash
python backend/db/seeds/run_all_seeds.py
```

## Validação

Para validar se todos os seeds foram aplicados corretamente, execute:

```bash
python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Roles
cur.execute('SELECT COUNT(*) FROM roles')
print(f'Roles: {cur.fetchone()[0]} (esperado >= 4)')

# Superadmin
cur.execute('SELECT COUNT(*) FROM users WHERE is_superadmin = true')
print(f'Superadmin: {cur.fetchone()[0]} (esperado = 1)')

# Organizations
cur.execute('SELECT COUNT(*) FROM organizations')
print(f'Organizations: {cur.fetchone()[0]} (esperado >= 1)')

# Categories
cur.execute('SELECT COUNT(*) FROM categories')
print(f'Categories: {cur.fetchone()[0]} (esperado = 6)')

cur.close()
conn.close()
"
```

## Ordem de Dependências

```
roles → superadmin → organization
                  ↘ categories
```

## Idempotência

Todos os seeds são idempotentes - podem ser executados múltiplas vezes sem causar duplicação de dados. Cada seed verifica se os dados já existem antes de inserir.

## Regras do Sistema

- **R3**: Sistema deve ter exatamente 1 super administrador
- **R4**: Roles: dirigente, coordenador, treinador, atleta
- **R15**: Categorias globais definidas por idade
- **R34**: V1 opera com clube único
- **RDB6**: Partial unique index garante apenas 1 superadmin
- **RDB11**: Categorias definidas exclusivamente por idade
