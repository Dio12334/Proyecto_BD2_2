import snscrape.modules.twitter as sntwitter
import json

class creator_index:

    def __init__(self) -> None:
        pass

    # @Input: keyword (frase de búsqueda), capacidad máxima de retorno
    # @Return: 2 archivos en memoria secundaria:
    #   - Index.txt: Los id de los tweets recuperados
    #   - Data.json: Los objetos que representan los tweets recuperados
    # :: Trae n tweets (n < maxTweets) que contienen al menos una vez a keyword 
    def make_new_index(self, keyword, maxTweets):

        # Archivos que procederan a llenarse   
        json_file = open('resources/data.json', 'a', newline='\n', encoding='utf8')
        index_file = open('resources/index.txt', 'a', newline='\n', encoding='utf8')
        json_file.truncate(0)
        index_file.truncate(0)

        # Búsqueda y estructuración de tweets como objetos
        # Si sabe lo que hace, puede probar a cambiar los parametros del scrapper,
        # como el lenjuage, la fecha límite o la posibilidad de capturar respuestas.
        cont = 0
        for retrieved_cont,tweet in enumerate(sntwitter.TwitterSearchScraper(keyword + ' lang:es until:2021-06-30 -filter:links -filter:replies').get_items()):
            if retrieved_cont >= maxTweets:
                index_file.write(str(format(cont, '09d')))
                break 
            content = (tweet.content).replace("\n", " ").replace("\"","").replace("-"," ").replace('_'," ").replace('\\'," ").replace('\r'," ").replace('\t'," ")             
            my_details = {
                'id': tweet.id,
                'username' : tweet.user.username,
                'date' : tweet.date,
                'content' : content,
                'url' : tweet.url
            }
            index_file.write(str(format(cont, '09d')))
            cont += 2 + 19 + len(tweet.user.username) + len(str(tweet.date)) + len(content) + len (tweet.url) + 27 + 4*6 + 4*2 +11 -9
            json_file.write(json.dumps(my_details, ensure_ascii=False, default=str))
            index_file.write('\n')
            json_file.write('\n') 
        return
