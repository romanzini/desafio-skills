# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

---

## Análise Manual

### Projeto 1 — code-smells-project (Python/Flask — API E-commerce)

| # | Arquivo:Linha | Problema | Severidade | Justificativa |
|---|---------------|----------|------------|---------------|
| 1 | `app.py:59-78` | RCE — endpoint `/admin/query` executa SQL arbitrário sem autenticação | CRITICAL | Qualquer pessoa pode destruir o banco ou exfiltrar dados com uma chamada HTTP |
| 2 | `models.py:28,48,58,68,92,110,140+` | SQL Injection em 10+ queries por concatenação de string | CRITICAL | Login, busca e CRUD vulneráveis a bypass e exfiltração de dados |
| 3 | `app.py:7` | SECRET_KEY hardcoded no código-fonte | CRITICAL | Histórico do Git expõe a chave; qualquer pessoa pode forjar sessões |
| 4 | `controllers.py:289` | SECRET_KEY exposta na resposta JSON do health check | HIGH | Endpoint público vaza credencial sem necessidade de acesso ao repo |
| 5 | `app.py:47-57` | `/admin/reset-db` sem autenticação | HIGH | Zera o banco de produção com uma requisição HTTP anônima |
| 6 | `models.py:171-233` | N+1 queries — 3 cursores aninhados por pedido | MEDIUM | Degrada performance quadraticamente com volume de dados |
| 7 | `database.py:4` | Estado global mutável para conexão de banco | MEDIUM | Race condition em ambientes multi-thread |
| 8 | `database.py:76-83` | Senhas de seed em plaintext no banco | LOW | Dump do arquivo `.db` expõe todas as senhas de teste |
| 9 | `controllers.py:208-210` | Notificações como `print()` | LOW | Sem observabilidade real; logs misturados com output do servidor |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API)

| # | Arquivo:Linha | Problema | Severidade | Justificativa |
|---|---------------|----------|------------|---------------|
| 1 | `src/utils.js:1-7` | Chave live de gateway de pagamento hardcoded (`pk_live_...`) | CRITICAL | Permite transações fraudulentas; comprometimento imediato em produção |
| 2 | `src/AppManager.js:4-139` | God Class — banco + rotas + pagamento + auditoria em 1 classe | CRITICAL | Nenhuma funcionalidade pode ser testada em isolamento; SRP violado completamente |
| 3 | `src/AppManager.js:43-78` | Lógica de checkout (pagamento, usuário, matrícula) dentro do route handler | HIGH | Não reutilizável, não testável; 5 níveis de callback hell |
| 4 | `src/utils.js:9-10` | Estado global mutável exportado (`globalCache`, `totalRevenue`) | HIGH | Dados compartilhados entre requisições causam inconsistências |
| 5 | `src/AppManager.js:131-137` | Deleção de usuário sem cascade — orfaniza matrículas e pagamentos | HIGH | Integridade referencial corrompida; o próprio código documenta o bug |
| 6 | `src/AppManager.js:80-129` | N+1 queries em 3 níveis no relatório financeiro | MEDIUM | 401 queries para 10 cursos × 20 alunos |
| 7 | `src/AppManager.js:43-78` | Callback hell — 5 níveis de aninhamento | MEDIUM | Ilegível e não maintível |
| 8 | `src/utils.js:17-23` | `badCrypto` — base64 usado como hash de senha | LOW | Senhas recuperáveis trivialmente |
| 9 | `src/AppManager.js:29-34` | Nomes de variáveis de uma letra (`u`, `e`, `p`, `cid`, `cc`) | LOW | Sem contexto; requer consulta constante à documentação |

### Projeto 3 — task-manager-api (Python/Flask — Task Manager, parcialmente organizado)

