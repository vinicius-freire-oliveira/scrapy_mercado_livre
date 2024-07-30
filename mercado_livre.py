import requests
from bs4 import BeautifulSoup
import pandas as pd

def extrair_dados_da_pagina(url):
    # Realiza a requisição para obter o conteúdo da página
    response = requests.get(url)
    site = BeautifulSoup(response.text, 'html.parser')

    produtos_data = []

    # Encontrar todos os produtos na página
    produtos = site.findAll('div', attrs={'class': 'ui-search-result__wrapper'})
    
    for produto in produtos:
        # Encontrar o link do produto
        link = produto.find('a', attrs={'class': 'ui-search-link'})
        link_url = link['href'] if link else 'Não disponível'
        
        # Encontrar o nome do produto
        nome = produto.find('h2', attrs={'class': 'ui-search-item__title'})
        nome_texto = nome.text if nome else 'Não disponível'
        
        # Encontrar o preço do produto
        preco = produto.find('span', attrs={
            'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'
        })
        
        if preco:
            try:
                # Extraindo os componentes do preço
                simbolo = preco.find('span', class_='andes-money-amount__currency-symbol').text
                inteiro = preco.find('span', class_='andes-money-amount__fraction').text
                centavos = preco.find('span', class_='andes-money-amount__cents')
                centavos_texto = centavos.text if centavos else '00'
                preco_texto = f'{simbolo}{inteiro},{centavos_texto}'
            except AttributeError:
                preco_texto = 'Formato de preço desconhecido'
        else:
            preco_texto = 'Não disponível'
        
        produtos_data.append({
            'Nome': nome_texto,
            'Link': link_url,
            'Preço': preco_texto
        })

    return produtos_data

# Perguntar ao usuário qual produto ele está procurando
produto_nome = input('Qual produto você procura? ')
produto_nome = produto_nome.replace(' ', '_')  # Substituir espaços por %20 para URL

# URLs das páginas
url_base = f'https://lista.mercadolivre.com.br/{produto_nome}'
url_pagina_atual = f'{url_base}'
url_pagina_seguinte = f'{url_base}_Desde_50'

# Exibir a URL da página de resultados
print(f'URL da página de resultados: {url_base}')

# Extrair dados da página atual
dados_pagina_atual = extrair_dados_da_pagina(url_pagina_atual)

# Extrair dados da próxima página
dados_pagina_seguinte = extrair_dados_da_pagina(url_pagina_seguinte)

# Combinar dados das duas páginas
todos_dados = dados_pagina_atual + dados_pagina_seguinte

# Criar DataFrame com os dados coletados
dados = pd.DataFrame(todos_dados)

# Salvar os dados em um arquivo CSV
csv_filename = f'{produto_nome}_dados.csv'
dados.to_csv(csv_filename, index=False, encoding='utf-8')

# Confirmar que o arquivo foi salvo
print(f'Os dados foram salvos em {csv_filename}')

# Exibir as primeiras 30 linhas e as linhas restantes
print('Primeiros 30 produtos:')
print(dados.head(30))

print('\nProdutos restantes:')
print(dados.tail(len(dados) - 30))
