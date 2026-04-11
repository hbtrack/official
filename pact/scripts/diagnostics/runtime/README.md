# Diagnósticos de Runtime

Scripts para verificar objetivamente o ambiente de execução Python na VPS e compatibilidade do código HB Track.

## Scripts

### `diag_vps_python_runtime.sh`

Script bash que executa verificação completa do runtime Python na VPS.

**Verificações realizadas:**

1. **Python do venv** — Confirma qual Python o systemd está configurado para usar
2. **Comando systemd** — Mostra o `ExecStart` real do serviço (não o da doc)
3. **Python do processo** — Inspeciona `/proc/<PID>/exe` para ver qual Python está rodando
4. **Compatibilidade do código** — Testa se o código HB Track é compatível com o Python detectado:
   - Compila todos os `.py` (detecta `match/case`, sintaxe inválida)
   - Importa `app.main` (detecta type hints/stdlib incompatíveis)
   - Verifica dependências (`pip check`)
5. **Logs do journald** — Busca evidências de runtime anteriores no log do serviço

**Uso:**

```bash
# 1. Copiar para VPS
scp scripts/diagnostics/runtime/diag_vps_python_runtime.sh deploy@SEU_IP_VPS:/tmp/

# 2. SSH na VPS
ssh deploy@SEU_IP_VPS

# 3. Executar
chmod +x /tmp/diag_vps_python_runtime.sh
/tmp/diag_vps_python_runtime.sh
```

**Exit codes:**

- `0` = OK (todas verificações passaram)
- `1` = AVISO (verificações não-críticas falharam)
- `2` = ERRO (verificações críticas falharam)

**Side-effects:** `FS_READ`, `DB_READ` (somente leitura)

---

## Evidência de Runtime no Journald

O `app/main.py` foi modificado para registrar informações de runtime Python **toda vez que o serviço inicia**.

Isso cria evidência permanente no journald que pode ser consultada a qualquer momento:

```bash
# Ver logs de startup recentes
journalctl -u hbtrack-backend.service -n 100 --no-pager | grep RUNTIME

# Ver última inicialização
journalctl -u hbtrack-backend.service --since today | grep RUNTIME
```

**Exemplo de saída:**

```
RUNTIME sys.executable = /home/deploy/hbtrack-backend/current/venv/bin/python
RUNTIME sys.version = 3.11.5 (main, Sep 11 2023, 13:54:46) [GCC 11.4.0]
RUNTIME Python 3.11.5
```

---

## Troubleshooting

### O script reporta Python 3.8 mas você desenvolve em 3.11+

**Causa:** O venv da VPS foi criado com Python 3.8 do sistema.

**Solução:**

1. Instalar Python 3.11+ na VPS:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   ```

2. Recriar o venv:
   ```bash
   cd /home/deploy/hbtrack-backend/current
   python3.11 -m venv venv
   ./venv/bin/pip install -r requirements.txt
   ```

3. Reiniciar o serviço:
   ```bash
   sudo systemctl restart hbtrack-backend.service
   ```

### O script falha ao compilar ou importar

**Causa:** Código usa features Python > 3.8 (ex: `match/case`, novos type hints).

**Ações:**

1. Identificar qual arquivo/linha falhou (output do script)
2. Verificar compatibilidade no código-fonte
3. Opções:
   - Atualizar Python da VPS (recomendado)
   - ou Refatorar código para ser compatível com 3.8

### ExecStart usa flags de gunicorn mas é uvicorn

**Causa:** Configuração incorreta no `hbtrack-backend.service`.

**Solução:**

Editar `/etc/systemd/system/hbtrack-backend.service`:

```ini
[Service]
ExecStart=/home/deploy/hbtrack-backend/current/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --log-config logging.conf
```

Recarregar:

```bash
sudo systemctl daemon-reload
sudo systemctl restart hbtrack-backend.service
```

---

## Integração com CI/CD

Este script **não** faz parte dos gates de CI local porque requer ambiente VPS.

Ele é executado **manualmente** quando:

- Houver suspeita de divergência Python dev vs prod
- Após atualização de Python na VPS
- Para auditoria de runtime (compliance)

---

## Ver também

- [VPS/infra/SYSTEMD.md](../../../VPS/infra/SYSTEMD.md) — Configuração do systemd
- [ROADMAP.md](../../../ROADMAP.md) — Status do projeto
- [protocolos de validação.md](../../../protocolos%20de%20validação.md) — Protocolos de verificação
