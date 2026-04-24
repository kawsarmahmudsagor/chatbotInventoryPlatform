from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from modules.agents.models.agent_model import Agent
import os
from pathlib import Path
from core.enums import VectorStoreType
from utils.convert_to_txt import convert_to_txt
from utils.hash_utils import should_embed

def create_vector_store(store_type, chatbot_id, embeddings, chunks):
    """
    Create a vector store (Chroma or FAISS) for a chatbot and return the store.
    Returns: vectordb, persist_path
    """
    persist_path = f"uploads/vectorstore/{store_type.lower()}/chatbot_{chatbot_id}"
    os.makedirs(persist_path, exist_ok=True)

    if store_type.lower() == VectorStoreType.chroma:
        vectordb = Chroma(
            persist_directory=persist_path,
            embedding_function=embeddings
        )
        vectordb.add_documents(chunks)
        vectordb.persist()
        return vectordb, persist_path

    elif store_type.lower() == VectorStoreType.faiss:
        vectordb = FAISS.from_documents(chunks, embeddings)
        vectordb.save_local(persist_path)
        return vectordb, persist_path

    else:
        raise ValueError("Unsupported vector store. Only 'chroma' and 'faiss' are supported.")



def load_vectorstore(store_type, db_path, embeddings):
    """
    Load a vector store using the path stored in DB.
    db_path should be exactly the path saved in DB, e.g., 'uploads/vectorstore/chroma/chatbot_28'
    """
    if not os.path.isdir(db_path):
        raise ValueError(f"{store_type.capitalize()} vector store not found at {db_path}")

    if store_type.lower() == VectorStoreType.chroma:
        return Chroma(persist_directory=db_path, embedding_function=embeddings)
    elif store_type.lower() == VectorStoreType.faiss:
        return FAISS.load_local(db_path, embeddings)
    else:
        raise ValueError("Unsupported vector store. Only 'chroma' and 'faiss' are supported.")


def embedd_document(db, agent_id, embedd_obj, document_objs):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.status == "active"
    ).first()
    if not agent:
        raise ValueError("Agent not found or inactive")

    embeddings = OllamaEmbeddings(model=embedd_obj.model_name)

    docs_to_embed = []
    updated_docs = []

    for doc in document_objs:
        should_reembed, new_hash = should_embed(
            doc.file_path,
            doc.hash_address
        )

        if should_reembed:
            text = convert_to_txt(Path(doc.file_path))

            docs_to_embed.append(
                LCDocument(page_content=text)
            )
            doc.hash_address = new_hash
            updated_docs.append(doc)

    if not docs_to_embed:
        print(f"[INFO] No document changes detected for agent {agent_id}")
        return None, None
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs_to_embed)

    vectordb, persist_path = create_vector_store(
        agent.vector_store_type,
        agent_id,
        embeddings,
        chunks
    )

    return vectordb, persist_path

def get_rag_context(question: str, vectordb, k: int = 3):
    """
    SAFE RAG QUERY - prevents NoneType crash
    """

    if vectordb is None:
        raise ValueError("[RAG] Vector DB is not initialized")

    docs_found = vectordb.similarity_search(question, k=k)

    if not docs_found:
        return "", []

    context = "\n\n".join([d.page_content for d in docs_found])
    metadata_list = [d.metadata for d in docs_found]

    return context, metadata_list

    # def get_rag_context(question: str, vectordb, k: int = 3):
#     docs_found = vectordb.similarity_search(question, k=k)
#     if not docs_found:
#         return "", []

#     context = "\n\n".join([d.page_content for d in docs_found])
#     metadata_list = [d.metadata for d in docs_found]
#     return context, metadata_list
