# app/rag.py
import os
from shutil import rmtree
from pathlib import Path
from backend.core.config import settings
from chatbot.chatbotInventoryPlatform.backend.modules.rag.utils.convert_to_text import convert_to_txt
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

class RagService():

    
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY

    def embedd_document(documents_dir: str):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        vector_embeddings_dir = os.path.join(current_dir, "../embeddings")
        if os.path.exists(vector_embeddings_dir):
            rmtree(vector_embeddings_dir)

        os.makedirs(vector_embeddings_dir, exist_ok=True)

        def load_documents_from_folder(folder: Path):
            docs = []
            for file_path in folder.iterdir():
                if file_path.suffix.lower() in [".pdf", ".docx", ".doc"]:
                    text = convert_to_txt(file_path)
                    docs.append(Document(page_content=text, metadata={"source": str(file_path.name)}))
            return docs

        docs = load_documents_from_folder(documents_dir)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )


        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=vector_embeddings_dir
        )
        vectordb.persist()

    # ----------------------------
    # Helper function
    # ----------------------------
    def get_rag_context(question: str):
        """
        Get relevant context and metadata from vector store for a question.
        """
        docs_found = vectordb.similarity_search(question, k=3)

        if not docs_found:
            return "", []

        # Concatenate document content
        context = "\n\n".join([d.page_content for d in docs_found])
        metadata_list = [d.metadata for d in docs_found]

        return context, metadata_list
