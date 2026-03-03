# Fix Celery Worker Service on VPS
# Corrige o path da aplicação Celery e reinicia o serviço

Write-Host "=== Corrigindo Celery Worker na VPS ===" -ForegroundColor Cyan

# 1. Corrigir o path no arquivo de serviço
Write-Host "`n1. Corrigindo path de app.worker.app para app.core.celery_app..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S sed -i 's|app.worker.app|app.core.celery_app|' /etc/systemd/system/hbtrack-worker.service"

# 2. Verificar correção
Write-Host "`n2. Verificando arquivo corrigido..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S cat /etc/systemd/system/hbtrack-worker.service"

# 3. Recarregar systemd
Write-Host "`n3. Recarregando systemd daemon..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S systemctl daemon-reload"

# 4. Reiniciar serviço
Write-Host "`n4. Reiniciando hbtrack-worker..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S systemctl restart hbtrack-worker"

Start-Sleep -Seconds 3

# 5. Verificar status
Write-Host "`n5. Verificando status do serviço..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S systemctl status hbtrack-worker --no-pager -l"

# 6. Verificar processo Celery rodando
Write-Host "`n6. Verificando processos Celery..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "ps aux | grep -i '[c]elery' || echo 'Nenhum processo Celery encontrado'"

# 7. Verificar logs recentes
Write-Host "`n7. Logs recentes do worker (últimas 20 linhas)..." -ForegroundColor Yellow
ssh -i $env:USERPROFILE\.ssh\hbtrack_deploy davi@191.252.185.34 "echo 98701665 | sudo -S journalctl -u hbtrack-worker -n 20 --no-pager"

Write-Host "`n=== Processo concluído ===" -ForegroundColor Green
Write-Host "`nSe o status mostrar 'active (running)', o worker está operacional!" -ForegroundColor Green
