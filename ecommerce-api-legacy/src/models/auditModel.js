const { getDb, run } = require('../database');

const AuditModel = {
    log: async (action) => {
        const db = getDb();
        await run(db,
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    },
};

module.exports = AuditModel;
