The repo contains the code for building a RAG-based assistant to chat with Papers With Code.


### 1.  Indexing

To data you first need to create an index on Upstash and fill in the credentials in the `.env` file:

```
UPSTASH_URL=...
UPSTASH_TOKEN=...
```

Then you run this command:

```bash
poetry run python -m src.index_papers --query "OpenAI" --limit 200
```

![](./assets/indexing.png)


### 2. Run the Streamlit application to interact with the RAG

```bash
poetry run python -m streamlit run  src/app.py --theme.primaryColor "#135aaf"
```

![](./assets/rag-upstash.gif)


### More details

Check Medium post.