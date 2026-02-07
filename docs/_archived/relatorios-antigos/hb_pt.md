<!-- STATUS: DEPRECATED | arquivado -->

Análise do Sistema HB Track e Recomendações de Arquitetura de Frontend  
📋 Resumo Executivo

Analisei seu sistema abrangente de rastreamento de handebol. Trata-se de uma plataforma de gestão esportiva em nível enterprise, com atenção excepcional à conformidade regulatória, integridade de dados e trilhas de auditoria. A arquitetura de backend é sólida, mas o frontend apresenta uma oportunidade empolgante de criar algo realmente diferenciado no mercado de tecnologia esportiva.

1️⃣ Análise do Sistema: O que Você Construiu  
Forças do Backend ✅

Excelência Arquitetural:

- Autorização baseada em escopo com hierarquia adequada (superadmin → dirigente → coordenador → treinador → atleta)
- Trilhas de auditoria imutáveis — nada é excluído permanentemente; tudo é rastreado com actor_id, timestamp, old_value, new_value
- Camada de cache inteligente com invalidação baseada em TTL (cachetools → TTL de 120s)
- Otimizado para performance com 9 índices estratégicos em consultas de alto tráfego
- Roteamento canônico (/teams/{team_id}/matches/{match_id}/events) que impõe escopo de forma implícita

Sofisticação do Modelo de Domínio:

- Vínculos temporais — team_registrations e org_memberships são vinculados no tempo, permitindo reconstrução histórica
- Padrão de Estado + Flags para atletas (ativa + injured/medical_restriction/suspended_until/load_restricted) — excelente para lidar com condições sobrepostas
- Suporte a múltiplas organizações desde a V1 com isolamento adequado
- Precisão no domínio esportivo — categorias por idade, regras de gênero, exceções para goleiras, limite de elenco (16), limite de minutos (80)

Conformidade Regulatória:

- Janelas de edição R40 (10min autoedição → 24h com aprovação → somente leitura)
- Suporte a Idempotency-Key para intake evitando duplicidades
- Restrições de unicidade em RG/CPF/telefone/email com conflitos 409
- Modo dry-run para validação antes do commit

Áreas para Melhoria 🔧  
Pontos de Atenção no Backend:

Limitações da Estratégia de Cache

- Cachetools em memória não escala horizontalmente — se você subir múltiplas instâncias FastAPI, cada uma terá seu próprio cache
- Sem estratégia de aquecimento de cache para o dashboard na primeira requisição
- Recomendação: Migrar para Redis com cache compartilhado entre instâncias; implementar pre-warming em background para dashboards

Camada de Tempo Real Ausente

- Sem WebSocket/SSE para atualizações ao vivo de jogo — o frontend precisa ficar em polling
- Recomendação: Adicionar endpoint /ws/matches/{match_id}/live para streaming em tempo real de eventos durante jogos

Limitações de Paginação

- Usa paginação baseada em OFFSET — degrada com conjuntos de dados grandes
- Recomendação: Implementar paginação baseada em cursor para listas >10k (ex.: ?cursor=last_id)

Sem Operações em Lote

- Criar 16 entradas de elenco requer 16 requisições POST
- Recomendação: Adicionar POST /teams/{team_id}/matches/{match_id}/roster/bulk aceitando array

Endpoints de Agregação Ausentes

- Relatórios exigem agregação no cliente de dados paginados
- Recomendação: Adicionar /reports/export/{type} com agregação completa no servidor para geração de PDF

Ajuste de Alertas de Carga

- Limiares de ACWR (0.8–1.5) são fixos — diferentes equipes podem precisar de faixas customizadas
- Recomendação: Tornar limiares configuráveis por organização em tabela de settings

2️⃣ O Frontend Perfeito: Arquitetura e Design System  
Validação da Stack ✅

Sua stack atual é excelente para este domínio. Eis o porquê:

