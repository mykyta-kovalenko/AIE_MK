import re
from rank_bm25 import BM25Okapi
from typing import List, Tuple
from collections import defaultdict

class BM25Retriever:
    """
    A sparse retriever using the BM25 algorithm
    """
    def __init__(self, corpus: List[str]):
        self.corpus = corpus
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
    
    def _tokenize(self, text: str) -> List[str]: 
        """
        Cleans and tokenizes text
        """
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.split()

    def search_by_text(self, query_text: str, k: int) -> List[Tuple[str, float]]:
        """
        Searches the corpus for a given query text
        """
        tokenized_query = self._tokenize(query_text)
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_k_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:k]
        
        return [(self.corpus[i], doc_scores[i]) for i in top_k_indices]
    

class HybridRetriever:
    """
    A hybrid retriever that combines results from a dense and a sparse retriever
    using RRF
    """
    def __init__(self, dense_retriever, sparse_retriever):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever

    def search_by_text(self, query_text: str, k: int = 4, rrf_k: int = 60, detailed_results: bool = False):
        """
        Performs a hybrid search and combines the results
        """
        dense_results = self.dense_retriever.search_by_text(query_text, k=k)
        sparse_results = self.sparse_retriever.search_by_text(query_text, k=k)

        rrf_results = defaultdict(lambda: {'score': 0.0, 'sources': set()})

        for rank, (doc, _) in enumerate(dense_results, 1):
            rrf_results[doc]['score'] += 1 / (rrf_k + rank)
            rrf_results[doc]['sources'].add('dense')

        for rank, (doc, _) in enumerate(sparse_results, 1):
            rrf_results[doc]['score'] += 1 / (rrf_k + rank)
            rrf_results[doc]['sources'].add('sparse')
            
        sorted_docs = sorted(rrf_results.items(), key=lambda item: item[1]['score'], reverse=True)

        
        if detailed_results:
            return [{'doc': doc, 'score': data['score'], 'sources': list(data['sources'])} for doc, data in sorted_docs[:k]]
        
        return [(doc, data['score']) for doc, data in sorted_docs[:k]]