# Protocolo de Verificação: Runtime Python VPS

> **Status:** ATIVO  
> **Criado:** 2026-02-18  
> **Objetivo:** Verificar objetivamente qual Python a VPS está usando e se o código HB Track é compatível

---

## Contexto

Durante desenvolvimento local, pode haver divergência entre:

- **Python de desenvolvimento** (ex: 3.11+ com syntax moderna)
- **Python da VPS** (ex: 3.8 instalado no sistema)

Isso causa bugs silenciosos onde:
- ✅ Código funciona localmente
- ❌ Código quebra em produção (ou usa runtime diferente do documentado)

---

## Verificação Objetiva (Sem Suposição)

### 1. Qual Python o systemd está configurado para usar?

```bash
systemctl cat hbtrack-backend.service
systemctl show hbtrack-backend.service -p ExecStart
```

**Checagem:** O `ExecStart` aponta para `/home/deploy/.../venv/bin/uvicorn` ou `/usr/bin/python3`?

### 2. Qual Python o venv foi criado?

```bash
/home/deploy/hbtrack-backend/current/venv/bin/python -c "import sys; print(sys.version)"
```

**Checagem:** Versão é 3.8.x, 3.11.x, ou outra?

### 3. Qual Python o processo rodando agora está usando?

```bash
systemctl status hbtrack-backend.service --no-pager
# Pegar o PID e executar:
readlink -f /proc/<PID>/exe
```

**Checagem:** O symlink aponta para qual binário Python?

### 4. O código HB Track é compatível com esse Python?

```bash
# A) Compilar (detecta match/case, sintaxe)
/home/deploy/.../venv/bin/python -m compileall -q /home/deploy/.../app

# B) Importar (detecta type hints/stdlib)
/home/deploy/.../venv/bin/python -c "import importlib; importlib.import_module('app.main'); print('OK')"

# C) Dependências
/home/deploy/.../venv/bin/python -m pip check
```

**Checagem:** Todos os comandos retornam exit code 0?

### 5. Evidência permanente no journald

```bash
journalctl -u hbtrack-backend.service --no-pager | grep RUNTIME
```

**Checagem:** Logs contêm `RUNTIME sys.executable` e `RUNTIME sys.version`?

---

## Script Automatizado

Todas essas verificações foram consolidadas em:

```bash
scripts/diagnostics/runtime/diag_vps_python_runtime.sh
```

**Uso:**

```bash
# Copiar para VPS
scp scripts/diagnostics/runtime/diag_vps_python_runtime.sh deploy@VPS:/tmp/

# Executar na VPS
ssh deploy@VPS
chmod +x /tmp/diag_vps_python_runtime.sh
/tmp/diag_vps_python_runtime.sh
```

**Saída:**
- Relatório completo de todos os 5 níveis de verificação
- Exit code: `0` = OK, `1` = AVISO, `2` = ERRO

---

## Ações Corretivas

### Se Python da VPS é 3.8 e código usa 3.11+

**Opção A: Atualizar Python da VPS (recomendado)**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
cd /home/deploy/hbtrack-backend/current
python3.11 -m venv venv
./venv/bin/pip install -r requirements.txt
sudo systemctl restart hbtrack-backend.service
```

**Opção B: Refatorar código para Python 3.8**

- Remover `match/case`
- Usar `typing` backports (`typing_extensions`)
- Evitar novos type hints (`X | Y` → `Union[X, Y]`)

### Se ExecStart está errado

Editar `/etc/systemd/system/hbtrack-backend.service`:

```ini
[Service]
ExecStart=/home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recarregar:

```bash
sudo systemctl daemon-reload
sudo systemctl restart hbtrack-backend.service
```

---

## Evidência de Runtime Automática

**Modificação em `app/main.py`:**

No evento `startup`, o app agora registra:

```python
import sys
logger.warning(f"RUNTIME sys.executable = {sys.executable}")
logger.warning(f"RUNTIME sys.version = {sys.version}")
```

**Benefício:**
- Toda vez que o serviço sobe, o journald registra qual Python foi usado
- Evidência permanente, auditável, sem comandos manuais
- Permite detectar mudanças de runtime ao longo do tempo

**Consulta:**

```bash
journalctl -u hbtrack-backend.service --since "1 week ago" | grep RUNTIME
```

---

## Quando Executar Este Protocolo

- ✅ Após atualização de Python na VPS
- ✅ Quando houver erro "module not found" ou "syntax error" só em produção
- ✅ Antes de deploy de features usando syntax Python 3.10+
- ✅ Auditoria trimestral de runtime (compliance)

---

## Referências

- [scripts/diagnostics/runtime/README.md](c:\HB TRACK\scripts\diagnostics\runtime\README.md)
- [scripts/diagnostics/runtime/diag_vps_python_runtime.sh](c:\HB TRACK\scripts\diagnostics\runtime\diag_vps_python_runtime.sh)
- [Hb Track - Backend/app/main.py](c:\HB TRACK\Hb Track - Backend\app\main.py) (startup event com logging de runtime)
