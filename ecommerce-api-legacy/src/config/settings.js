module.exports = {
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    secretKey: process.env.SECRET_KEY || 'dev-key-CHANGE-IN-PRODUCTION',
};
