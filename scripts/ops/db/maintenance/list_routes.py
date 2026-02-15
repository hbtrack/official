# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ,DB_WRITE,FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=NO
# HB_SCRIPT_ENTRYPOINT=python scripts/ops/db/maintenance/list_routes.py
# HB_SCRIPT_OUTPUTS=stdout
from app.api.v1.routers import exercises

print("Rotas do exercises.router:")
for r in exercises.router.routes:
    methods = ', '.join(r.methods) if hasattr(r, 'methods') else 'N/A'
    print(f"  {r.path:40} {methods}")

