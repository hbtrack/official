from app.api.v1.routers import exercises

print("Rotas do exercises.router:")
for r in exercises.router.routes:
    methods = ', '.join(r.methods) if hasattr(r, 'methods') else 'N/A'
    print(f"  {r.path:40} {methods}")
