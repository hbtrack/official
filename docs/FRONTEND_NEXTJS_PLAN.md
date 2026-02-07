<!-- STATUS: NEEDS_REVIEW -->

# 🚀 PLANO DE INTEGRAÇÃO - FRONTEND NEXT.JS + BACKEND HB TRACKING

**Data:** 2025-12-25
**Template:** TailAdmin Free Next.js Admin Dashboard
**Backend:** HB Tracking API (FastAPI + PostgreSQL)
**Versão:** 2.0.0

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitetura da Integração](#arquitetura-da-integração)
4. [Setup Inicial](#setup-inicial)
5. [Personalização Visual](#personalização-visual)
6. [Autenticação JWT](#autenticação-jwt)
7. [Integração com Backend](#integração-com-backend)
8. [Mapeamento Completo de Páginas](#mapeamento-completo-de-páginas)
9. [Funcionalidades Principais](#funcionalidades-principais)
10. [Sistema de Mensagens](#sistema-de-mensagens)
11. [Sistema de Notificações](#sistema-de-notificações)
12. [Roadmap de Implementação](#roadmap-de-implementação)

---

## 🎯 VISÃO GERAL

### Objetivo
Criar uma aplicação web completa usando Next.js 16 + React 19 para gerenciar treinos, wellness e casos médicos de atletas, totalmente integrada com o backend FastAPI já implementado.

### Características Principais
- ✅ **Dashboard Personalizado** com métricas em tempo real
- ✅ **4 Módulos de Relatórios** (R1-R4) com gráficos interativos
- ✅ **Sistema de Mensagens** para comunicação com atletas
- ✅ **Notificações** em tempo real
- ✅ **Autenticação JWT** segura
- ✅ **Tema Customizado** com logo e cores personalizadas
- ✅ **Dark Mode** nativo
- ✅ **Responsivo** (mobile-first)

---

## 🛠️ STACK TECNOLÓGICO

### Frontend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Next.js** | 16.x | Framework React com SSR/SSG |
| **React** | 19 | Biblioteca UI |
| **TypeScript** | Latest | Type safety |
| **Tailwind CSS** | v4 | Estilização moderna |
| **ApexCharts** | Latest | Gráficos interativos |
| **React Hook Form** | Latest | Formulários |
| **Zod** | Latest | Validação de schemas |
| **SWR** / **TanStack Query** | Latest | Data fetching e cache |
| **Zustand** / **Jotai** | Latest | State management |

### Backend (Já Implementado)

| Tecnologia | Status | Endpoint |
|------------|--------|----------|
| **FastAPI** | ✅ Operacional | https://hbtrack.onrender.com |
| **PostgreSQL 17** | ✅ Neon Cloud | ep-soft-cake-ad07z2ue-pooler |
| **JWT Auth** | ✅ Implementado | /api/v1/auth/login |
| **12 Endpoints** | ✅ Funcionais | /api/v1/reports/* |

---

## 🏗️ ARQUITETURA DA INTEGRAÇÃO

### Estrutura de Comunicação

```
┌────────────────────────────────────────────────────────────┐
│                   NEXT.JS FRONTEND                         │
│              (Server Components + Client)                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          APP ROUTER (Next.js 16)                    │  │
│  │                                                     │  │
│  │  /dashboard         → Server Component             │  │
│  │  /reports/training  → Server Component             │  │
│  │  /reports/athletes  → Server Component             │  │
│  │  /messages          → Client Component             │  │
│  │  /notifications     → Client Component             │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          SERVER ACTIONS (Next.js)                   │  │
│  │                                                     │  │
│  │  - loginAction()                                    │  │
│  │  - getTrainingPerformance()                        │  │
│  │  - sendMessage()                                    │  │
│  │  - refreshViews()                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          API ROUTES (/api/*)                        │  │
│  │                                                     │  │
│  │  /api/auth/login     → Proxy to FastAPI            │  │
│  │  /api/reports/*      → Proxy to FastAPI            │  │
│  │  /api/messages       → WebSocket handler           │  │
│  │  /api/notifications  → SSE handler                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
└───────────────────────────┼────────────────────────────────┘
                            │
                    HTTPS (JSON)
                            │
┌───────────────────────────▼────────────────────────────────┐
│              FASTAPI BACKEND (Render)                      │
│          https://hbtrack.onrender.com/api/v1               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Authentication:                                           │
│  POST /auth/login                                          │
│                                                            │
│  Reports (R1-R4):                                          │
│  GET  /reports/training-performance                        │
│  GET  /reports/athletes                                    │
│  GET  /reports/wellness-summary                            │
│  GET  /reports/medical-summary                             │
│                                                            │
│  Maintenance:                                              │
│  POST /reports/refresh-all                                 │
│  GET  /reports/stats                                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Fluxo de Autenticação

```
1. User submits login form
   ↓
2. Next.js Server Action calls FastAPI /auth/login
   ↓
3. FastAPI validates credentials, returns JWT
   ↓
4. Next.js stores JWT in httpOnly cookie
   ↓
5. Subsequent requests include JWT automatically
   ↓
6. Next.js middleware validates JWT on protected routes
```

---

## ⚙️ SETUP INICIAL

### 1️⃣ Clone e Instalação

```bash
# Criar diretório do frontend
cd "c:\Hb Tracking"
mkdir "Hb Tracking - Frontend"
cd "Hb Tracking - Frontend"

# Clonar template Next.js
git clone https://github.com/TailAdmin/free-nextjs-admin-dashboard.git .

# Remover origin do template
git remote remove origin

# Adicionar seu repositório (opcional)
git remote add origin <seu-repo-frontend>

# Instalar dependências
npm install --legacy-peer-deps

# Verificar se funciona
npm run dev
# Acessar: http://localhost:3000
```

### 2️⃣ Estrutura de Pastas (Recomendada)

```
src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Grupo de rotas de auth
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/              # Grupo de rotas protegidas
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Dashboard principal
│   │   ├── reports/
│   │   │   ├── training/
│   │   │   │   └── page.tsx      # R1
│   │   │   ├── athletes/
│   │   │   │   ├── page.tsx      # R2 - Lista
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # R2 - Detalhes
│   │   │   ├── wellness/
│   │   │   │   └── page.tsx      # R3
│   │   │   └── medical/
│   │   │       └── page.tsx      # R4
│   │   ├── messages/
│   │   │   └── page.tsx          # Sistema de mensagens
│   │   ├── notifications/
│   │   │   └── page.tsx          # Centro de notificações
│   │   └── layout.tsx            # Layout com sidebar
│   ├── api/                      # API Routes
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts
│   │   ├── reports/
│   │   │   └── route.ts
│   │   ├── messages/
│   │   │   └── route.ts
│   │   └── notifications/
│   │       └── route.ts
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
├── components/                   # Componentes reutilizáveis
│   ├── ui/                       # Componentes UI base
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── chart.tsx
│   │   ├── modal.tsx
│   │   └── ...
│   ├── dashboard/                # Componentes do dashboard
│   │   ├── stats-card.tsx
│   │   ├── training-chart.tsx
│   │   ├── wellness-gauge.tsx
│   │   └── medical-alerts.tsx
│   ├── messages/                 # Componentes de mensagens
│   │   ├── message-list.tsx
│   │   ├── message-composer.tsx
│   │   └── message-thread.tsx
│   ├── notifications/            # Componentes de notificações
│   │   ├── notification-bell.tsx
│   │   ├── notification-list.tsx
│   │   └── notification-item.tsx
│   └── layout/                   # Componentes de layout
│       ├── header.tsx
│       ├── sidebar.tsx
│       └── footer.tsx
├── lib/                          # Utilitários e configurações
│   ├── api/                      # Cliente API
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   └── types.ts
│   ├── auth/                     # Autenticação
│   │   ├── session.ts
│   │   ├── jwt.ts
│   │   └── middleware.ts
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useTraining.ts
│   │   ├── useMessages.ts
│   │   └── useNotifications.ts
│   ├── store/                    # State management
│   │   ├── auth-store.ts
│   │   ├── notifications-store.ts
│   │   └── messages-store.ts
│   └── utils/                    # Funções utilitárias
│       ├── date.ts
│       ├── format.ts
│       └── validators.ts
├── types/                        # TypeScript types
│   ├── auth.ts
│   ├── reports.ts
│   ├── messages.ts
│   └── notifications.ts
└── styles/
    └── globals.css               # Estilos globais
```

### 3️⃣ Variáveis de Ambiente

**Criar:** `.env.local`
```bash
# Backend API
NEXT_PUBLIC_API_URL=https://hbtrack.onrender.com/api/v1
API_TIMEOUT=30000

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secret-key-change-this-in-production

# Development
NODE_ENV=development
```

**Criar:** `.env.production`
```bash
# Backend API
NEXT_PUBLIC_API_URL=https://hbtrack.onrender.com/api/v1
API_TIMEOUT=30000

# Authentication
NEXTAUTH_URL=https://seu-dominio-frontend.com
NEXTAUTH_SECRET=your-production-secret-key

# Production
NODE_ENV=production
```

### 4️⃣ Dependências Adicionais

```bash
# Data fetching e state
npm install swr axios
# ou
npm install @tanstack/react-query axios

# State management
npm install zustand
# ou
npm install jotai

# Forms e validação
npm install react-hook-form zod @hookform/resolvers

# Date handling
npm install date-fns

# Charts (se não estiver no template)
npm install apexcharts react-apexcharts

# Notifications
npm install react-hot-toast
# ou
npm install sonner

# Utilities
npm install clsx tailwind-merge
npm install lodash-es
npm install @types/lodash-es --save-dev
```

---

## 🎨 PERSONALIZAÇÃO VISUAL

### 1️⃣ Logo e Branding

**Criar:** `public/images/logo/`
```
logo.svg          # Logo principal (colorido)
logo-white.svg    # Logo para dark mode
logo-icon.svg     # Ícone pequeno (favicon)
```

**Atualizar:** `src/app/layout.tsx`
```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'HB Tracking - Gestão de Atletas',
  description: 'Sistema de gestão de treinos, wellness e casos médicos',
  icons: {
    icon: '/images/logo/logo-icon.svg',
  },
}
```

**Atualizar:** `src/components/layout/sidebar.tsx`
```tsx
import Image from 'next/image'

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo-container">
        <Image
          src="/images/logo/logo.svg"
          alt="HB Tracking"
          width={180}
          height={40}
          className="dark:hidden"
        />
        <Image
          src="/images/logo/logo-white.svg"
          alt="HB Tracking"
          width={180}
          height={40}
          className="hidden dark:block"
        />
      </div>
      {/* Rest of sidebar */}
    </aside>
  )
}
```

### 2️⃣ Tema de Cores Personalizado

**Atualizar:** `tailwind.config.ts`
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Cores primárias do seu branding
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',  // Cor principal
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        // Cores de status
        success: {
          light: '#d1fae5',
          DEFAULT: '#10b981',
          dark: '#065f46',
        },
        warning: {
          light: '#fef3c7',
          DEFAULT: '#f59e0b',
          dark: '#92400e',
        },
        danger: {
          light: '#fee2e2',
          DEFAULT: '#ef4444',
          dark: '#991b1b',
        },
        // Cores específicas do HB Tracking
        hb: {
          blue: '#0ea5e9',
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
```

**Adicionar fontes:** `src/app/layout.tsx`
```tsx
import { Inter, Poppins } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-poppins',
  display: 'swap',
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

### 3️⃣ Imagens Personalizadas

**Estrutura de imagens:**
```
public/images/
├── logo/
│   ├── logo.svg
│   ├── logo-white.svg
│   └── logo-icon.svg
├── athletes/
│   ├── default-avatar.png
│   └── team-photo.jpg
├── backgrounds/
│   ├── dashboard-hero.jpg
│   └── login-bg.jpg
├── icons/
│   ├── training.svg
│   ├── wellness.svg
│   ├── medical.svg
│   └── messages.svg
└── illustrations/
    ├── no-data.svg
    ├── empty-state.svg
    └── error-404.svg
```

**Componente de imagem otimizada:**

**Criar:** `src/components/ui/optimized-image.tsx`
```tsx
import Image from 'next/image'
import { useState } from 'react'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  fallback?: string
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
  fallback = '/images/default-placeholder.png',
}: OptimizedImageProps) {
  const [imgSrc, setImgSrc] = useState(src)

  return (
    <Image
      src={imgSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={() => setImgSrc(fallback)}
      loading="lazy"
      placeholder="blur"
      blurDataURL="data:image/svg+xml;base64,..."
    />
  )
}
```

---

## 🔐 AUTENTICAÇÃO JWT

### 1️⃣ Tipos TypeScript

**Criar:** `src/types/auth.ts`
```typescript
export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'coach' | 'athlete'
  teamId?: string
  seasonId?: string
  avatar?: string
}

export interface JWTPayload {
  sub: string  // user_id
  email: string
  role: string
  exp: number
  iat: number
}

export interface Session {
  user: User
  accessToken: string
  expiresAt: number
}
```

### 2️⃣ Cliente API

**Criar:** `src/lib/api/client.ts`
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor para adicionar JWT
    this.client.interceptors.request.use(
      (config) => {
        // Token será adicionado pelo middleware/server action
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor para tratar erros
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado, redirecionar para login
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }

  setAuthToken(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  removeAuthToken() {
    delete this.client.defaults.headers.common['Authorization']
  }
}

export const apiClient = new APIClient()
```

### 3️⃣ Server Actions para Autenticação

**Criar:** `src/lib/auth/actions.ts`
```typescript
'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { LoginCredentials, LoginResponse, Session } from '@/types/auth'
import { decodeJWT } from './jwt'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

export async function loginAction(credentials: LoginCredentials) {
  try {
    // Chamar backend FastAPI
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json()
      return { success: false, error: error.detail || 'Login failed' }
    }

    const data: LoginResponse = await response.json()

    // Decodificar JWT
    const payload = decodeJWT(data.access_token)

    if (!payload) {
      return { success: false, error: 'Invalid token' }
    }

    // Criar sessão
    const session: Session = {
      user: {
        id: payload.sub,
        email: payload.email,
        name: payload.email.split('@')[0], // Simplificado
        role: payload.role as 'admin' | 'coach' | 'athlete',
      },
      accessToken: data.access_token,
      expiresAt: payload.exp * 1000, // Converter para ms
    }

    // Salvar em httpOnly cookie
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
    return { success: false, error: 'Network error' }
  }
}

export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
  redirect('/login')
}

export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies()
  const sessionCookie = cookieStore.get('session')

  if (!sessionCookie) {
    return null
  }

  try {
    const session: Session = JSON.parse(sessionCookie.value)

    // Verificar se não expirou
    if (Date.now() > session.expiresAt) {
      cookieStore.delete('session')
      return null
    }

    return session
  } catch {
    return null
  }
}
```

### 4️⃣ Utilitário JWT

**Criar:** `src/lib/auth/jwt.ts`
```typescript
import { JWTPayload } from '@/types/auth'

export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    const payload = JSON.parse(
      Buffer.from(parts[1], 'base64').toString('utf-8')
    )

    return payload as JWTPayload
  } catch (error) {
    console.error('Error decoding JWT:', error)
    return null
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token)
  if (!payload) return true

  const now = Math.floor(Date.now() / 1000)
  return payload.exp < now
}
```

### 5️⃣ Middleware para Proteção de Rotas

**Criar:** `src/middleware.ts`
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const session = request.cookies.get('session')

  // Rotas públicas
  const publicPaths = ['/login', '/forgot-password', '/']
  const isPublicPath = publicPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  )

  // Se não tem sessão e tentando acessar rota protegida
  if (!session && !isPublicPath) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Se tem sessão e tentando acessar login
  if (session && request.nextUrl.pathname === '/login') {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|images|favicon.ico).*)',
  ],
}
```

### 6️⃣ Hook useAuth

**Criar:** `src/lib/hooks/useAuth.ts`
```typescript
'use client'

import { useRouter } from 'next/navigation'
import { loginAction, logoutAction } from '@/lib/auth/actions'
import { LoginCredentials } from '@/types/auth'

export function useAuth() {
  const router = useRouter()

  const login = async (credentials: LoginCredentials) => {
    const result = await loginAction(credentials)

    if (result.success) {
      router.push('/dashboard')
      router.refresh()
    }

    return result
  }

  const logout = async () => {
    await logoutAction()
  }

  return {
    login,
    logout,
  }
}
```

---

## 🔗 INTEGRAÇÃO COM BACKEND

### 1️⃣ Tipos de Relatórios

**Criar:** `src/types/reports.ts`
```typescript
// R1 - Training Performance
export interface TrainingPerformance {
  athlete_id: string
  athlete_name: string
  team_id: string
  team_name: string
  season_id: string
  season_name: string
  total_sessions: number
  avg_rpe: number
  avg_duration_minutes: number
  total_distance_km: number
  last_session_date: string
}

export interface TrainingTrend {
  date: string
  total_sessions: number
  avg_rpe: number
  avg_duration: number
}

// R2 - Athletes
export interface AthleteSummary {
  id: string
  name: string
  email: string
  team_id: string
  team_name: string
  total_sessions: number
  avg_rpe: number
  avg_duration_minutes: number
  last_session_date: string
}

// R3 - Wellness
export interface WellnessSummary {
  athlete_id: string
  athlete_name: string
  team_id: string
  season_id: string
  avg_fatigue: number
  avg_sleep_quality: number
  avg_stress: number
  avg_muscle_soreness: number
  last_assessment_date: string
}

// R4 - Medical
export interface MedicalSummary {
  athlete_id: string
  athlete_name: string
  team_id: string
  season_id: string
  total_cases: number
  active_cases: number
  avg_recovery_days: number
  injury_types: string[]
}

// Filtros compartilhados
export interface ReportFilters {
  season_id?: string
  team_id?: string
  athlete_id?: string
  start_date?: string
  end_date?: string
}
```

### 2️⃣ Server Actions para Relatórios

**Criar:** `src/lib/reports/actions.ts`
```typescript
'use server'

import { getSession } from '@/lib/auth/actions'
import {
  TrainingPerformance,
  AthleteSummary,
  WellnessSummary,
  MedicalSummary,
  ReportFilters,
} from '@/types/reports'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

async function fetchWithAuth(url: string, options?: RequestInit) {
  const session = await getSession()

  if (!session) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

// R1 - Training Performance
export async function getTrainingPerformance(
  filters?: ReportFilters
): Promise<TrainingPerformance[]> {
  const params = new URLSearchParams()

  if (filters) {
    if (filters.season_id) params.set('season_id', filters.season_id)
    if (filters.team_id) params.set('team_id', filters.team_id)
    if (filters.athlete_id) params.set('athlete_id', filters.athlete_id)
  }

  const url = `${API_URL}/reports/training-performance?${params.toString()}`
  return fetchWithAuth(url)
}

// R2 - Athletes
export async function getAthletes(
  filters?: ReportFilters
): Promise<AthleteSummary[]> {
  const params = new URLSearchParams()

  if (filters) {
    if (filters.season_id) params.set('season_id', filters.season_id)
    if (filters.team_id) params.set('team_id', filters.team_id)
  }

  const url = `${API_URL}/reports/athletes?${params.toString()}`
  return fetchWithAuth(url)
}

// R3 - Wellness
export async function getWellnessSummary(
  filters?: ReportFilters
): Promise<WellnessSummary[]> {
  const params = new URLSearchParams()

  if (filters) {
    if (filters.season_id) params.set('season_id', filters.season_id)
    if (filters.team_id) params.set('team_id', filters.team_id)
  }

  const url = `${API_URL}/reports/wellness-summary?${params.toString()}`
  return fetchWithAuth(url)
}

// R4 - Medical
export async function getMedicalSummary(
  filters?: ReportFilters
): Promise<MedicalSummary[]> {
  const params = new URLSearchParams()

  if (filters) {
    if (filters.season_id) params.set('season_id', filters.season_id)
    if (filters.team_id) params.set('team_id', filters.team_id)
  }

  const url = `${API_URL}/reports/medical-summary?${params.toString()}`
  return fetchWithAuth(url)
}

// Refresh Views
export async function refreshAllViews(): Promise<{ success: boolean }> {
  const url = `${API_URL}/reports/refresh-all`
  return fetchWithAuth(url, { method: 'POST' })
}
```

---

## 📄 MAPEAMENTO COMPLETO DE PÁGINAS

### Visão Geral das Páginas

| # | Página | Tipo | Template | Status | Endpoint Backend |
|---|--------|------|----------|--------|------------------|
| 1 | Landing Page | Pública | ✅ Existe | Customizar | - |
| 2 | Login | Pública | ✅ Existe | Adaptar | POST /auth/login |
| 3 | Forgot Password | Pública | ✅ Existe | Manter | - |
| 4 | Dashboard | Protegida | ✅ Existe | **Reescrever** | Múltiplos |
| 5 | Training Performance | Protegida | ❌ Criar | **Nova** | GET /reports/training-performance |
| 6 | Training Trends | Protegida | ❌ Criar | **Nova** | GET /reports/training-trends |
| 7 | Athletes List | Protegida | ❌ Criar | **Nova** | GET /reports/athletes |
| 8 | Athlete Detail | Protegida | ❌ Criar | **Nova** | GET /reports/athletes/{id} |
| 9 | Wellness Summary | Protegida | ❌ Criar | **Nova** | GET /reports/wellness-summary |
| 10 | Wellness Trends | Protegida | ❌ Criar | **Nova** | GET /reports/wellness-trends |
| 11 | Medical Summary | Protegida | ❌ Criar | **Nova** | GET /reports/medical-summary |
| 12 | Medical History | Protegida | ❌ Criar | **Nova** | GET /reports/athletes/{id}/medical-history |
| 13 | Messages | Protegida | ❌ Criar | **Nova** | API /messages |
| 14 | Notifications | Protegida | ❌ Criar | **Nova** | API /notifications |
| 15 | Profile | Protegida | ✅ Existe | Adaptar | - |
| 16 | Settings | Protegida | ✅ Existe | Adaptar | - |
| 17 | 404 Error | Pública | ✅ Existe | Manter | - |

---

### 1️⃣ LANDING PAGE (/)

**Tipo:** Pública
**Status no Template:** ✅ Existe
**Ação:** Customizar

**Localização:** `src/app/page.tsx`

**O que fazer:**
```tsx
// ANTES (Template genérico)
export default function Home() {
  return (
    <div>
      <h1>TailAdmin Dashboard</h1>
      {/* Conteúdo genérico */}
    </div>
  )
}

// DEPOIS (Customizado HB Tracking)
export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700">
      {/* Hero Section */}
      <section className="pt-20 pb-32 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <Image
            src="/images/logo/logo-white.svg"
            alt="HB Tracking"
            width={300}
            height={80}
            className="mx-auto mb-8"
          />
          <h1 className="text-5xl font-heading font-bold text-white mb-6">
            Sistema de Gestão de Atletas
          </h1>
          <p className="text-xl text-primary-100 mb-8">
            Gerencie treinos, wellness e casos médicos com eficiência
          </p>
          <Link
            href="/login"
            className="inline-block bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-primary-50 transition"
          >
            Acessar Plataforma
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon="📊"
            title="Relatórios Completos"
            description="Visualize performance, wellness e histórico médico"
          />
          <FeatureCard
            icon="💬"
            title="Comunicação Direta"
            description="Envie mensagens e notificações para atletas"
          />
          <FeatureCard
            icon="📈"
            title="Análise em Tempo Real"
            description="Gráficos interativos e métricas atualizadas"
          />
        </div>
      </section>
    </div>
  )
}
```

---

### 2️⃣ LOGIN PAGE (/login)

**Tipo:** Pública
**Status no Template:** ✅ Existe
**Ação:** Adaptar para integração com backend

**Localização:** `src/app/(auth)/login/page.tsx`

**O que fazer:**
```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/lib/hooks/useAuth'
import Image from 'next/image'
import Link from 'next/link'

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const router = useRouter()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setError('')

    try {
      const result = await login(data)

      if (!result.success) {
        setError(result.error || 'Erro ao fazer login')
      }
      // Se sucesso, o hook useAuth redireciona
    } catch (err) {
      setError('Erro de conexão com o servidor')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo */}
        <div className="text-center">
          <Image
            src="/images/logo/logo.svg"
            alt="HB Tracking"
            width={200}
            height={50}
            className="mx-auto dark:hidden"
          />
          <Image
            src="/images/logo/logo-white.svg"
            alt="HB Tracking"
            width={200}
            height={50}
            className="mx-auto hidden dark:block"
          />
          <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900 dark:text-white">
            Acesse sua conta
          </h2>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <input
                {...register('email')}
                type="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700"
                placeholder="seu@email.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Senha
              </label>
              <input
                {...register('password')}
                type="password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                Lembrar-me
              </label>
            </div>

            <Link href="/forgot-password" className="text-sm font-medium text-primary-600 hover:text-primary-500">
              Esqueceu a senha?
            </Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

