const CourseModel = require('../models/courseModel');
const UserModel = require('../models/userModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const AuditModel = require('../models/auditModel');

const PAYMENT_STATUS = {
    PAID: 'PAID',
    DENIED: 'DENIED',
};

/**
 * Simulates payment processing.
 * Cards starting with "4" are approved; all others are denied.
 */
function processPayment(cardNumber) {
    return cardNumber.startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
}

const CheckoutService = {
    checkout: async ({ userName, email, password, courseId, cardNumber }) => {
        const course = await CourseModel.findActiveById(courseId);
        if (!course) {
            const err = new Error('Curso nao encontrado');
            err.status = 404;
            throw err;
        }

        let user = await UserModel.findByEmail(email);
        if (!user) {
            const hashedPwd = UserModel.hashPassword(password || `temp_${Date.now()}`);
            const newUserId = await UserModel.create(userName, email, hashedPwd);
            user = { id: newUserId };
        }

        const paymentStatus = processPayment(cardNumber);
        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            const err = new Error('Pagamento recusado');
            err.status = 400;
            throw err;
        }

        const enrollmentId = await EnrollmentModel.create(user.id, courseId);
        await PaymentModel.create(enrollmentId, course.price, paymentStatus);
        await AuditModel.log(`Checkout curso ${courseId} por usuario ${user.id}`);

        return { enrollmentId, courseTitle: course.title };
    },
};

module.exports = CheckoutService;
