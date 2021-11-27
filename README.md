# Proyecto_BD2_2

## Pasos del procesamiento de la query
### Crear el indice (por bloques)



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
### Tokenizar la query

Para la tokenización de la query hacemos uso de la librería nltk.
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

Obtenemos la distancia de coseno de todos los tokens del query y 
sumamos al documento en el indice invertido de dicho token.

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
### Filtrar los mejores
Después de tokenizar la query y calcular la distancia de coseno de
ellas procedemos a ingresar todos los tweets en un max heap para que
posteriormente podamos obtener los k tweets más relevantes.

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
![](images/benchmark_buildindex.png)
### Queries benchmark
![](images/benchmarks_queries.png)
### Change index benchmark
![](images/benchmark_changeindex.png)
