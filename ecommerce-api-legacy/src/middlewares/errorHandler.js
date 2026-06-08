const errorHandler = (err, req, res, next) => {
    const status = err.status || 500;
    const message = err.message || 'Erro interno do servidor';
    console.error(`[ERROR] ${status} - ${message}`);
    res.status(status).json({ error: message });
};

module.exports = errorHandler;
