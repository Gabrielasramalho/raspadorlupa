# -*- coding: utf-8 -*-
"""3tri_trab_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WO8fE49yiqC9i0ZRZ5CHmYz5eQ2LFc_E
"""

import requests
import json
import pandas as pd

#Fazer uma requesição do tipo get no site da lupa para pegar a parte de verificações 
#O query foi copiado do próprio site da Lupa
response = requests.get("https://lupa.uol.com.br/jornalismo/categoria/verificamos")

#Declarar o token para acessar o json do site
headers = {"token": "S4otl4itHUavEuIIbVlrrgtt"}

query = '''
query ($tag: String, $perPage: Int, $page: Int) {
  NewsItems(
    with_tag: $tag
        page: $page
    per_page: $perPage
    sort_by: "first_published_at:desc"
  ) {
    total
    items {
      full_slug
      uuid
      first_published_at
      name
      content {
        hat
        custom_hat
        featured_title
        featured_image {
          filename
          __typename
        }
        resume
        authors {
          name
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
} 
'''
data = {
    "query": query,
    "variables": {
        "page": 1,
        "perPage": 30,
        "tag": "verificamos,verificamos,verificamos,Verificamos,Verificamos",
        },
}
#puxar os dados mostrá-los
response = requests.post("https://gapi.storyblok.com/v1/api",headers=headers,json=data)

print(response.json())

#mostrar dados em formato Json
resposta = response.json()
resposta

#Organizar os dados em dicionário 
data = json.loads(response.text)

# Extrai as informações de cada item em "NewsItems"
items = data['data']['NewsItems']['items']
items_data = []
for item in items:
    item_data = {
        'full_slug': item['full_slug'],
        'uuid': item['uuid'],
        'published_at': item['first_published_at'],
        'name': item['name'],
        'hat': item['content']['hat'],
        'custom_hat': item['content']['custom_hat'],
        'featured_title': item['content']['featured_title'],
        'resume': item['content']['resume']['content'][0]['content'][0]['text'],
        'author': item['content']['authors'][0]['name']
    }
    items_data.append(item_data)

# Cria o dataframe a partir do dicionário com as informações dos items
df = pd.DataFrame(items_data)

#Vincular dados à planilha no Google Sheets 
#instalar bibliotecas 
!pip install gspread oauth2client 
from oauth2client.service_account import ServiceAccountCredentials

#subir credenciais Google Sheets 
import gspread
credencialjson = "automacao-verificacao-lupa-e14459d5bbdc.json"
conta = ServiceAccountCredentials.from_json_keyfile_name(credencialjson)

api = gspread.authorize(conta)
planilha = api.open_by_key("1fUoWcnUwQlkSMDZAvNDVw3AA0t02oOtlD502w192zEo")
sheet = planilha.worksheet("verificações")

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

#completa as informações sem duplicações enviando os dados para o google sheets sempre atualizados durante a raspagem de dados.
# Set up authentication
credencialjson = "automacao-verificacao-lupa-e14459d5bbdc.json"
conta = ServiceAccountCredentials.from_json_keyfile_name(credencialjson)
api = gspread.authorize(conta)

# Open the worksheet
planilha = api.open_by_key("1fUoWcnUwQlkSMDZAvNDVw3AA0t02oOtlD502w192zEo")
sheet = planilha.worksheet("verificações")

# Make a GET request to the Lupa website to get the list of recent fact-checks
response = requests.get("https://lupa.uol.com.br/jornalismo/categoria/verificamos")
html_content = response.content

# Extract the IDs and URLs of the fact-checks from the HTML content
ids_and_urls = []
for line in html_content.splitlines():
    line = line.strip().decode("utf-8")
    if line.startswith('<h3 class="title">'):
        id_and_url = line.split('href="')[1].split('"')[0]
        ids_and_urls.append((id_and_url.split("/")[-1], id_and_url))

# Make a POST request to the Storyblok API to get the full content of each fact-check
headers = {"token": "S4otl4itHUavEuIIbVlrrgtt"}
query = '''
query ($slug: String) {
  Story(slug: $slug) {
    name
    created_at
    content {
      body {
        type
        attrs {
          src
        }
        content
      }
    }
  }
}
'''
new_data = []
for id, url in ids_and_urls:
    data = {
        "query": query,
        "variables": {
            "slug": f"jornalismo/{id}",
        },
    }
    response = requests.post("https://gapi.storyblok.com/v1/api", headers=headers, json=data)
    story = response.json()["data"]["Story"]
    title = story["name"]
    date = story["created_at"]
    content = story["content"]["body"]
    content_html = ""
    for item in content:
        if item["type"] == "text":
            content_html += item["content"]
        elif item["type"] == "image":
            content_html += f'<img src="{item["attrs"]["src"]}">'
    new_data.append({"id": id, "nome": title, "data": date, "conteudo": content_html})

# Retrieve the existing data from the worksheet
existing_data = sheet.get_all_values()
