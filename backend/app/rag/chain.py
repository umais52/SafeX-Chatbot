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
     "1. If the user says 'hi' or greets you, respond politely with: 'Hello! I am the SafeX AI assistant. How can I help you today?'\n"
     "2. For all other questions, answer ONLY using the Context below.\n"
     "3. If the Context does not contain the answer, you MUST reply EXACTLY with: 'I have forwarded this to our human expert.'\n"
     "4. Keep your answers brief and professional.\n\n"
     "Context:\n{context}"),
    ("human", "{question}")
])

# 2. Shared Embeddings and Vector Store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

from app.config import settings

# 3. LLM
llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=settings.GOOGLE_API_KEY)

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
