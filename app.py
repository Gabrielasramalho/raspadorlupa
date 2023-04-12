from flask import Flask

app = Flask(__name__)

from flask import Flask, render_template, request, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import requests
import pandas as pd
import json
from io import BytesIO

app = Flask(_name_)
app.config['SECRET_KEY'] = 'mysecretkey'

class SearchForm(FlaskForm):
    keyword = StringField('Palavra-chave', validators=[DataRequired()])
    search_type = SelectField('Tipo de busca', choices=[('todos', 'Todos'), ('ultimos_30_dias', 'Últimos 30 dias'), ('personalizado', 'Personalizado')], validators=[DataRequired()])
    start_date = StringField('Data inicial')
    end_date = StringField('Data final')
    submit = SubmitField('Buscar')

def search_lupa(keyword, search_type, start_date=None, end_date=None):
    if search_type == 'todos':
        url = f'https://gapi.storyblok.com/v1/api={keyword}'
    elif search_type == 'ultimos_30_dias':
        url = f'https://lupa.uol.com.br/wp-json/lupa/v1/posts?posts_per_page=1000&search={keyword}&days_apr=30'
    else:
        url = f'https://lupa.uol.com.br/wp-json/lupa/v1/posts?posts_per_page=1000&search={keyword}'
        if start_date:
            url += f'&start_date={start_date}'
        if end_date:
            url += f'&end_date={end_date}'
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data['posts'])
        if 'post_title' in df.columns:
            df = df[['post_title', 'Conteúdo', 'url']]
        else:
            df = df[['post_title', 'excerpt', 'url']]
        df.columns = ['post_title', 'Conteúdo', 'url']
        return df
    except json.JSONDecodeError:
        return pd.DataFrame()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        keyword = form.keyword.data
        search_type = form.search_type.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        df = search_lupa(keyword, search_type, start_date, end_date)
        output = make_response()
        writer = pd.ExcelWriter(f"{keyword}.xlsx")
        df.to_excel(writer, index=False)
        output.data = BytesIO()
        output.headers["Content-Disposition"] = f"attachment; filename={keyword}.xlsx"
        output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return output


    return render_template('index.html', form=form)

if _name_ == '_main_':
    app.run(debug=True)
