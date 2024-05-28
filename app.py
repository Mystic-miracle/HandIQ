import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import torch



from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers
from langchain.llms import Replicate


from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
import tempfile
from dotenv import load_dotenv


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.create_documents(text)
    return chunks

def detect_document(image_bytes):
    generated_text=" "
    """Detects document features in an image."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)

    response = client.document_text_detection(image=image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print(f"\nBlock confidence: {block.confidence}\n")

            for paragraph in block.paragraphs:
                print("Paragraph confidence: {}".format(paragraph.confidence))

                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    print(
                        "Word text: {} (confidence: {})".format(
                            word_text, word.confidence
                        )
                    )
                    
                    generated_text+=" "+word_text

                    for symbol in word.symbols:
                        print(
                            "\tSymbol: {} (confidence: {})".format(
                                symbol.text, symbol.confidence
                            )
                        )

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    
    print(generated_text)
    return generated_text
    


# def get_pdf_text(pdf_docs):
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     return text
#________________________________________________MYCODE ends____________________________________________#


load_dotenv()
# def initialize_session_state():
#     if 'history' not in st.session_state:
#         st.session_state['history'] = []

#     if 'generated' not in st.session_state:
#         st.session_state['generated'] = ["Hello! You can ask me anything related to your notes"]

#     if 'past' not in st.session_state:
#         st.session_state['past'] = ["Hey"]

# def conversation_chat(query, chain, history):
#     result = chain({"question": query, "chat_history": history})
#     history.append((query, result["answer"]))
#     return result["answer"]

# def display_chat_history(chain):
#     reply_container = st.container()
#     container = st.container()
#     print("hello chat")

#     with container:
#         with st.form(key='my_form', clear_on_submit=False):
#             user_input = st.text_input("Question:", placeholder="Ask about your notes", key='input')
#             submit_button = st.form_submit_button(label='Send')
#             print("heello message")
#             print("user input"+user_input)

#         if submit_button and user_input:
#             with st.spinner('Generating response...'):
#                 output = conversation_chat(user_input, chain, st.session_state['history'])

#             print("heello message/submit")
#             st.session_state['past'].append(user_input)
#             st.session_state['generated'].append(output)

#     if st.session_state['generated']:
#         with reply_container:
#             for i in range(len(st.session_state['generated'])):
#                 message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
#                 message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

# def create_conversational_chain(vector_store):
#     load_dotenv()
#     llm = Replicate(
#         streaming = True,
#         model = "replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781", 
#         callbacks=[StreamingStdOutCallbackHandler()],
#         input = {"temperature": 0.01, "max_length" :500,"top_p":1})
#     memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
#     chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
#                                                  retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
#                                                  memory=memory)
#     return chain

# def main():
#     load_dotenv()
#     initialize_session_state()


#     st.title("HandIQ")
    
   
#     st.subheader("Your documents")
#     pdf_docs = st.file_uploader(
#             "Upload your notes here and click on 'Process'", accept_multiple_files=True)
#     if st.button("Process") :
#                 with st.spinner("Processing"):
#                      img_bytes = pdf_docs[0].read()
#                      raw_text=detect_document(img_bytes)
                    
#                      text=[]
#                      text.extend(get_text_chunks(raw_text))

  
#                      text_chunks = text
#                 # Create embeddings
                
#                      embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", 
#                                            model_kwargs={'device': 'cuda:0'})

#         # Create vector store
#                      vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)

#         # Create the chain object
#                      chain = create_conversational_chain(vector_store)
    
   

        

        
                
#                      display_chat_history(chain)

# if __name__ == "__main__":
#     main()


# #_________________________________________________________________________________________________#






def get_vectorstore(text_chunks):
    #embeddings = OpenAIEmbeddings()
    
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl",
                                       model_kwargs={'device': 'cuda:0'})
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    #llm = ChatOpenAI()
    
    llm = HuggingFaceHub(repo_id="google/flan-t5-xxl",model_kwargs={"temperature":0.5, "max_length":512}, huggingfacehub_api_token="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")
   

    

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain





def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
           st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="handIQ",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("handIQ :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your notes here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                #get text from images
                img_bytes = pdf_docs[0].read() 
                raw_text=detect_document(img_bytes)
                # get pdf text
                #raw_text = get_pdf_text(pdf_docs)
                text=[]
                text.extend(raw_text)

                # get the text chunks
                #text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text)

                # create conversation chain
                print("start now")
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)


if __name__ == '__main__':
    main()
