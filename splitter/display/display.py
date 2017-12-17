
from urlparse import urlparse, urljoin
import linker.eatlas as eatlas
import linker.google as google
from flask import Flask, render_template, redirect, flash, jsonify, request, url_for, redirect
import geopandas as gpd
import argparse
from wtforms import StringField, BooleanField, SelectField
from flask_wtf import Form
from messenger.emailer import send_email
import os
from glob import glob

from jinja2 import Environment, PackageLoader, select_autoescape

from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return True
    #return username == 'admin' and password == 'BuiltEasy123!'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

env = Environment(
    loader=PackageLoader('display', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

app = Flask(__name__)
global gpdfs

gpdfs = {}

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

# class SelectorForm(Form):
#     suburbfield = SelectField(u'Suburb')
#     filefield = SelectField(u'File')


# def is_safe_url(target):
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#         ref_url.netloc == test_url.netloc


# def get_redirect_target():
#     for target in request.args.get('next'), request.referrer:
#         if not target:
#             continue
#         if is_safe_url(target):
#             return target
# class RedirectForm(Form):
#     def redirect(self, endpoint='index', **values):
#         if is_safe_url(self.next.data):
#             return redirect(self.next.data)
#         target = get_redirect_target()
#         return redirect(target or url_for(endpoint, **values))


class SuburbForm(Form):
    suburbfield = SelectField(u'Suburb', choices=[])
    

class FileSelectorForm(Form):
    filefield = SelectField(u'File', choices=[])

class BaseEmailForm(Form):
    emailsfield = StringField('emails')

def format_gpdf(gpdf, idx=0, items=20):
    cols = ["LOT", "PLAN"]

    display_gpdf = gpdf[cols].iloc[idx*items:(idx+1)*items]
    display_gpdf["CENT"] = gpdf.geometry.centroid.apply(
        lambda x: "(%.4f, %.4f)" % x.coords[0])

    # Generate links
    display_gpdf["eatlas_link"] = gpdf.geometry.apply(
        lambda x: eatlas.get_link(x))
    display_gpdf["google_link"] = gpdf.geometry.apply(
        lambda x: google.get_link(x))
    display_gpdf["google_static_link"] = gpdf.geometry.apply(
        lambda x: google.get_link(x, 'static'))

    return display_gpdf

def get_files_by_suburb():
    shp_files = [y for x in os.walk(os.path.dirname(os.path.realpath(__file__)) + "/" + "../data/output/")
                 for y in glob(os.path.join(x[0], '*.shp'))]

    #Filter to make sure there is a correct number of subdirectories
    temp = []
    suburbs = set([])
    listing_dict = {}
    for shp_file in shp_files:
        split_path = shp_file.split("/")
        suburb = split_path[-2]
        if suburb in listing_dict:
            listing_dict[suburb].append(split_path[-1])
        else:
            listing_dict[suburb] = [split_path[-1]]

    return listing_dict

@app.route("/corners")
def show_corner_options():
    pass
    

#@requires_auth
@app.route("/", methods=['GET', 'POST'])
def return_suburbs():
    files_dict = get_files_by_suburb()
    form=SuburbForm()
    print "Keys: ", files_dict.keys()
    form.suburbfield.choices = [(x, x) for x in files_dict.keys()]
    if form.validate_on_submit():
        # do something with the form data here
        
        return redirect('/files/' + form.suburbfield.data)

    return render_template('suburbs.html', form=form)


@app.route("/files/<suburb>", methods=['GET', 'POST'])
#@requires_auth
def return_files_in_suburb(suburb):
    form = FileSelectorForm()
    files_dict = get_files_by_suburb()
    form.filefield.choices = [(x, x) for x in files_dict[suburb]]
    if form.validate_on_submit():
        # do something with the form data here

        return redirect('/corners/' + suburb + '/' + form.filefield.data+ "/0")
    return render_template('files.html', form=form)

@app.route("/corners/<suburb>/<filename>/<int:page_no>", methods=['GET', 'POST'])
#@requires_auth
def show_tables(suburb, filename, page_no):
    suburbfilename=suburb + filename
    if suburbfilename not in gpdfs:
        gpdfs[suburbfilename] = gpd.read_file(os.path.dirname(os.path.realpath(
            __file__)) + '/../data/output/' + suburb + '/' + filename)

    gpdf = gpdfs[suburbfilename]
    display_gpdf = format_gpdf(gpdf, page_no)

    class EmailForm(BaseEmailForm):
        properties = []
            
    property_fields = []
    for idx in display_gpdf.index:
        field = BooleanField(
            'selectproperty' + str(idx), default=False)
        setattr(EmailForm, 'selectproperty' + str(idx), field)
    
    form = EmailForm()

    if form.validate_on_submit():
        indices = []
        for idx in display_gpdf.index:
            if getattr(form, "selectproperty" + str(idx)).data:
                indices.append(idx)
            filtered_display_gpdf = display_gpdf.loc[indices]
        print "sending email..."

        template = env.get_template('email.html')
        send_email(form.emailsfield.data.split(","), "Selected Corner Blocks", template.render(rows=filtered_display_gpdf.iterrows(),
                    idx=page_no, form=form))
        flash('Email(s) sent.')
    
    # TODO: Build form checkboxes based on display_gpdf
    return render_template('web.html', rows=display_gpdf.iterrows(), idx=page_no, form=form)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process arguments to the data analyzer.')
    # parser.add_argument('--mapfile',
    #                     metavar='file path',
    #                     type=str,
    #                     nargs='?',
    #                     default="../data/truncated/banyo/shp/geo/out.shp",
    #                     #default="../data/output/some-date/output.shp",
    #                     help='The path to the mapfile data')

    # args = parser.parse_args()
    # print "Args: ", args
    print "Serving..."
    app.config.from_object('config')

    app.run()
