<!-- STATUS: NEEDS_REVIEW -->

PROJETO DE IMPLEMENTAÇÃO DO MODULO DE EQUIPES 


PAGINA DE EQUIPE /TEAMS

A Pagina inicial de 


<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Team Management Dashboard | HB Track</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script>
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    fontFamily: {
                        sans: ["Inter", "sans-serif"],
                        display: ["Manrope", "sans-serif"],
                        mono: ["JetBrains Mono", "monospace"],
                    },
                    fontSize: {
                        'title': ['22px', '1.2'],
                        'subtitle': ['15px', '1.4'],
                        'body': ['13px', '1.5'],
                        'meta': ['12px', '1.4'],
                        'badge': ['11px', '1'],
                    },
                    colors: {
                        slate: {
                            850: '#151b28',
                        },
                        hb: {
                            surface: '#ffffff',
                            background: '#f8fafc',
                            border: '#e2e8f0',
                            text: '#0f172a',
                            muted: '#64748b',
                            subtle: '#94a3b8',
                            active: '#f1f5f9',
                        }
                    }
                },
            },
        };
    </script>
<style type="text/tailwindcss">
        @layer base {
            body {
                @apply bg-hb-background text-hb-text antialiased selection:bg-slate-200 selection:text-black font-sans;
            }
            .dark body {
                @apply bg-[#0a0a0a] text-slate-200 selection:bg-slate-800 selection:text-white;
            }
        }.custom-scrollbar::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            @apply bg-slate-300 dark:bg-slate-700 rounded-sm;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            @apply bg-slate-400 dark:bg-slate-600;
        }
        .glass-panel {
            @apply bg-white dark:bg-[#111] border border-hb-border dark:border-slate-800;
        }
    </style>
</head>
<body class="flex h-screen overflow-hidden transition-colors duration-300">
<main class="flex-1 flex overflow-hidden relative bg-hb-surface dark:bg-[#0a0a0a]">
<div class="w-full lg:w-[520px] flex flex-col border-r border-hb-border dark:border-slate-800 z-10 bg-white dark:bg-[#0f0f0f]">
<div class="px-6 py-5 border-b border-hb-border dark:border-slate-800 flex-shrink-0">
<div class="flex items-center justify-between mb-5">
<h1 class="font-display font-medium text-title text-slate-900 dark:text-white tracking-tight">Equipes</h1>
<div class="flex items-center gap-2">
<button class="flex items-center gap-1.5 px-3 py-1.5 text-meta font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-black border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-sm transition-all shadow-sm">
<span class="material-symbols-outlined text-[16px]">tune</span>
                            Filtrar
                        </button>
<button class="flex items-center gap-1.5 px-3 py-1.5 text-meta font-medium text-white bg-slate-900 dark:bg-slate-100 dark:text-black border border-transparent rounded-sm hover:bg-slate-800 dark:hover:bg-slate-300 transition-all shadow-sm">
<span class="material-symbols-outlined text-[16px]">add</span>
                            Novo
                        </button>
</div>
</div>
<div class="relative group">
<span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400 group-focus-within:text-slate-600 dark:group-focus-within:text-slate-200 transition-colors">
<span class="material-symbols-outlined text-[18px]">search</span>
</span>
<input class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-sm py-2 pl-9 pr-4 text-[13px] text-slate-900 dark:text-white placeholder-slate-400 focus:ring-0 focus:border-slate-400 dark:focus:border-slate-600 transition-all shadow-sm" placeholder="Buscar por nome, ID ou categoria..." type="text"/>
</div>
</div>
<div class="grid grid-cols-12 gap-4 px-6 py-2 border-b border-hb-border dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/20 text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
<div class="col-span-6 pl-1">Identificação</div>
<div class="col-span-3 text-right">Categoria</div>
<div class="col-span-3 text-right pr-1">Estado</div>
</div>
<div class="flex-1 overflow-y-auto custom-scrollbar bg-white dark:bg-[#0f0f0f]">
<div class="divide-y divide-hb-border dark:divide-slate-800">
<div class="group grid grid-cols-12 gap-4 px-6 py-3.5 cursor-pointer bg-slate-50 dark:bg-slate-800/30 border-l-[3px] border-l-slate-900 dark:border-l-white transition-all">
<div class="col-span-6 flex flex-col justify-center pl-0.5">
<span class="text-body font-medium text-slate-900 dark:text-white">Cadete Masculino</span>
<span class="text-meta font-mono text-slate-400 mt-0.5">ID: 1767506541</span>
</div>
<div class="col-span-3 flex items-center justify-end">
<span class="px-2 py-0.5 rounded-sm text-badge font-medium bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 shadow-sm">
                                CAT-3
                            </span>
</div>
<div class="col-span-3 flex items-center justify-end gap-2 pr-0.5">
<span class="text-badge text-slate-500 dark:text-slate-400">Ativo</span>
<div class="h-1.5 w-1.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100 dark:ring-emerald-900/30"></div>
</div>
</div>
<div class="group grid grid-cols-12 gap-4 px-6 py-3.5 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/20 border-l-[3px] border-l-transparent transition-all">
<div class="col-span-6 flex flex-col justify-center pl-0.5">
<span class="text-body font-medium text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Equipe Teste Auth</span>
<span class="text-meta font-mono text-slate-400 mt-0.5 group-hover:text-slate-500 transition-colors">ID: 1767506527</span>
</div>
<div class="col-span-3 flex items-center justify-end">
<span class="text-badge text-slate-500 group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-300">CAT-1</span>
</div>
<div class="col-span-3 flex items-center justify-end gap-2 pr-0.5">
<span class="text-badge text-slate-400">Inativo</span>
<div class="h-1.5 w-1.5 rounded-full bg-slate-300 dark:bg-slate-700"></div>
</div>
</div>
<div class="group grid grid-cols-12 gap-4 px-6 py-3.5 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/20 border-l-[3px] border-l-transparent transition-all">
<div class="col-span-6 flex flex-col justify-center pl-0.5">
<span class="text-body font-medium text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Oponente Smoke Test</span>
<span class="text-meta font-mono text-slate-400 mt-0.5 group-hover:text-slate-500 transition-colors">ID: SMK-8842</span>
</div>
<div class="col-span-3 flex items-center justify-end">
<span class="text-badge text-slate-500 group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-300">CAT-1</span>
</div>
<div class="col-span-3 flex items-center justify-end gap-2 pr-0.5">
<span class="text-badge text-slate-400">Inativo</span>
<div class="h-1.5 w-1.5 rounded-full bg-slate-300 dark:bg-slate-700"></div>
</div>
</div>
<div class="group grid grid-cols-12 gap-4 px-6 py-3.5 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/20 border-l-[3px] border-l-transparent transition-all">
<div class="col-span-6 flex flex-col justify-center pl-0.5">
<span class="text-body font-medium text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Juvenil A</span>
<span class="text-meta font-mono text-slate-400 mt-0.5 group-hover:text-slate-500 transition-colors">ID: JUV-A-23</span>
</div>
<div class="col-span-3 flex items-center justify-end">
<span class="text-badge text-slate-500 group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-300">CAT-2</span>
</div>
<div class="col-span-3 flex items-center justify-end gap-2 pr-0.5">
<span class="text-badge text-slate-500 dark:text-slate-400">Ativo</span>
<div class="h-1.5 w-1.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100 dark:ring-emerald-900/30"></div>
</div>
</div>
<div class="group grid grid-cols-12 gap-4 px-6 py-3.5 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/20 border-l-[3px] border-l-transparent transition-all">
<div class="col-span-6 flex flex-col justify-center pl-0.5">
<span class="text-body font-medium text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Infantil B</span>
<span class="text-meta font-mono text-slate-400 mt-0.5 group-hover:text-slate-500 transition-colors">ID: INF-B-24</span>
</div>
<div class="col-span-3 flex items-center justify-end">
<span class="text-badge text-slate-500 group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-300">CAT-4</span>
</div>
<div class="col-span-3 flex items-center justify-end gap-2 pr-0.5">
<span class="text-badge text-slate-500 dark:text-slate-400">Ativo</span>
<div class="h-1.5 w-1.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100 dark:ring-emerald-900/30"></div>
</div>
</div>
</div>
<div class="p-4 text-center border-t border-hb-border dark:border-slate-800 bg-slate-50/30 dark:bg-black">
<button class="text-badge text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors font-medium flex items-center justify-center gap-2 mx-auto">
<span class="material-symbols-outlined text-[14px]">refresh</span>
                        Carregar mais
                    </button>
</div>
</div>
<div class="px-6 py-2.5 border-t border-hb-border dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 text-[10px] font-mono text-slate-400 flex justify-between items-center">
<span>Registros: 5 / 24</span>
<span class="flex items-center gap-1.5">
<span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    Sync: 14:02:45
                </span>
</div>
</div>
<div class="flex-1 bg-slate-50/50 dark:bg-[#050505] flex flex-col items-center justify-center p-12 transition-colors relative hidden lg:flex">
<div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: radial-gradient(#64748b 1px, transparent 1px); background-size: 24px 24px;"></div>
<div class="max-w-md w-full text-center relative z-10 p-8 rounded-lg border border-slate-200/50 dark:border-slate-800 bg-white/50 dark:bg-[#111]/50 backdrop-blur-sm">
<div class="h-14 w-14 mx-auto mb-6 text-slate-300 dark:text-slate-700 flex items-center justify-center bg-white dark:bg-slate-900 rounded-full border border-slate-100 dark:border-slate-800 shadow-sm">
<span class="material-symbols-outlined text-[28px] text-slate-400">splitscreen_left</span>
</div>
<h2 class="text-[16px] font-medium text-slate-900 dark:text-white mb-2">Detalhes da Equipe</h2>
<p class="text-slate-500 dark:text-slate-400 text-body leading-relaxed mb-8 max-w-xs mx-auto">
                    Selecione um registro na lista lateral para visualizar a ficha técnica, performance e configurações.
                </p>
<div class="flex items-center justify-center gap-3">
<button class="px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-xs font-medium rounded-sm hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm">
                        Documentação
                    </button>
<button class="px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-xs font-medium rounded-sm hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm">
                        Suporte
                    </button>
</div>
</div>
</div>
</main>
<div class="fixed bottom-5 right-5 z-50">
<button class="h-10 w-10 flex items-center justify-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 rounded-full shadow-md hover:text-slate-900 dark:hover:text-white transition-all" onclick="document.documentElement.classList.toggle('dark')">
<span class="material-symbols-outlined dark:hidden block text-[20px]">dark_mode</span>
<span class="material-symbols-outlined hidden dark:block text-[20px]">light_mode</span>
</button>
</div>

</body></html>