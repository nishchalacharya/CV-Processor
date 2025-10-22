# import re

# def split_sections(text: str) -> dict:
#     """
#     Splits a CV text into common sections using regex heuristics.
#     """
#     sections = {
#         "experience": "",
#         "education": "",
#         "skills": "",
#         "certifications": "",
#         "projects": "",
#         "summary": ""
#     }

#     # Normalize
#     text = text.replace("\n", " ")

#     # Split by common section names
#     parts = re.split(r'(?i)(experience|work experience|education|academic background|skills|technical skills|certifications|projects|summary|profile)', text)

#     # Build dictionary
#     for i in range(1, len(parts), 2):
#         key = parts[i].strip().lower()
#         if key in sections:
#             sections[key] = parts[i+1].strip()

#     return sections








import re
from typing import Dict, List

class UniversalSectionSplitter:
    def __init__(self):
        # Universal section headers across all professions
        self.section_patterns = {
            'contact': r'(?:contact|personal|details|information)',
            'summary': r'(?:summary|objective|profile|about)',
            'experience': r'(?:experience|work\s*history|employment|career)',
            'education': r'(?:education|academic|qualifications|degrees)',
            'skills': r'(?:skills|competencies|expertise|technical\s*skills)',
            'projects': r'(?:projects|portfolio|work\s*samples)',
            'certifications': r'(?:certifications|licenses|accreditations)',
            'awards': r'(?:awards|honors|achievements)',
            'languages': r'(?:languages|language\s*skills)',
            'publications': r'(?:publications|papers|research)'
        }
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Split CV text into sections using universal patterns"""
        sections = {}
        lines = text.split('\n')
        
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            section_found = self._identify_section(line_clean)
            
            if section_found and section_found != current_section:
                # Save previous section
                if current_content and current_section:
                    sections[current_section] = ' '.join(current_content).strip()
                
                # Start new section
                current_section = section_found
                current_content = [line_clean]
            else:
                current_content.append(line_clean)
        
        # Save the last section
        if current_content and current_section:
            sections[current_section] = ' '.join(current_content).strip()
        
        return sections
    
    def _identify_section(self, line: str) -> str:
        """Identify which section a line belongs to"""
        line_lower = line.lower()
        
        # Check for section headers (often in ALL CAPS, bold, or followed by colons)
        if len(line) < 100:  # Likely a header if short
            for section, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower) or self._is_section_header(line):
                    return section
        
        return None
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header"""
        # Headers are often short, in caps, or have specific formatting
        if len(line.strip()) < 50:
            if line.isupper() or line.endswith(':') or re.search(r'^[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*:$', line):
                return True
        return False
