from routes.portfolio import portfolio as portfolio_blueprint
from routes.auth import auth as auth_blueprint
import config.flask_config as flask
import os

app = flask.app
# Adding routes from main.py
app.register_blueprint(portfolio_blueprint)
app.register_blueprint(auth_blueprint)
if __name__ == '__main__':
    # Run the flask app on debug mode.
    app.run(debug=True, port=os.environ.get('PORT'))