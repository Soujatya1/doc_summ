
import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing_extensions import Concatenate

#Streamlit interface
st.title("Document Summary Generator")
uploaded_file = st.file_uploader("Upload a PDF file", type = "pdf")

if uploaded_file is not None:
  pdf = PdfReader(uploaded_file)

  #Read text from pdf
  text = ''
  for i, page in enumerate(pdf.pages):
      content = page.extract_text()
      if content:
          text += content

  docs = [Document(page_content = text)]

  api_key = "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"

  llm = ChatGroq(groq_api_key = api_key, model_name = 'llama-3.3-70b-versatile', temperature = 0.2, top_p = 0.2)

  template = '''Write a very concise, well-explained, point-wise, short summary of the following text. I will tip you $1000, if you provide good and user-acceptable response.
  HR: '{text}. Also, mention what the document uploaded is aimed at doing, as in its purpose.'
  '''

  prompt = PromptTemplate(
      input_variables = ['text'],
      template = template
  )

  result=[]
  chain = load_summarize_chain(
      llm,
      chain_type = 'stuff',
      prompt = prompt,
      verbose = False
  )
  output_summary = chain.invoke(docs)
  output = output_summary['output_text']
  print(output)

  st.write("Summary:")
  st.write(output)
else:
  st.write("Please upload a PDF file.")