Escolha | Justificativa  
Next.js 16 | App Router com React Server Components = perfeito para SSR do dashboard; Turbopack para dev rápido  
React 19 | Novo compilador = memoização automática, melhor renderização concorrente para atualizações ao vivo  
TanStack Query v5 | Melhor da categoria para gestão de cache com stale-while-revalidate; crítico para respeitar headers de cache do backend  
Tailwind v4 | CSS-first com camadas nativas = bundle menor, sem overhead de JS, dark mode pronto  
React Hook Form + Zod | Mínimos re-renders + validação type-safe = perfeito para wizard de intake complexo  
Framer Motion | Animações declarativas para transições de passo, feedback de UI otimista  
Lucide Icons | Tree-shakeable, estilo consistente para UI esportiva (apito, prancheta, batimento cardíaco)

Nenhuma mudança necessária — esta stack atinge o ponto ideal de performance, experiência do desenvolvedor e escalabilidade.

Tokens do Design System  
Paleta de Cores (Otimizada para Handebol)

```css
/* globals.css */
@import "tailwindcss";

@layer base {
  :root {
    /* Cores Semânticas */
    --color-court: 215 25% 27%;        /* Azul-acinzentado da quadra para mapas espaciais */
    --color-goal: 142 76% 36%;         /* Verde do gol para sucesso */
    --color-miss: 0 84% 60%;           /* Vermelho para arremesso perdido */
    --color-save: 221 83% 53%;         /* Azul para defesa da goleira */
    
    /* Cores de Estado */
    --color-active: 142 71% 45%;       /* Atleta ativa */
    --color-injured: 0 84% 60%;        /* Lesionada */
    --color-suspended: 38 92% 50%;     /* Suspensa */
    --color-restricted: 45 93% 47%;    /* Restrição médica/carga */
    --color-dispensed: 240 5% 65%;     /* Dispensada */
    
    /* Carga/Bem-estar */
    --color-load-low: 45 93% 47%;      /* ACWR < 0.8 */
    --color-load-optimal: 142 71% 45%; /* ACWR 0.8-1.5 */
    --color-load-high: 0 84% 60%;      /* ACWR > 1.5 */
    
    /* Base da UI */
    --color-background: 0 0% 100%;
    --color-foreground: 222 47% 11%;
    --color-card: 0 0% 100%;
    --color-border: 214 32% 91%;
    --color-accent: 210 40% 96%;
  }
  
  .dark {
    --color-background: 222 47% 11%;
    --color-foreground: 210 40% 98%;
    --color-card: 222 47% 16%;
    --color-border: 217 33% 17%;
    --color-accent: 217 33% 22%;
  }
}
```

Sistema de Tipografia

```css
@layer base {
  :root {
    --font-heading: 'Inter', system-ui, sans-serif;
    --font-body: 'Inter', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    /* Escala para dashboards densos em dados */
    --text-xs: 0.75rem;    /* Rótulos */
    --text-sm: 0.875rem;   /* Corpo de texto */
    --text-base: 1rem;     /* Padrão */
    --text-lg: 1.125rem;   /* Subtítulos */
    --text-xl: 1.25rem;    /* Títulos */
    --text-2xl: 1.5rem;    /* Títulos de página */
    --text-4xl: 2.25rem;   /* Números de destaque no dashboard */
  }
}
```

Escala de Espaçamento (Otimizada para Tempo de Jogo)

```css
@layer base {
  :root {
    --spacing-game: 0.25rem;  /* Espaçamento justo para dashboards ao vivo */
    --spacing-compact: 0.5rem;
    --spacing-normal: 1rem;
    --spacing-relaxed: 1.5rem;
    --spacing-section: 2.5rem;
  }
}
```

Primitivos de Componentes  
1. Componente de Badge de Estado

