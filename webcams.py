#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging.config
from bottle import Bottle, run, route, response, template, request, redirect
from pygments import highlight, lexers, formatters
from requests import post, get
from json import dumps
from os.path import exists, expanduser, abspath, join
from bs4 import BeautifulSoup

APP_NAME = 'xc_skiing_webcams'

HTTP_HOST = '127.0.0.1'
HTTP_PORT = 5001
HTTP_CDF = '/cdf'
HTTP_KNB = '/knb'
HTTP_DEBUG = True

WEBCAM_CDF_URL = "http://webcam.inforoute67.fr/WebcamFTP/CHAMP-DU-FEU/"
WEBCAM_KNB_URL = [
    "http://webcam.itteleservice.de/webcams/nachtloipe-webcam/skicam.jpg",
    "http://webcam.itteleservice.de/webcams/nachtloipe-webcam/skihuette.jpg",
    "http://webcam.itteleservice.de/webcams/nachtloipe-webcam/skicam2.jpg"
]

HTML_INDEX = """
<html>
  <body>
  <b>{{application}}</b>.<br/>
  XC Skiing Webcams<br/>
  </body>
</html>
"""

WEBCAMS_INDEX = """
<html>
  <body>
    <img src="{{webcam}}">
  <body>
</html>
"""

WEBCAMS_TABLE = """
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <title>Realtime Table</title>
  </head>
  <body>
    <table class="table" id="flights">
      <tr>
        % for webcam in webcams:
        <td>
          <img src={{webcam}}>
        </td>
      % end
      </tr>
    </table>
  </body>
</html>
"""

api = Bottle()


def get_url_paths(url, ext='', params={}):
    response = get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent


@api.route('/')
def index():
    return template(HTML_INDEX, application=APP_NAME)


@api.route('{}'.format(HTTP_CDF))
def cdf():
    response.content_type = 'image/jpg'
    cdf_pictures = get_url_paths(WEBCAM_CDF_URL, ext='jpg')
    return get(url=cdf_pictures[len(cdf_pictures) - 1])


@api.route('{}'.format(HTTP_KNB))
def knb():
    # response.content_type = 'image/jpg'
    return template(WEBCAMS_TABLE, webcams=WEBCAM_KNB_URL)


def json_formatter(data, colorize=False, sort=True, comments=''):
    if data != {}:
        output = dumps(data, indent=4, sort_keys=sort, ensure_ascii=False)
        if colorize:
            print(highlight('{}{}'.format(comments, output), lexers.JsonLexer(), formatters.TerminalFormatter()))
        else:
            print('{}{}'.format(comments, output))


def initialize_logger():
    logger = logging.getLogger('{}'.format(APP_NAME))
    logger.setLevel(logging.INFO)
    sh = logging.handlers.SysLogHandler()
    sh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    sh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(sh_formatter)
    ch.setFormatter(ch_formatter)
    # add the handlers to the logger
    logger.addHandler(sh)
    logger.addHandler(ch)
    return logger


def full_path(path):
    # to prevent errors with debian container under Windows
    if path[0] == '~' and not exists(path):
        path = expanduser(path)
    return abspath(path)


if __name__ == '__main__':
    logs = initialize_logger()
    api.run(host=HTTP_HOST, port=HTTP_PORT, debug=HTTP_DEBUG)
