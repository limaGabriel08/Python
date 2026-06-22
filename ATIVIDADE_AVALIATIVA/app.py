# Cenário: B - Cinema
# Aluno: Aluno

import os

from flask import Flask

from controllers import cinema_bp, dashboard_bp
from dados_iniciais import popular_dados
from models import db


def criar_app():
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )

    pasta = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        pasta, "cinema.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cinema_bp)

    with app.app_context():
        db.create_all()
        popular_dados()

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
