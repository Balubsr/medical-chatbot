from flask import Flask, render_template,jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from src.prompt import *
import os



app = Flask(__name__)


load_dotenv()

load_dotenv()

# Load API keys
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY #type: ignore
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY # type: ignore


embedings = download_hugging_face_embeddings()
index_name = "medibot"
docsearch = PineconeVectorStore.from_existing_index(index_name, embedings, text_key="source")


retriever = docsearch.as_retriever(serach_type = "similarity" ,search_kwargs={"k": 3})

chatmodel = init_chat_model("google_genai:gemini-2.5-flash-lite")

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

question_answering_chain = create_stuff_documents_chain(chatmodel, prompt)
rag_chain = create_retrieval_chain(
    retriever,
    question_answering_chain
)



@app.route("/")
def index():
    return render_template('chat.html')




@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    response = rag_chain.invoke({"input": msg})
    print("Response : ", response["answer"])
    return str(response["answer"])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
    print(True)