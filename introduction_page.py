import requests
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH


GEMINI_API_KEY = "AIzaSyCmFMR-XyUb2GdR1Hdub5_g_C6xjnpTqaA"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

def fetch_introduction(topic, report_type='college'):
    """
    Fetch Introduction content for the given topic using the Gemini API.
    The introduction will be tailored for either school or college reports.
    """
    # Different prompts for school vs college reports
    if report_type == 'school':
        prompt = (f"Create an introduction for the topic: {topic}. Format it strictly as follows:\n\n\n\n"
                        
                        "Managing personal finances can be challenging, often leading to overspending or inadequate savings. An expense tracker is an essential tool to help individuals monitor and control their spending habits. This project aims to develop an expense tracker using Python, a powerful and versatile programming language known for its simplicity and extensive library support.\n"
                        "The expense tracker will enable users to log daily expenses, categorize them, and analyze their spending patterns over various time periods. By providing visualizations and summaries, users can gain insights into their financial behavior and make informed decisions. Additionally, the tracker will feature budget management, allowing users to set spending limits for different categories and receive alerts when they approach or exceed these limits.\n"
                        "The project will leverage Python’s robust libraries, such as SQLite for database management, Tkinter for creating a user-friendly graphical interface. This expense tracker aims to empower users to take control of their finances through detailed tracking, insightful analysis, and effective budget management."
                        "Keep it to 1-2 short paragraphs maximum.")
    else:
        prompt = (f"Create an introduction for the topic: {topic}. Format it strictly as follows:\n\n\n\n"
                        
                        "Managing personal finances can be challenging, often leading to overspending or inadequate savings. An expense tracker is an essential tool to help individuals monitor and control their spending habits. This project aims to develop an expense tracker using Python, a powerful and versatile programming language known for its simplicity and extensive library support.\n"
                        "The expense tracker will enable users to log daily expenses, categorize them, and analyze their spending patterns over various time periods. By providing visualizations and summaries, users can gain insights into their financial behavior and make informed decisions. Additionally, the tracker will feature budget management, allowing users to set spending limits for different categories and receive alerts when they approach or exceed these limits.\n"
                        "The project will leverage Python’s robust libraries, such as SQLite for database management, Tkinter for creating a user-friendly graphical interface. This expense tracker aims to empower users to take control of their finances through detailed tracking, insightful analysis, and effective budget management."
                        "Keep it to 1-2 paragraphs maximum.")
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    params = {'key': GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_URL, headers=HEADERS, params=params, json=data)
        response.raise_for_status()
        content = response.json()
        if 'candidates' in content and len(content['candidates']) > 0:
            return content['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"No content found for Introduction on topic: {topic}."
    except requests.exceptions.RequestException as e:
        return f"Error fetching Introduction content: {e}"
    

def post_process_introduction_to_doc(text, document, report_type='college'):
    """
    Format the introduction section and add it to the Word document.
    Adds a heading followed by the text, with different formatting for school and college reports.
    Applies justification and advanced formatting settings.
    """
    # Set Times New Roman as Default Font
    style = document.styles['Normal']
    style.font.name = 'Times New Roman'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    # Split the introduction into paragraphs
    paragraphs = text.strip().split('\n')

    for para in paragraphs:
        if para.strip():  # Skip empty lines
            p = document.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.widow_control = True
            p.paragraph_format.keep_together = True
            p.paragraph_format.keep_with_next = True

            run = p.add_run(para.strip())
            run.font.name = 'Times New Roman'

            # Font size and style differences for report types
            if report_type == 'school':
                run.font.size = Pt(12)
            else:  # college
                run.font.size = Pt(12)  # Use same size or change to Pt(11) if needed