**Endpoint Backend:** `POST /api/v1/auth/login`

---

### 3️⃣ DASHBOARD (/dashboard)

**Tipo:** Protegida
**Status no Template:** ✅ Existe
**Ação:** **Reescrever completamente**

**Localização:** `src/app/(dashboard)/dashboard/page.tsx`

**Código completo já fornecido na seção "Funcionalidades Principais"**

**Endpoints Backend:**
- `GET /api/v1/reports/training-performance`
- `GET /api/v1/reports/wellness-summary`
- `GET /api/v1/reports/medical-summary`

**Componentes necessários:**
- `StatsCard` - Card de métricas
- `TrainingChart` - Gráfico de treinos
- `WellnessGauge` - Gauge de wellness
- `MedicalAlerts` - Alertas médicos

---

### 4️⃣ TRAINING PERFORMANCE (/reports/training)

**Tipo:** Protegida
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/reports/training/page.tsx`

**Criar:**
```tsx
import { getSession } from '@/lib/auth/actions'
import { getTrainingPerformance, getTrainingTrends } from '@/lib/reports/actions'
import TrainingTable from '@/components/reports/training-table'
import TrainingTrendsChart from '@/components/reports/training-trends-chart'
import FilterBar from '@/components/reports/filter-bar'

export default async function TrainingPerformancePage({
  searchParams,
}: {
  searchParams: { season_id?: string; team_id?: string }
}) {
  const session = await getSession()

  // Carregar dados baseado em filtros
  const [performance, trends] = await Promise.all([
    getTrainingPerformance({
      season_id: searchParams.season_id,
      team_id: searchParams.team_id,
    }),
    getTrainingTrends({
      season_id: searchParams.season_id,
    }),
  ])

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Performance de Treino (R1)
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Visualize métricas agregadas de treino por atleta, equipe e temporada
        </p>
      </div>

      {/* Filtros */}
      <FilterBar />

      {/* Gráfico de Tendências */}
      <div className="mb-6">
        <TrainingTrendsChart data={trends} />
      </div>

      {/* Tabela de Dados */}
      <TrainingTable data={performance} />
    </div>
  )
}
```

**Endpoint Backend:** `GET /api/v1/reports/training-performance`

**Query Params:**
- `season_id` (opcional)
- `team_id` (opcional)
- `athlete_id` (opcional)

---

### 5️⃣ ATHLETES LIST (/reports/athletes)

**Tipo:** Protegida
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/reports/athletes/page.tsx`

