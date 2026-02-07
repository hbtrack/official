<!-- STATUS: NEEDS_REVIEW -->

# 🔧 Troubleshooting - Failed to Fetch Error

## Erro Detectado

```
TypeError: Failed to fetch
at request (trainings.ts)
at getSessions (trainings.ts)
at useSessions (useSessions.ts)
```

## Causa Provável

O erro "Failed to fetch" ocorre quando o navegador **não consegue nem iniciar** a requisição HTTP. Isso acontece ANTES do CORS, e indica:

1. ✅ **Backend não está rodando** (mais provável)
2. ⚠️ URL da API malformada
3. ⚠️ Problema de DNS/rede local
4. ⚠️ Cache do Next.js/Turbopack

## ✅ Verificações Realizadas

- ✅ Backend responde na porta 8000 (testado com Python socket)
- ✅ Endpoint `/api/v1/health` retorna 200 OK
- ✅ Endpoint `/api/v1/training-sessions` existe (retorna 401 sem auth)
- ✅ CORS configurado corretamente no backend
- ✅ Variável `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1` configurada
- ✅ Componente SessionsList tem tratamento de erro
- ✅ Hook useSessions melhorado com mensagens específicas

## 🔍 Melhorias Aplicadas

### 1. Hook useSessions.ts
```typescript
// Adicionado tratamento específico para "Failed to fetch"
catch (err) {
  if (errorMessage.includes('Failed to fetch')) {
    error: 'Não foi possível conectar ao servidor. Verifique se o backend está rodando.'
  } else if (errorMessage.includes('401')) {
    error: 'Sessão expirada. Faça login novamente.'
  }
}
```

### 2. API Client (client.ts)
```typescript
// Adicionado try-catch específico para TypeError de rede
catch (err) {
  if (err instanceof TypeError && err.message === 'Failed to fetch') {
    throw new Error(`Failed to fetch: Não foi possível conectar ao backend em ${url}`);
  }
}

// Adicionado log de debug
console.log(`[API] ${method} ${url}`, { hasToken: !!token });
```

## 🚀 Solução - Checklist

### Passo 1: Verificar Backend Rodando

```powershell
# Terminal 1 - Verificar se o backend está UP
cd "c:\HB TRACK\Hb Track - Backend"
python -c "import socket; sock = socket.socket(); sock.settimeout(1); result = sock.connect_ex(('127.0.0.1', 8000)); print('✅ Backend UP' if result == 0 else '❌ Backend DOWN'); sock.close()"
```

**Se backend não estiver rodando:**

```powershell
# Iniciar backend
cd "c:\HB TRACK\Hb Track - Backend"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Passo 2: Verificar Frontend

```powershell
# Terminal 2 - Parar e reiniciar o dev server do Next.js
cd "c:\HB TRACK\Hb Track - Fronted"

# Parar (Ctrl+C se estiver rodando)

# Limpar cache do Turbopack
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue

# Reiniciar
npm run dev
```

### Passo 3: Verificar Autenticação

1. Abra o navegador em `http://localhost:3000`
2. Faça login novamente
3. Abra DevTools (F12) → Console
4. Acesse `/trainings/sessions`
5. Verifique os logs:

```
[API] GET http://127.0.0.1:8000/api/v1/training-sessions { hasToken: true/false }
```

**Se `hasToken: false`:**
- Cookie `hb_access_token` não existe
- Usuário não está autenticado
- Fazer login novamente

### Passo 4: Testar Endpoint Direto

```powershell
# Testar sem autenticação (deve retornar 401)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/training-sessions" -UseBasicParsing
# Esperado: {"detail":{"error_code":"UNAUTHORIZED",...}}

# Se retornar "Connection refused" ou erro de rede:
# Backend não está rodando!
```

## 🎯 Diagnóstico Final

Com base nos testes:

1. **Backend está respondendo** ✅
2. **CORS configurado** ✅  
3. **Endpoint existe** ✅
4. **Frontend tem .env correto** ✅

**Ação necessária:**

O erro "Failed to fetch" ocorre porque:

### Opção A: Backend não está realmente rodando
- Testar: `Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health"`
- Se falhar: Iniciar backend com uvicorn

### Opção B: Next.js não pegou a variável de ambiente
- **Solução:** Reiniciar o dev server do Next.js
- Mudanças em `.env.local` só são aplicadas após restart

### Opção C: Problema de autenticação
- Frontend tenta fazer fetch sem token
- Backend retorna 401
- Erro é capturado mas mensagem é genérica
- **Solução:** Verificar se usuário está logado e cookie existe

## 📝 Próximos Passos

1. **Reinicie o backend E o frontend** (ordem importante!)
2. **Faça login novamente** no sistema
3. **Verifique o console do navegador** para logs de debug
4. Se persistir, compartilhe:
   - Logs do console (F12)
   - Log do terminal do backend
   - Resultado de `Get-Content .env.local` no frontend

## 🔧 Comandos Rápidos de Diagnóstico

```powershell
# Teste completo de conectividade
cd "c:\HB TRACK"

# 1. Backend UP?
cd "Hb Track - Backend"
python -c "import socket; sock = socket.socket(); print('✅ Backend UP' if sock.connect_ex(('127.0.0.1', 8000)) == 0 else '❌ Backend DOWN')"

# 2. API responde?
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -UseBasicParsing | Select-Object StatusCode

# 3. Variável de ambiente?
cd "..\Hb Track - Fronted"
Get-Content .env.local | Select-String "API_URL"

# 4. Token existe? (abrir no navegador console)
document.cookie.match(/hb_access_token/)
```

## ✅ Checklist de Solução

- [ ] Backend rodando (porta 8000)
- [ ] Frontend reiniciado (limpar cache .next)
- [ ] Usuário autenticado (cookie hb_access_token existe)
- [ ] Console do navegador mostra logs `[API] GET ...`
- [ ] Sem erros de CORS no console
- [ ] Mensagem de erro específica aparece no componente

**Após aplicar as correções acima, o erro deve ser substituído por uma mensagem clara:**
- "Não foi possível conectar ao servidor. Verifique se o backend está rodando."
- OU "Sessão expirada. Faça login novamente."
