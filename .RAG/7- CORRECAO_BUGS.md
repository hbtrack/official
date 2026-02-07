Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Auditar código em busca de bugs sistêmicos e corrigi-los.

CATEGORIAS DE BUGS A PROCURAR:

SSR/Cookies

serverApiClient sem cookies corretos
Componentes Client tentando ler cookies diretamente
Cache incorreto (falta no-store em mutações)
Redirects e Loops

Redirects que causam loops infinitos
middleware com regras conflitantes
callbackUrl não preservado
Tratamento de Erros

try/catch vazio ou genérico demais
Erros 500 que deviam ser 404
NotFoundError não capturado
Erros não logados
RBAC

Permissões checadas só no frontend
Falta validação de role no backend
401 quando deveria ser 403
Validações

Validação só no frontend
Falta tratamento de duplicados (UniqueViolation)
Inputs não sanitizados
Race Conditions

router.refresh não aguardado
setState em componente unmounted
Requests concorrentes sem lock
PARA CADA BUG ENCONTRADO:

Localize o arquivo e linha
Explique o problema e impacto
Proponha correção
Implemente correção
Verifique que testes passam
ENTREGUE:

Lista de bugs encontrados (severidade: crítico/alto/médio)
Arquivos modificados + diff
Resultado dos testes após correções