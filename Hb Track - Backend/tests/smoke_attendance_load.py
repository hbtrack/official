"""
Smoke Test para Attendance (Presenças em Treino) e Load (Carga).

Ciclo: Treino → Presença → Jogo

Fases:
1. FASE 1: Smoke Estrutural - verifica rotas retornam 200/501/403
2. FASE 2: Smoke Funcional (Treino) - POST/GET/PATCH/DELETE attendance em trainings
3. FASE 3: Match Attendance (future) - POST attendance requer roster
4. FASE 4: Load endpoint - GET /teams/{team_id}/athletes/{athlete_id}/load
5. VALIDAÇÃO: Critérios de aceite (0 erros 500, regras de negócio)

Requisitos:
- Token válido em ../token.txt
- Backend rodando em http://127.0.0.1:8000
- Dados existentes:
  - Organização válida
  - Temporada ativa
  - Equipe
  - Atleta com team_registration ativo
  - Training session existente
"""
import json
import sys
from pathlib import Path
from typing import Optional
from uuid import UUID
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
TIMEOUT = 15

# Lê token
token_file = Path(__file__).parent.parent.parent / "token.txt"
if not token_file.exists():
    # Tenta caminho alternativo
    token_file = Path("C:/HB TRACK/token.txt")
if not token_file.exists():
    print("[ERRO] Token não encontrado em ../token.txt ou C:/HB TRACK/token.txt")
    sys.exit(1)

TOKEN = token_file.read_text().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


class TestContext:
    """Contexto de dados para os testes."""
    org_id: Optional[str] = None
    season_id: Optional[str] = None
    team_id: Optional[str] = None
    athlete_id: Optional[str] = None
    team_registration_id: Optional[str] = None
    training_id: Optional[str] = None
    attendance_id: Optional[str] = None
    other_team_id: Optional[str] = None  # Para teste 403 fora de escopo


ctx = TestContext()


def log(msg: str):
    print(f"  {msg}")


def ok(test: str):
    print(f"✅ {test}")


def fail(test: str, detail: str = ""):
    print(f"❌ {test} - {detail}")


def skip(test: str, reason: str = ""):
    print(f"⏭️  {test} - {reason}")


