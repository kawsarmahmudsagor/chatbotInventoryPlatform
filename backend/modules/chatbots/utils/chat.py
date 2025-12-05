from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from chatbot.chatbotInventoryPlatform.backend.modules.rag import rag_service
from backend.core.config import settings


GOOGLE_API_KEY = settings.GOOGLE_API_KEY


model = init_chat_model(
    model="google_genai:gemini-2.5-flash-lite",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a virtual sales assistant in an e-commerce store. "
               "Converse with users as if you are a real-life sales assistant: friendly, professional, and approachable. "
               "Be formal and don't joke around too much."
               "Proactively suggest products or promotions based on the user's previous interactions and purchase history. "
               "Anticipate the user's needs, ask clarifying questions politely, and make personalized recommendations. "
               "Keep conversations natural and engaging, as if the user is talking to a knowledgeable and personable sales expert."),
    ("human", "Conversation so far:\n{history}\n\nNew question:\n{question}")
])

chain = prompt | model


def handle_conversation_single_turn(history: str, question: str):
    
    rag_context, rag_metadata = rag_service.get_rag_context(question)

    if rag_context:
        metadata_text = "\n".join([f"{m}" for m in rag_metadata])
        full_question = (
            f"Use the context below to answer the question accurately.\n\n"
            f"CONTEXT:\n{rag_context}\n\n"
            f"METADATA:\n{metadata_text}\n\n"
            f"QUESTION:\n{question}"
        )
    else:
        full_question = (
            f"No relevant company or product policy information was found.\n"
            f"Answer based only on the user question if possible.\n\nQUESTION:\n{question}"
        )

    history = ""
    response = chain.invoke({
        "history": history,
        "question": full_question
    })

    ai_text = response.content

    return ai_text, history

def handle_conversation_multi_turn(history: str, question: str):
    
    rag_context, rag_metadata = rag_service.get_rag_context(question)

    if rag_context:
        # Include both context and metadata in the prompt
        metadata_text = "\n".join([f"{m}" for m in rag_metadata])
        full_question = (
            f"Use the context below to answer the question accurately.\n\n"
            f"CONTEXT:\n{rag_context}\n\n"
            f"METADATA:\n{metadata_text}\n\n"
            f"QUESTION:\n{question}"
        )
    else:
        full_question = (
            f"No relevant company or product policy information was found.\n"
            f"Answer based only on the user question if possible.\n\nQUESTION:\n{question}"
        )

    response = chain.invoke({
        "history": history,
        "question": full_question
    })

    ai_text = response.content

    new_history = history + f"\nUser: {question}\nAI: {ai_text}"

    return ai_text, new_history
