#!/usr/bin/python3
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import override
import argparse
import configparser
import json
import logging
import mimetypes
import os
import signal
import subprocess
import zipfile

logger = logging.getLogger(__name__)

methods = []
def method(path, method="GET"):
    def decorator(f):
        methods.append({"method": method, "path" : path, "function" : f})
        return f
    return decorator

# Define custom HTTPHandler
class HTTPHandler(SimpleHTTPRequestHandler):

    @override
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def end_with_code(self, code):
        self.send_response(code)
        self.end_headers()
    
    def end_with_json(self, dictionary, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(dictionary).encode("utf-8"))

    @override
    def log_message(self, format, *args):
        logger.info("%s", format % args)


    @override
    def do_GET(self):
        self.do_REQUEST("GET", super().do_GET)

    @override
    def do_POST(self):
        self.do_REQUEST("POST", lambda : self.end_with_code(404))

    @override
    def end_headers(self):
        if urlparse(self.path).path.endswith(".vue"):
            self.send_header("Cache-control", "no-store")
        super().end_headers()

    def do_REQUEST(self, method, fallback_method):
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            selected_methods = list(filter(lambda m : m["method"]==method and path.startswith(m["path"]), methods))
            if len(selected_methods) > 0:
                selected_methods[0]["function"](self, parsed_path)
            else:
                fallback_method()
        except Exception as e:
            logger.error(e)
            self.end_with_code(500)

    def get_app(self, parsed_path):
        parts = parsed_path.path.split('/')
        return None if len(parts) < 3 else next(filter(lambda a : a['id'] == parts[2], apps))
    
    def send_app_file(self, parsed_path, file, validator):
        app = self.get_app(parsed_path)
        if not app:
            return self.end_with_code(404)
        file_path = app.get(file)
        if not file_path:
            return self.end_with_code(404)
        if not validator(file_path):
            return self.end_with_code(500)
        _, extension = os.path.splitext(file_path)
        mime = mimetypes.types_map[extension]
        try:
            with open(os.path.expanduser(file_path), 'rb') as f:
                self.send_response(200)
                self.send_header("Content-type", mime)
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.end_with_code(500)

    @method("/apps")
    def apps(self, parsed_path):
        self.end_with_json(apps)

    @method("/covers")
    def covers(self, parsed_path):
        self.send_app_file(parsed_path, 'cover', lambda p : p.split('.')[-1].lower() in ['jpg', 'png', 'gif', 'webp'])

    @method("/info")
    def info(self, parsed_path):
        self.send_app_file(parsed_path, 'info', lambda p : p.split('.')[-1].lower() in ['txt', 'html', 'htm'])

    @method("/soundtracks")
    def soundtracks(self, parsed_path):
        self.send_app_file(parsed_path, 'soundtrack', lambda p : p.split('.')[-1].lower() in ['mp3', 'ogg', 'wav'])

    @method("/run_sounds")
    def run_sounds(self, parsed_path):
        self.send_app_file(parsed_path, 'run_sound', lambda p : p.split('.')[-1].lower() in ['mp3', 'ogg', 'wav'])

    def run_app_command(self, parsed_path, command):
        app = self.get_app(parsed_path)
        if not app:
            return self.end_with_code(404)
        shell_cmd = app.get(command)
        if not shell_cmd:
            return self.end_with_code(404)
        global app_handle
        app_handle = subprocess.Popen(shell_cmd, shell=True, preexec_fn=os.setsid)
        global current_app
        current_app = app
        global state
        state['last_app'] = app['id']
        save_state()
        self.end_with_code(200)

    @method("/run_default", "POST")
    def run_default(self, parsed_path):
        self.run_app_command(parsed_path, 'run_default')

    @method("/run_config", "POST")
    def run_config(self, parsed_path):
        self.run_app_command(parsed_path, 'run_config')

    @method("/shutdown", "POST")
    def shutdown(self, parsed_path):
        logger.info(f"Running pre-shutdown command: {on_exit}")
        if on_exit:
            subprocess.call(on_exit, shell=True)
        logger.info("Shutting down server")
        exit(0)

    @method("/refresh", "POST")
    def refresh(self, parsed_path):
        global apps
        config = read_configuration(config_file)
        apps = read_applications(config) 
        self.end_with_code(200)

    @method("/exit", "POST")
    def exit_app(self, parsed_path):
        app = self.get_app(parsed_path)
        if not app:
            app = current_app
        shell_cmd = app.get('kill_default')
        if not shell_cmd:
            os.killpg(os.getpgid(app_handle.pid), signal.SIGTERM)
        else:
            subprocess.Popen(shell_cmd, shell=True)
        self.end_with_code(200)

    @method("/state")
    def get_state(self, parsed_path):
        self.end_with_json(state)

    @method("/state", "POST")
    def set_state(self, parsed_path):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        global state
        state = json.loads(post_body) # Verify content format
        save_state()
        self.end_with_code(200)

    @method("/version")
    def get_state(self, parsed_path):
        r1 = subprocess.run(['git','log','-n','1','HEAD','--format=%cI'], 
            stdout=subprocess.PIPE, cwd=Path(script_path).parent.parent.absolute())
        local_version = r1.stdout.decode('utf-8').strip()
        remote_version = None
        try:
            subprocess.run(['git','fetch'])
            r2 = subprocess.run(['git','log','-n','1','origin/main','--format=%cI'], 
                stdout=subprocess.PIPE, cwd=Path(script_path).parent.parent.absolute())
            remote_version = r2.stdout.decode('utf-8').strip()
        except Exception as e:
            logger.error("Unable to fetch remote version: %s", str(e))
        self.end_with_json({"local_version":local_version, "remote_version":remote_version})

    @method("/update", "POST")
    def update(self, parsed_path):
        result = subprocess.run(['git','pull'], 
            stdout=subprocess.PIPE, cwd=Path(script_path).parent.parent.absolute())
        self.end_with_code(200 if result.returncode == 0 else 500)
    
    @method("/upload", "POST")
    def upload(self, parsed_path):
        app_zip = os.path.join(upload_dir, "app.zip")
        with open(app_zip, 'wb') as app_file:
            file_length = int(self.headers['Content-Length'])
            app_file.write(self.rfile.read(file_length))
        app_ini = os.path.join(upload_dir, "app.ini")
        with zipfile.ZipFile(app_zip) as z:
            with open(app_ini, 'wb') as f:
                f.write(z.read('app.ini'))
        app_config = configparser.ConfigParser(allow_no_value=True)
        app_config.read(app_ini)
        app = {}
        for section in app_config.sections():
            app['id'] = section[4:]
            app['version'] = app_config.get(section, 'version', fallback='')
            app['title'] = app_config.get(section, 'title')
            app['subtitle'] = app_config.get(section, 'subtitle', fallback='')
        self.end_with_json(app)

    @method("/deploy", "POST")
    def upload(self, parsed_path):
        app_id = parsed_path.path.split('/')[2]
        app_zip = os.path.join(upload_dir, "app.zip")
        target_dir = os.path.join(resources_dir, app_id)
        app_ini = os.path.join(target_dir, "app.ini")
        assert subprocess.run(['unzip', '-o', app_zip,'-d',target_dir], stdout=subprocess.PIPE).returncode == 0
        assert subprocess.run(['sed', '-i', '-e', f"s|$appdir|{target_dir}|g", app_ini], stdout=subprocess.PIPE).returncode == 0
        os.symlink(app_ini, os.path.join(deploy_dir, app_id))
        global state
        state['last_app'] = app_id
        self.end_with_code(200)

