
import linker.eatlas as eatlas
import linker.google as google
from flask import Flask, render_template, redirect, flash
import geopandas as gpd
import argparse
from wtforms import StringField, BooleanField
from flask_wtf import Form
from messenger.emailer import send_email

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('display', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

app = Flask(__name__)
global gpdf


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


@app.route("/corners/<int:page_no>", methods=['GET', 'POST'])
def show_tables(page_no):
    global gpdf
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
    parser = argparse.ArgumentParser(description='Process arguments to the data analyzer.')
    parser.add_argument('--mapfile',
                        metavar='file path',
                        type=str,
                        nargs='?',
                        default="../data/truncated/banyo/shp/geo/out.shp",
                        #default="../data/output/some-date/output.shp",
                        help='The path to the mapfile data')

    args = parser.parse_args()
    print "Args: ", args
    gpdf = gpd.read_file(args.mapfile)
    print "Serving..."
    app.config.from_object('config')

    app.run(debug=True)
