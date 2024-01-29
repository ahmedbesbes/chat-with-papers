from typing import List, Optional, Tuple, Union
from uuid import uuid4
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from tqdm import tqdm
from upstash_vector import Index


class UpstashVectorStore:
    def __init__(self, index: Index, embeddings: Embeddings):
        self.index = index
        self.embeddings = embeddings

    def delete_vectors(
        self,
        ids: Union[str, List[str]] = None,
        delete_all: bool = None,
    ):
        if delete_all:
            self.index.reset()
        else:
            self.index.delete(ids)

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
        batch_size: int = 32,
    ):
        texts = []
        metadatas = []
        all_ids = []

        for document in tqdm(documents):
            text = document.page_content
            metadata = document.metadata
            metadata = {"context": text, **metadata}
            texts.append(text)
            metadatas.append(metadata)

            if len(texts) >= batch_size:
                ids = [str(uuid4()) for _ in range(len(texts))]
                all_ids += ids
                embeddings = self.embeddings.embed_documents(texts, batch_size=250)
                self.index.upsert(
                    vectors=zip(ids, embeddings, metadatas),
                )
                texts = []
                metadatas = []

        if len(texts) > 0:
            ids = [str(uuid4()) for _ in range(len(texts))]
            all_ids += ids
            embeddings = self.embeddings.embed_documents(texts)
            self.index.upsert(
                vectors=zip(ids, embeddings, metadatas),
            )

        n = len(all_ids)
        print(f"Successfully indexed {n} dense vectors to Upstash.")
        print(self.index.stats())
        return all_ids

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
    ) -> List[Tuple[Document, float]]:
        query_embedding = self.embeddings.embed_query(query)
        query_results = self.index.query(
            query_embedding,
            top_k=k,
            include_metadata=True,
        )
        output = []
        for query_result in query_results:
            score = query_result.score
            metadata = query_result.metadata
            context = metadata.pop("context")
            doc = Document(
                page_content=context,
                metadata=metadata,
            )
            output.append((doc, score))
        return output
