import os
import sys
import site

# Add virtualenv site packages
site.addsitedir(os.path.join(os.path.dirname(__file__),     'env/local/lib64/python2.7/site-packages'))
site.addsitedir(os.path.join(os.path.dirname(__file__),     'env/local/lib/python2.7/site-packages'))

# Path of execution
sys.path.append('/var/www/rest-dev')

# Fired up virtualenv before include application
activate_env = os.path.expanduser(os.path.join(os.path.dirname(__file__), 'env/bin/activate_this.py'))
execfile(activate_env, dict(__file__=activate_env))

# import my_flask_app as application
from display.display import app as application