**Criar:**
```tsx
import { getAthletes } from '@/lib/reports/actions'
import AthleteCard from '@/components/reports/athlete-card'
import SearchBar from '@/components/ui/search-bar'
import Link from 'next/link'

export default async function AthletesListPage({
  searchParams,
}: {
  searchParams: { search?: string; team_id?: string }
}) {
  const athletes = await getAthletes({
    team_id: searchParams.team_id,
  })

  // Filtrar por busca
  const filteredAthletes = searchParams.search
    ? athletes.filter((a) =>
        a.name.toLowerCase().includes(searchParams.search!.toLowerCase())
      )
    : athletes

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
            Atletas (R2)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {filteredAthletes.length} atletas encontrados
          </p>
        </div>

        <SearchBar />
      </div>

      {/* Grid de atletas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAthletes.map((athlete) => (
          <Link key={athlete.id} href={`/reports/athletes/${athlete.id}`}>
            <AthleteCard athlete={athlete} />
          </Link>
        ))}
      </div>

      {filteredAthletes.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Nenhum atleta encontrado</p>
        </div>
      )}
    </div>
  )
}
```

**Endpoint Backend:** `GET /api/v1/reports/athletes`

---

### 6️⃣ ATHLETE DETAIL (/reports/athletes/[id])

**Tipo:** Protegida
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/reports/athletes/[id]/page.tsx`

**Criar:**
```tsx
import { getAthleteDetail, getAthleteMedicalHistory } from '@/lib/reports/actions'
import AthleteHeader from '@/components/reports/athlete-header'
import TrainingSessions from '@/components/reports/training-sessions'
import WellnessHistory from '@/components/reports/wellness-history'
import MedicalHistory from '@/components/reports/medical-history'

