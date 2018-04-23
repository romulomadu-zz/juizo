# Juizo

Brazil Judiciary's salaries data analysis.
 
# Objectives

Analyse data information about Judiciary employees salaries, searching for irregularities and huge privilegies. 

# Key Words

judiciary, corruption, salary, social control, magistrados, salários, Brazil, Brasil, corrupção, benefícios

# Instructions

Clone the directory in your computer doing: 

`git clone https://github.com/romulomadu/juizo.git`

Create a virtual enviroment with your favorite tool (virtualenv, conda, ...).

Install required packages using pip:

`pip install -r requirements.txt`

Run the `main.py` program, it will do the follow:

* Download files .xls with salary information from CNJ's [page](http://www.cnj.jus.br/transparencia/remuneracao-dos-magistrados) and save in directory `/data`.
* Read files using pandas, extract, prepare and store data in sqlite database file `judiciario.db` creating the follow tables:
  - contracheque
  - subsidio
  - indenizacoes
  - direitos_eventuais
  - dados_cadastrais

Note: each table have data from all files.

After run `main.py` you are prepared to do your analysis 

# Make your own analysis

There is a jupyter notebook file with a example of how read data from database and make some analysis, feel free to make your own and commit it!

# How to contribute

- You can improve `main.py`.
- You can make analysis in notebook and send it.
- Feel free to create you own crawler for extract adittional data from judiciary pages, news, etc.

__Note__: If you don't no how to make version control with jupyter notebook, you can look this repo [here](https://github.com/toobaz/ipynb_output_filter), or you can use nbdime, see [here](https://github.com/jupyter/nbdime)

# Superset dashboards

If you want to use Apache Superset to make dashboards, there is a example of dashboard on `/dashboards` folder, you can import it. More information about Superset can be found [here](https://superset.incubator.apache.org/).

![figura1](superset_example.png)



  

 





