from waitress import serve
from index8081 import app
import logging
if __name__ == '__main__':

    serve(app.server, threads=100, port=8081,host='0.0.0.0')