"""
Script de recon para INV-TRAIN-041 (endpoint com autenticação)
Extrai metadados do OpenAPI para criar SPEC Classe F correto
"""

import json
from pathlib import Path

openapi_path = Path(r"C:\HB TRACK\docs\_generated\openapi.json")

with open(openapi_path, encoding='utf-8') as f:
    spec = json.load(f)

# Candidatos: endpoints com GET que têm security
candidates = []

for path, methods in spec['paths'].items():
    for method, details in methods.items():
        if method == 'get' and isinstance(details, dict):
            op_id = details.get('operationId')
            security = details.get('security', [])
            
            if security:  # Tem security
                security_schemes = []
                for sec_obj in security:
                    if isinstance(sec_obj, dict):
                        security_schemes.extend(sec_obj.keys())
                
                responses = list(details.get('responses', {}).keys())
                
                candidates.append({
                    'path': path,
                    'method': method.upper(),
                    'operationId': op_id,
                    'security': security_schemes,
                    'responses': responses
                })

# Mostrar os 5 primeiros candidatos
print(f"Found {len(candidates)} GET endpoints with security\n")
print("Top 5 candidates for INV-TRAIN-041:\n")

for i, candidate in enumerate(candidates[:5], 1):
    print(f"{i}. {candidate['path']}")
    print(f"   operationId: {candidate['operationId']}")
    print(f"   method: {candidate['method']}")
    print(f"   security: {candidate['security']}")
    print(f"   responses: {candidate['responses']}")
    print()

# Escolher /api/v1/teams GET se existir
teams_endpoint = None
for candidate in candidates:
    if candidate['path'] == '/api/v1/teams':
        teams_endpoint = candidate
        break

if teams_endpoint:
    print("=" * 60)
    print("RECOMMENDED: /api/v1/teams GET")
    print("=" * 60)
    print(f"operationId: {teams_endpoint['operationId']}")
    print(f"method: {teams_endpoint['method']}")
    print(f"path: {teams_endpoint['path']}")
    print(f"security: {teams_endpoint['security']}")
    print(f"responses: {teams_endpoint['responses']}")
    print()
    print("SPEC template:")
    print("api.operation_id:", f'"{teams_endpoint["operationId"]}"')
    print("api.method:", f'"{teams_endpoint["method"]}"')
    print("api.path:", f'"{teams_endpoint["path"]}"')
    print("api.responses:")
    for resp in sorted(teams_endpoint['responses']):
        print(f'  - "{resp}"')
    print("api.security:")
    for scheme in teams_endpoint['security']:
        print(f'  - "{scheme}"')
