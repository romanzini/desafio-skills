const { getDb, run, get, all } = require('../database');

const CourseModel = {
    findActiveById: async (id) => {
        const db = getDb();
        return get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    },

    findAll: async () => {
        const db = getDb();
        return all(db, "SELECT * FROM courses");
    },
};

module.exports = CourseModel;
