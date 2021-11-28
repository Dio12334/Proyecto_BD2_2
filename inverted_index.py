from resources.tweets import creator_index
import json
import math
from tw_proccesing import TweetProccesor
import os
import sys
from glob import glob
from heapq import heappop, heappush, heapify
sys.path.append('resources')

size_tweets = 20000
tp = TweetProccesor()

class InvertedIndex:

    # @Input: La cantidad de tweets que se recuperarán y el límite de tweets por bloque.
    # @Output: El inverted index particionado en n/block índices intermedios.
    # :: Es un algoritmo SPIMI: usamos un diccionario para almacenar las frecuencias
    def __build_inverted_index(self, n, block):
        tw_index = 1
        lengths = {}
        with open("resources/data.json", "r") as file:

            # Partición por bloques
            for j in range(math.ceil(n/block)):
                local_terms = {}

                # Partición por tweets
                for _ in range(block):
                    tweet_data = json.loads(file.readline())
                    tokens = tp.tokenize(tweet_data["content"])
                    lengths[tw_index] = len(tokens)
                    terms = {}
                    # Construye la tupla (cant_palabras, tw_index) para cada termino
                    for token in tokens:
                        if terms.get(token) is None or terms.get(token)[1] != tw_index:
                            terms[token] = (1, tw_index)
                        else:
                            terms[token] = (terms[token][0] + 1, tw_index)
                    # Añadimos la información de este tweet a su índice
                    for term in terms:
                        if local_terms.get(term) is None:
                            local_terms[term] = [(terms[term][0], terms[term][1])]
                        else:
                            local_terms[term].append((terms[term][0], terms[term][1]))
                    tw_index += 1

                # Indice i-ésimo 
                inverted_index = {}
                for word in local_terms:
                    inverted_index[word] = {
                        "DF": len(local_terms[word]),
                        "TF": local_terms[word]
                    }

                # Escritura del i-ésimo índice temporal local
                json_file = open('resources/indexs/i' + str(j) + '.json', 'a', newline='\n', encoding='utf8')
                json_file.truncate(0)
                json_file.write(json.dumps(inverted_index, ensure_ascii=False, default=str))

        # Escritura de las longitudes de los tweets
        lengths_file = open('resources/lengths.json', 'a', newline='\n', encoding='utf8')
        lengths_file.truncate(0)
        lengths_file.write(json.dumps(lengths, ensure_ascii=False, default=str))
        return

    # @Input: Los n bloques que se particionaron en __build_inverted_index
    # @Output: El índice invertido final, que es la unión de todos los índices intermedios
    def __merge(self):
        inverted_index = {}

        # Lectura de los índices temporales
        for local_index in glob('resources/indexs/*.json'):
            with open(local_index, "r") as index:
                local_dict = json.loads(index.readline())
            
            # Colocamos las frecuencias
            for k in local_dict.keys():
                if k not in inverted_index.keys():
                    inverted_index[k] = local_dict[k]
                else:
                    # Dado que cada tweet se revisa secuencialmente, no hay colisiones en los TF
                    inverted_index[k]['TF'] += (local_dict[k]['TF'])
                    # Se suman las frecuencias de documentos
                    inverted_index[k]['DF'] += (local_dict[k]['DF'])
            os.remove(local_index)

        # Escribimos el índice completo
        json_file = open('resources/i_index.json', 'a', newline='\n', encoding='utf8')
        json_file.truncate(0)
        json_file.write(json.dumps(inverted_index, ensure_ascii=False, default=str))
        return

    # :: Define las particiones y, usando las funciones anteriores, construye el índice
    def BSBI_builder(self):
        block = int(size_tweets / 20)
        self.__build_inverted_index(size_tweets, block)
        self.__merge()
        return

# @Input: La query, la cantidad de tweets a recuperar (k) y la cantidad total de tweets (n).
# @Output: Los k tweets más relevantes según el scoring de coseno.
def process_query(query, k, n):
    tokens = tp.tokenize(query)
    qnorm = len(tokens)

    # Obtenemos la frecuencia de las palabras en la query
    query_words = {}
    for q in tokens:
        if query_words.get(q) is None:
            query_words[q] = 1
        else:
            query_words[q] += 1

    # Leemos el index desde un archivo (memoria secundaria)
    tweets = {}
    with open('resources/i_index.json', "r") as index:
        i_dic = json.loads(index.readline())
    with open('resources/lengths.json', "r") as lens:
        lengths = json.loads(lens.readline())

    # Calculamos la distancia de coseno:
    for q in query_words:
        if i_dic.get(q) is not None:
            i = i_dic[q]
            idf = math.log10(n/i['DF'])
            # Normalizamos localmente el vector de palabras en el query
            qq = (1 + math.log10(query_words[q])) * idf / qnorm
            for tweet in i['TF']:
                # Sumamos a un documento el puntaje que va consiguiendo (con dist. de coseno)
                tf = 1 + math.log10(tweet[0])
                ii = tf * idf / lengths[str(tweet[1])]
                cosine = round(ii * qq, 4)
                if tweets.get(tweet[1]) is None:
                    tweets[tweet[1]] = cosine
                else:
                    tweets[tweet[1]] += cosine
    heap = []

    # Debemos hacer una segunda pasada porque los cosenos podrían haberse modificado...
    for tweet in tweets:
        heappush(heap, (-1 * tweets[tweet], tweet))

    # Uso de fila de prioridades para el ranking
    retrieved = {}
    for i in range(min(k, len(tweets))):
        retrieved[heap[0][1]] = -1 * heap[0][0]
        heappop(heap)
        heapify(heap)
    return retrieved

# :: Cambia la temática de los tweets en base a una frase
def change_index_theme(keyword, maxtweets):
    global size_tweets
    size_tweets = maxtweets
    index_creator = creator_index()
    index_creator.make_new_index(keyword, maxtweets)
    ii = InvertedIndex()
    ii.BSBI_builder()
    return

def do_query(q, qns):
    rpta = process_query(q, qns, size_tweets)
    indexs = open("resources/index.txt", "r")
    tweets = open("resources/data.json", "r")
    jsondic = []
    json_file = open('static/data/rpta.json', 'a', newline='\n', encoding='utf8')
    json_file.truncate(0)
    for n in rpta:
        indexs.seek(0, 0)
        tweets.seek(0, 0)
        indexs.read((n-1)*10)
        line_tweet1 = int(indexs.read(10))
        line_tweet2 = int(indexs.read(10))
        tweets.read(line_tweet1)
        json_line = tweets.read(line_tweet2 - line_tweet1-1)
        json_line = json.loads(json_line)
        json_line['score'] = rpta[n]
        jsondic.append(json_line)
    json_file.write(json.dumps(jsondic, indent=6, ensure_ascii=False))
    return len(rpta)