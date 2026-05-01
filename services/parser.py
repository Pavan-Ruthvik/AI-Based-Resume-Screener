import pdfplumber
import docx
import pandas as pd
import os

def parse_file(file_obj, filename):
    ext = os.path.splitext(filename)[1].lower()
    name = os.path.splitext(filename)[0]
    
    try:
        if ext == '.pdf':
            text = ""
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return {"name": name, "text": text}
            
        elif ext == '.docx':
            doc = docx.Document(file_obj)
            text = "\n".join([para.text for para in doc.paragraphs])
            return {"name": name, "text": text}
            
        elif ext == '.csv':
            df = pd.read_csv(file_obj)
            resume_col = 'Resume' if 'Resume' in df.columns else 'resume'
            if resume_col not in df.columns:
                raise ValueError("CSV must contain a 'Resume' column")
            
            results = []
            for idx, row in df.iterrows():
                c_name = row.get('Name', row.get('name', f"Candidate_{idx+1}"))
                results.append({"name": str(c_name), "text": str(row[resume_col])})
            return results
            
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
    except Exception as e:
        return {"name": name, "error": str(e)}