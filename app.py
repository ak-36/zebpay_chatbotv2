import streamlit as st
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer

st.set_page_config(page_title="ZebPay Chatbot v2", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("ZiVa💬🦙")
st.info("Your Guide to cryto-trading", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about waste management!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_files=["1.docx", "2.docx", "3.docx", "chat_history.docx"], recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, system_prompt="You are an assistant who is expert in cryptocurrency. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
         memory = ChatMemoryBuffer.from_defaults(token_limit=15000)
         st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", memory=memory, system_prompt="You are a customer support chatbot and an expert in cryptocurrency. If you do not find any answers to the question just say 'Connecting you to customer support'", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
