<!-- STATUS: NEEDS_REVIEW -->

# FLUXO DE TRABALHO FRONTEND - HB TRACKING

**Versão:** 1.0.0
**Projeto:** HB Tracking - Sistema de Gestão de Handebol
**RAG:** [REGRAS_SISTEMAS.md](REGRAS_SISTEMAS.md)
**Backend:** https://hbtrack.onrender.com/api/v1
**Data:** 2025-12-25

---

## 📚 SUMÁRIO

- [Introdução](#introdução)
- [Arquitetura Frontend](#arquitetura-frontend)
- [FASE 1: Setup e Configuração Inicial](#fase-1-setup-e-configuração-inicial)
- [FASE 2: Autenticação e Segurança](#fase-2-autenticação-e-segurança)
- [FASE 3: Integração com Backend](#fase-3-integração-com-backend)
- [FASE 4: Personalização Visual](#fase-4-personalização-visual)
- [FASE 5: Dashboard Principal](#fase-5-dashboard-principal)
- [FASE 6: Páginas de Relatórios (R1-R4)](#fase-6-páginas-de-relatórios-r1-r4)
- [FASE 7: Mensagens e Notificações](#fase-7-mensagens-e-notificações)
- [FASE 8: Refinamento e Deploy](#fase-8-refinamento-e-deploy)
- [Apêndices](#apêndices)

---

## 🎯 INTRODUÇÃO

### Objetivo do Fluxo

Este documento define **a ordem exata de implementação do frontend** do HB Tracking utilizando o template **TailAdmin Next.js** integrado ao backend FastAPI já deployado.

### Princípios de Implementação

1. **Zero Breaking Changes**: Cada fase deve ser testável e funcionando antes da próxima
2. **Backend First**: Toda tela deve consumir dados reais do backend (https://hbtrack.onrender.com/api/v1)
3. **Conformidade RAG**: Seguir REGRAS_SISTEMAS.md em todas as decisões
4. **Granularidade Máxima**: Cada passo tem comandos exatos, código completo e verificação
5. **Auditabilidade Visual**: Cada fase termina com links para o humano validar visualmente

### Stack Tecnológico (Definitivo)

**Core:**
- Next.js 16 (App Router)
- React 19
- TypeScript 5+
- Tailwind CSS v4

**Bibliotecas:**
- ApexCharts (gráficos de relatórios)
- React Hook Form + Zod (formulários e validação)
- Zustand (state management)
- date-fns (manipulação de datas)

**Integração:**
- Server Components (data fetching)
- Server Actions (backend calls)
- httpOnly Cookies (JWT storage)
- Middleware (route protection)

### Backend Disponível (100% Operacional)

**Endpoints de Autenticação:**
- `POST /api/v1/auth/login` → JWT token
- `POST /api/v1/auth/refresh` → Renovar token
- `GET /api/v1/auth/me` → Dados do usuário logado

**Endpoints de Relatórios (R1-R4):**
- `GET /api/v1/reports/training-performance` → R1 (Performance em Treinos)
- `GET /api/v1/reports/training-trends` → R1 (Tendências de treinos)
- `GET /api/v1/reports/athletes` → R2 (Lista de atletas)
- `GET /api/v1/reports/athletes/{id}` → R2 (Atleta individual)
- `GET /api/v1/reports/wellness-summary` → R3 (Prontidão e Bem-Estar)
- `GET /api/v1/reports/medical-summary` → R4 (Gerenciamento de Lesões)

**Endpoints de Refresh (POST):**
- `POST /api/v1/reports/refresh-training-performance`
- `POST /api/v1/reports/refresh-athletes`
- `POST /api/v1/reports/refresh-wellness`
- `POST /api/v1/reports/refresh-medical`

**Autenticação:**
- JWT Bearer Token
- Roles: `admin`, `coordenador`, `treinador`, `atleta`
- Token expira em 7 dias

---

## 🏗️ ARQUITETURA FRONTEND

### Estrutura de Camadas

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 1: PÁGINAS (App Router)                        │
│  └─ Server Components + Client Components              │
│     Ex: app/(dashboard)/dashboard/page.tsx              │
└─────────────────────────────────────────────────────────┘
              ↓ usa ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 2: SERVER ACTIONS                               │
│  └─ Comunicação com backend FastAPI                    │
│     Ex: lib/reports/actions.ts                          │
└─────────────────────────────────────────────────────────┘
              ↓ chama ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 3: BACKEND API (FastAPI)                        │
│  └─ https://hbtrack.onrender.com/api/v1                │
└─────────────────────────────────────────────────────────┘
              ↓ retorna ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 4: POSTGRESQL (Neon)                            │
│  └─ Materialized Views (R1-R4)                          │
└─────────────────────────────────────────────────────────┘
```

### Padrão de Nomenclatura

**Páginas (App Router):**
- Formato: `app/(grupo)/[pagina]/page.tsx`
- Exemplo: `app/(dashboard)/training-performance/page.tsx`

**Server Actions:**
- Prefixo: `'use server'` (primeira linha)
- Localização: `src/lib/[dominio]/actions.ts`
- Exemplo: `src/lib/auth/actions.ts`, `src/lib/reports/actions.ts`

**Client Components:**
- Prefixo: `'use client'` (primeira linha)
- Localização: `src/components/[categoria]/`
- Exemplo: `src/components/Charts/TrainingChart.tsx`

**TypeScript Types:**
- Localização: `src/types/`
- Exemplo: `src/types/reports.ts`, `src/types/auth.ts`

**Stores (Zustand):**
- Localização: `src/store/`
- Exemplo: `src/store/notifications.ts`

---

## 🔧 FASE 1: SETUP E CONFIGURAÇÃO INICIAL

**Objetivo:** Clonar template TailAdmin Next.js, configurar ambiente e estruturar projeto.

**Duração Estimada:** 30-45 minutos

**Pré-requisitos:**
- Node.js 18+ instalado
- Git instalado
- Editor de código (VSCode recomendado)

---

### 1.1 - Clonar e Instalar Template

**Passo 1.1.1:** Clonar template TailAdmin Next.js

```bash
cd "c:\Hb Tracking"
git clone https://github.com/TailAdmin/free-nextjs-admin-dashboard.git hb-tracking-frontend
cd hb-tracking-frontend
```

**Verificação:**
```bash
ls -la
# Deve mostrar: package.json, next.config.ts, app/, src/, public/
```

---

**Passo 1.1.2:** Instalar dependências

```bash
npm install
```

**Verificação:**
```bash
npm list --depth=0
# Deve mostrar: next@16.x.x, react@19.x.x, typescript@5.x.x
```

---

**Passo 1.1.3:** Testar execução local

```bash
npm run dev
```

**Verificação Manual:**
1. Abrir navegador: http://localhost:3000
2. Deve exibir dashboard do template TailAdmin
3. Navegar para: http://localhost:3000/auth/signin
4. Confirmar que página de login existe

**Links para Verificação Visual:**
- ✅ Dashboard: http://localhost:3000
- ✅ Login: http://localhost:3000/auth/signin
- ✅ Profile: http://localhost:3000/profile

**Parar servidor:** `Ctrl + C`

---

### 1.2 - Configurar Variáveis de Ambiente

**Passo 1.2.1:** Criar arquivo `.env.local`

```bash
touch .env.local
```

**Passo 1.2.2:** Adicionar variáveis de ambiente

**Arquivo:** `.env.local`

```env
# Backend API
NEXT_PUBLIC_API_URL=https://hbtrack.onrender.com/api/v1

# App Config
NEXT_PUBLIC_APP_NAME=HB Tracking
NEXT_PUBLIC_APP_DESCRIPTION=Sistema de Gestão de Handebol

# Session
SESSION_SECRET=hb-tracking-secret-key-2025-change-in-production

# Node Environment
NODE_ENV=development
```

**Referências RAG:**
- **R26**: Permissões por papel (URL do backend deve refletir ambiente)
- **RDB1**: Variáveis de ambiente não devem conter dados sensíveis do usuário

---

**Passo 1.2.3:** Adicionar `.env.local` ao `.gitignore`

**Arquivo:** `.gitignore` (verificar se já existe)

```gitignore
# Env files
.env*.local
.env.production
```

**Verificação:**
```bash
cat .env.local | grep NEXT_PUBLIC_API_URL
# Deve retornar: NEXT_PUBLIC_API_URL=https://hbtrack.onrender.com/api/v1
```

---

### 1.3 - Estruturar Diretórios do Projeto

**Passo 1.3.1:** Criar estrutura de pastas

```bash
mkdir -p src/lib/auth
mkdir -p src/lib/reports
mkdir -p src/lib/utils
mkdir -p src/types
mkdir -p src/store
mkdir -p src/components/Charts
mkdir -p src/components/Reports
mkdir -p src/components/Messages
mkdir -p src/components/Notifications
```

**Verificação:**
```bash
ls -la src/
# Deve mostrar: lib/, types/, store/, components/
```

---

**Passo 1.3.2:** Criar arquivo de tipos globais

**Arquivo:** `src/types/index.ts`

```typescript
/**
 * Tipos globais do HB Tracking Frontend
 *
 * Referências RAG:
 * - R26: Roles disponíveis (admin, coordenador, treinador, atleta)
 */

export type UserRole = 'admin' | 'coordenador' | 'treinador' | 'atleta'

export interface ApiError {
  detail: string
  status_code?: number
}

export interface PaginationParams {
  skip?: number
  limit?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}
```

---

**Passo 1.3.3:** Criar utilitário de fetch

**Arquivo:** `src/lib/utils/fetch.ts`

```typescript
/**
 * Utilitários de fetch para comunicação com backend
 *
 * Referências RAG:
 * - Backend: https://hbtrack.onrender.com/api/v1
 */

import { ApiError } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

export class ApiException extends Error {
  statusCode: number
  detail: string

  constructor(statusCode: number, detail: string) {
    super(detail)
    this.statusCode = statusCode
    this.detail = detail
    this.name = 'ApiException'
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'Unknown error',
      }))
      throw new ApiException(response.status, error.detail)
    }

    return response.json()
  } catch (error) {
    if (error instanceof ApiException) {
      throw error
    }
    throw new ApiException(500, 'Network error')
  }
}
```

---

### 1.4 - Configurar TypeScript

**Passo 1.4.1:** Atualizar `tsconfig.json`

**Arquivo:** `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/types/*": ["./src/types/*"],
      "@/store/*": ["./src/store/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Verificação:**
```bash
npx tsc --noEmit
# Não deve retornar erros
```

---

### 1.5 - Configurar Scripts NPM

**Passo 1.5.1:** Atualizar `package.json` (adicionar scripts)

**Arquivo:** `package.json` (adicionar à seção `"scripts"`)

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "format": "prettier --write \"src/**/*.{ts,tsx}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx}\""
  }
}
```

---

### ✅ CHECKLIST FASE 1: Setup e Configuração Inicial

- [ ] Template TailAdmin Next.js clonado
- [ ] Dependências instaladas (`npm install`)
- [ ] Servidor local rodando (`npm run dev`)
- [ ] Dashboard do template visível em http://localhost:3000
- [ ] Página de login visível em http://localhost:3000/auth/signin
- [ ] Arquivo `.env.local` criado com `NEXT_PUBLIC_API_URL`
- [ ] Estrutura de diretórios criada (lib/, types/, store/, components/)
- [ ] Arquivo `src/types/index.ts` criado
- [ ] Arquivo `src/lib/utils/fetch.ts` criado
- [ ] `tsconfig.json` atualizado com paths
- [ ] `package.json` atualizado com scripts
- [ ] Type check sem erros (`npm run type-check`)

### 🔗 LINKS PARA VERIFICAÇÃO VISUAL - FASE 1

**Antes de prosseguir, CONFIRME visualmente:**

1. **Dashboard Template:**
   http://localhost:3000
   ✅ Deve exibir dashboard com sidebar, header, stats cards

2. **Página de Login:**
   http://localhost:3000/auth/signin
   ✅ Deve exibir formulário de login com email/password

3. **Página de Profile:**
   http://localhost:3000/profile
   ✅ Deve exibir página de perfil (mesmo sem dados)

4. **Estrutura de Arquivos:**
   ```
   hb-tracking-frontend/
   ├── .env.local              ✅ Criado
   ├── src/
   │   ├── lib/
   │   │   ├── auth/           ✅ Criado (vazio)
   │   │   ├── reports/        ✅ Criado (vazio)
   │   │   └── utils/
   │   │       └── fetch.ts    ✅ Criado
   │   ├── types/
   │   │   └── index.ts        ✅ Criado
   │   ├── store/              ✅ Criado (vazio)
   │   └── components/
   │       ├── Charts/         ✅ Criado (vazio)
   │       ├── Reports/        ✅ Criado (vazio)
   │       ├── Messages/       ✅ Criado (vazio)
   │       └── Notifications/  ✅ Criado (vazio)
   ```

**⚠️ NÃO PROSSIGA PARA FASE 2 SEM CONFIRMAR TODOS OS ITENS ACIMA!**

---

## 🔐 FASE 2: AUTENTICAÇÃO E SEGURANÇA

**Objetivo:** Implementar autenticação JWT com Next.js App Router, middleware de proteção de rotas e gerenciamento de sessão.

**Duração Estimada:** 1-2 horas

**Pré-requisitos:**
- FASE 1 completa e verificada
- Backend de autenticação operacional: https://hbtrack.onrender.com/api/v1/auth/login

---

### 2.1 - Criar Tipos de Autenticação

**Passo 2.1.1:** Criar tipos de autenticação

**Arquivo:** `src/types/auth.ts`

```typescript
/**
 * Tipos de autenticação
 *
 * Referências RAG:
 * - R26: Roles (admin, coordenador, treinador, atleta)
 * - Backend: POST /api/v1/auth/login
 */

import { UserRole } from './index'

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface JWTPayload {
  sub: string          // user_id (UUID)
  email: string
  role: UserRole
  organization_id: string
  exp: number          // timestamp de expiração
  iat: number          // timestamp de emissão
}

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  organization_id: string
}

export interface Session {
  user: User
  accessToken: string
  expiresAt: number    // timestamp em ms
}

export interface AuthState {
  isAuthenticated: boolean
  user: User | null
  isLoading: boolean
}
```

---

### 2.2 - Implementar Decodificação de JWT

**Passo 2.2.1:** Criar utilitário de JWT

**Arquivo:** `src/lib/auth/jwt.ts`

```typescript
/**
 * Utilitários de JWT
 *
 * Referências RAG:
 * - JWT contém: sub (user_id), email, role, organization_id, exp, iat
 */

import { JWTPayload } from '@/types/auth'

/**
 * Decodifica JWT sem verificar assinatura (validação no backend)
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    const payload = parts[1]
    const decoded = JSON.parse(
      Buffer.from(payload, 'base64').toString('utf-8')
    )

    return decoded as JWTPayload
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

/**
 * Verifica se token está expirado
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token)
  if (!payload) return true

  const now = Math.floor(Date.now() / 1000)
  return payload.exp < now
}

/**
 * Calcula tempo restante até expiração (em ms)
 */
export function getTimeUntilExpiration(token: string): number {
  const payload = decodeJWT(token)
  if (!payload) return 0

  const now = Date.now()
  const expiresAt = payload.exp * 1000
  return Math.max(0, expiresAt - now)
}
```

---

### 2.3 - Implementar Server Actions de Autenticação

**Passo 2.3.1:** Criar Server Actions de login

**Arquivo:** `src/lib/auth/actions.ts`

```typescript
'use server'

/**
 * Server Actions de autenticação
 *
 * Referências RAG:
 * - R26: Autenticação via JWT
 * - Backend: POST /api/v1/auth/login
 */

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { LoginCredentials, LoginResponse, Session, User } from '@/types/auth'
import { decodeJWT } from './jwt'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

/**
 * Ação de login
 */
export async function loginAction(credentials: LoginCredentials) {
  try {
    // Chamada ao backend
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json()
      return {
        success: false,
        error: error.detail || 'Falha no login'
      }
    }

    const data: LoginResponse = await response.json()
    const payload = decodeJWT(data.access_token)

    if (!payload) {
      return {
        success: false,
        error: 'Token inválido'
      }
    }

    // Criar sessão
    const session: Session = {
      user: {
        id: payload.sub,
        email: payload.email,
        name: payload.email.split('@')[0], // Nome temporário
        role: payload.role,
        organization_id: payload.organization_id,
      },
      accessToken: data.access_token,
      expiresAt: payload.exp * 1000, // Converter para ms
    }

    // Salvar sessão em cookie httpOnly
    const cookieStore = await cookies()
    cookieStore.set('session', JSON.stringify(session), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 dias
      path: '/',
    })

    return { success: true }
  } catch (error) {
    console.error('Login error:', error)
    return {
      success: false,
      error: 'Erro de conexão com o servidor'
    }
  }
}

/**
 * Ação de logout
 */
export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
  redirect('/auth/signin')
}

/**
 * Obter sessão atual
 */
export async function getSession(): Promise<Session | null> {
  try {
    const cookieStore = await cookies()
    const sessionCookie = cookieStore.get('session')

    if (!sessionCookie) {
      return null
    }

    const session: Session = JSON.parse(sessionCookie.value)

    // Verificar se token expirou
    const now = Date.now()
    if (session.expiresAt < now) {
      // Sessão expirada, limpar cookie
      cookieStore.delete('session')
      return null
    }

    return session
  } catch (error) {
    console.error('Get session error:', error)
    return null
  }
}

/**
 * Obter usuário atual
 */
export async function getCurrentUser(): Promise<User | null> {
  const session = await getSession()
  return session?.user || null
}

/**
 * Verificar se usuário tem role específica
 */
export async function hasRole(allowedRoles: string[]): Promise<boolean> {
  const user = await getCurrentUser()
  if (!user) return false
  return allowedRoles.includes(user.role)
}
```

---

### 2.4 - Criar Hook de Autenticação (Client)

**Passo 2.4.1:** Criar hook `useAuth`

**Arquivo:** `src/lib/hooks/useAuth.ts`

```typescript
'use client'

/**
 * Hook de autenticação (client-side)
 *
 * Usa Server Actions para login/logout
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { loginAction, logoutAction } from '@/lib/auth/actions'
import { LoginCredentials } from '@/types/auth'

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await loginAction(credentials)

      if (result.success) {
        router.push('/dashboard')
        router.refresh()
        return { success: true }
      } else {
        setError(result.error || 'Erro desconhecido')
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMessage = 'Erro ao fazer login'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await logoutAction()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    login,
    logout,
    isLoading,
    error,
  }
}
```

---

### 2.5 - Criar Middleware de Proteção de Rotas

**Passo 2.5.1:** Criar middleware

**Arquivo:** `src/middleware.ts` (raiz do projeto)

```typescript
/**
 * Middleware de proteção de rotas
 *
 * Referências RAG:
 * - R26: Proteção de rotas por role
 * - Rotas públicas: /, /auth/*
 * - Rotas protegidas: /dashboard, /training-performance, etc.
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const session = request.cookies.get('session')
  const { pathname } = request.nextUrl

  // Rotas públicas (não requerem autenticação)
  const publicPaths = ['/', '/auth/signin', '/auth/signup']
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path))

  // Se não tem sessão e tenta acessar rota protegida
  if (!session && !isPublicPath) {
    const url = request.nextUrl.clone()
    url.pathname = '/auth/signin'
    url.searchParams.set('redirect', pathname)
    return NextResponse.redirect(url)
  }

  // Se tem sessão e tenta acessar página de login
  if (session && pathname.startsWith('/auth/signin')) {
    const url = request.nextUrl.clone()
    url.pathname = '/dashboard'
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.svg$).*)',
  ],
}
```

---

### 2.6 - Adaptar Página de Login

**Passo 2.6.1:** Atualizar página de login do template

**Arquivo:** `app/(auth)/signin/page.tsx` (ou localização equivalente no template)

```typescript
'use client'

/**
 * Página de Login
 *
 * Referências RAG:
 * - R26: Autenticação via JWT
 * - Backend: POST /api/v1/auth/login
 */

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/lib/hooks/useAuth'
import Link from 'next/link'

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function SignInPage() {
  const [showPassword, setShowPassword] = useState(false)
  const { login, isLoading, error } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    await login(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            HB Tracking
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Sistema de Gestão de Handebol
          </p>
        </div>

        {/* Card de Login */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            Entrar
          </h2>

          {/* Erro de Login */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Formulário */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                {...register('email')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="seu@email.com"
                disabled={isLoading}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Senha */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Senha
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password')}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="••••••"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                  disabled={isLoading}
                >
                  {showPassword ? 'Ocultar' : 'Mostrar'}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Botão de Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          {/* Link para Cadastro (se necessário) */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ainda não tem conta?{' '}
              <Link
                href="/auth/signup"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                Cadastre-se
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 2.7 - Testar Autenticação

**Passo 2.7.1:** Instalar dependências de validação

```bash
npm install react-hook-form @hookform/resolvers zod
```

---

**Passo 2.7.2:** Reiniciar servidor de desenvolvimento

```bash
npm run dev
```

---

**Passo 2.7.3:** Testar fluxo de login

**Credenciais de teste (usar credenciais reais do backend):**
- Email: `admin@hbtracking.com` (ou qualquer usuário criado no backend)
- Senha: sua senha real

**Fluxo de teste:**
1. Acessar: http://localhost:3000/auth/signin
2. Preencher email e senha
3. Clicar em "Entrar"
4. Deve redirecionar para: http://localhost:3000/dashboard
5. Abrir DevTools → Application → Cookies
6. Verificar cookie `session` existe e contém JWT

---

### ✅ CHECKLIST FASE 2: Autenticação e Segurança

- [ ] Arquivo `src/types/auth.ts` criado
- [ ] Arquivo `src/lib/auth/jwt.ts` criado (decodificação JWT)
- [ ] Arquivo `src/lib/auth/actions.ts` criado (Server Actions)
- [ ] Arquivo `src/lib/hooks/useAuth.ts` criado (hook client)
- [ ] Arquivo `src/middleware.ts` criado (proteção de rotas)
- [ ] Página de login adaptada (`app/(auth)/signin/page.tsx`)
- [ ] Dependências instaladas (`react-hook-form`, `@hookform/resolvers`, `zod`)
- [ ] Login funcional (redireciona para /dashboard)
- [ ] Cookie `session` criado após login
- [ ] Middleware redireciona rotas protegidas sem sessão
- [ ] Logout funcional (limpa cookie e redireciona para /auth/signin)

### 🔗 LINKS PARA VERIFICAÇÃO VISUAL - FASE 2

**Antes de prosseguir, CONFIRME visualmente:**

1. **Página de Login Adaptada:**
   http://localhost:3000/auth/signin
   ✅ Formulário com email/password
   ✅ Botão "Entrar"
   ✅ Validação de campos (email inválido, senha < 6 caracteres)

2. **Fluxo de Login:**
   - Preencher email e senha válidos
   - Clicar "Entrar"
   - ✅ Deve redirecionar para http://localhost:3000/dashboard

3. **Cookie de Sessão:**
   DevTools → Application → Cookies → http://localhost:3000
   ✅ Cookie `session` existe
   ✅ httpOnly = true
   ✅ sameSite = lax

4. **Proteção de Rotas:**
   - Fazer logout (ou limpar cookie)
   - Tentar acessar: http://localhost:3000/dashboard
   - ✅ Deve redirecionar para /auth/signin

5. **Redirecionamento Pós-Login:**
   - Já logado, tentar acessar: http://localhost:3000/auth/signin
   - ✅ Deve redirecionar para /dashboard

**⚠️ NÃO PROSSIGA PARA FASE 3 SEM CONFIRMAR TODOS OS ITENS ACIMA!**

---

## 🔌 FASE 3: INTEGRAÇÃO COM BACKEND

**Objetivo:** Criar Server Actions para todos os endpoints de relatórios (R1-R4) e testar conectividade com backend FastAPI.

**Duração Estimada:** 2-3 horas

**Pré-requisitos:**
- FASE 2 completa e verificada
- Backend operacional: https://hbtrack.onrender.com/api/v1
- Usuário logado com JWT válido

---

### 3.1 - Criar Tipos de Relatórios

**Passo 3.1.1:** Criar tipos para R1 (Training Performance)

**Arquivo:** `src/types/reports.ts`

```typescript
/**
 * Tipos de relatórios (R1-R4)
 *
 * Referências RAG:
 * - R1: Relatório de Performance em Treinos
 * - R2: Relatório Individual de Atleta
 * - R3: Relatório de Prontidão e Bem-Estar
 * - R4: Relatório de Gerenciamento de Lesões
 */

// ============================================================================
// R1: TRAINING PERFORMANCE
// ============================================================================

export interface TrainingPerformanceMetrics {
  total_athletes: number
  presentes: number
  ausentes: number
  dm: number
  lesionadas: number
  attendance_rate: number
  avg_minutes: number | null
  avg_rpe: number | null
  avg_internal_load: number | null
  stddev_internal_load: number | null
  load_ok_count: number
  data_completeness_pct: number
  avg_fatigue_after: number | null
  avg_mood_after: number | null
}

export interface TrainingPerformanceReport {
  session_id: string
  organization_id: string
  season_id: string | null
  team_id: string | null
  session_at: string
  main_objective: string | null
  planned_load: number | null
  group_climate: number | null
  metrics: TrainingPerformanceMetrics
  created_at: string
  updated_at: string
}

export interface TrainingPerformanceFilters {
  season_id?: string
  team_id?: string
  start_date?: string
  end_date?: string
  min_attendance_rate?: number
  skip?: number
  limit?: number
}

export interface TrainingPerformanceTrend {
  period: 'week' | 'month'
  period_start: string
  period_end: string
  sessions_count: number
  avg_attendance_rate: number
  avg_internal_load: number | null
  avg_fatigue: number | null
  avg_mood: number | null
}

// ============================================================================
// R2: ATHLETE INDIVIDUAL
// ============================================================================

export interface AthleteReadinessMetrics {
  avg_sleep_hours: number | null
  avg_sleep_quality: number | null
  avg_fatigue_pre: number | null
  avg_stress: number | null
  avg_muscle_soreness: number | null
  last_sleep_hours: number | null
  last_fatigue: number | null
}

export interface AthleteTrainingLoadMetrics {
  avg_internal_load: number | null
  avg_rpe: number | null
  avg_minutes: number | null
  load_7d: number | null
  load_28d: number | null
  last_internal_load: number | null
}

export interface AthleteAttendanceMetrics {
  total_sessions: number
  sessions_presente: number
  sessions_ausente: number
  sessions_dm: number
  sessions_lesionada: number
  attendance_rate: number
}

export interface AthleteWellnessMetrics {
  avg_fatigue_after: number | null
  avg_mood_after: number | null
}

export interface AthleteIndividualReport {
  athlete_id: string
  person_id: string
  full_name: string
  nickname: string | null
  birth_date: string | null
  position: string | null
  current_age: number | null
  expected_category_code: string | null
  current_state: 'ativa' | 'lesionada' | 'dispensada'
  current_season_id: string | null
  current_team_id: string | null
  organization_id: string
  readiness: AthleteReadinessMetrics
  training_load: AthleteTrainingLoadMetrics
  attendance: AthleteAttendanceMetrics
  wellness: AthleteWellnessMetrics
  active_medical_cases: number
  last_session_at: string | null
}

export interface AthleteListFilters {
  season_id?: string
  team_id?: string
  state?: 'ativa' | 'lesionada' | 'dispensada'
  min_attendance_rate?: number
  skip?: number
  limit?: number
}

// ============================================================================
// R3: WELLNESS SUMMARY
// ============================================================================

export interface WellnessSummaryMetrics {
  avg_sleep_hours: number | null
  avg_sleep_quality: number | null
  avg_fatigue: number | null
  avg_stress: number | null
  avg_muscle_soreness: number | null
  avg_mood: number | null
  athletes_with_low_sleep: number
  athletes_with_high_fatigue: number
  athletes_with_high_stress: number
}

export interface WellnessSummaryReport {
  period_start: string
  period_end: string
  organization_id: string
  season_id: string | null
  team_id: string | null
  metrics: WellnessSummaryMetrics
  total_athletes: number
  total_sessions: number
}

export interface WellnessSummaryFilters {
  season_id?: string
  team_id?: string
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

// ============================================================================
// R4: MEDICAL SUMMARY
// ============================================================================

export interface MedicalCaseSummary {
  id: string
  athlete_id: string
  athlete_name: string
  case_type: 'lesao' | 'doenca' | 'cirurgia' | 'outro'
  severity: 'leve' | 'moderada' | 'grave'
  status: 'ativo' | 'recuperacao' | 'alta'
  reason: string | null
  started_at: string
  ended_at: string | null
  days_active: number
  affected_sessions: number
}

export interface MedicalSummaryMetrics {
  total_cases: number
  active_cases: number
  cases_in_recovery: number
  cases_closed: number
  avg_days_active: number | null
  cases_by_severity: {
    leve: number
    moderada: number
    grave: number
  }
  cases_by_type: {
    lesao: number
    doenca: number
    cirurgia: number
    outro: number
  }
}

export interface MedicalSummaryReport {
  organization_id: string
  season_id: string | null
  team_id: string | null
  period_start: string
  period_end: string
  metrics: MedicalSummaryMetrics
  cases: MedicalCaseSummary[]
}

export interface MedicalSummaryFilters {
  season_id?: string
  team_id?: string
  status?: 'ativo' | 'recuperacao' | 'alta'
  severity?: 'leve' | 'moderada' | 'grave'
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}
```

---

### 3.2 - Criar Server Actions para Relatórios

**Passo 3.2.1:** Criar Server Actions para R1

**Arquivo:** `src/lib/reports/actions.ts`

```typescript
'use server'

/**
 * Server Actions para relatórios (R1-R4)
 *
 * Referências RAG:
 * - R1: Training Performance
 * - R2: Athlete Individual
 * - R3: Wellness Summary
 * - R4: Medical Summary
 *
 * Backend: https://hbtrack.onrender.com/api/v1/reports
 */

import { getSession } from '@/lib/auth/actions'
import {
  TrainingPerformanceReport,
  TrainingPerformanceFilters,
  TrainingPerformanceTrend,
  AthleteIndividualReport,
  AthleteListFilters,
  WellnessSummaryReport,
  WellnessSummaryFilters,
  MedicalSummaryReport,
  MedicalSummaryFilters,
} from '@/types/reports'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

/**
 * Utilitário para fetch autenticado
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const session = await getSession()

  if (!session) {
    throw new Error('Não autenticado')
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options?.headers,
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Erro desconhecido',
    }))
    throw new Error(error.detail || 'Erro na requisição')
  }

  return response.json()
}

// ============================================================================
// R1: TRAINING PERFORMANCE
// ============================================================================

/**
 * Obter relatório de performance em treinos
 */
export async function getTrainingPerformance(
  filters?: TrainingPerformanceFilters
): Promise<TrainingPerformanceReport[]> {
  const params = new URLSearchParams()

  if (filters?.season_id) params.set('season_id', filters.season_id)
  if (filters?.team_id) params.set('team_id', filters.team_id)
  if (filters?.start_date) params.set('start_date', filters.start_date)
  if (filters?.end_date) params.set('end_date', filters.end_date)
  if (filters?.min_attendance_rate)
    params.set('min_attendance_rate', filters.min_attendance_rate.toString())
  if (filters?.skip !== undefined) params.set('skip', filters.skip.toString())
  if (filters?.limit !== undefined)
    params.set('limit', filters.limit.toString())

  const queryString = params.toString()
  const endpoint = `/reports/training-performance${queryString ? `?${queryString}` : ''}`

  return fetchWithAuth<TrainingPerformanceReport[]>(endpoint)
}

/**
 * Obter tendências de performance em treinos
 */
export async function getTrainingTrends(
  filters?: {
    season_id?: string
    team_id?: string
    period?: 'week' | 'month'
  }
): Promise<TrainingPerformanceTrend[]> {
  const params = new URLSearchParams()

  if (filters?.season_id) params.set('season_id', filters.season_id)
  if (filters?.team_id) params.set('team_id', filters.team_id)
  if (filters?.period) params.set('period', filters.period)

  const queryString = params.toString()
  const endpoint = `/reports/training-trends${queryString ? `?${queryString}` : ''}`

  return fetchWithAuth<TrainingPerformanceTrend[]>(endpoint)
}

/**
 * Refresh materialized view de training performance
 */
export async function refreshTrainingPerformance(): Promise<{
  status: string
  view: string
  refreshed_at?: string
  error?: string
}> {
  return fetchWithAuth('/reports/refresh-training-performance', {
    method: 'POST',
  })
}

// ============================================================================
// R2: ATHLETE INDIVIDUAL
// ============================================================================

/**
 * Listar relatórios de atletas
 */
export async function getAthletesList(
  filters?: AthleteListFilters
): Promise<AthleteIndividualReport[]> {
  const params = new URLSearchParams()

  if (filters?.season_id) params.set('season_id', filters.season_id)
  if (filters?.team_id) params.set('team_id', filters.team_id)
  if (filters?.state) params.set('state', filters.state)
  if (filters?.min_attendance_rate)
    params.set('min_attendance_rate', filters.min_attendance_rate.toString())
  if (filters?.skip !== undefined) params.set('skip', filters.skip.toString())
  if (filters?.limit !== undefined)
    params.set('limit', filters.limit.toString())

  const queryString = params.toString()
  const endpoint = `/reports/athletes${queryString ? `?${queryString}` : ''}`

  return fetchWithAuth<AthleteIndividualReport[]>(endpoint)
}

/**
 * Obter relatório individual de atleta
 */
export async function getAthleteReport(
  athleteId: string
): Promise<AthleteIndividualReport> {
  return fetchWithAuth<AthleteIndividualReport>(
    `/reports/athletes/${athleteId}`
  )
}

/**
 * Refresh materialized view de atletas
 */
export async function refreshAthletes(): Promise<{
  status: string
  view: string
  refreshed_at?: string
  error?: string
}> {
  return fetchWithAuth('/reports/refresh-athletes', {
    method: 'POST',
  })
}

// ============================================================================
// R3: WELLNESS SUMMARY
// ============================================================================

/**
 * Obter relatório de prontidão e bem-estar
 */
export async function getWellnessSummary(
  filters?: WellnessSummaryFilters
): Promise<WellnessSummaryReport> {
  const params = new URLSearchParams()

  if (filters?.season_id) params.set('season_id', filters.season_id)
  if (filters?.team_id) params.set('team_id', filters.team_id)
  if (filters?.start_date) params.set('start_date', filters.start_date)
  if (filters?.end_date) params.set('end_date', filters.end_date)
  if (filters?.skip !== undefined) params.set('skip', filters.skip.toString())
  if (filters?.limit !== undefined)
    params.set('limit', filters.limit.toString())

  const queryString = params.toString()
  const endpoint = `/reports/wellness-summary${queryString ? `?${queryString}` : ''}`

  return fetchWithAuth<WellnessSummaryReport>(endpoint)
}

/**
 * Refresh materialized view de wellness
 */
export async function refreshWellness(): Promise<{
  status: string
  view: string
  refreshed_at?: string
  error?: string
}> {
  return fetchWithAuth('/reports/refresh-wellness', {
    method: 'POST',
  })
}

// ============================================================================
// R4: MEDICAL SUMMARY
// ============================================================================

/**
 * Obter relatório de gerenciamento de lesões
 */
export async function getMedicalSummary(
  filters?: MedicalSummaryFilters
): Promise<MedicalSummaryReport> {
  const params = new URLSearchParams()

  if (filters?.season_id) params.set('season_id', filters.season_id)
  if (filters?.team_id) params.set('team_id', filters.team_id)
  if (filters?.status) params.set('status', filters.status)
  if (filters?.severity) params.set('severity', filters.severity)
  if (filters?.start_date) params.set('start_date', filters.start_date)
  if (filters?.end_date) params.set('end_date', filters.end_date)
  if (filters?.skip !== undefined) params.set('skip', filters.skip.toString())
  if (filters?.limit !== undefined)
    params.set('limit', filters.limit.toString())

  const queryString = params.toString()
  const endpoint = `/reports/medical-summary${queryString ? `?${queryString}` : ''}`

  return fetchWithAuth<MedicalSummaryReport>(endpoint)
}

/**
 * Refresh materialized view de medical
 */
export async function refreshMedical(): Promise<{
  status: string
  view: string
  refreshed_at?: string
  error?: string
}> {
  return fetchWithAuth('/reports/refresh-medical', {
    method: 'POST',
  })
}
```

---

### 3.3 - Testar Conectividade com Backend

**Passo 3.3.1:** Criar página de teste de API

**Arquivo:** `app/(dashboard)/api-test/page.tsx`

```typescript
/**
 * Página de teste de API (desenvolvimento)
 *
 * Testar conectividade com backend e endpoints de relatórios
 */

import { getSession } from '@/lib/auth/actions'
import {
  getTrainingPerformance,
  getAthletesList,
  getWellnessSummary,
  getMedicalSummary,
} from '@/lib/reports/actions'

export default async function ApiTestPage() {
  const session = await getSession()

  if (!session) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Teste de API</h1>
        <p className="text-red-600">Você não está autenticado.</p>
      </div>
    )
  }

  // Testar endpoints
  let trainingData = null
  let athletesData = null
  let wellnessData = null
  let medicalData = null

  try {
    trainingData = await getTrainingPerformance({ limit: 5 })
  } catch (error: any) {
    trainingData = { error: error.message }
  }

  try {
    athletesData = await getAthletesList({ limit: 5 })
  } catch (error: any) {
    athletesData = { error: error.message }
  }

  try {
    wellnessData = await getWellnessSummary()
  } catch (error: any) {
    wellnessData = { error: error.message }
  }

  try {
    medicalData = await getMedicalSummary()
  } catch (error: any) {
    medicalData = { error: error.message }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Teste de API - Relatórios</h1>

      <div className="space-y-6">
        {/* Sessão */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">Sessão Atual</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto">
            {JSON.stringify(session.user, null, 2)}
          </pre>
        </div>

        {/* R1: Training Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">
            R1: Training Performance
          </h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto max-h-96">
            {JSON.stringify(trainingData, null, 2)}
          </pre>
        </div>

        {/* R2: Athletes */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">R2: Athletes List</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto max-h-96">
            {JSON.stringify(athletesData, null, 2)}
          </pre>
        </div>

        {/* R3: Wellness Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">R3: Wellness Summary</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto max-h-96">
            {JSON.stringify(wellnessData, null, 2)}
          </pre>
        </div>

        {/* R4: Medical Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">R4: Medical Summary</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto max-h-96">
            {JSON.stringify(medicalData, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}
```

---

**Passo 3.3.2:** Testar página de API

```bash
npm run dev
```

**Acesso:** http://localhost:3000/api-test

**Verificações:**
1. Sessão atual deve mostrar usuário logado
2. R1 deve retornar array de relatórios ou erro explicativo
3. R2 deve retornar array de atletas ou erro explicativo
4. R3 deve retornar relatório de wellness ou erro explicativo
5. R4 deve retornar relatório médico ou erro explicativo

**⚠️ IMPORTANTE:** Se qualquer endpoint retornar erro, verificar:
- Backend está rodando: https://hbtrack.onrender.com/health
- Token JWT ainda é válido (não expirou)
- Endpoint existe no backend: https://hbtrack.onrender.com/api/v1/docs

---

### ✅ CHECKLIST FASE 3: Integração com Backend

- [ ] Arquivo `src/types/reports.ts` criado (tipos R1-R4)
- [ ] Arquivo `src/lib/reports/actions.ts` criado (Server Actions)
- [ ] Server Action `getTrainingPerformance()` implementado
- [ ] Server Action `getTrainingTrends()` implementado
- [ ] Server Action `getAthletesList()` implementado
- [ ] Server Action `getAthleteReport()` implementado
- [ ] Server Action `getWellnessSummary()` implementado
- [ ] Server Action `getMedicalSummary()` implementado
- [ ] Server Actions de refresh implementados (4 endpoints POST)
- [ ] Página de teste `/api-test` criada
- [ ] Todos os endpoints retornam dados ou erro explicativo
- [ ] Token JWT sendo enviado corretamente (Authorization: Bearer)

### 🔗 LINKS PARA VERIFICAÇÃO VISUAL - FASE 3

**Antes de prosseguir, CONFIRME visualmente:**

1. **Página de Teste de API:**
   http://localhost:3000/api-test
   ✅ Sessão atual exibindo dados do usuário
   ✅ R1 retornando dados ou erro
   ✅ R2 retornando dados ou erro
   ✅ R3 retornando dados ou erro
   ✅ R4 retornando dados ou erro

2. **Backend Swagger UI:**
   https://hbtrack.onrender.com/api/v1/docs
   ✅ Endpoint `/reports/training-performance` disponível
   ✅ Endpoint `/reports/athletes` disponível
   ✅ Endpoint `/reports/wellness-summary` disponível
   ✅ Endpoint `/reports/medical-summary` disponível

3. **DevTools - Network Tab:**
   - Acessar http://localhost:3000/api-test
   - Abrir DevTools → Network → Filtrar "reports"
   - ✅ Requests para backend com status 200 ou 401/404
   - ✅ Header `Authorization: Bearer ...` presente

**⚠️ NÃO PROSSIGA PARA FASE 4 SEM CONFIRMAR CONECTIVIDADE COM BACKEND!**

---

## 🎨 FASE 4: PERSONALIZAÇÃO VISUAL

**Objetivo:** Customizar template TailAdmin com identidade visual do HB Tracking (logo, cores, fontes, imagens).

**Duração Estimada:** 1-2 horas

**Pré-requisitos:**
- FASE 3 completa e verificada
- Assets visuais (logo, imagens) preparados

---

### 4.1 - Configurar Logo e Favicon

**Passo 4.1.1:** Adicionar logo ao projeto

**Instruções:**
1. Preparar logo em 3 formatos:
   - `logo.svg` (versão principal, colorida)
   - `logo-white.svg` (versão para dark mode)
   - `favicon.ico` (16x16, 32x32, 48x48)

2. Copiar arquivos para `public/images/`:
```bash
mkdir -p public/images/logo
# Copiar arquivos de logo para public/images/logo/
# Copiar favicon.ico para public/
```

---

**Passo 4.1.2:** Atualizar metadata do app

**Arquivo:** `app/layout.tsx` (ou `src/app/layout.tsx` se estrutura diferente)

```typescript
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HB Tracking - Sistema de Gestão de Handebol',
  description: 'Sistema completo de gestão de atletas, treinos e relatórios de handebol',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
```

---

### 4.2 - Configurar Tema Tailwind (Cores)

**Passo 4.2.1:** Atualizar paleta de cores

**Arquivo:** `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Cores principais do HB Tracking
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Azul principal
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        secondary: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',  // Rosa/Roxo secundário
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
          950: '#4a044e',
        },
        success: {
          500: '#10b981',  // Verde para sucessos
          600: '#059669',
        },
        warning: {
          500: '#f59e0b',  // Amarelo para avisos
          600: '#d97706',
        },
        danger: {
          500: '#ef4444',  // Vermelho para erros/lesões
          600: '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
```

---

**Passo 4.2.2:** Importar fontes do Google

**Arquivo:** `app/layout.tsx` (adicionar no `<head>` ou importar no CSS)

```typescript
import { Inter, Poppins } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const poppins = Poppins({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-poppins',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${poppins.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

---

### 4.3 - Atualizar Componente de Header (Logo)

**Passo 4.3.1:** Localizar componente Header do template

**Arquivo:** `src/components/Header/index.tsx` (ou localização equivalente)

**Modificações:**
1. Substituir logo do template por logo HB Tracking
2. Atualizar título "TailAdmin" para "HB Tracking"

**Exemplo de código (adaptar ao template):**

```typescript
import Link from 'next/link'
import Image from 'next/image'

export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-3">
          <Image
            src="/images/logo/logo.svg"
            alt="HB Tracking"
            width={40}
            height={40}
            className="dark:hidden"
          />
          <Image
            src="/images/logo/logo-white.svg"
            alt="HB Tracking"
            width={40}
            height={40}
            className="hidden dark:block"
          />
          <span className="text-xl font-heading font-semibold text-gray-900 dark:text-white">
            HB Tracking
          </span>
        </Link>

        {/* Resto do header (user menu, notifications, etc.) */}
      </div>
    </header>
  )
}
```

---

### 4.4 - Atualizar Sidebar (Navegação)

**Passo 4.4.1:** Localizar componente Sidebar do template

**Arquivo:** `src/components/Sidebar/index.tsx` (ou localização equivalente)

**Modificações:**
1. Atualizar menu de navegação para refletir páginas do HB Tracking
2. Adicionar ícones para relatórios (R1-R4)

**Exemplo de menu de navegação:**

```typescript
const menuItems = [
  {
    label: 'Dashboard',
    icon: HomeIcon,
    href: '/dashboard',
  },
  {
    label: 'Relatórios',
    icon: ChartBarIcon,
    children: [
      {
        label: 'Performance em Treinos',
        href: '/training-performance',
      },
      {
        label: 'Atletas',
        href: '/athletes',
      },
      {
        label: 'Prontidão e Bem-Estar',
        href: '/wellness',
      },
      {
        label: 'Gerenciamento de Lesões',
        href: '/medical',
      },
    ],
  },
  {
    label: 'Mensagens',
    icon: ChatBubbleLeftIcon,
    href: '/messages',
  },
  {
    label: 'Notificações',
    icon: BellIcon,
    href: '/notifications',
  },
  {
    label: 'Perfil',
    icon: UserIcon,
    href: '/profile',
  },
  {
    label: 'Configurações',
    icon: CogIcon,
    href: '/settings',
  },
]
```

---

### 4.5 - Adicionar Imagens Personalizadas

**Passo 4.5.1:** Preparar imagens para dashboard

**Diretórios sugeridos:**
```
public/images/
├── logo/
│   ├── logo.svg
│   ├── logo-white.svg
│   └── favicon.ico
├── athletes/
│   └── placeholder.jpg (placeholder de atleta)
├── banners/
│   └── dashboard-hero.jpg (banner do dashboard)
└── icons/
    ├── training.svg
    ├── wellness.svg
    └── medical.svg
```

---

**Passo 4.5.2:** Usar Next.js Image para otimização

**Exemplo de uso:**

```typescript
import Image from 'next/image'

<Image
  src="/images/banners/dashboard-hero.jpg"
  alt="Dashboard HB Tracking"
  width={1200}
  height={400}
  className="rounded-lg"
  priority
/>
```

---

### ✅ CHECKLIST FASE 4: Personalização Visual

- [ ] Logo HB Tracking adicionado (`public/images/logo/logo.svg`)
- [ ] Logo para dark mode adicionado (`public/images/logo/logo-white.svg`)
- [ ] Favicon atualizado (`public/favicon.ico`)
- [ ] Metadata do app atualizado (`app/layout.tsx`)
- [ ] Paleta de cores configurada (`tailwind.config.ts`)
- [ ] Fontes Google importadas (Inter + Poppins)
- [ ] Header atualizado com logo HB Tracking
- [ ] Sidebar atualizado com menu de navegação correto
- [ ] Imagens personalizadas adicionadas
- [ ] Dark mode funcionando corretamente

### 🔗 LINKS PARA VERIFICAÇÃO VISUAL - FASE 4

**Antes de prosseguir, CONFIRME visualmente:**

1. **Dashboard com Logo Atualizado:**
   http://localhost:3000/dashboard
   ✅ Logo HB Tracking visível no header
   ✅ Título "HB Tracking" ao lado do logo
   ✅ Favicon HB Tracking na aba do navegador

2. **Dark Mode:**
   - Alternar tema (light/dark)
   - ✅ Logo muda de colorido para branco
   - ✅ Cores do tema aplicadas corretamente
   - ✅ Contraste adequado em ambos os modos

3. **Sidebar:**
   ✅ Menu "Relatórios" com 4 sub-itens:
   - Performance em Treinos
   - Atletas
   - Prontidão e Bem-Estar
   - Gerenciamento de Lesões
   ✅ Mensagens e Notificações visíveis
   ✅ Perfil e Configurações visíveis

4. **Fontes:**
   DevTools → Computed → Font
   ✅ Body usando "Inter"
   ✅ Headings usando "Poppins"

**⚠️ NÃO PROSSIGA PARA FASE 5 SEM CONFIRMAR IDENTIDADE VISUAL COMPLETA!**

---

## 📊 FASE 5: DASHBOARD PRINCIPAL

**Objetivo:** Reescrever página de dashboard com cards de estatísticas, gráficos de relatórios (R1-R4) e resumo executivo.

**Duração Estimada:** 3-4 horas

**Pré-requisitos:**
- FASE 4 completa e verificada
- ApexCharts instalado

---

### 5.1 - Instalar Biblioteca de Gráficos

**Passo 5.1.1:** Instalar ApexCharts para React

```bash
npm install apexcharts react-apexcharts
npm install --save-dev @types/react-apexcharts
```

---

### 5.2 - Criar Componente de Gráfico (Training Performance)

**Passo 5.2.1:** Criar componente de gráfico de linha

**Arquivo:** `src/components/Charts/TrainingPerformanceChart.tsx`

```typescript
'use client'

/**
 * Gráfico de Performance em Treinos (R1)
 *
 * Exibe tendências de carga interna, presença e fadiga ao longo do tempo
 */

import dynamic from 'next/dynamic'
import { TrainingPerformanceTrend } from '@/types/reports'

const Chart = dynamic(() => import('react-apexcharts'), { ssr: false })

interface TrainingPerformanceChartProps {
  data: TrainingPerformanceTrend[]
}

export default function TrainingPerformanceChart({
  data,
}: TrainingPerformanceChartProps) {
  const categories = data.map((item) =>
    new Date(item.period_start).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
    })
  )

  const attendanceData = data.map((item) => item.avg_attendance_rate)
  const loadData = data.map((item) => item.avg_internal_load || 0)
  const fatigueData = data.map((item) => item.avg_fatigue || 0)

  const options: any = {
    chart: {
      type: 'line',
      height: 350,
      toolbar: {
        show: false,
      },
    },
    colors: ['#3b82f6', '#10b981', '#f59e0b'],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: 'smooth',
      width: 2,
    },
    xaxis: {
      categories: categories,
      labels: {
        style: {
          colors: '#64748b',
        },
      },
    },
    yaxis: [
      {
        title: {
          text: 'Taxa de Presença (%)',
          style: {
            color: '#3b82f6',
          },
        },
        labels: {
          style: {
            colors: '#3b82f6',
          },
        },
      },
      {
        opposite: true,
        title: {
          text: 'Carga Interna',
          style: {
            color: '#10b981',
          },
        },
        labels: {
          style: {
            colors: '#10b981',
          },
        },
      },
    ],
    legend: {
      position: 'top',
      horizontalAlign: 'right',
    },
    tooltip: {
      shared: true,
      intersect: false,
    },
  }

  const series = [
    {
      name: 'Taxa de Presença (%)',
      data: attendanceData,
    },
    {
      name: 'Carga Interna Média',
      data: loadData,
    },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Tendências de Performance em Treinos
      </h3>
      <Chart
        options={options}
        series={series}
        type="line"
        height={350}
      />
    </div>
  )
}
```

---

### 5.3 - Criar Cards de Estatísticas

**Passo 5.3.1:** Criar componente de stat card

**Arquivo:** `src/components/Dashboard/StatCard.tsx`

```typescript
/**
 * Card de estatística (reutilizável)
 */

import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}

const colorClasses = {
  blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
  green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
  yellow:
    'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400',
  red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
  purple:
    'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
}

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
}: StatCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {subtitle}
            </p>
          )}
          {trend && (
            <div className="flex items-center gap-1 mt-2">
              <span
                className={`text-sm font-medium ${
                  trend.direction === 'up'
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {trend.direction === 'up' ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                vs. período anterior
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>{icon}</div>
        )}
      </div>
    </div>
  )
}
```

---

### 5.4 - Reescrever Página de Dashboard

**Passo 5.4.1:** Criar página de dashboard completa

**Arquivo:** `app/(dashboard)/dashboard/page.tsx`

```typescript
/**
 * Dashboard Principal - HB Tracking
 *
 * Referências RAG:
 * - R1: Performance em Treinos
 * - R2: Atletas
 * - R3: Wellness
 * - R4: Medical
 */

import { getSession } from '@/lib/auth/actions'
import {
  getTrainingPerformance,
  getTrainingTrends,
  getAthletesList,
  getWellnessSummary,
  getMedicalSummary,
} from '@/lib/reports/actions'
import StatCard from '@/components/Dashboard/StatCard'
import TrainingPerformanceChart from '@/components/Charts/TrainingPerformanceChart'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/auth/signin')
  }

  // Buscar dados dos relatórios
  const [trainingData, trainingTrends, athletesData, wellnessData, medicalData] =
    await Promise.all([
      getTrainingPerformance({ limit: 10 }).catch(() => []),
      getTrainingTrends({ period: 'week' }).catch(() => []),
      getAthletesList({ limit: 100 }).catch(() => []),
      getWellnessSummary().catch(() => null),
      getMedicalSummary().catch(() => null),
    ])

  // Calcular estatísticas
  const totalSessions = trainingData.length
  const avgAttendance =
    trainingData.length > 0
      ? (
          trainingData.reduce((sum, t) => sum + t.metrics.attendance_rate, 0) /
          trainingData.length
        ).toFixed(1)
      : '0'

  const totalAthletes = athletesData.length
  const activeAthletes = athletesData.filter(
    (a) => a.current_state === 'ativa'
  ).length
  const injuredAthletes = athletesData.filter(
    (a) => a.current_state === 'lesionada'
  ).length

  const activeMedicalCases = medicalData?.metrics.active_cases || 0

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Bem-vindo(a), {session.user.name}!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total de Treinos"
          value={totalSessions}
          subtitle="Últimos registros"
          color="blue"
        />
        <StatCard
          title="Taxa de Presença Média"
          value={`${avgAttendance}%`}
          subtitle="Últimos treinos"
          color="green"
        />
        <StatCard
          title="Atletas Ativas"
          value={activeAthletes}
          subtitle={`de ${totalAthletes} total`}
          color="purple"
        />
        <StatCard
          title="Casos Médicos Ativos"
          value={activeMedicalCases}
          subtitle={`${injuredAthletes} atletas lesionadas`}
          color="red"
        />
      </div>

      {/* Gráfico de Tendências */}
      {trainingTrends.length > 0 && (
        <TrainingPerformanceChart data={trainingTrends} />
      )}

      {/* Resumo de Wellness */}
      {wellnessData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Resumo de Prontidão
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Horas de Sono (média)
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {wellnessData.metrics.avg_sleep_hours?.toFixed(1) || 'N/A'}h
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Fadiga (média)
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {wellnessData.metrics.avg_fatigue?.toFixed(1) || 'N/A'}/10
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Atletas com Fadiga Alta
                </span>
                <span className="font-semibold text-red-600 dark:text-red-400">
                  {wellnessData.metrics.athletes_with_high_fatigue}
                </span>
              </div>
            </div>
          </div>

          {/* Últimos Treinos */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Últimos Treinos
            </h3>
            <div className="space-y-3">
              {trainingData.slice(0, 5).map((training) => (
                <div
                  key={training.session_id}
                  className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700 last:border-0"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {new Date(training.session_at).toLocaleDateString(
                        'pt-BR'
                      )}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {training.main_objective || 'Sem objetivo definido'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {training.metrics.attendance_rate.toFixed(0)}%
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      presença
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

### 5.5 - Adicionar Loading States

**Passo 5.5.1:** Criar loading skeleton para dashboard

**Arquivo:** `app/(dashboard)/dashboard/loading.tsx`

```typescript
/**
 * Loading state para dashboard
 */

export default function DashboardLoading() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      {/* Header Skeleton */}
      <div>
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-2"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-64"></div>
      </div>

      {/* Stats Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow"
          >
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-3"></div>
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
          </div>
        ))}
      </div>

      {/* Chart Skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
        <div className="h-[350px] bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>
  )
}
```

---

### ✅ CHECKLIST FASE 5: Dashboard Principal

- [ ] ApexCharts instalado (`npm install apexcharts react-apexcharts`)
- [ ] Componente `TrainingPerformanceChart` criado
- [ ] Componente `StatCard` criado
- [ ] Página `dashboard/page.tsx` reescrita
- [ ] Stats cards exibindo dados reais do backend
- [ ] Gráfico de tendências funcionando
- [ ] Resumo de wellness exibido
- [ ] Últimos treinos listados
- [ ] Loading state implementado
- [ ] Dark mode funcionando em todos os componentes

### 🔗 LINKS PARA VERIFICAÇÃO VISUAL - FASE 5

**Antes de prosseguir, CONFIRME visualmente:**

1. **Dashboard Completo:**
   http://localhost:3000/dashboard
   ✅ 4 stat cards com dados reais:
   - Total de Treinos
   - Taxa de Presença Média
   - Atletas Ativas
   - Casos Médicos Ativos
   ✅ Gráfico de tendências com linha de presença e carga
   ✅ Resumo de prontidão (sono, fadiga, atletas em alerta)
   ✅ Lista de últimos 5 treinos

2. **Responsividade:**
   - Redimensionar janela
   - ✅ Grid de cards adapta de 4 → 2 → 1 colunas
   - ✅ Gráfico responsivo
   - ✅ Layout funciona em mobile (< 768px)

3. **Dark Mode:**
   - Alternar tema
   - ✅ Cores do gráfico visíveis em dark mode
   - ✅ Cards com background correto
   - ✅ Texto legível em ambos os temas

4. **Loading State:**
   - Forçar reload da página (Ctrl+Shift+R)
   - ✅ Skeletons aparecem antes de carregar dados

**⚠️ NÃO PROSSIGA PARA FASE 6 SEM DASHBOARD FUNCIONAL E VISUALMENTE CORRETO!**

---

**🎯 CONTINUE PARA FASE 6:** [Páginas de Relatórios (R1-R4)](#fase-6-páginas-de-relatórios-r1-r4)

**Total de caracteres até aqui:** ~50.000
**Fases restantes:** 6, 7, 8 (a serem criadas no próximo bloco)

---

_Documento continua nas próximas fases..._