```tsx
// src/components/ui/StateBadge.tsx
import { cn } from '@/lib/utils';
import { 
  CheckCircle, AlertCircle, Ban, Clock, 
  Activity, Zap 
} from 'lucide-react';

interface StateBadgeProps {
  state: 'ativa' | 'dispensada' | 'arquivada';
  flags?: {
    injured?: boolean;
    medical_restriction?: boolean;
    suspended_until?: string;
    load_restricted?: boolean;
  };
  size?: 'sm' | 'md' | 'lg';
}

export function StateBadge({ state, flags, size = 'md' }: StateBadgeProps) {
  const variants = {
    ativa: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    dispensada: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
    arquivada: 'bg-gray-100 text-gray-600 dark:bg-gray-900/20 dark:text-gray-500'
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  return (
    <div className="flex flex-wrap gap-1.5">
      {/* Estado Base */}
      <span className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        variants[state],
        sizes[size]
      )}>
        {state === 'ativa' && <CheckCircle className="w-3.5 h-3.5" />}
        {state === 'dispensada' && <Ban className="w-3.5 h-3.5" />}
        {state}
      </span>

      {/* Flags */}
      {flags?.injured && (
        <span className={cn(
          'inline-flex items-center gap-1 rounded-full font-medium',
          'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
          sizes[size]
        )}>
          <AlertCircle className="w-3.5 h-3.5" />
          Lesionada
        </span>
      )}

      {flags?.suspended_until && (
        <span className={cn(
          'inline-flex items-center gap-1 rounded-full font-medium',
          'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
          sizes[size]
        )}>
          <Clock className="w-3.5 h-3.5" />
          Suspensa
        </span>
      )}

      {flags?.medical_restriction && (
        <span className={cn(
          'inline-flex items-center gap-1 rounded-full font-medium',
          'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
          sizes[size]
        )}>
          <Activity className="w-3.5 h-3.5" />
          Restrição
        </span>
      )}

      {flags?.load_restricted && (
        <span className={cn(
          'inline-flex items-center gap-1 rounded-full font-medium',
          'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400',
          sizes[size]
        )}>
          <Zap className="w-3.5 h-3.5" />
          Carga Limitada
        </span>
      )}
    </div>
  );
}
```

2. Componente de Mapa de Quadra (Scouting)

```tsx
// src/components/game/CourtMap.tsx
'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface Zone {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

const ZONES: Zone[] = [
  { id: 'shot_6m_left', label: '6m L', x: 10, y: 30, width: 35, height: 40 },
  { id: 'shot_6m_center', label: '6m C', x: 45, y: 30, width: 20, height: 40 },
  { id: 'shot_6m_right', label: '6m R', x: 65, y: 30, width: 35, height: 40 },
  { id: 'shot_9m_left', label: '9m L', x: 5, y: 70, width: 30, height: 20 },
  { id: 'shot_9m_center', label: '9m C', x: 35, y: 70, width: 30, height: 20 },
  { id: 'shot_9m_right', label: '9m R', x: 65, y: 70, width: 30, height: 20 },
  { id: 'shot_wing_left', label: 'Ponta L', x: 0, y: 10, width: 10, height: 80 },
  { id: 'shot_wing_right', label: 'Ponta R', x: 90, y: 10, width: 10, height: 80 }
];

interface CourtMapProps {
  events: Array<{
    zone: string;
    success: boolean;
  }>;
  onZoneClick?: (zoneId: string) => void;
  interactive?: boolean;
}

export function CourtMap({ events, onZoneClick, interactive = false }: CourtMapProps) {
  const [hoveredZone, setHoveredZone] = useState<string | null>(null);

  const getZoneStats = (zoneId: string) => {
    const zoneEvents = events.filter(e => e.zone === zoneId);
    const total = zoneEvents.length;
    const success = zoneEvents.filter(e => e.success).length;
    return { total, success, rate: total ? (success / total) * 100 : 0 };
  };

  return (
    <div className="relative w-full aspect-[2/1] bg-court rounded-lg overflow-hidden">
      {/* Linha do Gol */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-white" />
      
      {/* Linha dos 6m */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <path
          d="M 10% 30% L 90% 30%"
          stroke="white"
          strokeWidth="2"
          strokeDasharray="4 4"
          opacity="0.6"
        />
        <path
          d="M 5% 70% L 95% 70%"
          stroke="white"
          strokeWidth="1"
          strokeDasharray="4 4"
          opacity="0.4"
        />
      </svg>

      {/* Zonas */}
      {ZONES.map(zone => {
        const stats = getZoneStats(zone.id);
        const heatIntensity = Math.min(stats.total / 10, 1); // Normalize para 0-1
        
        return (
          <button
            key={zone.id}
            className={cn(
              'absolute transition-all duration-200',
              'border border-white/20',
              interactive && 'hover:border-white/60 hover:scale-105 cursor-pointer',
              hoveredZone === zone.id && 'border-white ring-2 ring-white/50'
            )}
            style={{
              left: `${zone.x}%`,
              top: `${zone.y}%`,
              width: `${zone.width}%`,
              height: `${zone.height}%`,
              backgroundColor: `rgba(255, 255, 255, ${heatIntensity * 0.3})`
            }}
            onClick={() => interactive && onZoneClick?.(zone.id)}
            onMouseEnter={() => setHoveredZone(zone.id)}
            onMouseLeave={() => setHoveredZone(null)}
            disabled={!interactive}
          >
            <div className="flex flex-col items-center justify-center h-full text-white">
              <span className="text-xs font-semibold">{zone.label}</span>
              {stats.total > 0 && (
                <>
                  <span className="text-lg font-bold">{stats.success}/{stats.total}</span>
                  <span className="text-xs opacity-80">{stats.rate.toFixed(0)}%</span>
                </>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}
```

