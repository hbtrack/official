<!-- STATUS: NEEDS_REVIEW -->

# 🎨 PLANO DE INTEGRAÇÃO - FRONTEND ANGULAR + BACKEND

**Data:** 2025-12-25
**Template:** TailAdmin Free Angular Dashboard
**Backend:** HB Tracking API (FastAPI + PostgreSQL)
**Versão:** 1.0.0

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitetura da Integração](#arquitetura-da-integração)
4. [Configuração Inicial](#configuração-inicial)
5. [Implementação de Autenticação](#implementação-de-autenticação)
6. [Serviços e Modelos](#serviços-e-modelos)
7. [Páginas e Componentes](#páginas-e-componentes)
8. [Checklist de Implementação](#checklist-de-implementação)

---

## 🎯 VISÃO GERAL

### Objetivo
Integrar o template TailAdmin Angular Dashboard com a API REST do HB Tracking para criar uma aplicação completa de gestão de treinos, wellness e casos médicos de atletas.

### Escopo
- ✅ Autenticação JWT
- ✅ 4 módulos de relatórios (R1-R4)
- ✅ Dashboard com métricas em tempo real
- ✅ Gestão de usuários por perfil (Admin, Coach, Athlete)
- ✅ Responsividade e dark mode
- ✅ Integração com API de produção (Render)

---

## 🛠️ STACK TECNOLÓGICO

### Frontend
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| Angular | 20+ | Framework principal |
| TypeScript | Latest | Linguagem |
| Tailwind CSS | Latest | Estilização |
| RxJS | Latest | Programação reativa |
| Chart.js / ApexCharts | Latest | Visualização de dados |

### Backend (Já Implementado)
| Tecnologia | Versão | Status |
|------------|--------|--------|
| FastAPI | Latest | ✅ Operacional |
| PostgreSQL 17 | 17 | ✅ Neon Cloud |
| SQLAlchemy | 2.0 | ✅ ORM |
| Alembic | Latest | ✅ Migrations |
| JWT | - | ✅ Autenticação |

---

## 🏗️ ARQUITETURA DA INTEGRAÇÃO

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    ANGULAR FRONTEND                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Components  │  │   Services   │  │    Guards    │    │
│  │              │  │              │  │              │    │
│  │ - Dashboard  │  │ - Auth       │  │ - AuthGuard  │    │
│  │ - Reports    │  │ - Training   │  │ - RoleGuard  │    │
│  │ - Athletes   │  │ - Wellness   │  │              │    │
│  │ - Wellness   │  │ - Medical    │  │              │    │
│  │ - Medical    │  │ - Refresh    │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│                   ┌────────▼────────┐                      │
│                   │  HTTP Interceptor│                      │
│                   │  (JWT Token)     │                      │
│                   └────────┬────────┘                      │
└────────────────────────────┼─────────────────────────────┘
                             │
                    HTTPS (JSON)
                             │
┌────────────────────────────▼─────────────────────────────┐
│                  FASTAPI BACKEND                         │
│              https://hbtrack.onrender.com                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Routers    │  │   Services   │  │  Schemas     │ │
│  │              │  │              │  │              │ │
│  │ - Auth       │  │ - Training   │  │ - Pydantic   │ │
│  │ - Reports    │  │ - Athlete    │  │ - Validation │ │
│  │ - Refresh    │  │ - Wellness   │  │              │ │
│  │              │  │ - Medical    │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                   ┌────────▼────────┐                   │
│                   │  PostgreSQL DB  │                   │
│                   │  (Neon Cloud)   │                   │
│                   └─────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### Endpoints Backend Disponíveis

**Autenticação:**
- `POST /api/v1/auth/login` - Login e obtenção de JWT token

**Relatórios (R1 - Training Performance):**
- `GET /api/v1/reports/training-performance` - Performance geral
- `GET /api/v1/reports/training-trends` - Tendências por temporada

**Relatórios (R2 - Athletes):**
- `GET /api/v1/reports/athletes` - Lista de atletas com resumo
- `GET /api/v1/reports/athletes/{id}` - Detalhes de atleta

**Relatórios (R3 - Wellness):**
- `GET /api/v1/reports/wellness-summary` - Resumo de wellness
- `GET /api/v1/reports/wellness-trends` - Tendências de wellness

**Relatórios (R4 - Medical):**
- `GET /api/v1/reports/medical-summary` - Resumo de casos médicos
- `GET /api/v1/reports/athletes/{id}/medical-history` - Histórico médico

**Manutenção:**
- `POST /api/v1/reports/refresh/{view_name}` - Refresh de view específica
- `POST /api/v1/reports/refresh-all` - Refresh de todas as views
- `GET /api/v1/reports/stats` - Estatísticas das views

---

## ⚙️ CONFIGURAÇÃO INICIAL

### 1️⃣ Clone e Setup do Template

```bash
# Criar diretório do frontend
cd "c:\Hb Tracking"
mkdir "Hb Tracking - Frontend"
cd "Hb Tracking - Frontend"

# Clonar template
git clone https://github.com/TailAdmin/free-angular-tailwind-dashboard.git .

# Instalar Angular CLI (se necessário)
npm install -g @angular/cli

# Instalar dependências
npm install

# Testar se funciona
npm start
# Acessar: http://localhost:4200
```

### 2️⃣ Configuração de Environments

**Criar:** `src/environments/environment.development.ts`
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  apiTimeout: 30000
};
```

**Criar:** `src/environments/environment.production.ts`
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://hbtrack.onrender.com/api/v1',
  apiTimeout: 30000
};
```

**Atualizar:** `angular.json`
```json
{
  "projects": {
    "tailadmin-angular": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "fileReplacements": [
                {
                  "replace": "src/environments/environment.ts",
                  "with": "src/environments/environment.production.ts"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

### 3️⃣ Instalar Dependências Adicionais

```bash
# HTTP Client (já vem com Angular)
# RxJS (já vem com Angular)

# Charts (se não estiver no template)
npm install chart.js ng2-charts
npm install apexcharts ng-apexcharts

# Date handling
npm install date-fns

# Utilities
npm install lodash-es
npm install @types/lodash-es --save-dev
```

---

## 🔐 IMPLEMENTAÇÃO DE AUTENTICAÇÃO

### 1️⃣ Modelo de Autenticação

**Criar:** `src/app/models/auth.model.ts`
```typescript
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'coach' | 'athlete';
  teamId?: string;
  seasonId?: string;
}

export interface JWTPayload {
  sub: string;  // user_id
  email: string;
  role: string;
  exp: number;
}
```

### 2️⃣ Serviço de Autenticação

**Criar:** `src/app/services/auth.service.ts`
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoginRequest, LoginResponse, User, JWTPayload } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    const storedUser = this.getUserFromStorage();
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${environment.apiUrl}/auth/login`,
      credentials
    ).pipe(
      tap(response => {
        // Salvar token
        localStorage.setItem('access_token', response.access_token);

        // Decodificar JWT e extrair user info
        const user = this.decodeToken(response.access_token);

        // Salvar user
        localStorage.setItem('current_user', JSON.stringify(user));
        this.currentUserSubject.next(user);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    // Verificar se token não expirou
    const payload = this.decodeToken(token);
    if (!payload) return false;

    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now;
  }

  hasRole(role: string): boolean {
    const user = this.currentUserValue;
    return user?.role === role;
  }

  private decodeToken(token: string): User | null {
    try {
      const payload: JWTPayload = JSON.parse(atob(token.split('.')[1]));

      return {
        id: payload.sub,
        email: payload.email,
        name: payload.email.split('@')[0], // Simplificado
        role: payload.role as 'admin' | 'coach' | 'athlete'
      };
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  private getUserFromStorage(): User | null {
    const userJson = localStorage.getItem('current_user');
    if (!userJson) return null;

    try {
      return JSON.parse(userJson);
    } catch {
      return null;
    }
  }
}
```

### 3️⃣ HTTP Interceptor

**Criar:** `src/app/interceptors/auth.interceptor.ts`
```typescript
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    // Adicionar token JWT ao header
    const token = this.authService.getToken();

    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Token inválido ou expirado
          this.authService.logout();
        }
        return throwError(() => error);
      })
    );
  }
}
```

**Registrar interceptor em:** `src/app/app.config.ts`
```typescript
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([AuthInterceptor])
    )
  ]
};
```

### 4️⃣ Auth Guard

**Criar:** `src/app/guards/auth.guard.ts`
```typescript
import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    if (this.authService.isAuthenticated()) {
      // Verificar role se especificado na rota
      const requiredRole = route.data['role'];

      if (requiredRole && !this.authService.hasRole(requiredRole)) {
        this.router.navigate(['/dashboard']);
        return false;
      }

      return true;
    }

    // Não autenticado, redirecionar para login
    this.router.navigate(['/auth/login']);
    return false;
  }
}
```

---

## 🗂️ SERVIÇOS E MODELOS

### Modelos TypeScript (baseados nos schemas Pydantic)

**Criar:** `src/app/models/reports.model.ts`
```typescript
// R1 - Training Performance
export interface TrainingPerformance {
  athlete_id: string;
  athlete_name: string;
  team_id: string;
  team_name: string;
  season_id: string;
  season_name: string;
  total_sessions: number;
  avg_rpe: number;
  avg_duration_minutes: number;
  total_distance_km: number;
  last_session_date: string;
}

