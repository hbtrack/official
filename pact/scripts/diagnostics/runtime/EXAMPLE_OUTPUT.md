# Exemplo de Saída — diag_vps_python_runtime.sh

Este arquivo mostra a saída esperada do script de diagnóstico em um cenário onde **tudo está OK**.

---

## Cenário: VPS com Python 3.11, venv configurado corretamente

```bash
$ /tmp/diag_vps_python_runtime.sh

========================================
1. Python do venv (usado pelo systemd)
========================================
Python executable: /home/deploy/hbtrack-backend/current/venv/bin/python

sys.executable:
  /home/deploy/hbtrack-backend/current/venv/bin/python

sys.version:
  3.11.5 (main, Sep 11 2023, 13:54:46) [GCC 11.4.0]

Major.Minor: 3.11
✓ Venv está usando Python 3.11

========================================
2. Comando systemd (ExecStart)
========================================
Unit file completo:

# /etc/systemd/system/hbtrack-backend.service
[Unit]
Description=HB Track Backend API
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/home/deploy/hbtrack-backend/current
Environment="PATH=/home/deploy/hbtrack-backend/current/venv/bin"
ExecStart=/home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

ExecStart isolado:
ExecStart={ path=/home/deploy/hbtrack-backend/current/venv/bin/uvicorn ; argv[]=/home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
✓ ExecStart usa o venv esperado (/home/deploy/hbtrack-backend/current/venv)

========================================
3. Python do processo em execução
========================================
Status do serviço:
● hbtrack-backend.service - HB Track Backend API
     Loaded: loaded (/etc/systemd/system/hbtrack-backend.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-02-18 14:23:10 UTC; 2h 15min ago
   Main PID: 12345 (uvicorn)
      Tasks: 3 (limit: 2339)
     Memory: 142.5M
        CPU: 5.234s
     CGroup: /system.slice/hbtrack-backend.service
             ├─12345 /home/deploy/hbtrack-backend/current/venv/bin/python /home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
             ├─12346 /home/deploy/hbtrack-backend/current/venv/bin/python -c from multiprocessing.resource_tracker import main;main(4)
             └─12347 /home/deploy/hbtrack-backend/current/venv/bin/python -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=5, pipe_handle=7) --multiprocessing-fork

MainPID: 12345
Python em execução: /home/deploy/hbtrack-backend/current/venv/bin/python3.11
✓ Processo está usando Python do venv esperado

Cmdline do processo:
/home/deploy/hbtrack-backend/current/venv/bin/python /home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

========================================
4. Compatibilidade do código com runtime
========================================
A) Compilando código (detecção de sintaxe incompatível)...
✓ Código compila sem erros de sintaxe

B) Importando entrypoint (app.main)...
✓ Entrypoint app.main importado com sucesso

C) Verificando dependências (pip check)...
✓ Todas as dependências estão satisfeitas

========================================
5. Logs recentes do serviço (journalctl)
========================================
Últimos 30 logs do serviço:

Feb 18 14:23:10 vps systemd[1]: Started HB Track Backend API.
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:═══════════════════════════════════════════════════════════
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME sys.executable = /home/deploy/hbtrack-backend/current/venv/bin/python
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME sys.version = 3.11.5 (main, Sep 11 2023, 13:54:46) [GCC 11.4.0]
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME Python 3.11.5
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:═══════════════════════════════════════════════════════════
Feb 18 14:23:10 vps uvicorn[12345]: INFO:app.main:🚀 HB Tracking API v1 iniciando...
Feb 18 14:23:11 vps uvicorn[12345]: INFO:app.main:✅ Database: PostgreSQL 15.3
Feb 18 14:23:11 vps uvicorn[12345]: INFO:app.main:📊 Ambiente: production
Feb 18 14:23:11 vps uvicorn[12345]: INFO:app.main:✅ Background tasks iniciadas (WebSocket cleanup, notification cleanup)
Feb 18 14:23:11 vps uvicorn[12345]: INFO:app.main:🚀 HB Tracking API v1 iniciada
Feb 18 14:23:11 vps uvicorn[12345]: INFO:uvicorn.error:Started server process [12345]
Feb 18 14:23:11 vps uvicorn[12345]: INFO:uvicorn.error:Waiting for application startup.
Feb 18 14:23:11 vps uvicorn[12345]: INFO:uvicorn.error:Application startup complete.
Feb 18 14:23:11 vps uvicorn[12345]: INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

Filtrando por 'RUNTIME' ou 'sys.executable':
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME sys.executable = /home/deploy/hbtrack-backend/current/venv/bin/python
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME sys.version = 3.11.5 (main, Sep 11 2023, 13:54:46) [GCC 11.4.0]
Feb 18 14:23:10 vps uvicorn[12345]: WARNING:app.main:RUNTIME Python 3.11.5

========================================
Resumo
========================================
✓ Todas as verificações passaram

Exit code: 0
```