export default async function AthleteDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const [athlete, medicalHistory] = await Promise.all([
    getAthleteDetail(params.id),
    getAthleteMedicalHistory(params.id),
  ])

  return (
    <div className="p-6">
      {/* Header com foto e info básica */}
      <AthleteHeader athlete={athlete} />

      {/* Tabs de conteúdo */}
      <div className="mt-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8">
            <TabButton label="Treinos" active />
            <TabButton label="Wellness" />
            <TabButton label="Histórico Médico" />
          </nav>
        </div>

        <div className="mt-6">
          {/* Tab Content */}
          <TrainingSessions sessions={athlete.recent_sessions} />
          <WellnessHistory stats={athlete.wellness_stats} />
          <MedicalHistory cases={medicalHistory} />
        </div>
      </div>
    </div>
  )
}
```

**Endpoint Backend:** `GET /api/v1/reports/athletes/{id}`

---

### 7️⃣ WELLNESS SUMMARY (/reports/wellness)

**Tipo:** Protegida
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/reports/wellness/page.tsx`

**Criar:**
```tsx
import { getWellnessSummary, getWellnessTrends } from '@/lib/reports/actions'
import WellnessGaugeGrid from '@/components/reports/wellness-gauge-grid'
import WellnessTrendsChart from '@/components/reports/wellness-trends-chart'
import WellnessTable from '@/components/reports/wellness-table'

export default async function WellnessSummaryPage({
  searchParams,
}: {
  searchParams: { season_id?: string; team_id?: string }
}) {
  const [summary, trends] = await Promise.all([
    getWellnessSummary({
      season_id: searchParams.season_id,
      team_id: searchParams.team_id,
    }),
    getWellnessTrends({
      season_id: searchParams.season_id,
    }),
  ])

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Wellness Summary (R3)
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitore fadiga, sono, estresse e dor muscular
        </p>
      </div>

      {/* Gauges de métricas */}
      <WellnessGaugeGrid data={summary} />

      {/* Gráfico de tendências */}
      <div className="mt-6">
        <WellnessTrendsChart data={trends} />
      </div>

      {/* Tabela detalhada */}
      <div className="mt-6">
        <WellnessTable data={summary} />
      </div>
    </div>
  )
}
```

