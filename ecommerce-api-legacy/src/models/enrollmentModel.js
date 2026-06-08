const { getDb, run, all } = require('../database');

const EnrollmentModel = {
    create: async (userId, courseId) => {
        const db = getDb();
        const result = await run(db,
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId]
        );
        return result.lastID;
    },

    findByCourse: async (courseId) => {
        const db = getDb();
        return all(db, "SELECT * FROM enrollments WHERE course_id = ?", [courseId]);
    },
};

module.exports = EnrollmentModel;
