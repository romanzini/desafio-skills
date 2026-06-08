================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js v18 + Express 4.18.2
Files:   3 analyzed (src/app.js, src/AppManager.js, src/utils.js) | ~170 lines of code

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Credenciais de Producao Hardcoded no Codigo-Fonte
File: src/utils.js:1-7
Description: O objeto `config` exportado contem credenciais de producao em texto literal: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (chave live real de gateway de pagamento), `smtpUser: "no-reply@fullcycle.com.br"`. Essas credenciais sao publicadas em qualquer commit ao repositorio.
Impact: Exposicao da chave de producao do gateway de pagamento permite transacoes fraudulentas. Comprometimento da conta de email e banco de dados.
Recommendation: Mover todas as credenciais para variaveis de ambiente via process.env. Criar .env.example com placeholders. Revogar e rotacionar imediatamente as chaves expostas.

### [CRITICAL] God Class — AppManager Concentra Banco, Rotas, Pagamento e Auditoria
File: src/AppManager.js:4-139
Description: A classe AppManager inicializa o schema do banco (initDb), registra todas as rotas (setupRoutes), processa pagamentos (linha 46), cria usuarios (linha 68-72), insere matriculas (linha 50-63), registra logs de auditoria (linha 57) e gera relatorio financeiro (linhas 80-129). Seis responsabilidades distintas em uma unica classe.
Impact: Impossivel testar qualquer funcionalidade em isolamento. Qualquer mudanca em uma responsabilidade pode quebrar outra. Viola Single Responsibility Principle completamente.
Recommendation: Separar em Models (UserModel, CourseModel, EnrollmentModel, PaymentModel), Services (CheckoutService), Controllers e Routes independentes.

### [HIGH] Logica de Negocio Dentro do Route Handler (Callback Hell 5 niveis)
File: src/AppManager.js:28-78
Description: O handler de POST /api/checkout tem 5 niveis de callbacks aninhados realizando: validacao de curso (db.get), busca de usuario (db.get), criacao de usuario (db.run), insercao de matricula (db.run), insercao de pagamento (db.run), log de auditoria (db.run) — tudo dentro do callback de rota. O processamento de pagamento `cc.startsWith("4")` e a logica de negocios estao diretamente no handler.
Impact: Codigo ilegivel e impossivel de testar. Logica de pagamento acoplada a camada HTTP. Erro em qualquer nivel silencia os demais.
Recommendation: Extrair para CheckoutService com async/await. Separar logica de pagamento, criacao de usuario e matricula em metodos de servico/model.

### [HIGH] Estado Global Mutavel Exportado e Compartilhado
File: src/utils.js:9-10
Description: `let globalCache = {}` e `let totalRevenue = 0` sao declarados como variaveis mutaveis de modulo e exportados: `module.exports = { globalCache, totalRevenue }`. A funcao `logAndCache` modifica `globalCache` em runtime.
Impact: Estado compartilhado entre requisicoes. Em producao com multiplas instancias ou workers, o cache e inconsistente. `totalRevenue` nunca e atualizado mas e exportado como se fosse confiavel.
Recommendation: Remover estado global. Usar banco de dados ou cache dedicado (Redis) para dados compartilhados. Substituir globalCache por logging estruturado.

### [HIGH] Cascade Deletion Ignorada — Banco com Dados Orfaos
File: src/AppManager.js:131-137
Description: O endpoint DELETE /api/users/:id deleta o usuario mas deixa enrollments e payments relacionados no banco. O proprio comentario no codigo documenta o problema: `res.send("Usuario deletado, mas as matriculas e pagamentos ficaram sujos no banco.")`.
Impact: Integridade referencial corrompida. Queries ao relatorio financeiro retornam dados de usuarios inexistentes. Dados orfaos acumulam indefinidamente.
Recommendation: Deletar payments e enrollments do usuario antes de deletar o usuario, ou configurar FOREIGN KEY ... ON DELETE CASCADE.

### [MEDIUM] N+1 Queries em 3 Niveis no Relatorio Financeiro
File: src/AppManager.js:80-129
Description: O relatorio financeiro executa: 1 query para todos os cursos, depois para CADA curso faz query de enrollments, depois para CADA enrollment faz query de usuario E query de pagamento. Com C cursos, E enrollments por curso: 1 + C + C*E + C*E queries.
Impact: Com 10 cursos e 20 alunos cada = 401 queries por requisicao. Timeout em producao.
Recommendation: Usar JOIN unico: `SELECT c.title, u.name, p.amount, p.status FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id LEFT JOIN users u ON u.id = e.user_id LEFT JOIN payments p ON p.enrollment_id = e.id`.

