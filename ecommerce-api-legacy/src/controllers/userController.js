const UserModel = require('../models/userModel');

const userController = {
    deleteUser: async (req, res, next) => {
        try {
            const userId = parseInt(req.params.id, 10);
            if (isNaN(userId)) {
                return res.status(400).json({ error: 'ID invalido' });
            }

            const deleted = await UserModel.deleteWithCascade(userId);
            if (!deleted) {
                return res.status(404).json({ error: 'Usuario nao encontrado' });
            }

            return res.status(200).json({ message: 'Usuario e dados relacionados deletados com sucesso' });
        } catch (err) {
            next(err);
        }
    },
};

module.exports = userController;