| # | Arquivo:Linha | Problema | Severidade | Justificativa |
|---|---------------|----------|------------|---------------|
| 1 | `models/user.py:29,32` | MD5 para hash de senha | CRITICAL | Vulnerável a rainbow tables; quebrado para uso criptográfico desde 2004 |
| 2 | `services/notification_service.py:10` | Senha de email hardcoded (`'senha123'`) | CRITICAL | Credencial de produção exposta no repositório |
| 3 | `routes/user_routes.py:210` | Login retorna token falso (`'fake-jwt-token-' + str(user.id)`) | CRITICAL | Autenticação inexistente; qualquer usuário pode se passar por outro |
| 4 | `models/user.py:21` | Hash de senha incluído em `to_dict()` e retornado pela API | HIGH | Expõe hashes para todos os clientes via GET /users |
| 5 | `routes/task_routes.py:42,52,67...` | `Query.get()` deprecated no SQLAlchemy 2.0 em 5+ locais | HIGH | Pode quebrar em futuras atualizações; gera warnings de deprecation |
| 6 | `routes/task_routes.py:12-63` | Cálculo de overdue + resolução de nomes no route handler | HIGH | N+1 queries oculto (User.query.get por task); lógica não reutilizável |
| 7 | `routes/report_routes.py:53-68` | N+1 queries por usuário no summary report | MEDIUM | N+1 queries com escala linear de usuários |
| 8 | `routes/task_routes.py:62,237` | `except:` bare que engole todos os erros silenciosamente | MEDIUM | Bugs críticos mascarados como "Erro interno" |
| 9 | `routes/task_routes.py:31-38,71-80,171-180,282-287` | Lógica de overdue duplicada em 6 lugares | LOW | Model já tem `is_overdue()` mas nenhuma rota o usa |
| 10 | `app.py:7` | Imports não utilizados (`os`, `sys`, `json`) | LOW | Poluição do namespace |

---

## Construção da Skill

### Decisões de design

A skill foi estruturada em **1 arquivo de prompt principal** (`SKILL.md`) + **5 arquivos de referência** especializados. Essa separação garante que o SKILL.md seja conciso (instrucional) enquanto os arquivos de referência funcionam como bases de conhecimento extensas.

**Por que 5 arquivos e não 1?** Arquivos menores e temáticos permitem que o agente carregue apenas o contexto relevante para cada fase, evitando que o prompt fique extenso demais. O SKILL.md referencia explicitamente qual arquivo ler em cada fase.

### Estrutura dos arquivos de referência

| Arquivo | Finalidade |
|---------|-----------|
| `01-project-analysis.md` | Heurísticas de detecção: tabelas de sinal → linguagem/framework/banco, detecção de arquitetura por presença de diretórios |
| `02-antipatterns-catalog.md` | 16 anti-patterns com exemplos de código DETECTAR em Python e Node.js, severidade e recomendação |
| `03-report-template.md` | Template de saída padronizado com regras de preenchimento (arquivo:linha exatos, exemplos bom/ruim) |
| `04-mvc-guidelines.md` | Estrutura MVC alvo em Python e Node.js com exemplos de código por camada |
| `05-refactoring-playbook.md` | 10 transformações antes/depois com código real (incluindo casos dos 3 projetos analisados) |

### Anti-patterns no catálogo e por que foram incluídos

- **SQL Injection (AP-01)** — presente em 2 dos 3 projetos; risco mais crítico detectado na análise
- **Credenciais Hardcoded (AP-02)** — presente em todos os 3 projetos; vetores de ataque imediatos
- **Endpoint Sem Autenticação (AP-03)** — `/admin/query` e `/admin/reset-db` no Projeto 1
- **God Class (AP-04)** — AppManager no Projeto 2; monólito mais extremo
- **Lógica no Controller (AP-05)** — padrão recorrente nos 3 projetos
- **Estado Global Mutável (AP-06)** — `globalCache` no Projeto 2; `db_connection` no Projeto 1
- **Exposição de Dados Sensíveis (AP-07)** — `password` no Projeto 3; `secret_key` no Projeto 1
- **Cascade Deletion Ignorada (AP-08)** — documentada explicitamente no Projeto 2
- **N+1 Queries (AP-09)** — presente nos 3 projetos com formas diferentes
- **Sem Error Handling Centralizado (AP-10)** — padrão inconsistente nos 3 projetos
- **Callback Hell (AP-11)** — específico do Projeto 2 (Node.js async)
- **APIs Deprecated (AP-12)** — `Query.get()` no Projeto 3; incluído por requisito do desafio
- **Código Duplicado (AP-13)** — lógica de overdue em 6 lugares no Projeto 3
- **Nomenclatura Ruim (AP-14)** — variáveis de uma letra no Projeto 2
- **Imports Desnecessários (AP-15)** — Projeto 3
- **Criptografia Fraca (AP-16)** — MD5 no Projeto 3; `badCrypto` no Projeto 2

### Como a skill é agnóstica de tecnologia

