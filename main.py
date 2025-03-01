from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Validate OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")

# LangChain and Neo4j setup (from your original code)
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.retrievers import BaseRetriever
from typing import List
from pydantic import BaseModel as PydanticBaseModel, Field

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="index_for_Product",
    node_label="Product",
    text_node_properties=[
        "name", "date", "sensorType", "organization", "orbitType",
        "spatialExtent", "instrument", "isoStandard", "visualizationUrl",
        "referenceSystem", "platform", "compositeType"
    ],
    embedding_node_property="embedding",
)

class CustomRetriever(BaseRetriever, PydanticBaseModel):
    vector_index: Neo4jVector = Field(...)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        docs, scores = zip(*self.vector_index.similarity_search_with_score(query))
        for doc, score in zip(docs, scores):
            doc.metadata["score"] = score
        return docs

retriever = CustomRetriever(vector_index=vector_index)

def update_scores(docs):
    for doc in docs:
        doc.metadata["score"] *= 10
        doc.page_content += f"\nScore: {doc.metadata['score']}"
    return docs

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

graph_chain = (
    {"context": retriever | update_scores, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# FastAPI setup
app = FastAPI(
    title="STACHAT",
    version="1.0.0.v",
    description="API for querying datasets using LangChain and Neo4j."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request body
class QueryRequest(BaseModel):
    question: str

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to STACHAT!"}

@app.post("/query", tags=["Query"])
async def query_dataset(request: QueryRequest):
    try:
        # Run the pipeline with the provided question
        response = graph_chain.invoke(request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))