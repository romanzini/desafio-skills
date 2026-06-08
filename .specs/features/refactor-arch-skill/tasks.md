# Tasks — Skill: refactor-arch

## Contexto
Desafio: criar uma skill de refatoração arquitetural automatizada (MVC) que funcione em 3 projetos legados com stacks distintas.

## Estado atual do repositório
- `code-smells-project/` — Python/Flask, 6 arquivos planos, sem separação de camadas
- `ecommerce-api-legacy/` — Node.js/Express, 3 arquivos em `src/`, estrutura mínima
- `task-manager-api/` — Python/Flask, 17 arquivos, com models/routes/services/utils (parcialmente organizado)
- `.claude/skills/` — NÃO EXISTE (a criar)
- `reports/` — NÃO EXISTE (a criar)

---

## TASK-01 — Análise manual: code-smells-project
**O que:** Ler todos os arquivos Python do projeto e documentar >= 5 problemas com severidade, arquivo e linha.
**Onde:** `code-smells-project/` (app.py, controllers.py, models.py, database.py)
**Done when:** Lista documentada com >= 1 CRITICAL/HIGH, >= 2 MEDIUM, >= 2 LOW
**Status:** pending

## TASK-02 — Análise manual: ecommerce-api-legacy
**O que:** Ler todos os arquivos JS do projeto e documentar >= 5 problemas com severidade, arquivo e linha.
**Onde:** `ecommerce-api-legacy/src/` (app.js, AppManager.js, utils.js)
**Done when:** Lista documentada com >= 1 CRITICAL/HIGH, >= 2 MEDIUM, >= 2 LOW
**Status:** pending

## TASK-03 — Análise manual: task-manager-api
**O que:** Ler todos os arquivos Python do projeto (incluindo models/, routes/, services/, utils/) e documentar >= 5 problemas.
**Onde:** `task-manager-api/`
**Done when:** Lista documentada com >= 1 CRITICAL/HIGH, >= 2 MEDIUM, >= 2 LOW
**Status:** pending

## TASK-04 — Criar SKILL.md
**O que:** Escrever o prompt principal da skill com 3 fases sequenciais.
**Onde:** `code-smells-project/.claude/skills/refactor-arch/SKILL.md`
**Requisitos:**
- Fase 1: detectar stack, mapear arquitetura, imprimir resumo formatado
- Fase 2: auditar contra catálogo, gerar relatório, PAUSAR e pedir [y/n]
- Fase 3 (só após y): refatorar para MVC, validar boot + endpoints
**Done when:** Arquivo criado e referencia todos os 5 arquivos de referência
**Status:** pending

## TASK-05 — Criar arquivos de referência da skill (5 arquivos)
**O que:** Criar os 5 arquivos de conhecimento que a skill usa.
**Onde:** `code-smells-project/.claude/skills/refactor-arch/`

| Arquivo | Conteúdo obrigatório |
|---------|---------------------|
| `01-project-analysis.md` | Heurísticas de detecção de linguagem/framework/banco/arquitetura |
| `02-antipatterns-catalog.md` | >= 8 anti-patterns com severidade + sinais de detecção + APIs deprecated |
| `03-report-template.md` | Template do relatório de auditoria (Fase 2) |
| `04-mvc-guidelines.md` | Regras do padrão MVC alvo (Models, Views/Routes, Controllers) |
| `05-refactoring-playbook.md` | >= 8 padrões de transformação com exemplos antes/depois |

**Done when:** 5 arquivos criados, catálogo tem >= 8 anti-patterns, playbook tem >= 8 transformações
**Status:** pending

## TASK-06 — Executar skill no Projeto 1 (code-smells-project)
**O que:** Invocar `/refactor-arch` no projeto 1, validar 3 fases, salvar relatório.
**Onde:** `code-smells-project/`
**Steps:**
1. `cd code-smells-project && claude "/refactor-arch"`
2. Verificar Fase 1: stack e domínio detectados corretamente
3. Verificar Fase 2: >= 5 findings, >= 1 CRITICAL/HIGH
4. Confirmar Fase 3 com `y`
5. Verificar: estrutura MVC criada, app inicia, endpoints respondem
6. Salvar saída da Fase 2 em `reports/audit-project-1.md`
7. Commit do código refatorado
**Done when:** Checklist de validação completo + relatório salvo
**Status:** pending

## TASK-07 — Executar skill no Projeto 2 (ecommerce-api-legacy)
**O que:** Copiar skill, invocar `/refactor-arch`, validar 3 fases, salvar relatório.
**Onde:** `ecommerce-api-legacy/`
**Steps:**
1. Copiar `.claude/skills/refactor-arch/` para `ecommerce-api-legacy/`
2. `cd ecommerce-api-legacy && claude "/refactor-arch"`
3. Verificar 3 fases (Node.js/Express)
4. Salvar saída em `reports/audit-project-2.md`
5. Commit do código refatorado
**Done when:** Checklist de validação completo + relatório salvo
**Status:** pending

## TASK-08 — Executar skill no Projeto 3 (task-manager-api)
**O que:** Copiar skill, invocar `/refactor-arch`, validar 3 fases, salvar relatório.
**Onde:** `task-manager-api/`
**Steps:**
1. Copiar `.claude/skills/refactor-arch/` para `task-manager-api/`
2. `cd task-manager-api && claude "/refactor-arch"`
3. Verificar que detecta Python/Flask e domínio Task Manager
4. Verificar que encontra problemas mesmo em projeto parcialmente organizado
5. Salvar saída em `reports/audit-project-3.md`
6. Commit do código refatorado
**Done when:** Checklist de validação completo + relatório salvo
**Status:** pending

## TASK-09 — Atualizar README.md
**O que:** Adicionar 4 seções obrigatórias ao README.md existente.
**Onde:** `desafio-skills/README.md`
**Seções:**
- **Análise Manual:** problemas encontrados por projeto, severidade, justificativa
- **Construção da Skill:** decisões de design, anti-patterns escolhidos, agnoscticidade
- **Resultados:** resumo dos 3 relatórios, antes/depois, checklists preenchidos, logs
- **Como Executar:** pré-requisitos, comandos por projeto, validação
**Done when:** Arquivo atualizado com as 4 seções preenchidas
**Status:** pending

---

## Critérios de Aceite Globais

| Critério | Requisito |
|----------|-----------|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO — 3/3 projetos |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO — 3/3 projetos |
| Fase 2 inclui >= 1 CRITICAL ou HIGH | OBRIGATÓRIO — 3/3 projetos |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO — 3/3 projetos |
| Skill pausa antes da Fase 3 | OBRIGATÓRIO |
| Relatórios em `reports/` | OBRIGATÓRIO — 3 arquivos |
