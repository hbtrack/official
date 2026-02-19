# HB TRACK KANBAN
Como Estruturar a Atualização do Kanban **HB track**
Para identificar o que já foi feito e o que falta fazer, siga este roteiro:

**Leia as Instruções**: 
Analise a lista todas as tarefas, funcionalidades, correções ou requisitos mencionados.
**Classifique cada Item**: Para cada item da lista, classifique-o em uma das duas categorias.
 DB/BK/FR-[XXX]-000: Exemplo de nome de tarefa/funcionalidade/correção/requisito, onde: 
 **DB** = Database, **BK** = Backend, **FR** = Frontend, **XXX** = número sequencial.
 **XXX** = Identificador único do módulo para cada tarefa 
 **000** = Número sequencial da tarefa dentro do módulo
**CONCLUÍDO**: Itens que já foram implementados, testados e entregues no sistema.
**PENDENTE**: Itens que ainda não foram iniciados, estão em andamento ou não foram entregues.


## Mapeie para o Kanban

* Identificação dos itens [CONCLUÍDOS], [PENDENTES] e **EM ANDAMENTO**: mova-os para a coluna correspondente. 
* Para cada um desses cards, anexe as evidências obtidas nos **TESTES** para formalizar a entrega.
* Para os itens [PENDENTES]: Verifique se já existe um card para eles no seu Kanban.
* Se não existir, crie um novo card na coluna **BACKLOG** ou **A FAZER (TO DO)**.
* Se já existir, garanta que ele está na coluna correta (ex: **A FAZER (TO DO)**, **EM ANDAMENTO**).



# HB TRACK EXECUTOR - DIRETRIZES DE IMPLEMENTAÇÃO


BACKLOG | A FAZER (TO DO) | EM ANDAMENTO | CONCLUÍDO
--- | --- | --- | ---   


# MODULO AUTH HB TRACK

Toda tarefa deve seguir o formato de identificação DB/BK/FR-[XXX]-000 e ser classificada como [CONCLUÍDO], [PENDENTE] ou **EM ANDAMENTO**. As evidências dos testes realizados para validar a funcionalidade de cada tarefa devem ser anexadas para formalizar a entrega.

Exemlo de tarefa: 

* DB-AUTH-001 - Implementar tabela de usuários no banco de dados.**EM ANDAMENTO**
* BK-AUTH-001 - Criar API de autenticação para login de usuários.**A FAZER (TO DO)**
* FR-AUTH-001 - Desenvolver interface de login para os usuários.**CONCLUÍDO** -`Anexar evidências dos testes realizados para validar a funcionalidade de login`


[STATUS]