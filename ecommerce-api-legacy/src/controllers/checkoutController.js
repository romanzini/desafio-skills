const CheckoutService = require('../services/checkoutService');

const checkoutController = {
    checkout: async (req, res, next) => {
        try {
            const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

            if (!userName || !email || !courseId || !cardNumber) {
                return res.status(400).json({ error: 'Campos obrigatorios: usr, eml, c_id, card' });
            }

            const result = await CheckoutService.checkout({
                userName,
                email,
                password,
                courseId,
                cardNumber,
            });

            return res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
        } catch (err) {
            next(err);
        }
    },
};

module.exports = checkoutController;
