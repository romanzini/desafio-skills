# 03 — Template de Relatório de Auditoria

Use este template para gerar o output da Fase 2. Preencha todas as seções. Não omita campos.

---

## Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <Linguagem> + <Framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [CRITICAL] <Nome do Anti-Pattern>
File: <arquivo>:<linha-inicial>-<linha-final>
Description: <O que está errado, em 1-2 frases concretas>
Impact: <Qual o risco ou problema causado>
Recommendation: <O que deve ser feito para corrigir>

### [CRITICAL] <Nome do Anti-Pattern>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <Nome do Anti-Pattern>
File: <arquivo>:<linha-inicial>-<linha-final>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Nome do Anti-Pattern>
File: <arquivo>:<linha-inicial>-<linha-final>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <Nome do Anti-Pattern>
File: <arquivo>:<linha-inicial>-<linha-final>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================
```

---

## Regras de preenchimento

### Campo `File`
- Sempre incluir arquivo + número de linha exato
- Para spans longos: `arquivo.py:10-50`
- Para linha única: `arquivo.py:7`
- Para múltiplas ocorrências do mesmo anti-pattern: listar cada arquivo separadamente como um finding ou mencionar "também em: arquivo2.py:23, arquivo3.py:45"

### Campo `Description`
- Ser específico — incluir o trecho de código problemático quando possível
- Exemplo bom: `SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'`
- Exemplo ruim: `Credencial insegura encontrada`

### Campo `Impact`
- Descrever a consequência real, não apenas repetir o problema
- Exemplo bom: `Qualquer pessoa com acesso ao repositório obtém acesso à conta de pagamento em produção`
- Exemplo ruim: `Isso é inseguro`

### Campo `Recommendation`
- Ação concreta, não vaga
- Exemplo bom: `Mover para variável de ambiente PAYMENT_KEY e carregar com os.getenv('PAYMENT_KEY')`
- Exemplo ruim: `Use variáveis de ambiente`

### Ordenação dos findings
1. CRITICAL (todos)
2. HIGH (todos)
3. MEDIUM (todos)
4. LOW (todos)
- Dentro de cada severidade, ordenar por impacto (mais grave primeiro)

### Contagem de linhas de código
- Python: contar linhas não-vazias e não-comentadas em todos os arquivos `.py`
- Node.js: contar linhas não-vazias em todos os arquivos `.js`/`.ts`
- Usar `~` para indicar aproximação (ex: `~300 lines of code`)

---

## Exemplo preenchido

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~400 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:28
Description: Query SQL construída por concatenação de string: `"SELECT * FROM produtos WHERE id = " + str(id)`. Repete-se em 8+ locais no arquivo.
Impact: Permite leitura e modificação arbitrária de qualquer dado do banco. Vulnerabilidade exploitável remotamente.
Recommendation: Substituir por queries parametrizadas: `cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))`

### [CRITICAL] Hardcoded Credentials
File: app.py:7
Description: SECRET_KEY definida como literal string 'minha-chave-super-secreta-123' diretamente no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão.
Recommendation: Usar variável de ambiente: `app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-insecure")`

================================
Total: 9 findings
================================
```
