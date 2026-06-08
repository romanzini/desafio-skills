const { getDb, run, get, all, hashPassword, checkPassword } = require('../database');

const UserModel = {
    findByEmail: async (email) => {
        const db = getDb();
        return get(db, "SELECT id, name, email FROM users WHERE email = ?", [email]);
    },

    findById: async (id) => {
        const db = getDb();
        return get(db, "SELECT id, name, email FROM users WHERE id = ?", [id]);
    },

    create: async (name, email, hashedPassword) => {
        const db = getDb();
        const result = await run(db,
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, hashedPassword]
        );
        return result.lastID;
    },

    deleteWithCascade: async (userId) => {
        const db = getDb();
        const enrollments = await all(db, "SELECT id FROM enrollments WHERE user_id = ?", [userId]);
        for (const enr of enrollments) {
            await run(db, "DELETE FROM payments WHERE enrollment_id = ?", [enr.id]);
        }
        await run(db, "DELETE FROM enrollments WHERE user_id = ?", [userId]);
        const result = await run(db, "DELETE FROM users WHERE id = ?", [userId]);
        return result.changes > 0;
    },

    hashPassword,
    checkPassword,
};

module.exports = UserModel;
