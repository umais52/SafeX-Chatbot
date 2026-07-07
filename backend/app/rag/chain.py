from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory

qa_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are the SafeX Solutions Support Assistant.\n"
     "RULES:\n"
     "1. If the user says 'hi' or greets you, respond politely.\n"
     "2. If the user makes a conversational follow-up or formatting request (e.g., 'ok', 'thanks', 'list in bullet points', 'bold it'), fulfill it using the Chat History.\n"
     "3. For factual questions about SafeX, use ONLY the Context below.\n"
     "4. If a factual question cannot be answered using the Context or Chat History, you MUST reply EXACTLY with: 'The answer to this question is not available in the context provided by SafeX. If you would like me to send your request to an admin, please provide your email address (e.g., xyz@example.com).'\n"
     "5. Keep your answers professional.\n\n"
     "Context:\n{context}\n\n"
     "Chat History:\n{chat_history}"),
    ("human", "{question}")
])

# 2. Shared Embeddings and Vector Store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

from app.config import settings
from langchain_ollama import ChatOllama

# 3. LLM Configuration with Fallback
gemini_llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)
ollama_llm = ChatOllama(model=settings.OLLAMA_FALLBACK_MODEL, base_url=settings.OLLAMA_BASE_URL)
llm = gemini_llm.with_fallbacks([ollama_llm])

# 4. Global Memory Map
# This maps session_id to its own ConversationBufferWindowMemory instance.
_session_memories = {}

def get_chain_for_session(session_id: str) -> ConversationalRetrievalChain:
    """Returns a chain configured with the specific memory for this session."""
    if session_id not in _session_memories:
        _session_memories[session_id] = ConversationBufferWindowMemory(
            k=5, 
            memory_key="chat_history", 
            return_messages=True, 
            output_key="answer"
        )
    
    # Rebuild the chain to attach this specific session's memory
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=_session_memories[session_id],
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        return_source_documents=True
    )
