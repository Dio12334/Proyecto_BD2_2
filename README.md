# Proyecto_BD2_2

## Archivos usados en memoria secundaria
- **resources/Data.json:** Colección de máximo 20K tweets que fueron filtrados a través de una frase de consulta en la función change_index_theme

- **resources/indexs:** Carpeta donde se guardan los índices SPIMI locales que serán fusionados en la función merge. Siempre son 20 índices. Al unirlos en el índice final, son eliminados.

- **resources/i_index.json:** Índice Invertido final.

- **resources/index.txt:** Índice para poder ubicarnos en un tweet dada su posición lógica en la colección, ya que la API los guarda en espacios de longitud variable.

- **resources/lengths.json:** Archivo donde se guardan las longitudes de todos los tweets. Es imprescindible para la normalización al momento de realizar la similitud de coseno

- **static/data/rpta.json:** Archivo que contiene los K tweets más relevantes a la consulta del usuario, es decir, es el output de la función do_query.

## Pasos del procesamiento de la query
### Crear el indice (por bloques)

Creamos el indice invertido a base de los datos en data.json 
y guardamos los tokens y sus respectivos pesos DF y TF en un diccionario
de diccionarios. Esto corresponde a un sólo bloque de tweets.

```python
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

```
Recibe los n bloques que se particionarion en la función anterior y
devuelve el índice invertido final (La unión de todos loa índices
intermedios)
```python
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
```
Define las particiones y, ysa las funciones anteriores para construir  
el índice invertido final

```python
    def BSBI_builder(self):
        block = int(size_tweets / 20)
        self.__build_inverted_index(size_tweets, block)
        self.__merge()
        return

```
### Tokenizar la query

Para la tokenización de la query hacemos uso de la librería nltk,
cuya implementación soporta parcialmente consultas en el lenguaje
español.
Donde usamos las funciones encode, decode, stem, tokenize. Luego,
procedemos a deshacernos de los stopwords con ayuda de la librería
y nuestra lista de caracteres a no incluir.

```python
    def tokenize(self, tweet):
        tweet = tweet.encode('ascii', 'ignore').decode('ascii')
        return [
            self.stemmer.stem(t) for t in self.tknzr.tokenize(tweet)
            if t not in stopwords.words('spanish') and
                t not in 
                ["<", ">", ",", "º", ":", ";", ".", "!", "¿", "?", ")", "(", "@", "'",'"','\"', '.', '...', '....']
        ]
```
### Aplicar cosenos

Obtenemos la distancia de coseno de la query y buscamos sus
términos en el índice para aplicar el coseno a los tweets
que contienen dichas palabras. También usamos el archivo
lengths.json, el cual contiene los tamaños de los tweets, que
fueron guardados en disco al crea los índices locales.

```python
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

```
### Filtrar los k mejores tweets
Después de procesar la query y calcular la distancia del coseno con respecto
a los tweets de la colección, se filtran los k mejores tweets haciendo uso
de un max heap con la distancia de coseno.

```python
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

```

## Benchmarks

### Build index benchmark
Este es el tiempo de creación del indice invertido
![](images/benchmark_buildindex.png)
### Queries benchmark
Estos son los tiempos que nos tomó encontrar las siguientes busquedas:
1. Cristiano Ronaldo
2. Toni Kroos
3. Sheriff
4. Manchester City
![](images/benchmarks_queries.png)
### Change index benchmark
Este es el tiempo que toma el cambiar el contexto de los tweets a los
que se le van a hacer la busqueda.
![](images/benchmark_changeindex.png)
