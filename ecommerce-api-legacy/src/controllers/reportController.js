const { getDb, all, get } = require('../database');

const reportController = {
    financialReport: async (req, res, next) => {
        try {
            const db = getDb();

            // Single JOIN query replaces the original N+1 nested callbacks
            const rows = await all(db, `
                SELECT
                    c.id AS course_id,
                    c.title AS course_title,
                    u.name AS student_name,
                    p.amount,
                    p.status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
            `);

            const reportMap = {};
            for (const row of rows) {
                if (!reportMap[row.course_id]) {
                    reportMap[row.course_id] = {
                        course: row.course_title,
                        revenue: 0,
                        students: [],
                    };
                }
                if (row.student_name) {
                    reportMap[row.course_id].students.push({
                        student: row.student_name,
                        paid: row.status === 'PAID' ? row.amount : 0,
                    });
                    if (row.status === 'PAID') {
                        reportMap[row.course_id].revenue += row.amount;
                    }
                }
            }

            return res.status(200).json(Object.values(reportMap));
        } catch (err) {
            next(err);
        }
    },
};

module.exports = reportController;
