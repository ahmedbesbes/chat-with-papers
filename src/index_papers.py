import os
import click
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import VertexAIEmbeddings
from upstash_vector import Index
from src.paperswithcode import extract_papers
from src.upstash import UpstashVectorStore


@click.command()
@click.option("--query", type=str)
@click.option("--batch_size", type=int, default=32)
@click.option("--limit", type=int, default=None)
def cli(query, batch_size, limit):
    load_dotenv()
    click.echo(f"Extracting papers matching this query: {query}")
    papers = extract_papers(query)
    click.echo(f"Extraction complete ✅: ({len(papers)} papers)")
    documents = [
        Document(
            page_content=paper["abstract"],
            metadata={
                "id": paper["id"] if paper["id"] else "",
                "arxiv_id": paper["arxiv_id"] if paper["arxiv_id"] else "",
                "url_pdf": paper["url_pdf"] if paper["url_pdf"] else "",
                "title": paper["title"] if paper["title"] else "",
                "authors": paper["authors"] if paper["authors"] else "",
                "published": paper["published"] if paper["published"] else "",
            },
        )
        for paper in papers
    ]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["."],
    )
    splits = text_splitter.split_documents(documents)
    splits = splits[:limit]

    index = Index(
        url=os.environ.get("UPSTASH_URL"),
        token=os.environ.get("UPSTASH_TOKEN"),
    )
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")
    upstash_vector_store = UpstashVectorStore(index, embeddings)
    click.echo("Indexing to Upstash ...")
    ids = upstash_vector_store.add_documents(splits, batch_size=batch_size)
    click.echo(f"Successfully indexed {len(ids)} vector to Upstash")


if __name__ == "__main__":
    cli()
