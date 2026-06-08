const { getDb, run, get } = require('../database');

const PaymentModel = {
    create: async (enrollmentId, amount, status) => {
        const db = getDb();
        const result = await run(db,
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status]
        );
        return result.lastID;
    },

    findByEnrollment: async (enrollmentId) => {
        const db = getDb();
        return get(db, "SELECT amount, status FROM payments WHERE enrollment_id = ?", [enrollmentId]);
    },
};

module.exports = PaymentModel;