3️⃣ Navegação e Arquitetura da Informação  
Navegação Primária (Ciente de Papéis)

```
┌─────────────────────────────────────────────┐
│  [Logo] HB Track                            │
├─────────────────────────────────────────────┤
│                                             │
│  🏠 Dashboard     (todos os papéis)         │
│  👤 Perfil        (todos os papéis)         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  📋 Intake        (treinador+)              │
│  🏃 Atletas       (treinador+)              │
│  🏆 Equipes       (coord+)                  │
│  📅 Temporadas    (coord+)                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  🎯 Treinos       (treinador+)              │
│  ⚽ Jogos         (treinador+)              │
│  🎮 Scout         (treinador+)              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  💪 Wellness      (todos os papéis - próprios dados) │
│  📊 Relatórios    (coord+)                  │
│  🚨 Alertas       (coord+)                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  ⚙️  Admin        (dirigente+)              │
│  🌐 Organizações  (apenas superadmin)       │
└─────────────────────────────────────────────┘
```

Experiência Mobile do Atleta (Navegação Inferior)

```
┌───────────────────────────────┐
│   [Foto de Perfil]  Maria S.  │
│   Cadete Fem · Ativa  🟢      │
│                               │
│   ┌─────────────────────────┐ │
│   │  Hoje                   │ │
│   │  🏋️ Treino 18:00        │ │
│   │  ⚽ Jogo Sáb 15:00      │ │
│   │  💪 Wellness pendente   │ │
│   └─────────────────────────┘ │
│                               │
│   ┌─────────────────────────┐ │
│   │  Alertas                │ │
│   │  ⚠️ Carga semanal alta  │ │
│   │  ✅ Streak 12 treinos   │ │
│   └─────────────────────────┘ │
├───────────────────────────────┤
│  🏠 Home · 📊 Stats · 💪 Bem-│
│  estar · 👤 Perfil            │
└───────────────────────────────┘
```

4️⃣ Fluxos de Usuário Críticos  
Fluxo 1: Wizard de Intake (Otimizado)

