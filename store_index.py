from dotenv import load_dotenv
import os
from src.helper import load_pdf_file, filter_to_minimal_docs, text_split, download_hugging_face_embeddings
from pinecone import Pinecone as PC
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from typing import List

load_dotenv()

# Load API keys
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


index_name = "medibot"  

pc = PC(api_key=PINECONE_API_KEY)
index = pc.Index(index_name)


embeddings = download_hugging_face_embeddings()

vectorstore = PineconeVectorStore(index=index, embedding=embeddings, text_key="source")

retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

results: List[Document] = retriever.invoke("What are the precautions for diabetes?")
for r in results:
    print(r.page_content)
    print(r.metadata)