**Endpoint Backend:** `GET /api/v1/reports/wellness-summary`

---

### 8️⃣ MEDICAL SUMMARY (/reports/medical)

**Tipo:** Protegida
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/reports/medical/page.tsx`

**Criar:**
```tsx
import { getMedicalSummary } from '@/lib/reports/actions'
import MedicalStatsCards from '@/components/reports/medical-stats-cards'
import MedicalCasesTable from '@/components/reports/medical-cases-table'
import InjuryTypesChart from '@/components/reports/injury-types-chart'

export default async function MedicalSummaryPage({
  searchParams,
}: {
  searchParams: { season_id?: string; team_id?: string; status?: string }
}) {
  const summary = await getMedicalSummary({
    season_id: searchParams.season_id,
    team_id: searchParams.team_id,
  })

  // Filtrar por status se necessário
  const activeCases = summary.filter((s) => s.active_cases > 0)

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Medical Summary (R4)
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Acompanhe lesões, doenças e tempo de recuperação
        </p>
      </div>

      {/* Stats Cards */}
      <MedicalStatsCards data={summary} />

      {/* Gráfico de tipos de lesão */}
      <div className="mt-6">
        <InjuryTypesChart data={summary} />
      </div>

      {/* Tabela de casos */}
      <div className="mt-6">
        <MedicalCasesTable
          data={searchParams.status === 'active' ? activeCases : summary}
        />
      </div>
    </div>
  )
}
```

**Endpoint Backend:** `GET /api/v1/reports/medical-summary`

---

### 9️⃣ MESSAGES (/messages)

**Tipo:** Protegida (Client Component)
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Código completo já fornecido na seção "Sistema de Mensagens"**

**Backend:** Requer nova migration + endpoints (criar)

---

### 🔟 NOTIFICATIONS (/notifications)

**Tipo:** Protegida (Client Component)
**Status no Template:** ❌ Não existe
**Ação:** **Criar nova página**

**Localização:** `src/app/(dashboard)/notifications/page.tsx`

**Criar:**
```tsx
'use client'

