from waitress import serve
from index8082 import app
import logging
if __name__ == '__main__':

    serve(app.server, threads=100, port=8082,host='0.0.0.0')