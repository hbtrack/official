<!-- STATUS: NEEDS_REVIEW -->

# 🚀 Checklist de Deploy - Implementação Async

**Data**: 2024-01-14
**Versão**: 1.0 - Production Ready
**Objetivo**: Deploy seguro das correções async em staging/produção

---

## ✅ Pré-requisitos

- [x] Sprint 1 completa (services async)
- [x] Sprint 2 completa (relationships)
- [x] Validação 100% executada
- [x] Documentação atualizada
- [x] Rollback plan preparado

---

## 📋 Checklist de Deploy em Staging

### 1. Preparação (5 min)

```bash
# 1.1 Fazer backup do código atual
cd /path/to/hbtrack-backend
git branch backup-pre-async-$(date +%Y%m%d)
git push origin backup-pre-async-$(date +%Y%m%d)

# 1.2 Verificar branch
git status
git log --oneline -5

# 1.3 Verificar que está no diretório correto
pwd
```

**Checklist:**
- [ ] Backup criado
- [ ] Branch verificado
- [ ] Git log mostra commits async

---

### 2. Deploy (10 min)

```bash
# 2.1 Pull das mudanças (se aplicável)
git pull origin main

# 2.2 Verificar que não há migrations pendentes
alembic current
alembic heads

# 2.3 Reiniciar servidor
systemctl restart hbtrack-api
# OU
docker-compose restart api
# OU
supervisorctl restart hbtrack

# 2.4 Aguardar inicialização (30 segundos)
sleep 30
```

**Checklist:**
- [ ] Pull executado
- [ ] Migrations verificadas (nenhuma necessária)
- [ ] Servidor reiniciado
- [ ] Aguardou inicialização

---

### 3. Verificação Imediata (5 min)

```bash
# 3.1 Health check
curl http://localhost:8000/health
# Esperado: {"status": "ok"}

# 3.2 Verificar logs (últimas 50 linhas)
tail -50 /var/log/hbtrack/api.log

# 3.3 Procurar erros críticos
tail -500 /var/log/hbtrack/api.log | grep -i "error\|exception\|traceback"

# 3.4 Procurar erros async específicos
tail -500 /var/log/hbtrack/api.log | grep -E "awaited|DetachedInstance"
```

**Checklist:**
- [ ] Health check OK
- [ ] Logs sem erros críticos
- [ ] Logs sem erros "can't be awaited"
- [ ] Logs sem "DetachedInstanceError"

---

### 4. Testes Funcionais (15 min)

#### 4.1 Autenticação (CRÍTICO)
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Extrair token da resposta
export TOKEN="<token-from-response>"

# Testar /users/me (usa User.person relationship)
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:**
- [ ] Login retorna 200
- [ ] Token válido
- [ ] /users/me retorna dados de user + person
- [ ] Sem erros de lazy loading

#### 4.2 Matches Service (CRÍTICO)
```bash
# Listar matches
curl -X GET "http://localhost:8000/api/v1/matches?page=1&size=20" \
  -H "Authorization: Bearer $TOKEN"

# Verificar resposta
# Esperado: Lista de matches sem erros
```

**Checklist:**
- [ ] Listagem retorna 200
- [ ] Response tem matches[]
- [ ] Sem erros async nos logs

#### 4.3 Training Sessions
```bash
# Listar training sessions
curl -X GET "http://localhost:8000/api/v1/training-sessions?page=1&size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Checklist:**
- [ ] Listagem retorna 200
- [ ] Sem erros async

#### 4.4 Competitions
```bash
# Listar competitions
curl -X GET "http://localhost:8000/api/v1/competitions?page=1&size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Checklist:**
- [ ] Listagem retorna 200
- [ ] Relationships (team, creator) funcionando
- [ ] Sem erros async

---

### 5. Monitoramento (24h)

