import pandas as pd
import sqlite3
import re
import unidecode
import matplotlib.pyplot as plt
from glob import glob
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.request import urlretrieve, urlopen

# remove pandas warnings
pd.options.mode.chained_assignment = None  # default='warn'


def fit_filename(text):	
    """Function to fit link name as file name.

    Args:
        text: link name which will be changed to fit as file name.
        
    Returns:
        The return value is a string with file name fitted.

    """
    # decoding and filling blank spaces with underscore 
    text = unidecode.unidecode(text)
    text = re.sub(' ','_',text)
    
    return re.sub(r'[^a-zA-Z0-9_]','',text) + '.xls'

def fit_text(text):
    """Function to fit original columns name to column name that will be stored in db.

    Args:
        text: column name which will be changed to fit as db column.
        
    Returns:
        The return value is a string with columns name fitted..

    """
    # remove parenthesis terms
    text = re.sub('\(\S*\)|\s\(\S*\)','',text)
    # decoding and filling blank spaces with underscore    
    text = unidecode.unidecode(text)
    text = re.sub(' ','_',text)

    return re.sub(r'[^a-zA-Z0-9_]','',text.lower())


if __name__ == "__main__":

    ### CRAWLING ###

    url_path  = 'http://www.cnj.jus.br'
    url_base = 'http://www.cnj.jus.br/transparencia/remuneracao-dos-magistrados'
    path = './data/'

    links = list()
    files = list()

    # crawling the page
    with urlopen(url_base) as page:
        soup = BeautifulSoup(page, 'html.parser')
        # find strong tags which have files href within
        for strong in tqdm(soup.find_all('strong'), desc='Getting links.'):
            # find files href
            href = [a['href'] for a in strong.find_all('a', href=True) if a.text]
            rel = [fit_filename(a.get_text()) for a in strong.find_all('a', href=True) if a.text]

            if href:
                # store href and file names in lists
            	links.append(href[0])            
            	files.append(rel[0])

    # save files in data path
    for link, file in tqdm(zip(links,files), desc='Retrieving files.', unit='files'):
        url = url_path + link
        file_path = path + file	
        urlretrieve(url, file_path)


    ### PROCESING DATA ###

    # read files
    files = glob('./data/*.xls')

    # columns to change in tables
    unnamed_contracheque = {
        'Unnamed: 0' : 1,
        'Unnamed: 1' : 'Nome',
        'Unnamed: 2' : 'Cargo',
        'Unnamed: 3' : 'Lotação',
        'Unnamed: 14' : 'Rendimento Líquido(10)',
        'Unnamed: 15' : 'Remuneração do orgão de origem(11) (R$)',
        'Unnamed: 16' : 'Diárias(12) (R$)'  
        }
    unnamed_subsidio = {
        'Unnamed: 0' : 1,
        'Unnamed: 1' : 'Nome',
        'Unnamed: 8' : 2
    }
    unnamed_indenizacoes = {
        'Unnamed: 0' : 1,
        'Unnamed: 1' : 'Nome'    
    }
    unnamed_direitos_eventuais = {
        'Unnamed: 0' : 1,
        'Unnamed: 1' : 'Nome'    
    }
    unnamed_dados_cadastrais = {
        'Unnamed: 0' : 1        
    }

    # saving original columns labels
    pres_labels_contracheque = pd.read_excel(files[0], skiprows=19).rename(columns=unnamed_contracheque).iloc[:,1:17].columns
    pres_labels_subsidio = pd.read_excel(files[0], skiprows=4, sheetname=1).rename(columns=unnamed_subsidio).iloc[:,1:8].columns
    pres_labels_indenizacoes = pd.read_excel(files[0], skiprows=4, sheetname=2).rename(columns=unnamed_indenizacoes).iloc[:,1:15].columns
    pres_labels_direitos_eventuais = pd.read_excel(files[0], skiprows=4, sheetname=3).rename(columns=unnamed_direitos_eventuais).iloc[:,1:17].columns
    pres_labels_dados_cadastrais = pd.read_excel(files[0], skiprows=3, sheetname=4).iloc[:,1:6].columns

    # fitting labels as they will be stored in db
    db_labels_contracheque = [fit_text(col) for col in pres_labels_contracheque]
    db_labels_subsidio = [fit_text(col) for col in pres_labels_subsidio]
    db_labels_indenizacoes = [fit_text(col) for col in pres_labels_indenizacoes]
    db_labels_direitos_eventuais = [fit_text(col) for col in pres_labels_direitos_eventuais]
    db_labels_dados_cadastrais = [fit_text(col) for col in pres_labels_dados_cadastrais]


    # opend connection with sqlite3 db
    conn = sqlite3.connect('judiciario.db')

    log =  list()

    # prepare data and store in db
    for file in tqdm(files, desc=f"Reading and saving data.", unit='files'):
        # read each of excel file
        df_contracheque = pd.read_excel(file, skiprows=19).rename(columns=unnamed_contracheque).iloc[:,1:17].fillna(0.0)
        df_subsidio = pd.read_excel(file, skiprows=4, sheetname=1).rename(columns=unnamed_subsidio).iloc[:,1:8].fillna(0.0)
        df_indenizacoes = pd.read_excel(file, skiprows=4, sheetname=2).rename(columns=unnamed_indenizacoes).iloc[:,1:15].fillna(0.0)
        df_direitos_eventuais = pd.read_excel(file, skiprows=4, sheetname=3).rename(columns=unnamed_direitos_eventuais).iloc[:,1:17].fillna(0.0)
        df_dados_cadastrais = pd.read_excel(file, skiprows=3, sheetname=4).iloc[:,1:6].fillna('None')    

        # change columns names to fitted ones
        df_contracheque.columns = db_labels_contracheque
        df_subsidio.columns = db_labels_subsidio
        df_indenizacoes.columns = db_labels_indenizacoes
        df_direitos_eventuais.columns = db_labels_direitos_eventuais
        df_dados_cadastrais.columns = db_labels_dados_cadastrais 
        
        # remove blank rows
        df_contracheque = df_contracheque[df_contracheque.nome!=0.0]
        df_subsidio = df_subsidio[df_subsidio.nome!=0.0]
        df_indenizacoes = df_indenizacoes[df_indenizacoes.nome!=0.0]
        df_direitos_eventuais = df_direitos_eventuais[df_direitos_eventuais.nome!=0.0]
        df_dados_cadastrais = df_dados_cadastrais[df_dados_cadastrais.nome!=0.0]
        
        # save dataframes in db tables.
        df_contracheque.to_sql('contracheque', conn, if_exists='append', index=False)
        df_subsidio.to_sql('subsidio', conn, if_exists='append', index=False)
        df_indenizacoes.to_sql('indenizacoes', conn, if_exists='append', index=False)
        df_direitos_eventuais.to_sql('direitos_eventuais', conn, if_exists='append', index=False)
        df_dados_cadastrais.to_sql('dados_cadastrais', conn, if_exists='append', index=False)
                     
    conn.close()