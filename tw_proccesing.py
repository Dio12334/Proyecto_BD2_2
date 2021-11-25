from nltk.tokenize import TweetTokenizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

class TweetProccesor:

    # :: Crea un stemmer óptimo para el lenguaje español.
    # :: También define el tokenizer de tweets de nltk
    def __init__(self):
        self.stemmer = SnowballStemmer(language='spanish')
        self.tknzr = TweetTokenizer()

    # @Input: Un tweet
    # @Output: La normalización de las palabras dentro del tweet
    # :: El filtrado de stopwords y la tokenización se realizan con las funciones nltk.
    # :: Se eliminan también algunos símbolos innecesarios para la búsqueda.
    # Complejidad: O(n*K) donde K es la cantidad de palabras en la stoplist.
    def tokenize(self, tweet):
        tweet = tweet.encode('ascii', 'ignore').decode('ascii')
        return [
            self.stemmer.stem(t) for t in self.tknzr.tokenize(tweet)
            if t not in stopwords.words('spanish') and
                t not in 
                ["<", ">", ",", "º", ":", ";", ".", "!", "¿", "?", ")", "(", "@", "'",'"','\"', '.', '...', '....']
        ]