1. **Detecção automática de stack** — `01-project-analysis.md` tem tabelas de heurísticas para Python, Node.js, Java, Go, Ruby, PHP. A skill determina a linguagem por extensão de arquivo e imports antes de aplicar qualquer julgamento.

2. **Catálogo bilíngue** — cada anti-pattern em `02-antipatterns-catalog.md` tem exemplos de detecção em Python E Node.js.

3. **Guidelines MVC adaptáveis** — `04-mvc-guidelines.md` define a estrutura MVC alvo para Python/Flask E Node.js/Express, com os convenções de cada ecossistema (`Blueprint` vs `Router`, `db.session` vs `db.run`).

4. **Instrução explícita no SKILL.md** — a Fase 3 instrui: *"Adapte o padrão MVC à linguagem e framework do projeto"*.

### Desafios encontrados e soluções

- **Projeto 2 usava callbacks aninhados**: o playbook inclui PT-06 com o padrão de conversão para async/await usando `util.promisify` como guia.
- **Projeto 3 já tinha estrutura parcial**: a Fase 3 do SKILL.md instrui a melhorar o que existe em vez de reconstruir do zero, mantendo models/ e routes/ existentes e adicionando controllers/.
- **SQLAlchemy 2.0 com APIs deprecated**: AP-12 do catálogo cobre especificamente `Query.get()` → `db.session.get()` com exemplo direto.

---

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|-------|----------|------|--------|-----|-------|
| code-smells-project | Python/Flask | 3 | 2 | 2 | 2 | 9 |
| ecommerce-api-legacy | Node.js/Express | 2 | 3 | 2 | 2 | 9 |
| task-manager-api | Python/Flask | 3 | 3 | 2 | 2 | 10 |

### Comparação antes/depois da estrutura

**Projeto 1 (code-smells-project):**
```
ANTES                          DEPOIS
code-smells-project/           code-smells-project/
├── app.py (88 linhas)         ├── config/settings.py
├── controllers.py (292 l.)    ├── models/
├── models.py (314 l.)         │   ├── produto_model.py
└── database.py (86 l.)        │   ├── usuario_model.py
                               │   └── pedido_model.py
                               ├── controllers/
                               │   ├── produto_controller.py
                               │   ├── usuario_controller.py
                               │   ├── pedido_controller.py
                               │   ├── relatorio_controller.py
                               │   └── health_controller.py
                               ├── routes/api_routes.py
                               ├── middlewares/error_handler.py
                               ├── database.py
                               └── app.py (composition root)
```

**Projeto 2 (ecommerce-api-legacy):**
```
ANTES                          DEPOIS
src/                           src/
├── app.js (14 linhas)         ├── config/settings.js
├── AppManager.js (141 l.)     ├── models/
└── utils.js (25 l.)           │   ├── userModel.js
                               │   ├── courseModel.js
                               │   ├── enrollmentModel.js
                               │   ├── paymentModel.js
                               │   └── auditModel.js
                               ├── services/checkoutService.js
                               ├── controllers/
                               │   ├── checkoutController.js
                               │   ├── reportController.js
                               │   └── userController.js
                               ├── routes/index.js
                               ├── middlewares/errorHandler.js
                               ├── database.js
                               └── app.js (composition root)
```

**Projeto 3 (task-manager-api):**
```
ANTES                          DEPOIS
├── app.py                     ├── config/settings.py (NOVO)
├── models/ (ok)               ├── models/
│   ├── user.py (MD5)          │   ├── user.py (werkzeug PBKDF2)
│   └── ...                    │   └── ... (sem alteração)
├── routes/ (lógica pesada)    ├── controllers/ (NOVO)
│   ├── task_routes.py         │   ├── task_controller.py
│   ├── user_routes.py         │   ├── user_controller.py
│   └── report_routes.py       │   └── report_controller.py
├── services/                  ├── routes/ (thin wrappers)
│   └── notification_service   │   ├── task_routes.py
│       (senha hardcoded)       │   ├── user_routes.py
└── ...                        │   └── report_routes.py
                               └── services/notification_service.py
                                   (credenciais via os.getenv)
```

