from waitress import serve
from index import app
import logging
if __name__ == '__main__':

    serve(app.server, threads=100, port=8080,host='0.0.0.0')