export interface TrainingTrend {
  date: string;
  total_sessions: number;
  avg_rpe: number;
  avg_duration: number;
}

// R2 - Athlete Summary
export interface AthleteSummary {
  id: string;
  name: string;
  email: string;
  team_id: string;
  team_name: string;
  total_sessions: number;
  avg_rpe: number;
  avg_duration_minutes: number;
  last_session_date: string;
}

export interface AthleteDetail extends AthleteSummary {
  recent_sessions: TrainingSession[];
  wellness_stats: WellnessStats;
  medical_history: MedicalCase[];
}

// R3 - Wellness
export interface WellnessSummary {
  athlete_id: string;
  athlete_name: string;
  team_id: string;
  season_id: string;
  avg_fatigue: number;
  avg_sleep_quality: number;
  avg_stress: number;
  avg_muscle_soreness: number;
  last_assessment_date: string;
}

export interface WellnessTrend {
  date: string;
  avg_fatigue: number;
  avg_sleep_quality: number;
  avg_stress: number;
  avg_muscle_soreness: number;
}

// R4 - Medical
export interface MedicalSummary {
  athlete_id: string;
  athlete_name: string;
  team_id: string;
  season_id: string;
  total_cases: number;
  active_cases: number;
  avg_recovery_days: number;
  injury_types: string[];
}

