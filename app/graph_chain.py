from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import BM25Retriever
from typing import List
from pydantic import BaseModel, Field
import os
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Validate OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Neo4j vector index
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
    vector_index: Neo4jVector = Field(...)  

    def _get_relevant_documents(self, query: str) -> List[Document]:
        try:
            docs_and_scores = self.vector_index.similarity_search_with_score(query)
            docs, scores = zip(*docs_and_scores)
            
            for doc, score in zip(docs, scores):
                doc.metadata["score"] = score
            
            return list(docs)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

vector_retriever = CustomRetriever(vector_index=vector_index)

texts = [doc.page_content for doc in vector_index.similarity_search("query")]
metadatas = [doc.metadata for doc in vector_index.similarity_search("query")]
bm25_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)

class HybridRetriever(BaseRetriever, BaseModel):
    vector_retriever: BaseRetriever = Field(...)  
    bm25_retriever: BaseRetriever = Field(...)    

    def _get_relevant_documents(self, query: str) -> List[Document]:
        try:
            vector_docs = self.vector_retriever.invoke(query)
            bm25_docs = self.bm25_retriever.invoke(query)
            combined_docs = vector_docs + bm25_docs
            return combined_docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

hybrid_retriever = HybridRetriever(vector_retriever=vector_retriever, bm25_retriever=bm25_retriever)

template = """You are an expert in geospatial data. Answer the question based only on the following context:
{context}

Instructions:
- Format the response in a human-friendly way.
- Use bullet points for clarity.
- Provide additional context or explanations where necessary.
- Simplify technical terms and metadata.
- Include links for further exploration if available.

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def get_graph_chain(model_name: str):
    print('model name:', model_name)
    if model_name == "gpt-3.5-turbo":
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    elif model_name == "gpt-4-turbo":
        llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0) 
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    return (
        {"context": hybrid_retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )