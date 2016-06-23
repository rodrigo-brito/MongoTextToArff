#!/usr/bin/python
# -*- coding: UTF-8 -

import nltk, re
from pymongo import MongoClient
from unicodedata import normalize
from datetime import datetime
from Twitt import Twitt

def leituraMongoTwitt():
   # Conecta ao MongoDB
   connection = MongoClient()

   # seleciona a base de Twitts
   db = connection.Twitter.dolar_twitter

   # Efeg
   results = db.find()

   # close the connection to MongoDB
   connection.close()
   return results;

def leituraMongoDolar():
   # Conecta ao MongoDB
   connection = MongoClient()

   # seleciona a base de Twitts
   db = connection.Twitter.dados_dolar

   # Efeg
   results = db.find()

   # close the connection to MongoDB
   connection.close()
   return results;

def removeAcentos(texto):
   acentos = ['á','é','í','ó','ú','à','è','ì','ò','ù', 'ã','ẽ','ĩ','õ','ũ','â','ê','î','ô','û']
   s_acentos = ['a','e','i','o','u','a','e','i','o','u', 'a','e','i','o','u','a','e','i','o','u']
   for i in range(0, len(acentos)):
      texto = texto.replace(acentos[i], s_acentos[i])
   return texto


def tratarTexto( texto ):
   #inicializa stemmer
   stemmer = nltk.stem.RSLPStemmer()

   #remove links
   texto = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texto)

   #remove acentuacao
   texto = normalize('NFKD', texto).encode('ASCII', 'ignore')

   #remove simbolos
   texto = re.sub(r'[^\w]', ' ', texto)

   #separa em tokens
   tokens = nltk.word_tokenize(texto)

   #remove stopwords, remove caixa alta e deixa radical
   stopwords = nltk.corpus.stopwords.words('portuguese')
   texto = [ stemmer.stem(token.lower()) for token in tokens if token not in stopwords]
   texto = ' '.join(texto)
   texto = removeAcentos(texto.encode('utf8'))

   #remove acentuacao
   #texto = normalize('NFKD', texto.decode('utf-8')).encode('ASCII', 'ignore')

   #retorna texto tratado
   return texto

def main():
   twitts =  list(leituraMongoTwitt()[:])
   #twitts = sorted(twitts, key=lambda x: x['data'])

   #Separa as datas unicas e agrupa os Twitts
   datas = set([ x['data'].strftime("%Y-%m-%d") for x in twitts ])
   twitts_por_data = {}
   for data in datas:
      twitts_por_data[ data ] = []

   #Para cada Twitt, sao concatenados os textos referentes a sua data
   for twitt in twitts:
      data_formatada = twitt['data'].strftime("%Y-%m-%d")
      texto_limpo = tratarTexto(twitt['texto'])
      twitts_por_data[ data_formatada ].append( texto_limpo )

   #Armazena as cotacoes de dolar de acordo com a data dos mesmos
   cotacoes = leituraMongoDolar()
   dolar_por_data = {}
   for cotacao in cotacoes:
      data_formatada = datetime.strptime( cotacao['data'], '%d/%m/%Y').strftime("%Y-%m-%d")
      dolar_por_data[ data_formatada ] = {'valor': cotacao['valor'], 'aumentou': cotacao['aumentou'] }

   #cabecalho do WEKA
   print '@relation saida'
   print ''
   print '@attribute classe {1,0}'
   print '@attribute texto string'
   print ''
   print '@data'


   #Imprime saida para leitura no WEKA
   for data in twitts_por_data:
      print str(dolar_por_data[data]['aumentou'])+",\""+' '.join(twitts_por_data[ data ])+"\""
main()