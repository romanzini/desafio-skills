from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import Config
from database import get_db
from routes.api_routes import api_bp
from middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    CORS(app)
    app.register_blueprint(api_bp)
    register_error_handlers(app)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo a API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health"
            }
        })

    return app


app = create_app()

if __name__ == "__main__":
    get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO (v2.0 - MVC)")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
