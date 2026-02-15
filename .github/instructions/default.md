# .github/instructions/default.md
# Finalidade: Convenções fundamentais sempre ativas (GitHub Copilot)

Você está trabalhando no **HB Track**, um projeto corporativo de backend em Python com governança rigorosa.

## Princípios Fundamentais (MUST FOLLOW)

1. **Determinismo sobre eloquência**
   - Saídas estruturadas (YAML/JSON) preferidas em vez de prosa
   - Códigos de saída (exit codes) sempre explícitos
   - Sem linguagem ambígua ("talvez", "possivelmente")

2. **SSOT é sagrado**
   - Banco de dados: `docs/_ssot/schema.sql` (gerado pelo Alembic)
   - API: `docs/_ssot/openapi.json` (gerado a partir do código)
   - Se o código conflitar com o SSOT → o código está errado

3. **Notação de caminho (path)**
   - Sempre absoluto em relação à raiz do repositório
   - Apenas barras normais: `docs/_canon/00_START_HERE.md`
   - Nunca: `../`, `./`, `\`, ou caminhos absolutos do sistema operacional

4. **Padrões de documentação**
   - Todos os documentos CANÔNICOS possuem frontmatter YAML
   - Use BCP 14 keywords (MUST/SHOULD/MAY) in bold
   - Score de determinismo >= 4 para todos os protocolos

## Convenções de Nomenclatura de Arquivos
```yaml
naming_patterns:
  python_files: "snake_case.py"
  yaml_files: "kebab-case.yaml" OU "SCREAMING_SNAKE.yaml" (configurações)
  markdown_docs: "SCREAMING_SNAKE.md" (canônico) OU "kebab-case.md" (guias)
  
  examples:
    canonical: "AI_ARCH_EXEC_PROTOCOL.md"
    guide: "how-to-write-migrations.md"
    script: "validate_parity.py"
    config: "architect-config.yaml"
```

## Formato de Mensagem de Commit
```
<tipo>(<escopo>): <assunto>

<corpo>

<rodapé>
```

**Tipos:** feat, fix, docs, refactor, test, chore  
**Escopos:** api, db, docs, tests, scripts, ci

**Exemplo:**
```
docs(canon): add SSOT validation protocol

- Created AI_SSOT_VALIDATION_PROTOCOL.md
- Added pre/post-condition contracts
- Integrated with CI validation gates

Refs: ARCH-20250215-001
```

## Estilo de Código (Python)
```python
# Imports: padrão → terceiros → local
import os
import sys

from fastapi import APIRouter
from pydantic import BaseModel

from api.utils import validate_email

# Docstrings: Estilo Google
def authenticate_user(email: str, password: str) -> dict:
    """
    Autentica o usuário e retorna o token JWT.
    
    @implements: REQ-AUTH-001
    
    Args:
        email: Endereço de e-mail do usuário
        password: Senha em texto simples
    
    Returns:
        dict: {"token": str, "expires_at": datetime}
    
    Raises:
        ValueError: Se o formato do e-mail for inválido
        AuthError: Se as credenciais forem inválidas
    """
    pass

# Type hints: sempre
def process_data(items: list[dict]) -> tuple[int, list[str]]:
    """Processa itens e retorna contagem + erros."""
    pass
```

## Nunca Faça

- ❌ Hardcode de credenciais
- ❌ Modificar `.git/` diretamente
- ❌ Usar `rm -rf` em scripts
- ❌ Pular portões de validação (validation gates)
- ❌ Commitar sem rodar os testes