export interface MedicalCase {
  id: string;
  athlete_id: string;
  case_type: 'injury' | 'illness';
  description: string;
  severity: 'minor' | 'moderate' | 'severe';
  start_date: string;
  end_date?: string;
  status: 'active' | 'recovering' | 'resolved';
  recovery_percentage: number;
}

// Shared models
export interface TrainingSession {
  id: string;
  date: string;
  rpe: number;
  duration_minutes: number;
  distance_km?: number;
  session_type: string;
}

export interface WellnessStats {
  avg_fatigue: number;
  avg_sleep_quality: number;
  avg_stress: number;
  avg_muscle_soreness: number;
}

// Query params
export interface ReportFilters {
  season_id?: string;
  team_id?: string;
  athlete_id?: string;
  start_date?: string;
  end_date?: string;
}
```

### Serviços de Relatórios

**Criar:** `src/app/services/training.service.ts`
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { TrainingPerformance, TrainingTrend, ReportFilters } from '../models/reports.model';

@Injectable({
  providedIn: 'root'
})
export class TrainingService {
  private apiUrl = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  getPerformance(filters?: ReportFilters): Observable<TrainingPerformance[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.season_id) params = params.set('season_id', filters.season_id);
      if (filters.team_id) params = params.set('team_id', filters.team_id);
      if (filters.athlete_id) params = params.set('athlete_id', filters.athlete_id);
    }

    return this.http.get<TrainingPerformance[]>(
      `${this.apiUrl}/training-performance`,
      { params }
    );
  }

  getTrends(filters?: ReportFilters): Observable<TrainingTrend[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.season_id) params = params.set('season_id', filters.season_id);
      if (filters.start_date) params = params.set('start_date', filters.start_date);
      if (filters.end_date) params = params.set('end_date', filters.end_date);
    }

    return this.http.get<TrainingTrend[]>(
      `${this.apiUrl}/training-trends`,
      { params }
    );
  }
}
```

**Criar serviços similares para:**
- `athlete.service.ts` - R2
- `wellness.service.ts` - R3
- `medical.service.ts` - R4
- `refresh.service.ts` - Refresh de views

---

## 📄 PÁGINAS E COMPONENTES

### Estrutura de Páginas

```
src/app/
├── pages/
│   ├── auth/
│   │   ├── login/
│   │   └── forgot-password/
│   ├── dashboard/              # Dashboard principal
│   │   ├── dashboard.component.ts
│   │   ├── dashboard.component.html
│   │   └── components/
│   │       ├── training-summary-card/
│   │       ├── wellness-chart/
│   │       └── medical-alerts/
│   ├── training/               # R1
│   │   ├── performance/
│   │   └── trends/
│   ├── athletes/               # R2
│   │   ├── list/
│   │   └── detail/
│   ├── wellness/               # R3
│   │   ├── summary/
│   │   └── trends/
│   └── medical/                # R4
│       ├── cases/
│       └── history/
```

### Dashboard Principal