```tsx
// src/features/intake/IntakeWizard.tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';

const stepSchemas = {
  person: z.object({
    full_name: z.string().min(3, 'Nome muito curto'),
    gender: z.enum(['masculino', 'feminino']),
    birthdate: z.string().refine(date => {
      const age = new Date().getFullYear() - new Date(date).getFullYear();
      return age >= 8 && age <= 60;
    }, 'Idade deve estar entre 8 e 60 anos')
  }),
  contacts: z.object({
    email: z.string().email('Email inválido'),
    phone: z.string().regex(/^\+55\d{11}$/, 'Formato: +5511999999999'),
    rg: z.string().min(7).max(9)
  }),
  athlete: z.object({
    defensive_position_id: z.string().uuid(),
    offensive_position_ids: z.array(z.string().uuid()).optional()
  }).refine(data => {
    // Exceção para goleira: posições ofensivas devem estar vazias
    // Esta checagem deve usar dados reais de posições
    return true; // Implementar com contexto da API de posições
  }, 'Goleira não pode ter posições ofensivas')
};

export function IntakeWizard() {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [dryRunErrors, setDryRunErrors] = useState<string[]>([]);

  const { data: positions } = useQuery({
    queryKey: ['positions'],
    queryFn: () => fetch('/api/v1/positions').then(r => r.json())
  });

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await fetch('/api/v1/unified-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': crypto.randomUUID()
        },
        body: JSON.stringify({
          ...data,
          dry_run: dryRunMode
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw error;
      }
      
      return response.json();
    },
    onError: (error: any) => {
      if (error.status === 409) {
        setDryRunErrors(['Contato duplicado: ' + error.detail]);
      } else if (error.status === 422) {
        setDryRunErrors(error.detail.map((e: any) => e.msg));
      }
    }
  });

  const steps = [
    { id: 'person', label: 'Dados Pessoais', schema: stepSchemas.person },
    { id: 'contacts', label: 'Contatos & Docs', schema: stepSchemas.contacts },
    { id: 'athlete', label: 'Posições', schema: stepSchemas.athlete },
    { id: 'photo', label: 'Foto', schema: z.object({}) },
    { id: 'review', label: 'Revisar', schema: z.object({}) }
  ];

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(steps[step].schema),
    defaultValues: formData
  });

  const onNext = (data: any) => {
    setFormData(prev => ({ ...prev, ...data }));
    if (step < steps.length - 1) {
      setStep(step + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      createMutation.mutate(formData);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Stepper */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((s, i) => (
          <div
            key={s.id}
            className={cn(
              'flex-1 relative',
              i < step && 'text-green-600',
              i === step && 'text-blue-600 font-semibold',
              i > step && 'text-gray-400'
            )}
          >
            <div className="flex items-center">
              <div className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center',
                i <= step ? 'bg-blue-600 text-white' : 'bg-gray-200'
              )}>
                {i + 1}
              </div>
              <span className="ml-2 text-sm hidden md:block">{s.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={cn(
                'absolute top-4 left-full w-full h-0.5 -ml-4',
                i < step ? 'bg-green-600' : 'bg-gray-200'
              )} />
            )}
          </div>
        ))}
      </div>

      {/* Form */}
      <AnimatePresence mode="wait">
        <motion.form
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          onSubmit={handleSubmit(onNext)}
          className="space-y-6"
        >
          {/* Campos específicos do passo */}
          {steps[step].id === 'person' && (
            <>
              <input {...register('full_name')} placeholder="Nome Completo" />
              {errors.full_name && <p className="text-red-600 text-sm">{errors.full_name.message}</p>}
              
              <select {...register('gender')}>
                <option value="">Selecione...</option>
                <option value="masculino">Masculino</option>
                <option value="feminino">Feminino</option>
              </select>
              
              <input {...register('birthdate')} type="date" />
              {errors.birthdate && <p className="text-red-600 text-sm">{errors.birthdate.message}</p>}
            </>
          )}

          {/* Erros do dry-run */}
          {dryRunErrors.length > 0 && (
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-red-50 border border-red-200 rounded-lg p-4"
            >
              <h4 className="font-semibold text-red-800 mb-2">Erros encontrados:</h4>
              <ul className="list-disc list-inside text-sm text-red-700">
                {dryRunErrors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </motion.div>
          )}

          {/* Navegação */}
          <div className="flex justify-between pt-6">
            <button
              type="button"
              onClick={() => setStep(Math.max(0, step - 1))}
              disabled={step === 0}
              className="px-6 py-2 border rounded-lg disabled:opacity-50"
            >
              Voltar
+            </button>
+            
+            <button
+              type="submit"
+              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
+            >
+              {step < steps.length - 1 ? 'Próximo' : 'Finalizar'}
+            </button>
+          </div>
+        </motion.form>
+      </AnimatePresence>
+    </div>
+  );
+}
+```
+
+5️⃣ Estratégia de Busca de Dados  
+Configuração de Cache
+
+```ts
+// src/lib/queryClient.ts
+import { QueryClient } from '@tanstack/react-query';
+
+export const queryClient = new QueryClient({
+  defaultOptions: {
+    queries: {
+      staleTime: 60_000, // 1 min
+      gcTime: 300_000,   // 5 min
+      retry: 1,
+      refetchOnWindowFocus: false,
+      refetchOnReconnect: true
+    }
+  }
+});
+
+// Fábrica de chaves de cache
+export const keys = {
+  dashboard: (teamId?: string, seasonId?: string) => 
+    ['dashboard', 'summary', teamId, seasonId].filter(Boolean),
+  
+  athletes: (teamId: string, filters?: any) =>
+    ['athletes', teamId, filters],
+  
+  matches: (teamId: string, seasonId?: string) =>
+    ['matches', teamId, seasonId].filter(Boolean),
+  
+  reports: (type: string, teamId: string, days: number) =>
+    ['reports', type, teamId, days]
+};
+```
+
+Respeitando Headers de Cache do Backend
+
+```ts
+// src/lib/api.ts
+export async function fetchWithCache<T>(
+  url: string,
+  options?: RequestInit
+): Promise<{ data: T; cacheAge: number; ttl: number }> {
+  const response = await fetch(url, options);
+  
+  if (!response.ok) {
+    throw new Error(`API error: ${response.status}`);
+  }
+  
+  const data = await response.json();
+  const ttl = parseInt(response.headers.get('X-Cache-TTL') || '0');
+  const generatedAt = response.headers.get('X-Generated-At');
+  const cacheAge = generatedAt 
+    ? Date.now() - new Date(generatedAt).getTime()
+    : 0;
+  
+  return { data, cacheAge, ttl };
+}
+
+// Uso no React Query
+export function useDashboard(teamId?: string, seasonId?: string) {
+  return useQuery({
+    queryKey: keys.dashboard(teamId, seasonId),
+    queryFn: async () => {
+      const { data, ttl } = await fetchWithCache(
+        `/api/v1/dashboard/summary?team_id=${teamId}&season_id=${seasonId}`
+      );
+      return data;
+    },
+    staleTime: ({ state }) => {
+      // Use o TTL do backend se disponível
+      const ttl = state.data?.ttl || 60_000;
+      return ttl;
+    }
+  });
+}
+```
+
+6️⃣ Arquitetura do Dashboard em Tempo de Jogo  
+Entrada de Evento ao Vivo (Teclado-Primeiro)
+
+```tsx
+// src/features/game/LiveEventInput.tsx
+'use client';
+
+import { useEffect, useState } from 'react';
+import { useMutation, useQueryClient } from '@tanstack/react-query';
+import { toast } from 'sonner';
+
+const KEYBOARD_SHORTCUTS = {
+  '1': 'defense',
+  '2': 'transition_offense',
+  '3': 'attack_positional',
+  '4': 'transition_defense',
+  's': 'shot',
+  't': 'turnover',
+  'f': 'foul',
+  'g': 'goal'
+};
+
+interface LiveEventInputProps {
+  matchId: string;
+  teamId: string;
+}
+
+export function LiveEventInput({ matchId, teamId }: LiveEventInputProps) {
+  const [selectedPhase, setSelectedPhase] = useState<string>('');
+  const [eventQueue, setEventQueue] = useState<any[]>([]);
+  const queryClient = useQueryClient();
+
+  const createEventMutation = useMutation({
+    mutationFn: async (event: any) => {
+      const response = await fetch(
+        `/api/v1/teams/${teamId}/matches/${matchId}/events`,
+        {
+          method: 'POST',
+          headers: { 'Content-Type': 'application/json' },
+          body: JSON.stringify(event)
+        }
+      );
+      
+      if (!response.ok) throw new Error('Failed to create event');
+      return response.json();
+    },
+    onSuccess: () => {
+      queryClient.invalidateQueries({ queryKey: ['matches', teamId, matchId] });
+      toast.success('Evento registrado');
+    },
+    onError: (error) => {
+      toast.error('Erro ao registrar evento');
+      // Manter na fila para retry
+    },
+    retry: 3,
+    retryDelay: 1000
+  });
+
+  useEffect(() => {
+    const handleKeyPress = (e: KeyboardEvent) => {
+      const key = e.key.toLowerCase();
+      const action = KEYBOARD_SHORTCUTS[key as keyof typeof KEYBOARD_SHORTCUTS];
+      
+      if (action) {
+        e.preventDefault();
+        
+        if (['1', '2', '3', '4'].includes(key)) {
+          setSelectedPhase(action);
+          toast('Fase: ' + action, { duration: 1000 });
+        } else {
+          // Criar evento com fase selecionada
+          const event = {
+            match_id: matchId,
+            phase_of_play: selectedPhase || 'attack_positional',
+            event_type: action,
+            timestamp: new Date().toISOString()
+          };
+          
+          // Atualização otimista
+          setEventQueue(prev => [...prev, event]);
+          createEventMutation.mutate(event);
+        }
+      }
+    };
+
+    window.addEventListener('keydown', handleKeyPress);
+    return () => window.removeEventListener('keydown', handleKeyPress);
+  }, [selectedPhase, matchId]);
+
+  return (
+    <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-900 rounded-lg shadow-2xl p-4 w-80">
+      <div className="flex items-center justify-between mb-4">
+        <h3 className="font-semibold">Entrada Rápida</h3>
+        <span className="text-xs text-gray-500">
+          {eventQueue.length} na fila
+        </span>
+      </div>
+
+      {/* Seletor de Fase */}
+      <div className="grid grid-cols-4 gap-2 mb-4">
+        {Object.entries(KEYBOARD_SHORTCUTS)
+          .filter(([k]) => ['1', '2', '3', '4'].includes(k))
+          .map(([key, phase]) => (
+            <button
+              key={key}
+              onClick={() => setSelectedPhase(phase)}
+              className={cn(
+                'p-2 rounded text-xs font-medium transition-all',
+                selectedPhase === phase
+                  ? 'bg-blue-600 text-white'
+                  : 'bg-gray-100 hover:bg-gray-200'
+              )}
+            >
+              {key}: {phase.slice(0, 4)}
+            </button>
+          ))}
+      </div>
+
+      {/* Botões de Evento */}
+      <div className="grid grid-cols-2 gap-2">
+        {Object.entries(KEYBOARD_SHORTCUTS)
+          .filter(([k]) => !['1', '2', '3', '4'].includes(k))
+          .map(([key, event]) => (
+            <button
+              key={key}
+              onClick={() => {
+                const eventData = {
+                  match_id: matchId,
+                  phase_of_play: selectedPhase || 'attack_positional',
+                  event_type: event,
+                  timestamp: new Date().toISOString()
+                };
+                setEventQueue(prev => [...prev, eventData]);
+                createEventMutation.mutate(eventData);
+              }}
+              className="p-3 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
+            >
+              <kbd className="font-mono">{key}</kbd> {event}
+            </button>
+          ))}
+      </div>
+
+      {/* Ajuda dos Atalhos */}
+      <details className="mt-4 text-xs text-gray-600">
+        <summary className="cursor-pointer">Atalhos</summary>
+        <ul className="mt-2 space-y-1">
+          {Object.entries(KEYBOARD_SHORTCUTS).map(([key, action]) => (
+            <li key={key}>
+              <kbd className="font-mono bg-gray-100 px-1 rounded">{key}</kbd> = {action}
+            </li>
+          ))}
+        </ul>
+      </details>
+    </div>
+  );
+}
+```
+
+7️⃣ Plano de Sprints (4 Sprints × 2 Semanas)
+
+- Sprint 1: Fundação + Intake  
+  - Tokens do design system (cores, tipografia, espaçamento)  
+  - Fluxo de auth (login, contexto, navegação por papel)  
+  - Wizard de intake (5 passos, dry-run, Idempotency-Key)  
+  - Integração com Cloudinary para fotos  
+  - Lista/perfil básico de atleta  
+
+- Sprint 2: Dashboard + Relatórios  
+  - Dashboard consumindo /dashboard/summary  
+  - Relatórios (frequência, minutos, carga) com paginação  
+  - Alertas (carga, retorno de lesão) em cards  
+  - Filtros de time/temporada  
+  - Conscientização de cache com badges de idade do dado  
+
+- Sprint 3: Treino + Wellness  
+  - CRUD de sessões de treino com janelas de edição R40  
+  - Marcação de presença com checagem de elegibilidade  
+  - Formulários de wellness pré/pós (sliders, presets)  
+  - Rastreamento de adesão ao wellness  
+  - Visão mobile "Hoje" do atleta  
+
+- Sprint 4: Jogos + Scouting  
+  - Construtor de roster de jogo (cap 16, elegibilidade)  
+  - Presença no jogo (minutos, titular/reserva)  
+  - Entrada de eventos ao vivo (atalhos de teclado)  
+  - Mapa de quadra para rastrear arremessos  
+  - Exportação PDF para relatórios de atleta/time  
+
+8️⃣ Resumo das Recomendações-Chave
+
+Melhorias de Backend (Ordem de Prioridade)
+
+- Redis Cache → Compartilhado entre instâncias, cache warming  
+- WebSocket Live Events → Atualizações em tempo real durante jogos  
+- Paginação por Cursor → Para listas >10k linhas  
+- Criação de Roster em Lote → Um único POST para 16 atletas  
+- Agregação no Servidor → /reports/export/{type} para PDFs  
+- Limiares de ACWR Configuráveis → Por configuração da organização  
+
+Arquitetura de Frontend (Confirmada)
+
+✅ Mantenha sua stack — ela é perfeita para este domínio
+
+Padrões Críticos:
+
+- TanStack Query respeitando headers de cache
+- Entradas de tempo de jogo com teclado primeiro
+- Atualizações otimistas com rollback
+- Fila offline de eventos com retry
+- Sistema de badges State + Flags
+- Componentes de mapa de quadra/gol para dados espaciais
+- Intake passo a passo com autosave
+- Experiência mobile-first para atletas
+
+Prioridades do Design System:
+
+- Tokens de cor para estados/flags/níveis de carga
+- Componentes de badge para status de atleta
+- Primitivos de mapa de quadra para scouting
+- Layouts em cards para dashboard/relatórios
+- Dark mode para uso à beira da quadra
+
+🎯 Avaliação Final
+
+Seu backend está pronto para produção com pequenas oportunidades de otimização. O frontend tem uma oportunidade enorme de diferenciar o HB Track no mercado de tecnologia esportiva por:
+
+- Velocidade — Atalhos de teclado, UI otimista, cache inteligente
+- Clareza — Badges de estado, explicações de elegibilidade, mensagens de bloqueio
+- Engajamento — Streaks, lembretes de wellness, visão "Hoje" para atletas
+- Inteligência — Alertas de ACWR, distribuição de carga, prevenção de lesões
+
+Isso pode ser a melhor plataforma de handebol do mundo se você acertar a experiência em tempo de jogo e os fluxos mobile dos atletas. Foque o Sprint 4 em fazer o dashboard ao vivo/scouting parecer "roubar no jogo" — esse é seu fosso competitivo.
+
+Gostaria que eu detalhasse alguma área específica ou que eu ajudasse a implementar algum desses componentes?
