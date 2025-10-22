# from extract_text import extract_text
# from section_splitter import split_sections
# from llm_parser import parse_resume_with_llm
# from query_builder import build_job_query

# def main(file_path):
#     # Step 1: Extract
#     text = extract_text(file_path)
#     print("✅ Extracted raw text")

#     # Step 2: Split
#     sections = split_sections(text)
#     combined_text = " ".join(sections.values())
#     print("✅ Sections split")

#     # Step 3: Parse
#     structured = parse_resume_with_llm(combined_text)
#     print("✅ Parsed structured data:", structured)

#     # Step 4: Build query
#     query = build_job_query(structured)
#     print("\n🧠 Generated Job Query Prompt:\n")
#     print(query)

# if __name__ == "__main__":
#     path = input("Enter CV file path: ")
#     main(path)

from .extract_text import TextExtractor
from .section_splitter import UniversalSectionSplitter
from .llm_parser import UniversalParser
from .query_builder import UniversalQueryBuilder

class ResumeQueryBuilder:
    def __init__(self, google_api_key: str = None):
        self.text_extractor = TextExtractor()
        self.section_splitter = UniversalSectionSplitter()
        self.parser = UniversalParser(google_api_key)
        self.query_builder = UniversalQueryBuilder(google_api_key)
    
    def process_resume(self, file_path: str, file_type: str):
        """Main processing pipeline"""
        # Extract text
        text = self.text_extractor.extract_text(file_path, file_type)
        
        # Split into sections
        sections = self.section_splitter.split_into_sections(text)
        
        # Parse with LLM
        cv_data = self.parser.parse_cv(text, sections)
        
        # Build query
        job_query = self.query_builder.build_job_query(cv_data.dict())
        
        return {
            'raw_text': text,
            'sections': sections,
            'parsed_data': cv_data,
            'job_query': job_query
        }