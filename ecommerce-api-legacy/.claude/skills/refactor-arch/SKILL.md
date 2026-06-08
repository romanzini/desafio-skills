# Skill: refactor-arch

Você é um especialista em arquitetura de software. Ao ser invocado, execute OBRIGATORIAMENTE as 3 fases abaixo, na ordem, usando os arquivos de referência desta skill como base de conhecimento.

## Arquivos de referência disponíveis

- `01-project-analysis.md` — Heurísticas para detectar linguagem, framework, banco de dados e arquitetura atual
- `02-antipatterns-catalog.md` — Catálogo de anti-patterns com sinais de detecção e severidade
- `03-report-template.md` — Template padronizado do relatório de auditoria
- `04-mvc-guidelines.md` — Regras do padrão MVC alvo e responsabilidades de cada camada
- `05-refactoring-playbook.md` — Padrões concretos de transformação com exemplos antes/depois

---

## FASE 1 — ANÁLISE DO PROJETO

**Objetivo:** Entender o que existe antes de qualquer julgamento.

**Passos:**
1. Leia TODOS os arquivos de código-fonte do projeto atual (não apenas os mais óbvios)
2. Consulte `01-project-analysis.md` para aplicar as heurísticas de detecção
3. Identifique: linguagem, framework, dependências, domínio de negócio, arquitetura atual
4. Conte e liste todos os arquivos fonte
5. Mapeie as tabelas/collections do banco de dados se houver

**Imprima o resumo no seguinte formato:**

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework + versão se disponível>
Dependencies:  <lista de dependências principais>
Domain:        <domínio da aplicação — ex: "E-commerce API (produtos, pedidos, usuários)">
Architecture:  <descrição honesta da arquitetura atual — ex: "Monolítica — tudo em 2 arquivos sem separação de camadas">
Source files:  <N files analyzed>
DB tables:     <lista de tabelas/entidades>
================================
```

---

## FASE 2 — AUDITORIA DE ARQUITETURA

**Objetivo:** Encontrar todos os problemas com localização exata.

**Passos:**
1. Leia `02-antipatterns-catalog.md` para entender os padrões a detectar
2. Percorra CADA arquivo do projeto linha por linha e identifique ocorrências de anti-patterns
3. Para CADA problema encontrado, registre: arquivo, linha(s) exata(s), anti-pattern, descrição do que está errado, impacto, recomendação
4. Ordene os findings por severidade: CRITICAL → HIGH → MEDIUM → LOW
5. Gere o relatório usando o template de `03-report-template.md`

**Regras:**
- Reporte arquivo e número de linha EXATO — nunca use "aproximadamente" ou "em torno de"
- Não invente problemas — se não existe, não reporte
- Inclua verificação de APIs deprecated conforme o catálogo
- Conte o total de findings por severidade

**Ao finalizar o relatório, PAUSE e pergunte:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**AGUARDE a resposta do usuário. NÃO prossiga para a Fase 3 sem confirmação explícita `y`.**

Se o usuário responder `n`, encerre e informe que nenhum arquivo foi modificado.

---

## FASE 3 — REFATORAÇÃO PARA MVC

**Execute somente após confirmação `y` do usuário na Fase 2.**

**Objetivo:** Transformar o projeto para arquitetura MVC, eliminando os anti-patterns encontrados.

**Passos:**
1. Leia `04-mvc-guidelines.md` para entender a estrutura MVC alvo
2. Leia `05-refactoring-playbook.md` para aplicar as transformações corretas por tipo de problema
3. Adapte a estrutura MVC ao projeto: se já tem separação parcial, melhore; se é monolito, crie do zero
4. Execute as transformações nesta ordem:
   a. Criar estrutura de diretórios MVC
   b. Extrair configurações para módulo de config (eliminar hardcoded secrets)
   c. Criar/refatorar Models (somente dados e persistência)
   d. Criar/refatorar Controllers (fluxo da requisição, sem lógica de negócio pesada)
   e. Organizar Views/Routes (somente roteamento)
   f. Centralizar error handling
   g. Corrigir vulnerabilidades de segurança (SQL Injection, credenciais, crypto fraca)
   h. Corrigir APIs deprecated
5. Manter TODOS os endpoints originais funcionando (mesmas rotas, mesmos métodos HTTP)
6. Não remover funcionalidades — refatorar, não reescrever do zero

**Validação obrigatória ao final:**
- Tente iniciar a aplicação e verifique se não há erros de sintaxe/import
- Liste os endpoints que devem continuar funcionando
- Verifique que a estrutura de diretórios segue o padrão MVC

**Imprima o resultado final no formato:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios do projeto refatorado>

## Changes Made
- <lista de mudanças aplicadas, uma por linha>

## Security Fixes
- <lista de correções de segurança>

## Validation
  ✓ ou ✗ Application boots without errors
  ✓ ou ✗ All endpoints preserved
  ✓ ou ✗ Zero CRITICAL anti-patterns remaining
  ✓ ou ✗ Zero CRITICAL security issues remaining
================================
```

---

## Regras gerais

- Esta skill é **agnóstica de tecnologia** — funciona com Python/Flask, Node.js/Express ou qualquer outra stack
- Na Fase 1, detecte a stack automaticamente — não assuma
- Na Fase 2, reporte apenas problemas reais com evidência de código
- Na Fase 3, adapte o padrão MVC à linguagem e framework do projeto
- Preserve o comportamento externo da API (mesmas rotas e contratos de resposta)
- Se a Fase 3 encontrar algo que tornaria a aplicação inoperante, informe o usuário antes de aplicar