import { useNotifications } from '@/lib/store/notifications-store'
import NotificationItem from '@/components/notifications/notification-item'

export default function NotificationsPage() {
  const { notifications, markAsRead, markAllAsRead, removeNotification } =
    useNotifications()

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Notificações
        </h1>

        <button
          onClick={markAllAsRead}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Marcar todas como lidas
        </button>
      </div>

      <div className="space-y-4">
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onMarkAsRead={() => markAsRead(notification.id)}
            onRemove={() => removeNotification(notification.id)}
          />
        ))}

        {notifications.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Nenhuma notificação</p>
          </div>
        )}
      </div>
    </div>
  )
}
```

---

### 1️⃣1️⃣ PROFILE (/profile)

**Tipo:** Protegida
**Status no Template:** ✅ Existe
**Ação:** Adaptar

**Localização:** `src/app/(dashboard)/profile/page.tsx`

**O que fazer:**
- Manter estrutura do template
- Adicionar campos específicos (role, team, season)
- Integrar com backend para atualização de perfil
- Adicionar upload de avatar

---

### 1️⃣2️⃣ SETTINGS (/settings)

**Tipo:** Protegida
**Status no Template:** ✅ Existe
**Ação:** Adaptar

**Localização:** `src/app/(dashboard)/settings/page.tsx`

**O que fazer:**
- Manter tabs do template
- Adicionar configurações de notificações
- Configurações de privacidade
- Preferências de relatórios

---

### Resumo de Ações

**Páginas do Template:**
- ✅ Manter: 404, Forgot Password
- 🔄 Adaptar: Landing, Login, Profile, Settings
- 🔄 Reescrever: Dashboard

**Páginas Novas (Criar):**
- 📊 Training Performance
- 📊 Training Trends
- 👥 Athletes List
- 👤 Athlete Detail
- ❤️ Wellness Summary
- ❤️ Wellness Trends
- 🏥 Medical Summary
- 🏥 Medical History
- 💬 Messages
- 🔔 Notifications

**Total:** 17 páginas (7 do template + 10 novas)

---

## 📊 FUNCIONALIDADES PRINCIPAIS

### Dashboard Principal

**Criar:** `src/app/(dashboard)/dashboard/page.tsx`
```tsx
import { getSession } from '@/lib/auth/actions'
import {
  getTrainingPerformance,
  getWellnessSummary,
  getMedicalSummary,
} from '@/lib/reports/actions'
import StatsCard from '@/components/dashboard/stats-card'
import TrainingChart from '@/components/dashboard/training-chart'
import WellnessGauge from '@/components/dashboard/wellness-gauge'
import MedicalAlerts from '@/components/dashboard/medical-alerts'

export default async function DashboardPage() {
  const session = await getSession()

  // Carregar dados em paralelo
  const [training, wellness, medical] = await Promise.all([
    getTrainingPerformance(),
    getWellnessSummary(),
    getMedicalSummary(),
  ])

  // Calcular métricas agregadas
  const totalSessions = training.reduce((sum, t) => sum + t.total_sessions, 0)
  const avgRPE = training.reduce((sum, t) => sum + t.avg_rpe, 0) / training.length
  const activeCases = medical.reduce((sum, m) => sum + m.active_cases, 0)
  const avgWellness =
    wellness.reduce((sum, w) => sum + (w.avg_fatigue + w.avg_sleep_quality) / 2, 0) /
    wellness.length

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-gray-900 dark:text-white">
          Bem-vindo, {session?.user.name}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Dashboard - Visão Geral
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatsCard
          title="Total de Sessões"
          value={totalSessions}
          icon="training"
          trend={{ value: 12, isPositive: true }}
        />
        <StatsCard
          title="RPE Médio"
          value={avgRPE.toFixed(1)}
          icon="gauge"
          trend={{ value: 5, isPositive: false }}
        />
        <StatsCard
          title="Casos Ativos"
          value={activeCases}
          icon="medical"
          trend={{ value: 2, isPositive: false }}
        />
        <StatsCard
          title="Wellness Score"
          value={`${avgWellness.toFixed(0)}%`}
          icon="wellness"
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <TrainingChart data={training} />
        <WellnessGauge data={wellness} />
      </div>

      {/* Medical Alerts */}
      <MedicalAlerts data={medical} />
    </div>
  )
}
```

### Componente de Gráfico (ApexCharts)

**Criar:** `src/components/dashboard/training-chart.tsx`
```tsx
'use client'

