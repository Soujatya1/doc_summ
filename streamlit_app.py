import streamlit as st
from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Document Summary", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        """Format section titles in bold with reduced spacing"""
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, title, ln=True, align="L")
        self.ln(2)

    def chapter_body(self, body):
        """Format body text with reduced spacing"""
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, body)
        self.ln(2)

    def add_bullet_points(self, text):
        """Formats bullet points with reduced spacing"""
        self.set_font("Arial", "", 11)
        lines = text.split("\n")
        for line in lines:
            if line.strip():
                self.cell(5)
                self.cell(0, 5, f"• {line}", ln=True)
        self.ln(2)

# Streamlit interface
st.title("Document Summary Generator")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    pdf = PdfReader(uploaded_file)

    # Read text from PDF
    text = ''
    for page in pdf.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"

    docs = [Document(page_content=text)]


    llm = ChatGroq(groq_api_key='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', model_name='llama3-70b-8192', temperature=0.2, top_p=0.2)

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

    st.write("### Summary:")
    st.write(output)

    
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    
    sections = ["Overview", "Involved Parties", "Key Events", "Key Findings"]
    formatted_summary = {}

   
    for i in range(len(sections)):
        start = output.find(sections[i])
        end = output.find(sections[i + 1]) if i + 1 < len(sections) else len(output)
        if start != -1:
            formatted_summary[sections[i]] = output[start + len(sections[i]):end].strip()

    
    for section, content in formatted_summary.items():
        pdf.chapter_title(section)
        if "•" in content:  
            pdf.add_bullet_points(content)
        else:
            pdf.chapter_body(content)

    # Save the PDF
    pdf_output_path = "summary_output.pdf"
    pdf.output(pdf_output_path)

    # Provide download link
    with open(pdf_output_path, "rb") as pdf_file:
        st.download_button("Download Summary PDF", pdf_file, file_name="summary_output.pdf", mime="application/pdf")

else:
    st.write("Please upload a PDF file.")