# Define custom HTTPServer
class HTTPServer(BaseHTTPServer):

    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass) 

def save_state():
    with open(state_file, 'wb') as sf:
        sf.write(json.dumps(state).encode("utf-8"))

def read_configuration(config_file):
    config = configparser.ConfigParser(allow_no_value=True)
    config_files = [os.path.expanduser(config_file)]
    while len(config_files):
        cf = config_files.pop()
        if not os.path.isfile(cf):
            continue
        config.read(cf)
        if not config.has_section('INCLUDE'):
            continue
        includes = config.items('INCLUDE')
        config.remove_section('INCLUDE')
        for f, d in includes:
            file = os.path.expanduser(f)
            config_files += list(map(lambda f : os.path.join(file, os.path.expanduser(f)), os.listdir(file))) \
                if os.path.isdir(file) else [file]
    return config

def read_applications(config):
    apps = []
    for section in config.sections():
        if section.lower().startswith("app:"):
            app = {
                'id' : section[4:],
                'version' : config.get(section, 'version', fallback=''),
                'title' : config.get(section, 'title', fallback='Unknown'),
                'subtitle' : config.get(section, 'subtitle', fallback=''),
                'platform' : config.get(section, 'platform', fallback=''),
                'category' : config.get(section, 'category', fallback=''),
                'info' : config.get(section, 'info', fallback=''),
                'cover' : config.get(section, 'cover', fallback=''),
                'soundtrack' : config.get(section, 'soundtrack', fallback=''),
                'run_sound' : config.get(section, 'run_sound', fallback=''),
                'run_default' : config.get(section, 'run_default', fallback=''),
                'kill_default' : config.get(section, 'kill_default', fallback=''),
                'run_config' : config.get(section, 'run_config', fallback=''),
            }
            apps.append(app)
    return apps