### Checklist de validação — todos os projetos

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|----------|-----------|-----------|-----------|
| Linguagem detectada corretamente | ✓ Python | ✓ Node.js | ✓ Python |
| Framework detectado corretamente | ✓ Flask 3.1.1 | ✓ Express 4.18.2 | ✓ Flask 3.0.0 + SQLAlchemy |
| Domínio da aplicação descrito | ✓ E-commerce API | ✓ LMS com checkout | ✓ Task Manager API |
| Número de arquivos condiz | ✓ 4 arquivos | ✓ 3 arquivos | ✓ 10 arquivos |
| Relatório segue o template | ✓ | ✓ | ✓ |
| Cada finding tem arquivo e linha | ✓ | ✓ | ✓ |
| Findings ordenados por severidade | ✓ | ✓ | ✓ |
| Mínimo de 5 findings | ✓ 9 | ✓ 9 | ✓ 10 |
| Inclui >= 1 CRITICAL ou HIGH | ✓ 5 | ✓ 5 | ✓ 6 |
| Skill pausa antes da Fase 3 | ✓ | ✓ | ✓ |
| Estrutura de diretórios MVC | ✓ | ✓ | ✓ |
| Config extraída (sem hardcoded) | ✓ | ✓ | ✓ |
| Models criados com queries seguras | ✓ | ✓ | ✓ |
| Controllers concentram o fluxo | ✓ | ✓ | ✓ |
| Routes são thin wrappers | ✓ | ✓ | ✓ |
| Error handling centralizado | ✓ | ✓ | ✓ (via Flask handlers) |
| Entry point limpo | ✓ | ✓ | ✓ |
| Aplicação inicia sem erros | ✓ 18 rotas | ✓ módulos OK | ✓ 23 rotas |
| Endpoints originais respondem | ✓ | ✓ | ✓ |

### Validação de boot das aplicações

**Projeto 1:**
```
$ python3 verify_app.py
APP OK
Routes: 18
  /
  /health
  /login
  /pedidos
  /produtos
  /produtos/busca
  /relatorios/vendas
  /usuarios
  ...
```

**Projeto 2:**
```
$ node verify_app.js
Routes module loaded OK
DB module loaded OK
NODE APP IMPORTS OK
```

**Projeto 3:**
```
$ python3 verify_app.py
APP OK
Routes: 23
  /
  /categories
  /health
  /login
  /reports/summary
  /tasks
  /tasks/search
  /tasks/stats
  /users
  ...
```

### Observações sobre comportamento em stacks diferentes

- **Python (raw SQLite) vs Python (SQLAlchemy)**: o Projeto 1 usa sqlite3 direto — as correções de SQL Injection foram diretas (trocar concatenação por `?`). O Projeto 3 usa SQLAlchemy ORM — o problema era com `Query.get()` deprecated e N+1 via lazy loading.

- **Node.js callbacks vs Python sync**: A maior adaptação foi no Projeto 2, onde o callback hell de 5 níveis foi substituído por async/await com Promise wrappers para sqlite3.

- **Projeto parcialmente organizado (Projeto 3)**: a skill reconheceu que models/ e services/ já existiam e os preservou, adicionando apenas `controllers/` e `config/` em vez de reconstruir do zero.

---

## Como Executar

### Pré-requisitos

- **OpenCode** (ou Claude Code) instalado e configurado
- **Python 3.10+** e `pip` (ou `python3 -m pip`) para os projetos Python
- **Node.js 18+** e `npm` para o projeto Node.js

### Projeto 1 — code-smells-project (Python/Flask)

```bash
cd code-smells-project

# Instalar dependências
pip install flask flask-cors

# Executar a skill
claude "/refactor-arch"

# Validar que a aplicação inicia
python3 app.py
# ou: python3 verify_app.py
```

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

```bash
cd ecommerce-api-legacy

# Instalar dependências
npm install

# Executar a skill
claude "/refactor-arch"

# Validar que a aplicação inicia
node src/app.js
# ou: node verify_app.js
```

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

```bash
cd task-manager-api

# Instalar dependências
pip install flask flask-sqlalchemy flask-cors

# Executar a skill
claude "/refactor-arch"

# Validar que a aplicação inicia
python3 app.py
# ou: python3 verify_app.py
```

### Como validar que a refatoração funcionou

Para cada projeto, após a Fase 3:

1. **Boot sem erros** — a aplicação inicia sem traceback
2. **Rotas registradas** — rodar `verify_app.py` / `verify_app.js` mostra todas as rotas esperadas
3. **Estrutura MVC** — verificar que `models/`, `controllers/`, `routes/` existem e têm responsabilidades corretas
4. **Sem secrets hardcoded** — buscar por `SECRET_KEY =`, `password =` literais no código
5. **Queries parametrizadas** — buscar por concatenação de string em queries SQL

---

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.