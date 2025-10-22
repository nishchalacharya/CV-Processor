ResumeQueryBuilder/
│
├── src/
│   ├── extract_text.py           # Extract text from PDFs/DOCX/TXT
│   ├── section_splitter.py       # Regex-based section splitter
│   ├── llm_parser.py             # LLM (Gemini) semantic parser
│   ├── query_builder.py          # Convert structured info → job query
│   └── main.py                   # Entry point
│
├── app.py                        # streamlit 
├── requirements.txt
└── README.md


FLOW:


[ CV File (pdf/docx/txt) ]
          ↓
extract_text.py → Extract raw text
          ↓
section_splitter.py → Find Experience, Skills, Education sections
          ↓
llm_parser.py → Use Gemini or Groq to extract structured info
          ↓
query_builder.py → Create a structured prompt or query for RAG
