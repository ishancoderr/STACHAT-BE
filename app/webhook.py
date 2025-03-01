from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.retrievers import BaseRetriever
from typing import List
from pydantic import BaseModel, Field

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

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

class CustomRetriever(BaseRetriever, BaseModel):
    """Custom retriever that fetches relevant documents from Neo4j and scores them."""
    
    vector_index: Neo4jVector = Field(...)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve and score documents from the vector index."""
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

router = APIRouter()

@router.post("/webhook", tags=["Webhook"])
async def webhook_endpoint(query: dict):
    question = query.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    response = graph_chain.invoke(question)
    return {"answer": response.dict()}