**Adaptar:** `src/app/pages/dashboard/dashboard.component.ts`
```typescript
import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { TrainingService } from '../../services/training.service';
import { WellnessService } from '../../services/wellness.service';
import { MedicalService } from '../../services/medical.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  loading = true;
  currentUser$ = this.authService.currentUser;

  // Stats
  totalSessions = 0;
  avgRPE = 0;
  activeCases = 0;
  wellnessScore = 0;

  // Charts data
  trainingTrends: any[] = [];
  wellnessTrends: any[] = [];

  constructor(
    private trainingService: TrainingService,
    private wellnessService: WellnessService,
    private medicalService: MedicalService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;

    forkJoin({
      training: this.trainingService.getPerformance(),
      wellness: this.wellnessService.getSummary(),
      medical: this.medicalService.getSummary()
    }).subscribe({
      next: (data) => {
        this.processDashboardData(data);
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading dashboard:', error);
        this.loading = false;
      }
    });
  }

  private processDashboardData(data: any): void {
    // Calcular métricas agregadas
    const training = data.training;

    this.totalSessions = training.reduce(
      (sum: number, t: any) => sum + t.total_sessions,
      0
    );

    this.avgRPE = training.reduce(
      (sum: number, t: any) => sum + t.avg_rpe,
      0
    ) / training.length;

    // Processar outros dados...
  }
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Setup Inicial
- [ ] Clonar template TailAdmin
- [ ] Configurar environments (dev e production)
- [ ] Instalar dependências adicionais
- [ ] Testar build e serve local

### Fase 2: Autenticação
- [ ] Criar modelos de autenticação
- [ ] Implementar AuthService
- [ ] Criar HTTP Interceptor para JWT
- [ ] Implementar AuthGuard
- [ ] Adaptar página de login do template
- [ ] Testar fluxo de login/logout

### Fase 3: Serviços e Modelos
- [ ] Criar modelos TypeScript (reports.model.ts)
- [ ] Implementar TrainingService (R1)
- [ ] Implementar AthleteService (R2)
- [ ] Implementar WellnessService (R3)
- [ ] Implementar MedicalService (R4)
- [ ] Implementar RefreshService
- [ ] Testar chamadas API com Postman/Insomnia

### Fase 4: Dashboard
- [ ] Adaptar dashboard principal do template
- [ ] Criar cards de métricas (KPIs)
- [ ] Implementar gráficos de training trends
- [ ] Implementar gráficos de wellness
- [ ] Adicionar alertas de casos médicos ativos
- [ ] Implementar refresh automático

### Fase 5: Páginas de Relatórios
- [ ] Criar página Training Performance (R1)
- [ ] Criar página Training Trends (R1)
- [ ] Criar página Athletes List (R2)
- [ ] Criar página Athlete Detail (R2)
- [ ] Criar página Wellness Summary (R3)
- [ ] Criar página Wellness Trends (R3)
- [ ] Criar página Medical Cases (R4)
- [ ] Criar página Medical History (R4)

### Fase 6: Funcionalidades Avançadas
- [ ] Implementar filtros por temporada/equipe
- [ ] Adicionar paginação em listas
- [ ] Implementar busca/filtro em tabelas
- [ ] Adicionar exportação de dados (CSV/PDF)
- [ ] Implementar refresh manual de views
- [ ] Adicionar notificações/toasts

### Fase 7: Testes e Deploy
- [ ] Testar todos os fluxos com backend local
- [ ] Testar integração com backend de produção (Render)
- [ ] Validar responsividade mobile
- [ ] Testar dark mode
- [ ] Configurar build de produção
- [ ] Deploy frontend (Vercel/Netlify/Render)

---

## 🚀 PRÓXIMOS PASSOS

### Imediato (Hoje)
1. ✅ Clonar template TailAdmin
2. ✅ Configurar projeto base
3. ✅ Implementar autenticação básica
4. ✅ Testar login com backend

### Curto Prazo (Esta Semana)
1. Implementar todos os serviços de relatórios
2. Adaptar dashboard com dados reais
3. Criar páginas principais de relatórios
4. Testar integração completa

### Médio Prazo (Próximas 2 Semanas)
1. Implementar funcionalidades avançadas
2. Refinar UX/UI
3. Testes completos
4. Deploy em produção

---

## 📚 RECURSOS E DOCUMENTAÇÃO

### Backend
- **API Docs:** https://hbtrack.onrender.com/api/v1/docs
- **Backend Repo:** https://github.com/Davisermenho/Hb-Traking---Backend
- **Documentação:** `.vscode/docs/` no backend

### Frontend
- **Template:** https://github.com/TailAdmin/free-angular-tailwind-dashboard
- **Angular Docs:** https://angular.dev
- **Tailwind CSS:** https://tailwindcss.com
- **Chart.js:** https://www.chartjs.org

### Ferramentas
- **Postman:** Para testar API
- **Angular DevTools:** Para debug
- **Chrome DevTools:** Network e Console

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** 1.0.0
**Status:** 📋 **PLANEJAMENTO COMPLETO**