# Read command line arguments
script_path = os.path.realpath(__file__)
parser = argparse.ArgumentParser(description='Swoosh - A gamepad compatible carousel UI.')
parser.add_argument('-c', metavar='path', type=str, help='Configuration file path', 
    default=os.path.join(Path.home(),'.swoosh-config'))
parser.add_argument('-s', metavar='path', type=str, help='State file path', 
    default=os.path.join(Path.home(),'.swoosh-state'))
parser.add_argument('-u', metavar='path', type=str, help='Upload directory', 
    default=os.path.join(Path.home(),'.swoosh-upload'))
parser.add_argument('-r', metavar='path', type=str, help='Resources directory', 
    default=os.path.join(Path.home(),'.swoosh-resources'))
parser.add_argument('-d', metavar='path', type=str, help='Deploy directory', 
    default=os.path.join(Path.home(),'.swoosh-config.d'))
parser.add_argument('-l', metavar='path', type=str, help='Log file', default=None)
parser.add_argument('-v', metavar='log-level', type=str, help='Logging level (e.g. INFO)', 
    default="INFO")
args = parser.parse_args()
config_file = args.c
state_file = args.s
upload_dir = args.u
resources_dir = args.r
deploy_dir = args.d

# Load and read configuration file
config = read_configuration(config_file)
on_start = config.get('SWOOSH', 'on_start', fallback='')
on_exit = config.get('SWOOSH', 'on_exit', fallback='')
log_level = logging.getLevelName(config.get('SWOOSH', 'log_level', fallback=args.v))
log_file = config.get('SWOOSH', 'log_file', fallback=args.l)
http_port = int(config.get('SWOOSH', 'http_port', fallback='8000'))
state_file = os.path.expanduser(config.get('SWOOSH', 'state_file', fallback=state_file))
upload_dir = os.path.expanduser(config.get('SWOOSH', 'upload_dir', fallback=upload_dir))
resources_dir = os.path.expanduser(config.get('SWOOSH', 'resources_dir', fallback=resources_dir))
deploy_dir = os.path.expanduser(config.get('SWOOSH', 'deploy_dir', fallback=deploy_dir))
http_port = int(config.get('SWOOSH', 'http_port', fallback='8000'))
web_dir = os.path.expanduser(config.get('SWOOSH', 'web_dir', fallback=os.path.join(os.path.dirname(__file__), '../js')))
browser_cmd = config.get('SWOOSH', 'browser_cmd', fallback=f"firefox http://127.0.0.1:{http_port}")
apps = read_applications(config)

# Set up logging
logging.basicConfig(filename=log_file, level=log_level, format="%(asctime)s %(levelname)s %(message)s")

# Set default state
state = dict()

# Application handle
current_app = None
app_handle = None

# Read state file
if os.path.isfile(state_file):
    with open(state_file) as sf:
        state = json.load(sf)

# Start server
logger.debug('Running script: %s', script_path)
logger.debug('Initializing MIME types')
mimetypes.init()
logger.info('Starting HTTP server')
httpd = HTTPServer(web_dir, ("", http_port))
if browser_cmd != "":
    subprocess.Popen(browser_cmd, shell=True)
httpd.serve_forever()