import dynamic from 'next/dynamic'
import { TrainingPerformance } from '@/types/reports'

const Chart = dynamic(() => import('react-apexcharts'), { ssr: false })

interface Props {
  data: TrainingPerformance[]
}

export default function TrainingChart({ data }: Props) {
  const chartData = {
    series: [
      {
        name: 'Sessões',
        data: data.map(d => d.total_sessions),
      },
      {
        name: 'RPE Médio',
        data: data.map(d => d.avg_rpe),
      },
    ],
    options: {
      chart: {
        type: 'line' as const,
        toolbar: {
          show: false,
        },
      },
      colors: ['#0ea5e9', '#10b981'],
      stroke: {
        curve: 'smooth' as const,
        width: 2,
      },
      xaxis: {
        categories: data.map(d => d.athlete_name),
      },
      yaxis: [
        {
          title: {
            text: 'Sessões',
          },
        },
        {
          opposite: true,
          title: {
            text: 'RPE',
          },
          min: 0,
          max: 10,
        },
      ],
      legend: {
        position: 'top' as const,
      },
    },
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Performance de Treino</h3>
      <Chart
        options={chartData.options}
        series={chartData.series}
        type="line"
        height={300}
      />
    </div>
  )
}
```

---

## 💬 SISTEMA DE MENSAGENS

### 1️⃣ Tipos

**Criar:** `src/types/messages.ts`
```typescript
export interface Message {
  id: string
  from_user_id: string
  from_user_name: string
  from_user_avatar?: string
  to_user_id: string
  to_user_name: string
  content: string
  read: boolean
  created_at: string
  updated_at: string
}

export interface MessageThread {
  user_id: string
  user_name: string
  user_avatar?: string
  last_message: string
  last_message_date: string
  unread_count: number
}

