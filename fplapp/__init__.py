from flask import Flask


app = Flask(__name__)

if app.config['ENV'] == 'production':
    print('prod')
    app.config.from_object("fplapp.config.ProductionConfig")
elif app.config['ENV'] == 'development':
    print('dev')
    app.config.from_object("fplapp.config.DevelopmentConfig")
elif app.config['ENV'] == 'testing':
    app.config.from_object("fplapp.config.TestingConfig")




from fplapp import routes