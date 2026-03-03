"""Fix pre-existing import bug in exports.py: get_current_active_user não existia em security.py."""
import pathlib

f = pathlib.Path(__file__).parent.parent / "Hb Track - Backend/app/api/v1/routers/exports.py"
c = f.read_text(encoding="utf-8")

# 1. Fix import de get_current_active_user (não existe em security.py; usar get_current_context)
c = c.replace(
    "from app.core.security import get_current_active_user",
    "from app.core.context import get_current_context as get_current_active_user"
)

# 2. Trocar tipo User por ExecutionContext (vem da mesma context.py)
c = c.replace(
    "from app.models.user import User",
    "from app.core.context import ExecutionContext"
)

# 3. Trocar anotação de tipo nos parâmetros em todos os endpoints
c = c.replace(
    "Annotated[User, Depends(get_current_active_user)]",
    "Annotated[ExecutionContext, Depends(get_current_active_user)]"
)

# 4. ExecutionContext tem user_id: UUID, não .id;
#    substituir UUID(current_user.id) por current_user.user_id
c = c.replace("UUID(current_user.id)", "current_user.user_id")

f.write_text(c, encoding="utf-8")
print("exports.py corrigido OK")
print("Ocorrências restantes de 'get_current_active_user':", c.count("get_current_active_user"))
print("Ocorrências restantes de 'User':", c.count("User"))
print("Ocorrências restantes de 'UUID(current_user.id)':", c.count("UUID(current_user.id)"))