---

## Cenário: VPS com Python 3.8 (problema detectado)

```bash
$ /tmp/diag_vps_python_runtime.sh

========================================
1. Python do venv (usado pelo systemd)
========================================
Python executable: /home/deploy/hbtrack-backend/current/venv/bin/python

sys.executable:
  /home/deploy/hbtrack-backend/current/venv/bin/python

sys.version:
  3.8.10 (default, Nov 14 2022, 12:59:47) [GCC 9.4.0]

Major.Minor: 3.8
⚠ Venv está usando Python 3.8 (pode ter incompatibilidades com código 3.11+)

========================================
2. Comando systemd (ExecStart)
========================================
[...conteúdo similar...]
✓ ExecStart usa o venv esperado (/home/deploy/hbtrack-backend/current/venv)

========================================
3. Python do processo em execução
========================================
[...conteúdo similar...]
✓ Processo está usando Python do venv esperado

========================================
4. Compatibilidade do código com runtime
========================================
A) Compilando código (detecção de sintaxe incompatível)...
✗ Código FALHOU ao compilar:
  File "/home/deploy/hbtrack-backend/current/app/services/some_service.py", line 123
    match user_role:
          ^
SyntaxError: invalid syntax

B) Importando entrypoint (app.main)...
✗ Falha ao importar app.main:
ModuleNotFoundError: No module named 'typing_extensions'

C) Verificando dependências (pip check)...
⚠ Dependências com problemas:
fastapi 0.104.1 requires pydantic>=2.0.0, but you have pydantic 1.10.13

========================================
5. Logs recentes do serviço (journalctl)
========================================
[...logs anteriores...]
Feb 18 12:10:05 vps uvicorn[9876]: WARNING:app.main:RUNTIME sys.executable = /home/deploy/hbtrack-backend/current/venv/bin/python
Feb 18 12:10:05 vps uvicorn[9876]: WARNING:app.main:RUNTIME sys.version = 3.8.10 (default, Nov 14 2022, 12:59:47) [GCC 9.4.0]
Feb 18 12:10:05 vps uvicorn[9876]: WARNING:app.main:RUNTIME Python 3.8.10

========================================
Resumo
========================================
✗ Verificações críticas falharam - AÇÃO NECESSÁRIA

Exit code: 2
```

---

## Interpretação dos Resultados

### Exit Code 0 (OK)
- ✅ Python do venv está atualizado
- ✅ ExecStart aponta para o venv correto
- ✅ Processo em execução usa o Python certo
- ✅ Código compila sem erros
- ✅ Entrypoint importa corretamente
- ✅ Dependências satisfeitas

→ **Nenhuma ação necessária**

### Exit Code 1 (AVISO)
- ⚠ Pequenas divergências não-críticas detectadas
- ⚠ Ex: dependências desatualizadas mas funcionais

→ **Revisar logs, considerar atualização**

### Exit Code 2 (ERRO)
- ❌ Código não compila no Python da VPS
- ❌ Entrypoint não importa
- ❌ Dependências críticas faltando

→ **AÇÃO IMEDIATA NECESSÁRIA** (ver troubleshooting no README.md)

---

## Ver também

- [README.md](README.md) — Instruções completas e troubleshooting
- [docs/playbooks/pb_vps_python_runtime.md](../../../docs/playbooks/pb_vps_python_runtime.md) — Protocolo completo
