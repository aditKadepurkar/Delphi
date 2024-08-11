import chromadb
from chromadb import Collection
from helpers import get_description, getModel
import uuid

class Database:
    def __init__(self):
        client = chromadb.Client()
        self.database = client.get_or_create_collection('database')
        self.embedmodel = getModel()
    
    def add_to_database(self, file_list: list):
        sentences = []
        ids = []
        for file in file_list:
            sentences.append(get_description(file_path=file)) # need to start saving these so it doesnt take 100 years for the program to run each time
            ids.append(str(uuid.uuid4())) # generate a random id for each file
        # print(sentences)
        embeds = self.get_embedding_list(sentences=sentences)
        self.database.add(
            embeddings=embeds,
            documents=file_list,
            ids=ids,
        )
    
    def remove_from_database():
        pass
    
    def query_database(self, query: str):
        '''
        Search for files in the collection that match the query.
        
        @param query: str: The query to search for.
        @param collection: Collection: The collection to search in.
        @param embedmodel: SentenceTransformer: The model to be used for getting the embeddings.
        @return: list: The list of files that match the query.
        '''
        query_result = self.database.query(
            query_embeddings=[getEmbeddingList(self.embedmodel, query)],
            n_results=1,
        )
        return query_result['documents'][0][0]
    
    def get_embedding_list(self, sentences):
        """ This function returns the sentence embeddings for a given document using the SentenceTransformer model and encapsulates them inside a list.

        @param model: SentenceTransformer: The model to be used for getting the embeddings.
        @param sentences: list: The list of sentences for which embeddings are to be calculated. """

        embeddings = self.embedmodel.encode(sentences)
        return embeddings.tolist()