export interface SendMessageRequest {
  to_user_id: string
  content: string
}
```

### 2️⃣ Backend - Nova Tabela (Migrations)

**Nota:** Você precisará criar uma nova migration no backend para a tabela de mensagens.

**Backend:** `backend/db_migrations/versions/create_messages_table.py`
```python
"""create messages table

Revision ID: <novo_id>
Revises: b4b136a1af44
Create Date: 2025-12-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '<novo_id>'
down_revision = 'b4b136a1af44'

def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('from_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('read', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id']),
    )

    # Índices para performance
    op.create_index('idx_messages_to_user', 'messages', ['to_user_id', 'created_at'])
    op.create_index('idx_messages_from_user', 'messages', ['from_user_id', 'created_at'])

def downgrade() -> None:
    op.drop_table('messages')
```

### 3️⃣ Frontend - Página de Mensagens

**Criar:** `src/app/(dashboard)/messages/page.tsx`
```tsx
'use client'

import { useState, useEffect } from 'react'
import { getSession } from '@/lib/auth/actions'
import MessageList from '@/components/messages/message-list'
import MessageThread from '@/components/messages/message-thread'
import MessageComposer from '@/components/messages/message-composer'

export default function MessagesPage() {
  const [selectedUser, setSelectedUser] = useState<string | null>(null)

  return (
    <div className="p-6">
      <h1 className="text-3xl font-heading font-bold mb-6">Mensagens</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de conversas */}
        <div className="lg:col-span-1">
          <MessageList onSelectUser={setSelectedUser} />
        </div>

        {/* Thread de mensagens */}
        <div className="lg:col-span-2">
          {selectedUser ? (
            <>
              <MessageThread userId={selectedUser} />
              <MessageComposer userId={selectedUser} />
            </>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
              <p className="text-gray-500">
                Selecione uma conversa para começar
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

**Componente MessageThread:**

**Criar:** `src/components/messages/message-thread.tsx`
```tsx
'use client'

import { useEffect, useState } from 'react'
import { Message } from '@/types/messages'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface Props {
  userId: string
}

export default function MessageThread({ userId }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMessages()
  }, [userId])

  const loadMessages = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/messages/${userId}`)
      const data = await response.json()
      setMessages(data)
    } catch (error) {
      console.error('Error loading messages:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse">Carregando mensagens...</div>
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-[500px] overflow-y-auto">
      <div className="space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.from_user_id === userId ? 'justify-start' : 'justify-end'
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.from_user_id === userId
                  ? 'bg-gray-100 dark:bg-gray-700'
                  : 'bg-primary-500 text-white'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <span className="text-xs opacity-75">
                {format(new Date(message.created_at), 'HH:mm', { locale: ptBR })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 🔔 SISTEMA DE NOTIFICAÇÕES

### 1️⃣ Tipos

**Criar:** `src/types/notifications.ts`
```typescript
export interface Notification {
  id: string
  user_id: string
  type: 'info' | 'warning' | 'success' | 'error'
  title: string
  message: string
  read: boolean
  action_url?: string
  created_at: string
}

export interface NotificationSettings {
  email_enabled: boolean
  push_enabled: boolean
  training_alerts: boolean
  medical_alerts: boolean
  messages_alerts: boolean
}
```

### 2️⃣ Store Zustand

**Criar:** `src/lib/store/notifications-store.ts`
```typescript
import { create } from 'zustand'
import { Notification } from '@/types/notifications'

interface NotificationsState {
  notifications: Notification[]
  unreadCount: number
  addNotification: (notification: Notification) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
}

export const useNotifications = create<NotificationsState>((set) => ({
  notifications: [],
  unreadCount: 0,

  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    })),

  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
      unreadCount: state.notifications.find((n) => n.id === id && !n.read)
        ? state.unreadCount - 1
        : state.unreadCount,
    })),
}))
```

### 3️⃣ Componente Notification Bell

**Criar:** `src/components/notifications/notification-bell.tsx`
```tsx
'use client'

import { useState } from 'react'
import { useNotifications } from '@/lib/store/notifications-store'
import NotificationList from './notification-list'

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const { unreadCount } = useNotifications()

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
      >
        {/* Bell icon */}
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Badge */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-50">
          <NotificationList onClose={() => setIsOpen(false)} />
        </div>
      )}
    </div>
  )
}
```

---

## 🗺️ ROADMAP DE IMPLEMENTAÇÃO

### 📅 FASE 1: Setup e Autenticação (2-3 dias)

**Dia 1:**
- [x] Clonar template Next.js
- [x] Configurar ambiente (.env)
- [x] Instalar dependências adicionais
- [x] Configurar cores e tema personalizado
- [ ] Adicionar logo e assets

**Dia 2:**
- [ ] Implementar autenticação JWT
- [ ] Criar server actions para auth
- [ ] Implementar middleware de proteção
- [ ] Testar fluxo de login/logout

**Dia 3:**
- [ ] Criar cliente API
- [ ] Implementar tipos TypeScript
- [ ] Testar integração com backend de produção

---

### 📅 FASE 2: Dashboard e Relatórios (3-4 dias)

**Dia 4:**
- [ ] Implementar server actions para relatórios
- [ ] Criar página de dashboard principal
- [ ] Implementar cards de métricas (KPIs)

**Dia 5:**
- [ ] Criar gráficos de training performance
- [ ] Implementar wellness gauge
- [ ] Adicionar medical alerts

**Dia 6:**
- [ ] Criar página de Training Reports (R1)
- [ ] Criar página de Athletes (R2)

**Dia 7:**
- [ ] Criar página de Wellness (R3)
- [ ] Criar página de Medical Cases (R4)

---

### 📅 FASE 3: Mensagens e Notificações (2-3 dias)

**Dia 8:**
- [ ] Criar migration de mensagens no backend
- [ ] Implementar endpoints de mensagens
- [ ] Criar página de mensagens

**Dia 9:**
- [ ] Implementar sistema de notificações
- [ ] Criar notification bell component
- [ ] Integrar notificações no header

**Dia 10:**
- [ ] Implementar WebSocket/SSE para real-time
- [ ] Testar sistema de mensagens completo

---

### 📅 FASE 4: Refinamento e Deploy (2-3 dias)

**Dia 11:**
- [ ] Adicionar filtros e paginação
- [ ] Implementar busca
- [ ] Melhorar UX/UI

**Dia 12:**
- [ ] Testes completos (desktop e mobile)
- [ ] Otimizar performance
- [ ] Configurar build de produção

**Dia 13:**
- [ ] Deploy no Vercel/Netlify
- [ ] Configurar domínio
- [ ] Documentação final

---

## ✅ CHECKLIST COMPLETO

### Setup Inicial
- [ ] Template clonado e rodando
- [ ] Environment configurado
- [ ] Dependências instaladas
- [ ] Tema personalizado aplicado
- [ ] Logo e assets adicionados

### Autenticação
- [ ] Tipos TypeScript criados
- [ ] Server actions implementados
- [ ] Middleware configurado
- [ ] Página de login adaptada
- [ ] Fluxo testado com backend

### Integração Backend
- [ ] Cliente API criado
- [ ] Server actions de relatórios
- [ ] Tipos de todos os relatórios
- [ ] Testes com API de produção

### Dashboard
- [ ] Página principal implementada
- [ ] Cards de métricas (4)
- [ ] Gráficos de training
- [ ] Wellness gauge
- [ ] Medical alerts

### Páginas de Relatórios
- [ ] Training Performance (R1)
- [ ] Athletes List & Detail (R2)
- [ ] Wellness Summary (R3)
- [ ] Medical Cases (R4)

### Sistema de Mensagens
- [ ] Migration criada no backend
- [ ] Endpoints implementados
- [ ] Página de mensagens
- [ ] Thread de conversas
- [ ] Composer funcionando

### Sistema de Notificações
- [ ] Store Zustand criado
- [ ] Notification bell
- [ ] Lista de notificações
- [ ] Integração com eventos

### Funcionalidades Extras
- [ ] Filtros por temporada/equipe
- [ ] Paginação implementada
- [ ] Busca/filtro em tabelas
- [ ] Dark mode funcionando
- [ ] Responsividade mobile

### Deploy
- [ ] Build de produção OK
- [ ] Deploy realizado
- [ ] Domínio configurado
- [ ] SSL ativo
- [ ] Documentação criada

---

## 📚 RECURSOS E DOCUMENTAÇÃO

### Backend
- **API Docs:** https://hbtrack.onrender.com/api/v1/docs
- **Repo:** https://github.com/Davisermenho/Hb-Traking---Backend
- **Docs:** `.vscode/docs/PROJETO_CONCLUIDO.md`

### Frontend
- **Template:** https://github.com/TailAdmin/free-nextjs-admin-dashboard
- **Next.js Docs:** https://nextjs.org/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **ApexCharts:** https://apexcharts.com/docs/react-charts/

### Ferramentas
- **Vercel:** https://vercel.com (Deploy recomendado)
- **Postman:** Para testar API
- **React DevTools:** Para debug

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Clonar Template**
   ```bash
   cd "c:\Hb Tracking"
   mkdir "Hb Tracking - Frontend"
   cd "Hb Tracking - Frontend"
   git clone https://github.com/TailAdmin/free-nextjs-admin-dashboard.git .
   npm install --legacy-peer-deps
   npm run dev
   ```

2. **Configurar .env.local**
   ```bash
   NEXT_PUBLIC_API_URL=https://hbtrack.onrender.com/api/v1
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-secret-key
   ```

3. **Instalar Dependências**
   ```bash
   npm install axios swr zustand react-hook-form zod apexcharts react-apexcharts date-fns
   ```

4. **Começar Implementação**
   - Criar estrutura de pastas
   - Implementar autenticação
   - Testar integração com backend

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** 1.0.0
**Status:** 📋 **PRONTO PARA IMPLEMENTAÇÃO**

**🎯 Objetivo:** Frontend completo integrado com backend em ~10-13 dias