from flask import Flask
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_jsonpify import jsonify
import logging
import sys

URI = open('.mainudb', 'r').read()
LOG_PATH = 'log/mainu_api.log'
STDOUT_PATH = 'log/.trash'
STDERR_PATH = 'log/error.log'

sys.stdout = open(STDOUT_PATH, 'a')
sys.stderr = open(STDERR_PATH, 'a')
logging.basicConfig(filename=LOG_PATH,
                    format='%(asctime)s - %(funcName)s - ' +
                    '%(levelname)s - %(message)s',
                    filemode='a',
                    level=logging.DEBUG)

db_connect = create_engine(URI)
app = Flask(__name__)
api = Api(app)


class Bocadillos(Resource):
    def get(self):
        logging.info("Devuelve lista de bocadillos")
        conn = db_connect.connect()
        query = conn.execute("SELECT * FROM Bocadillo")
        return jsonify({'Bocadillos': [dict(zip(query.keys(), i))
                                       for i in query.cursor.fetchall()]})


api.add_resource(Bocadillos, '/getBocadillos')

if __name__ == '__main__':
    app.run(port=5002)
