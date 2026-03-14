# WORKSPACE_MIGRATION_NOTICE.md

**Data de Cutover:** 2026-03-13  
**Status:** ATIVO — Linux/WSL promovido como ambiente primário

---

## Decisão Operacional

A partir de **13 de março de 2026**, o ambiente de desenvolvimento canônico do projeto **HB Track** é:

**✅ Primário (ATIVO):**
- **Path:** `/home/davis/HB-TRACK` (WSL/Linux)
- **Uso:** Desenvolvimento, commits, testes, gates, evidências

**⚠️ Legado (BACKUP TEMPORÁRIO):**
- **Path:** `C:\HB TRACK` (Windows)
- **Uso:** Apenas contingência temporária — **NÃO** usar para desenvolvimento ativo
- **Status:** Congelado após cutover

---

## Regra de Gold Copy

**O workspace ativo único é `/home/davis/HB-TRACK`.**

Qualquer edição operacional deve ocorrer no ambiente WSL/Linux. O path Windows não deve receber:
- Novos commits originados dele
- Edições de código/docs com intenção de merge
- Execução de gates/validações oficiais
- Geração de artefatos para evidência

---

## Critério de Remoção do Backup Windows

O diretório `C:\HB TRACK` **poderá ser removido** quando:

1. ✅ Checklist de cutover WSL completo (10/10 seções)
2. ✅ Ao menos **1 ciclo completo de desenvolvimento** executado no WSL com sucesso (edição → commit → push → validação)
3. ✅ Ausência de problemas críticos no ambiente WSL por **7+ dias**
4. ✅ Confiança operacional baseada em evidência (não em percepção)

**Recomendação:** Aguardar pelo menos **2 semanas** de operação estável antes de remover.

---

## Evidências de Cutover

Consultar arquivos de evidência:
- **WSL:** `~/HB-TRACK/WSL_CUTOVER_STATUS.md`
- **Windows:** `C:\HB TRACK\WSL_CUTOVER_EVIDENCE.md`

---

## Instruções de Remoção (Quando Aplicável)

**⚠️ NÃO EXECUTAR antes de cumprir os critérios acima.**

```powershell
# Quando estiver pronto (após 2+ semanas de operação WSL estável):
# 1. Fazer backup final (opcional)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path "C:\HB TRACK" -DestinationPath "C:\Backups\HB_TRACK_final_$timestamp.zip"

# 2. Remover diretório Windows
Remove-Item -Path "C:\HB TRACK" -Recurse -Force -Confirm
```

---

## Contato / Dúvidas

Em caso de problemas no ambiente WSL ou necessidade de reverter temporariamente, consulte:
- [WSL_CUTOVER_EVIDENCE.md](WSL_CUTOVER_EVIDENCE.md)
- [PLANO.MD](PLANO.MD) — checklist completo de cutover
- GitHub Issues do projeto

---

**Última atualização:** 2026-03-13  
**Responsável:** Davis (via GitHub Copilot — cutover automatizado)