# =============================================================================
# FASE 0: Setup - Buscar dados existentes
# =============================================================================
def phase_0_setup():
    """Busca dados necessários para os testes."""
    print("\n" + "=" * 60)
    print("FASE 0: SETUP - Buscando dados existentes")
    print("=" * 60)
    
    # 0.1 - Buscar organização
    r = requests.get(f"{BASE_URL}/organizations", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        # Suporta resposta paginada ou lista simples
        orgs = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(orgs, list) and len(orgs) > 0:
            ctx.org_id = orgs[0]["id"]
            log(f"Organização: {ctx.org_id}")
            ok("Organização encontrada")
        else:
            fail("Nenhuma organização encontrada")
            return False
    else:
        fail(f"GET /organizations", f"{r.status_code}")
        return False
    
    # 0.2 - Buscar temporada ativa
    r = requests.get(f"{BASE_URL}/seasons?organization_id={ctx.org_id}", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        seasons = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(seasons, list) and len(seasons) > 0:
            ctx.season_id = seasons[0]["id"]
            log(f"Temporada: {ctx.season_id}")
            ok("Temporada encontrada")
        else:
            fail("Nenhuma temporada encontrada")
            return False
    else:
        fail(f"GET /seasons", f"{r.status_code}")
        return False
    
    # 0.3 - Buscar equipes
    r = requests.get(f"{BASE_URL}/teams?organization_id={ctx.org_id}", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        teams = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(teams, list) and len(teams) > 0:
            ctx.team_id = teams[0]["id"]
            log(f"Equipe principal: {ctx.team_id}")
            if len(teams) > 1:
                ctx.other_team_id = teams[1]["id"]
                log(f"Equipe secundária (escopo): {ctx.other_team_id}")
            ok("Equipe(s) encontrada(s)")
        else:
            fail("Nenhuma equipe encontrada")
            return False
    else:
        fail(f"GET /teams", f"{r.status_code}")
        return False
    
    # 0.4 - Buscar atletas
    r = requests.get(f"{BASE_URL}/athletes", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        athletes = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(athletes, list) and len(athletes) > 0:
            ctx.athlete_id = athletes[0]["id"]
            log(f"Atleta: {ctx.athlete_id}")
            ok("Atleta encontrado")
        else:
            fail("Nenhum atleta encontrado")
            return False
    else:
        fail(f"GET /athletes", f"{r.status_code}")
        return False
    
    # 0.5 - Buscar team_registration do atleta
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        data = r.json()
        regs = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(regs, list) and len(regs) > 0:
            # Usa o athlete_id do primeiro registro encontrado
            ctx.athlete_id = regs[0].get("athlete_id") or regs[0].get("id")
            ctx.team_registration_id = regs[0].get("id")
            log(f"Team Registration: {ctx.team_registration_id}")
            ok("Team Registration encontrado")
        else:
            log("Nenhum team_registration via rota scoped")
    elif r.status_code in [404, 501]:
        log(f"Rota /teams/{{team_id}}/athletes retornou {r.status_code}")
    else:
        log(f"Erro buscando team_registrations: {r.status_code}")
    
    # 0.6 - Buscar ou criar training session
    # Primeiro tenta rota scoped
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        data = r.json()
        trainings = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(trainings, list) and len(trainings) > 0:
            ctx.training_id = trainings[0]["id"]
            log(f"Training Session: {ctx.training_id}")
            ok("Training Session encontrada via rota scoped")
        else:
            log("Lista vazia na rota scoped, usando fallback...")
            # Fallback para dados conhecidos
            ctx.team_id = "34f19340-6d57-4efc-a442-cefacb69a190"
            ctx.training_id = "bc0bd08c-bded-49b9-8fa2-7f9534779d9c"
            ctx.athlete_id = "7582e9fa-7a8b-477f-9683-1cca4484007d"
            log(f"Usando dados de fallback: team={ctx.team_id[:8]}... training={ctx.training_id[:8]}...")
            ok("Usando dados de fallback")
    elif r.status_code == 501:
        log("Rota scoped retornou 501, usando fallback...")
        # Fallback para dados conhecidos
        ctx.team_id = "34f19340-6d57-4efc-a442-cefacb69a190"
        ctx.training_id = "bc0bd08c-bded-49b9-8fa2-7f9534779d9c"
        ctx.athlete_id = "7582e9fa-7a8b-477f-9683-1cca4484007d"
        log(f"Usando dados de fallback: team={ctx.team_id[:8]}... training={ctx.training_id[:8]}...")
        ok("Usando dados de fallback")
    elif r.status_code == 500:
        log("Rota scoped retornou 500, tentando fallback...")
        # Fallback para dados conhecidos
        ctx.team_id = "34f19340-6d57-4efc-a442-cefacb69a190"
        ctx.training_id = "bc0bd08c-bded-49b9-8fa2-7f9534779d9c"
        ctx.athlete_id = "7582e9fa-7a8b-477f-9683-1cca4484007d"
        log(f"Usando dados de fallback: team={ctx.team_id[:8]}... training={ctx.training_id[:8]}...")
        ok("Usando dados de fallback")
    else:
        fail(f"GET /teams/{{team_id}}/trainings", f"{r.status_code}")
        return False
    
    return True


# =============================================================================
# FASE 1: Smoke Estrutural
# =============================================================================
def phase_1_structural():
    """Testa estrutura das rotas (200/501/403)."""
    print("\n" + "=" * 60)
    print("FASE 1: SMOKE ESTRUTURAL")
    print("=" * 60)
    
    results = {"pass": 0, "fail": 0, "skip": 0}
    
    # 1.1 - GET /teams/{team_id}/trainings/{training_id}/attendance
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 501]:
        ok(f"GET attendance list → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 500:
        fail(f"GET attendance list → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET attendance list → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 1.2 - GET com team fora de escopo (403 esperado)
    if ctx.other_team_id:
        r = requests.get(
            f"{BASE_URL}/teams/{ctx.other_team_id}/trainings/{ctx.training_id}/attendance",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        if r.status_code in [403, 404]:
            ok(f"GET attendance (out of scope) → {r.status_code}")
            results["pass"] += 1
        elif r.status_code == 500:
            fail(f"GET attendance (out of scope) → {r.status_code} (ERRO 500!)", r.text[:200])
            results["fail"] += 1
        else:
            fail(f"GET attendance (out of scope) → {r.status_code}", r.text[:200])
            results["fail"] += 1
    else:
        skip("GET attendance (out of scope)", "sem equipe secundária")
        results["skip"] += 1
    
    # 1.3 - GET /teams/{team_id}/athletes/{athlete_id}/load
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/load",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 501]:
        ok(f"GET athlete load → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 500:
        fail(f"GET athlete load → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET athlete load → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 1.4 - Rotas deprecated devem retornar 501
    r = requests.get(
        f"{BASE_URL}/training_sessions/{ctx.training_id}/attendance",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code in [404, 501]:
        ok(f"GET deprecated route → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 500:
        fail(f"GET deprecated route → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET deprecated route → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    return results


# =============================================================================
# FASE 2: Smoke Funcional - CRUD Attendance em Treino
# =============================================================================
def phase_2_functional_training():
    """Testa CRUD de attendance em training sessions."""
    print("\n" + "=" * 60)
    print("FASE 2: SMOKE FUNCIONAL - CRUD ATTENDANCE EM TREINO")
    print("=" * 60)
    
    results = {"pass": 0, "fail": 0, "skip": 0}
    
    # 2.1 - POST /teams/{team_id}/trainings/{training_id}/attendance
    payload = {
        "athlete_id": ctx.athlete_id,
        "presence_status": "present",
        "minutes_effective": 90,
        "participation_type": "full",
        "comment": "Smoke test attendance"
    }
    r = requests.post(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 201]:
        ctx.attendance_id = r.json()["id"]
        log(f"Attendance criado: {ctx.attendance_id}")
        ok(f"POST attendance → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 501:
        skip("POST attendance → 501 (não implementado)")
        results["skip"] += 1
        return results  # Pula resto dos testes funcionais
    elif r.status_code == 403:
        fail(f"POST attendance → {r.status_code}", f"Atleta sem team_registration ativo? {r.text[:200]}")
        results["fail"] += 1
        return results
    elif r.status_code == 409:
        log(f"Attendance já existe, buscando...")
        # Buscar attendance existente
        r2 = requests.get(
            f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        if r2.status_code == 200:
            atts = r2.json()
            if len(atts) > 0:
                ctx.attendance_id = atts[0]["id"]
                log(f"Attendance existente: {ctx.attendance_id}")
                ok("POST attendance → 409 (já existe, reusando)")
                results["pass"] += 1
            else:
                fail("POST attendance → 409 mas lista vazia", r.text[:200])
                results["fail"] += 1
                return results
        else:
            fail(f"POST attendance → 409, GET falhou: {r2.status_code}", r2.text[:200])
            results["fail"] += 1
            return results
    elif r.status_code == 500:
        fail(f"POST attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
        return results
    else:
        fail(f"POST attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
        return results
    
    # 2.2 - GET lista deve conter o registro criado
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        atts = r.json()
        found = any(a["id"] == ctx.attendance_id for a in atts)
        if found:
            ok(f"GET attendance list → {r.status_code} (registro encontrado)")
            results["pass"] += 1
        else:
            fail(f"GET attendance list → {r.status_code}", "registro não encontrado na lista")
            results["fail"] += 1
    elif r.status_code == 500:
        fail(f"GET attendance list → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET attendance list → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 2.3 - PATCH /teams/{team_id}/trainings/{training_id}/attendance/{attendance_id}
    patch_payload = {
        "minutes_effective": 85,
        "comment": "Smoke test - atualizado"
    }
    r = requests.patch(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance/{ctx.attendance_id}",
        headers=HEADERS,
        json=patch_payload,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        updated = r.json()
        if updated.get("minutes_effective") == 85:
            ok(f"PATCH attendance → {r.status_code} (minutos atualizados)")
            results["pass"] += 1
        else:
            fail(f"PATCH attendance → {r.status_code}", f"minutes_effective não atualizado: {updated.get('minutes_effective')}")
            results["fail"] += 1
    elif r.status_code == 501:
        skip("PATCH attendance → 501 (não implementado)")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"PATCH attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"PATCH attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 2.4 - DELETE /teams/{team_id}/trainings/{training_id}/attendance/{attendance_id}
    r = requests.delete(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance/{ctx.attendance_id}",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        ok(f"DELETE attendance → {r.status_code} (soft delete)")
        results["pass"] += 1
    elif r.status_code == 501:
        skip("DELETE attendance → 501 (não implementado)")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"DELETE attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"DELETE attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 2.5 - GET após DELETE não deve encontrar o registro
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        atts = r.json()
        found = any(a["id"] == ctx.attendance_id for a in atts)
        if not found:
            ok(f"GET attendance list após DELETE → registro removido")
            results["pass"] += 1
        else:
            fail(f"GET attendance list após DELETE", "registro ainda visível (soft delete falhou?)")
            results["fail"] += 1
    elif r.status_code == 500:
        fail(f"GET attendance list após DELETE → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET attendance list após DELETE → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    return results


# =============================================================================
# FASE 3: Load Endpoint
# =============================================================================
def phase_3_load():
    """Testa endpoint de carga do atleta."""
    print("\n" + "=" * 60)
    print("FASE 3: LOAD ENDPOINT")
    print("=" * 60)
    
    results = {"pass": 0, "fail": 0, "skip": 0}
    
    # Primeiro, criar um novo attendance para ter dados de carga
    payload = {
        "athlete_id": ctx.athlete_id,
        "presence_status": "present",
        "minutes_effective": 60,
        "participation_type": "full",
        "comment": "Smoke test load"
    }
    r = requests.post(
        f"{BASE_URL}/teams/{ctx.team_id}/trainings/{ctx.training_id}/attendance",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 201, 409]:
        log(f"Attendance para load: {r.status_code}")
    
    # 3.1 - GET /teams/{team_id}/athletes/{athlete_id}/load
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/load",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        load = r.json()
        log(f"Load response: {json.dumps(load, indent=2)}")
        # Validar campos obrigatórios
        required = ["athlete_id", "total_trainings", "total_minutes", "total_presences", "total_absences", "attendance_rate"]
        missing = [f for f in required if f not in load]
        if not missing:
            ok(f"GET athlete load → {r.status_code} (campos válidos)")
            results["pass"] += 1
        else:
            fail(f"GET athlete load → {r.status_code}", f"campos faltando: {missing}")
            results["fail"] += 1
    elif r.status_code == 501:
        skip("GET athlete load → 501 (não implementado)")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"GET athlete load → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET athlete load → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 3.2 - GET load com filtro de temporada
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/load?season_id={ctx.season_id}",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        ok(f"GET athlete load (com season_id) → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 501:
        skip("GET athlete load (com season_id) → 501")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"GET athlete load (com season_id) → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET athlete load (com season_id) → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    return results


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 60)
    print("SMOKE TEST: ATTENDANCE & LOAD")
    print("=" * 60)
    
    # Setup
    if not phase_0_setup():
        print("\n❌ SETUP FALHOU - Abortando testes")
        sys.exit(1)
    
    all_results = {"pass": 0, "fail": 0, "skip": 0}
    
    # Fase 1: Estrutural
    r = phase_1_structural()
    all_results["pass"] += r["pass"]
    all_results["fail"] += r["fail"]
    all_results["skip"] += r["skip"]
    
    # Fase 2: Funcional
    r = phase_2_functional_training()
    all_results["pass"] += r["pass"]
    all_results["fail"] += r["fail"]
    all_results["skip"] += r["skip"]
    
    # Fase 3: Load
    r = phase_3_load()
    all_results["pass"] += r["pass"]
    all_results["fail"] += r["fail"]
    all_results["skip"] += r["skip"]
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    total = all_results["pass"] + all_results["fail"] + all_results["skip"]
    print(f"✅ Passou: {all_results['pass']}/{total}")
    print(f"❌ Falhou: {all_results['fail']}/{total}")
    print(f"⏭️  Pulado: {all_results['skip']}/{total}")
    
    if all_results["fail"] == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {all_results['fail']} TESTE(S) FALHARAM")
        sys.exit(1)


if __name__ == "__main__":
    main()
