const express = require('express');
const { initDb } = require('./database');
const routes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');
const settings = require('./config/settings');

const app = express();
app.use(express.json());
app.use(routes);
app.use(errorHandler);

initDb().then(() => {
    app.listen(settings.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
    });
}).catch((err) => {
    console.error('Falha ao inicializar banco de dados:', err);
    process.exit(1);
});

module.exports = app;
