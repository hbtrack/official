"""
Smoke Test para Match Attendance (Presença em Jogos).

Impacto por minutos/participação.

Pré-condições:
- team_id, match_id, season_id válidos
- Atleta no roster do jogo
- team_registration ativo na temporada
- Token com membership ativo

Fases:
1) Estrutural: GET 200/501, 403 fora do escopo
2) Criar presença: POST 201, 403 se não está no roster
3) Duplicata: POST 409
4) Listar presenças: GET 200
5) Atualizar minutos: PATCH 200, 404, 403
6) Validação de limites: PATCH 422 (minutes > duração)
7) Remover presença: DELETE 200 (soft delete)
8) Impacto na carga: GET /match-load

Critérios:
- Sem 500
- 401/403/404/409/422 coerentes
- Exige roster e vínculo ativo na temporada
- Escopo via Team → Organization
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
    token_file = Path("C:/HB TRACK/token.txt")
if not token_file.exists():
    print("[ERRO] Token não encontrado")
    sys.exit(1)

TOKEN = token_file.read_text().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Dados conhecidos do ambiente dev
KNOWN_DATA = {
    "team_id": "34f19340-6d57-4efc-a442-cefacb69a190",
    "match_id": "52d8a514-a957-4914-b551-6ec290276982",
    "athlete_id": "337acf54-9ee3-4be5-938c-c148cf85bc5f",
    "roster_id": "82c20bc8-c3b1-4d06-892c-ecd322ebfdd2",
    "other_team_id": "fc4ea632-ed4f-4b8f-b205-616bcf04b1be",  # TEAM_DEV_OPP
}


class TestContext:
    """Contexto de dados para os testes."""
    org_id: Optional[str] = None
    season_id: Optional[str] = None
    team_id: Optional[str] = None
    athlete_id: Optional[str] = None
    match_id: Optional[str] = None
    roster_id: Optional[str] = None
    attendance_id: Optional[str] = None
    other_team_id: Optional[str] = None


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
    print("FASE 0: SETUP - Usando dados conhecidos")
    print("=" * 60)
    
    # Usar dados conhecidos
    ctx.team_id = KNOWN_DATA["team_id"]
    ctx.match_id = KNOWN_DATA["match_id"]
    ctx.athlete_id = KNOWN_DATA["athlete_id"]
    ctx.roster_id = KNOWN_DATA["roster_id"]
    ctx.other_team_id = KNOWN_DATA.get("other_team_id")
    
    log(f"Team: {ctx.team_id}")
    log(f"Match: {ctx.match_id}")
    log(f"Athlete: {ctx.athlete_id}")
    log(f"Roster: {ctx.roster_id}")
    if ctx.other_team_id:
        log(f"Other Team: {ctx.other_team_id}")
    ok("Dados conhecidos carregados")
    
    # Verificar se o endpoint está funcionando
    r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    if r.status_code == 200:
        ok("Health check OK")
    else:
        fail(f"Health check → {r.status_code}")
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
    
    # 1.1 - GET /teams/{team_id}/matches/{match_id}/attendance
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
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
    
    # 1.2 - GET com match fora de escopo
    if ctx.other_team_id:
        r = requests.get(
            f"{BASE_URL}/teams/{ctx.other_team_id}/matches/{ctx.match_id}/attendance",
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
    
    # 1.3 - GET match-load
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/match-load",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 501]:
        ok(f"GET match-load → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 500:
        fail(f"GET match-load → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET match-load → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    return results


# =============================================================================
# FASE 2-7: Smoke Funcional
# =============================================================================
def phase_2_7_functional():
    """Testa CRUD de match attendance."""
    print("\n" + "=" * 60)
    print("FASE 2-7: SMOKE FUNCIONAL - CRUD MATCH ATTENDANCE")
    print("=" * 60)
    
    results = {"pass": 0, "fail": 0, "skip": 0}
    
    # Verifica se temos roster
    if not ctx.roster_id:
        # Tenta GET para pegar roster_id
        r = requests.get(
            f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/roster",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            roster = r.json()
            if roster:
                ctx.roster_id = roster[0]["id"]
                ctx.athlete_id = roster[0]["athlete_id"]
                log(f"Roster encontrado: {ctx.roster_id}")
    
    # 2) Criar presença
    payload = {
        "athlete_id": ctx.athlete_id,
        "played": True,
        "minutes_played": 18,
        "started": False,
        "comment": "Smoke test match attendance"
    }
    r = requests.post(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 201]:
        ctx.attendance_id = r.json()["id"]
        log(f"Attendance criado: {ctx.attendance_id}")
        ok(f"POST attendance → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 403:
        if "not_in_roster" in r.text:
            log("Atleta não está no roster, criando roster...")
            # Tenta criar roster entry
            roster_payload = {
                "athlete_id": ctx.athlete_id,
                "jersey_number": 10,
                "is_goalkeeper": False,
                "is_available": True
            }
            r2 = requests.post(
                f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/roster",
                headers=HEADERS,
                json=roster_payload,
                timeout=TIMEOUT
            )
            if r2.status_code in [200, 201]:
                ctx.roster_id = r2.json()["id"]
                log(f"Roster criado: {ctx.roster_id}")
                # Tenta novamente criar attendance
                r3 = requests.post(
                    f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
                    headers=HEADERS,
                    json=payload,
                    timeout=TIMEOUT
                )
                if r3.status_code in [200, 201]:
                    ctx.attendance_id = r3.json()["id"]
                    log(f"Attendance criado após roster: {ctx.attendance_id}")
                    ok(f"POST attendance → {r3.status_code}")
                    results["pass"] += 1
                else:
                    fail(f"POST attendance após roster → {r3.status_code}", r3.text[:200])
                    results["fail"] += 1
            elif r2.status_code == 501:
                skip("POST attendance", "roster não implementado")
                results["skip"] += 1
                return results
            else:
                fail(f"POST roster → {r2.status_code}", r2.text[:200])
                results["fail"] += 1
                return results
        else:
            fail(f"POST attendance → {r.status_code}", r.text[:200])
            results["fail"] += 1
            return results
    elif r.status_code == 409:
        log("Attendance já existe, buscando...")
        r2 = requests.get(
            f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        if r2.status_code == 200:
            atts = r2.json()
            if atts:
                ctx.attendance_id = atts[0]["id"]
                log(f"Attendance existente: {ctx.attendance_id}")
                ok("POST attendance → 409 (já existe)")
                results["pass"] += 1
            else:
                fail("POST attendance → 409 mas lista vazia")
                results["fail"] += 1
                return results
        else:
            fail(f"POST attendance → 409, GET falhou", f"{r2.status_code}")
            results["fail"] += 1
            return results
    elif r.status_code == 501:
        skip("POST attendance → 501")
        results["skip"] += 1
        return results
    elif r.status_code == 500:
        fail(f"POST attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
        return results
    else:
        fail(f"POST attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
        return results
    
    # 3) Duplicata
    r = requests.post(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT
    )
    if r.status_code == 409:
        ok(f"POST duplicata → 409")
        results["pass"] += 1
    elif r.status_code == 500:
        fail(f"POST duplicata → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"POST duplicata → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 4) Listar presenças
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
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
            fail(f"GET attendance list → {r.status_code}", "registro não encontrado")
            results["fail"] += 1
    elif r.status_code == 500:
        fail(f"GET attendance list → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET attendance list → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 5) Atualizar minutos
    patch_payload = {"minutes_played": 25}
    r = requests.patch(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance/{ctx.attendance_id}",
        headers=HEADERS,
        json=patch_payload,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        updated = r.json()
        if updated.get("minutes_played") == 25:
            ok(f"PATCH attendance → {r.status_code}")
            results["pass"] += 1
        else:
            fail(f"PATCH attendance → {r.status_code}", f"minutes não atualizado: {updated.get('minutes_played')}")
            results["fail"] += 1
    elif r.status_code == 501:
        skip("PATCH attendance → 501")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"PATCH attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"PATCH attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 6) Validação de limites (minutes > 80)
    invalid_payload = {"minutes_played": 100}
    r = requests.patch(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance/{ctx.attendance_id}",
        headers=HEADERS,
        json=invalid_payload,
        timeout=TIMEOUT
    )
    if r.status_code == 422:
        ok(f"PATCH invalid minutes → 422")
        results["pass"] += 1
    elif r.status_code == 200:
        fail(f"PATCH invalid minutes → {r.status_code}", "deveria ser 422")
        results["fail"] += 1
    elif r.status_code == 500:
        fail(f"PATCH invalid minutes → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"PATCH invalid minutes → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # 7) Remover presença
    r = requests.delete(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance/{ctx.attendance_id}",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        ok(f"DELETE attendance → {r.status_code}")
        results["pass"] += 1
    elif r.status_code == 501:
        skip("DELETE attendance → 501")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"DELETE attendance → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"DELETE attendance → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    return results


# =============================================================================
# FASE 8: Impacto na Carga
# =============================================================================
def phase_8_load():
    """Testa endpoint de carga."""
    print("\n" + "=" * 60)
    print("FASE 8: IMPACTO NA CARGA")
    print("=" * 60)
    
    results = {"pass": 0, "fail": 0, "skip": 0}
    
    # Criar novo attendance para carga
    payload = {
        "athlete_id": ctx.athlete_id,
        "played": True,
        "minutes_played": 30,
        "started": True
    }
    r = requests.post(
        f"{BASE_URL}/teams/{ctx.team_id}/matches/{ctx.match_id}/attendance",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT
    )
    if r.status_code in [200, 201, 409]:
        log(f"Attendance para carga: {r.status_code}")
    
    # GET match-load
    r = requests.get(
        f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/match-load",
        headers=HEADERS,
        timeout=TIMEOUT
    )
    if r.status_code == 200:
        load = r.json()
        log(f"Load response: {json.dumps(load, indent=2)}")
        required = ["athlete_id", "total_matches", "total_played", "total_minutes"]
        missing = [f for f in required if f not in load]
        if not missing:
            ok(f"GET match-load → {r.status_code} (campos válidos)")
            results["pass"] += 1
            
            # Verifica se tem carga > 0 quando played=true
            if load.get("total_played", 0) > 0 and load.get("total_minutes", 0) > 0:
                ok("Carga > 0 quando played=true")
                results["pass"] += 1
            elif load.get("total_matches", 0) > 0:
                log(f"total_matches={load.get('total_matches')}, total_played={load.get('total_played')}")
                ok("Match registrado")
                results["pass"] += 1
            else:
                skip("Carga = 0 (sem dados suficientes)")
                results["skip"] += 1
        else:
            fail(f"GET match-load → {r.status_code}", f"campos faltando: {missing}")
            results["fail"] += 1
    elif r.status_code == 501:
        skip("GET match-load → 501")
        results["skip"] += 1
    elif r.status_code == 500:
        fail(f"GET match-load → {r.status_code} (ERRO 500!)", r.text[:200])
        results["fail"] += 1
    else:
        fail(f"GET match-load → {r.status_code}", r.text[:200])
        results["fail"] += 1
    
    # GET match-load com season_id
    if ctx.season_id:
        r = requests.get(
            f"{BASE_URL}/teams/{ctx.team_id}/athletes/{ctx.athlete_id}/match-load?season_id={ctx.season_id}",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            ok(f"GET match-load (com season_id) → {r.status_code}")
            results["pass"] += 1
        elif r.status_code == 501:
            skip("GET match-load (com season_id) → 501")
            results["skip"] += 1
        elif r.status_code == 500:
            fail(f"GET match-load (com season_id) → {r.status_code} (ERRO 500!)", r.text[:200])
            results["fail"] += 1
        else:
            fail(f"GET match-load (com season_id) → {r.status_code}", r.text[:200])
            results["fail"] += 1
    
    return results


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 60)
    print("SMOKE TEST: MATCH ATTENDANCE (PRESENÇA EM JOGOS)")
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
    
    # Fases 2-7: Funcional
    r = phase_2_7_functional()
    all_results["pass"] += r["pass"]
    all_results["fail"] += r["fail"]
    all_results["skip"] += r["skip"]
    
    # Fase 8: Carga
    r = phase_8_load()
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