```bash
# 5.1 Script de monitoramento contínuo
watch -n 60 'tail -100 /var/log/hbtrack/api.log | grep -c "error\|exception"'

# 5.2 Monitorar erros async específicos
watch -n 300 'tail -500 /var/log/hbtrack/api.log | grep -E "awaited|DetachedInstance"'

# 5.3 Monitorar latência (se Prometheus disponível)
# curl http://localhost:9090/api/v1/query?query=http_request_duration_seconds
```

**Métricas a observar (24h):**
- [ ] Taxa de erro HTTP < 1%
- [ ] Latência p95 < 500ms
- [ ] Zero erros "can't be awaited"
- [ ] Zero "DetachedInstanceError"
- [ ] Taxa de autenticação OK > 99%

---

## 🚨 Critérios de Rollback

**EXECUTAR ROLLBACK SE:**
- [ ] Taxa de erro > 5% em 15 minutos
- [ ] Qualquer erro "can't be awaited" detectado
- [ ] Qualquer "DetachedInstanceError" detectado
- [ ] Autenticação falhando (> 10% de falhas)
- [ ] Latência p95 > 2 segundos

---

## ⏮️ Procedimento de Rollback

```bash
# 1. URGENTE - Voltar para versão anterior
git checkout backup-pre-async-$(date +%Y%m%d)

# 2. Reiniciar servidor
systemctl restart hbtrack-api

# 3. Verificar health
curl http://localhost:8000/health

# 4. Notificar equipe
echo "ROLLBACK EXECUTADO - $(date)" >> /var/log/hbtrack/rollback.log

# 5. Investigar logs
tail -1000 /var/log/hbtrack/api.log > /tmp/error-analysis-$(date +%Y%m%d-%H%M).log
```

---

## ✅ Deploy em Produção

**SOMENTE APÓS:**
- [ ] Staging rodando 48h sem erros
- [ ] Todos os testes funcionais OK
- [ ] Monitoramento 24h sem alertas
- [ ] Aprovação do tech lead

**Procedimento:**
1. Seguir mesmos passos de staging
2. Fazer deploy em horário de baixo tráfego (madrugada)
3. Monitorar por 72h
4. Manter rollback preparado por 1 semana

---

## 📊 Métricas de Sucesso

### Imediato (primeiras 2h)
- [ ] Zero erros async
- [ ] Autenticação 100% funcional
- [ ] Endpoints críticos respondendo

### 24 horas
- [ ] Taxa de erro < 1%
- [ ] Latência mantida ou melhorada
- [ ] Zero erros async detectados

### 1 semana
- [ ] Sistema estável
- [ ] Performance igual ou melhor
- [ ] Usuários sem reclamações

---

## 📞 Contatos de Emergência

**Em caso de problemas críticos:**
1. Executar rollback imediatamente
2. Notificar tech lead
3. Salvar logs para análise
4. Documentar o problema

---

## 📝 Log de Deploy

### Staging
- [ ] Data/Hora deploy: _______________
- [ ] Responsável: _______________
- [ ] Health check: [ ] OK [ ] ERRO
- [ ] Testes funcionais: [ ] OK [ ] ERRO
- [ ] Após 24h: [ ] OK [ ] ROLLBACK

### Produção
- [ ] Data/Hora deploy: _______________
- [ ] Responsável: _______________
- [ ] Health check: [ ] OK [ ] ERRO
- [ ] Testes funcionais: [ ] OK [ ] ERRO
- [ ] Após 72h: [ ] OK [ ] ROLLBACK

---

## 🎯 Aprovação Final

**Staging aprovado por:**
- [ ] Tech Lead: _______________ Data: ___/___/___
- [ ] DevOps: _______________ Data: ___/___/___

**Produção aprovada por:**
- [ ] Tech Lead: _______________ Data: ___/___/___
- [ ] Product Manager: _______________ Data: ___/___/___

---

**Versão**: 1.0
**Última atualização**: 2024-01-14
**Próxima revisão**: Após deploy em produção
