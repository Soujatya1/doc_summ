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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fpdf import FPDF

#Streamlit interface
st.title("Document Summary Generator")
uploaded_file = st.file_uploader("Upload a PDF file", type = "pdf")

if uploaded_file is not None:
    pdf = PdfReader(uploaded_file)

    # Read text from PDF
    text = ''
    for page in pdf.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"

    docs = [Document(page_content=text)]

    # API Key (Replace with your actual API key)
    api_key = "your_groq_api_key"

    llm = ChatGroq(groq_api_key=api_key, model_name='llama3-70b-8192', temperature=0.2, top_p=0.2)

    template = '''Write a very concise, well-explained, point-wise, short summary of the following text. Provide good and user-acceptable response.
    '{text}
    Create section-wise summary.
    The format should be:
    Overview
    Involved Parties
    Key Events
    Key Findings
    The summary should be formatted correctly as per this
    The Key events section needs to be more elaborate and each event should have a heading to it also in a pointer manner'
    '''

    prompt = PromptTemplate(input_variables=['text'], template=template)

    chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt, verbose=False)
    output_summary = chain.invoke(docs)
    output = output_summary['output_text']

    # Display summary on Streamlit
    st.write("### Summary:")
    st.write(output)

    # Generate a PDF with formatted text
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Document Summary", ln=True, align="C")
            self.ln(10)

        def chapter_title(self, title):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, ln=True, align="L")
            self.ln(5)

        def chapter_body(self, body):
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 8, body)
            self.ln(5)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    sections = ["Overview", "Involved Parties", "Key Events", "Key Findings"]
    for section in sections:
        if section in output:
            pdf.chapter_title(section)
            section_text = output.split(section, 1)[1].split("\n", 1)[1].strip()
            pdf.chapter_body(section_text)

    # Save the PDF
    pdf_output_path = "summary_output.pdf"
    pdf.output(pdf_output_path)

    # Provide download link
    with open(pdf_output_path, "rb") as pdf_file:
        st.download_button("Download Summary PDF", pdf_file, file_name="summary_output.pdf", mime="application/pdf")

else:
    st.write("Please upload a PDF file.")