### [MEDIUM] Funcao de Criptografia Insegura (badCrypto)
File: src/utils.js:17-23
Description: A funcao `badCrypto` usa Base64 (codificacao, nao hash) em loop de 10.000 iteracoes e retorna os primeiros 10 caracteres. Base64 e reversivel e nao e uma funcao de hash. O nome da propria funcao documenta que e insegura.
Impact: Senhas armazenadas com este "hash" sao facilmente reversidas. Espaco de saida de 10 chars em base64 e extremamente pequeno para brute force.
Recommendation: Usar `crypto.scryptSync(password, salt, 64)` (built-in Node.js) ou biblioteca `bcrypt`. Nunca usar base64 como hash de senha.

### [LOW] Nomes de Variaveis de Uma Letra no Handler de Checkout
File: src/AppManager.js:29-34
Description: Parametros do body extraidos com nomes sem contexto: `let u = req.body.usr`, `let e = req.body.eml`, `let p = req.body.pwd`, `let cid = req.body.c_id`, `let cc = req.body.card`.
Impact: Codigo ilegivel. Necessario consultar documentacao para entender o que cada variavel representa.
Recommendation: Usar nomes descritivos: `const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body`.

### [LOW] Ausencia de Middleware de Error Handling Centralizado
File: src/AppManager.js (arquivo inteiro)
Description: Erros retornam strings simples como `res.status(500).send("Erro DB")`, `res.status(404).send("Curso nao encontrado")`. Sem formato JSON consistente. Sem middleware `app.use((err, req, res, next) => {...})`.
Impact: Respostas de erro inconsistentes (algumas string, algumas JSON). Impossivel monitorar erros programaticamente.
Recommendation: Implementar middleware de error handler centralizado com formato JSON uniforme. Usar `next(err)` para propagar erros.

================================
Total: 9 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
ecommerce-api-legacy/
├── .claude/skills/refactor-arch/   (skill copiada)
├── src/
│   ├── config/
│   │   └── settings.js              (NOVO - process.env para todas as credenciais)
│   ├── models/
│   │   ├── userModel.js             (NOVO - CRUD + cascade delete)
│   │   ├── courseModel.js           (NOVO)
│   │   ├── enrollmentModel.js       (NOVO)
│   │   ├── paymentModel.js          (NOVO)
│   │   └── auditModel.js            (NOVO)
│   ├── services/
│   │   └── checkoutService.js       (NOVO - logica de checkout extraida)
│   ├── controllers/
│   │   ├── checkoutController.js    (NOVO - apenas orquestacao HTTP)
│   │   ├── reportController.js      (NOVO - JOIN unico em vez de N+1)
│   │   └── userController.js        (NOVO - cascade delete correto)
│   ├── routes/
│   │   └── index.js                 (NOVO - roteamento puro)
│   ├── middlewares/
│   │   └── errorHandler.js          (NOVO - error handling centralizado)
│   ├── database.js                  (NOVO - promise wrappers + seed com hash)
│   └── app.js                       (ATUALIZADO - composition root)
├── .env.example                     (NOVO)
└── package.json

## Changes Made
- Credenciais movidas de utils.js para process.env via config/settings.js
- AppManager.js decomposto em 5 Models + 1 Service + 3 Controllers + Routes
- Callback hell de 5 niveis convertido para async/await com try/catch
- N+1 queries substituidas por JOIN unico no relatorio financeiro
- Cascade deletion implementada corretamente em UserModel.deleteWithCascade()
- Error handling centralizado em middlewares/errorHandler.js
- Promise wrappers para sqlite3 em database.js

## Security Fixes
- CRITICAL Hardcoded credentials: todas as credenciais movidas para process.env
- HIGH Global mutable state: globalCache e totalRevenue removidos
- MEDIUM badCrypto: substituida por crypto.scryptSync() com salt aleatorio
- Seed data agora usa hash seguro para senhas

## Validation
  ✓ Application boots without errors
  ✓ All endpoints preserved (/api/checkout, /api/admin/financial-report, /api/users/:id)
  ✓ Zero CRITICAL anti-patterns remaining
  ✓ Zero CRITICAL security issues remaining
================================
