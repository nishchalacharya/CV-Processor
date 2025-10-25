


import google.generativeai as genai
import json
import os
import re
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
# from config.prompts import UNIVERSAL_EXTRACTION_PROMPT



UNIVERSAL_EXTRACTION_PROMPT = """
You are an expert at extracting structured information from resumes/CVs of ALL professions including:
- Engineering (civil, electrical, mechanical, software)
- Healthcare (doctors, nurses, therapists)
- Business (finance, accounting, management)
- Education (teachers, professors, administrators)
- Creative fields (design, writing, marketing)
- Skilled trades (construction, automotive, technical)
- And many other professions

Analyze the resume text below and extract the information in valid JSON format.

RESUME TEXT:
{cv_text}

Extract and return ONLY valid JSON with these exact fields:

{{
  "profession_field": "Primary professional field detected",
  "experience_years": "Total years of professional experience as number",
  "education": [
    {{"degree": "Degree name", "field": "Field of study", "institution": "School name"}}
  ],
  "skills": ["List of professional skills mentioned"],
  "job_titles": ["Previous job titles/positions found"],
  "industries": ["Industries worked in"],
  "technical_skills": ["Technical/professional skills specific to field"],
  "soft_skills": ["Communication, leadership, interpersonal skills"],
  "tools_technologies": ["Software, tools, equipment used"],
  "certifications": ["Professional certifications, licenses"],
  "languages": ["Languages spoken"],
  "key_achievements": ["Major accomplishments mentioned"],
  "education_level": "Highest education level (Bachelor's, Master's, PhD, etc.)",
  "summary": "Brief 2-3 sentence professional summary"
}}

IMPORTANT: 
- Return ONLY valid JSON, no other text
- Be completely profession-agnostic
- Estimate experience years if not explicitly stated
- Focus on the actual content of the resume
"""

UNIVERSAL_QUERY_PROMPT = """
Create a comprehensive and optimized job search query for this professional profile:

PROFESSION: {profession}
EXPERIENCE: {experience} years
EDUCATION LEVEL: {education_level}
PREVIOUS ROLES: {job_titles}
KEY SKILLS: {skills}
TECHNICAL EXPERTISE: {technical_skills}
TOOLS & TECHNOLOGIES: {tools}
INDUSTRIES: {industries}
KEY ACHIEVEMENTS: {achievements}

Generate a detailed search query that would effectively find relevant job opportunities on platforms like LinkedIn, Indeed, and other job boards.

The query should:
1. Include appropriate job titles based on experience level and profession
2. Mention key technical skills and technologies
3. Specify experience level when relevant
4. Include important frameworks, tools, and methodologies
5. Be specific enough to find quality matches but broad enough to capture opportunities
6. Use industry-standard terminology

Examples of good queries:
- "Junior Machine Learning Engineer Python TensorFlow Django FastAPI"
- "Backend Developer Python Django REST APIs Docker AWS"
- "AI Developer Machine Learning Deep Learning NLP Computer Vision"

Return ONLY the search query text, no explanations or additional text.
"""















class UniversalCVData(BaseModel):
    profession_field: str = "Professional"
    experience_years: float = 0.0
    education: List[Dict[str, str]] = []
    skills: List[str] = []
    job_titles: List[str] = []
    industries: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    tools_technologies: List[str] = []
    certifications: List[str] = []
    languages: List[str] = []
    key_achievements: List[str] = []
    education_level: str = "Unknown"
    summary: str = ""

class UniversalParser:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    def parse_cv(self, cv_text: str, sections: Dict[str, str] = None) -> UniversalCVData:
        """Parse CV text with robust fallback methods"""
        
        # First try LLM parsing if API key is available
        if self.model:
            try:
                llm_result = self._parse_with_llm(cv_text)
                if llm_result and (llm_result.experience_years > 0 or llm_result.skills or llm_result.job_titles):
                    return llm_result
            except Exception as e:
                print(f"LLM parsing failed: {e}")
        
        # Use enhanced rule-based parsing as fallback
        return self._truly_universal_parse(cv_text)
    
    def _parse_with_llm(self, cv_text: str) -> UniversalCVData:
        """Parse using Gemini LLM"""
        prompt = UNIVERSAL_EXTRACTION_PROMPT.format(
            cv_text=cv_text[:3000]  # Limit text length for LLM
        )
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result_data = json.loads(json_str)
            return UniversalCVData(**result_data)
        else:
            raise ValueError("No JSON found in LLM response")
    
    def _truly_universal_parse(self, cv_text: str) -> UniversalCVData:
        """Truly universal parsing for ALL professions"""
        text_lower = cv_text.lower()
        lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
        
        return UniversalCVData(
            profession_field=self._detect_profession_universal(text_lower, lines),
            experience_years=self._extract_experience_universal(text_lower, lines),
            education=self._extract_education_universal(lines),
            skills=self._extract_skills_universal(text_lower, lines),
            job_titles=self._extract_job_titles_universal(lines),
            industries=self._extract_industries_universal(text_lower),
            technical_skills=self._extract_technical_skills_universal(text_lower),
            soft_skills=self._extract_soft_skills_universal(text_lower),
            tools_technologies=self._extract_tools_universal(text_lower),
            certifications=self._extract_certifications_universal(lines),
            languages=self._extract_languages_universal(text_lower),
            key_achievements=self._extract_achievements_universal(lines),
            education_level=self._extract_education_level_universal(text_lower),
            summary=self._generate_summary_universal(cv_text)
        )
    
    def _detect_profession_universal(self, text_lower: str, lines: List[str]) -> str:
        """Detect profession from ANY field"""
        profession_categories = {
            # Engineering & Technical
            'Civil Engineering': ['civil engineer', 'structural engineer', 'construction', 'infrastructure', 'cad technician', 'site engineer'],
            'Electrical Engineering': ['electrical engineer', 'electronics engineer', 'power systems', 'circuit design', 'embedded systems'],
            'Mechanical Engineering': ['mechanical engineer', 'manufacturing engineer', 'cad designer', 'solidworks', 'thermodynamics'],
            'Software Engineering': ['software engineer', 'developer', 'programmer', 'full stack', 'frontend', 'backend'],
            
            # Healthcare & Medical
            'Healthcare': ['registered nurse', 'nurse practitioner', 'medical doctor', 'physician', 'healthcare', 'patient care'],
            'Dentistry': ['dentist', 'dental hygienist', 'orthodontist', 'dental assistant'],
            'Pharmacy': ['pharmacist', 'pharmacy technician', 'pharmaceutical'],
            'Therapy': ['physical therapist', 'occupational therapist', 'speech therapist'],
            
            # Business & Finance
            'Finance': ['financial analyst', 'accountant', 'cpa', 'investment banker', 'wealth management'],
            'Accounting': ['accountant', 'auditor', 'bookkeeper', 'tax specialist'],
            'Banking': ['banker', 'loan officer', 'branch manager', 'financial advisor'],
            
            # Management & Administration
            'Management': ['project manager', 'operations manager', 'general manager', 'team lead'],
            'HR': ['hr manager', 'recruiter', 'talent acquisition', 'human resources'],
            'Administration': ['administrative assistant', 'office manager', 'executive assistant'],
            
            # Education
            'Education': ['teacher', 'professor', 'educator', 'faculty', 'instructor', 'curriculum'],
            'Academic Research': ['researcher', 'research assistant', 'scientist', 'postdoc'],
            
            # Creative & Design
            'Design': ['graphic designer', 'ux designer', 'ui designer', 'creative director'],
            'Marketing': ['marketing manager', 'digital marketing', 'brand manager', 'seo specialist'],
            'Writing': ['writer', 'content writer', 'copywriter', 'technical writer'],
            
            # Sales & Customer Service
            'Sales': ['sales representative', 'account executive', 'business development', 'sales manager'],
            'Customer Service': ['customer service', 'client support', 'help desk', 'service representative'],
            
            # Legal
            'Legal': ['lawyer', 'attorney', 'paralegal', 'legal assistant', 'counsel'],
            
            # Skilled Trades
            'Construction Trades': ['carpenter', 'electrician', 'plumber', 'welder', 'contractor'],
            'Automotive': ['auto mechanic', 'technician', 'automotive engineer'],
            
            # Science & Research
            'Science': ['biologist', 'chemist', 'physicist', 'research scientist', 'lab technician'],
        }
        
        # Score professions based on keyword matches
        profession_scores = {}
        for profession, keywords in profession_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                profession_scores[profession] = score
        
        if profession_scores:
            return max(profession_scores.items(), key=lambda x: x[1])[0]
        
        return "Professional"
    
    def _extract_experience_universal(self, text_lower: str, lines: List[str]) -> float:
        """Extract years of experience for any profession"""
        # Direct year patterns
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?.*experience',
        ]
        
        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years = float(match)
                    max_years = max(max_years, years)
                except:
                    continue
        
        # Date range analysis
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current|now)'
        date_matches = re.findall(date_pattern, text_lower)
        if date_matches:
            total_years = 0
            for start, end in date_matches:
                try:
                    if end in ['present', 'current', 'now']:
                        end_year = 2024
                    else:
                        end_year = int(end)
                    start_year = int(start)
                    total_years += (end_year - start_year)
                except:
                    continue
            if total_years > 0:
                max_years = max(max_years, total_years)
        
        return max_years
    
    def _extract_education_universal(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract education information for any field"""
        education = []
        education_keywords = [
            'university', 'college', 'institute', 'school', 'academy',
            'bachelor', 'master', 'phd', 'doctorate', 'mba', 
            'degree', 'diploma', 'certificate', 'graduated'
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                # Extract degree type
                degree = "Unknown"
                degree_patterns = {
                    'PhD': r'\b(phd|doctorate)\b',
                    'Master\'s': r'\b(master|ms|m\.s|mba|m\.a|m\.sc)\b',
                    'Bachelor\'s': r'\b(bachelor|bs|b\.s|ba|b\.a|bsc|b\.sc)\b',
                    'Associate\'s': r'\b(associate|a\.a|a\.s)\b',
                    'Diploma': r'\b(diploma)\b',
                    'Certificate': r'\b(certificate)\b'
                }
                
                for deg_name, pattern in degree_patterns.items():
                    if re.search(pattern, line_lower):
                        degree = deg_name
                        break
                
                education.append({
                    "degree": degree,
                    "field": self._extract_field_universal(line),
                    "institution": line.strip()
                })
        
        return education[:3]
    
    def _extract_skills_universal(self, text_lower: str, lines: List[str]) -> List[str]:
        """Extract skills for ANY profession"""
        skills = set()
        
        # Universal professional skills
        universal_skills = [
            'project management', 'team leadership', 'communication', 'problem solving',
            'analytical skills', 'strategic planning', 'budget management', 'client relations',
            'research', 'training', 'mentoring', 'quality assurance', 'process improvement',
            'teamwork', 'collaboration', 'critical thinking', 'time management', 'organization',
            'public speaking', 'presentation skills', 'negotiation', 'decision making'
        ]
        
        # Add matching universal skills
        for skill in universal_skills:
            if skill in text_lower:
                skills.add(skill.title())
        
        # Field-specific skills patterns
        field_skills = {
            'engineering': ['cad design', 'structural analysis', 'circuit design', 'system integration'],
            'healthcare': ['patient care', 'medical terminology', 'clinical skills', 'health assessment'],
            'finance': ['financial analysis', 'accounting', 'budgeting', 'financial reporting'],
            'education': ['curriculum development', 'classroom management', 'lesson planning', 'student assessment'],
            'sales': ['sales techniques', 'client acquisition', 'account management', 'sales forecasting'],
            'design': ['design principles', 'color theory', 'typography', 'layout design']
        }
        
        # Add field-specific skills
        for field, field_skill_list in field_skills.items():
            if field in text_lower:
                for skill in field_skill_list:
                    if skill in text_lower:
                        skills.add(skill.title())
        
        # Extract from skills section
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['skill', 'competenc', 'expertise', 'proficient']) and len(line.strip()) < 60:
                # Check next lines for skills
                for j in range(i+1, min(i+8, len(lines))):
                    skill_line = lines[j].strip()
                    if skill_line and len(skill_line) < 80:
                        if not any(section in skill_line.lower() for section in ['experience', 'education', 'work']):
                            skills.add(skill_line)
        
        return list(skills)[:15]
    
    def _extract_job_titles_universal(self, lines: List[str]) -> List[str]:
        """Extract job titles from any profession"""
        titles = set()
        
        # Common job title patterns across all fields
        title_indicators = [
            'manager', 'director', 'coordinator', 'specialist', 'analyst', 
            'engineer', 'consultant', 'assistant', 'associate', 'officer',
            'supervisor', 'lead', 'head', 'chief', 'president', 'vice president',
            'teacher', 'instructor', 'professor', 'researcher', 'scientist',
            'technician', 'therapist', 'nurse', 'doctor', 'dentist',
            'designer', 'writer', 'editor', 'producer', 'artist'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if 5 < len(line_stripped) < 80:  # Reasonable title length
                line_lower = line_stripped.lower()
                
                # Check if line contains title indicators
                if any(indicator in line_lower for indicator in title_indicators):
                    titles.add(line_stripped)
                
                # Check for title-like patterns (capitalized, not sentences)
                elif (line_stripped.istitle() or 
                      (sum(1 for c in line_stripped if c.isupper()) > len(line_stripped) * 0.3)):
                    titles.add(line_stripped)
        
        return list(titles)[:10]
    
    def _extract_industries_universal(self, text_lower: str) -> List[str]:
        """Extract industries from any field"""
        industries = set()
        
        industry_keywords = {
            'Technology': ['technology', 'software', 'it', 'tech', 'saas', 'hardware'],
            'Finance': ['finance', 'banking', 'investment', 'financial services', 'insurance'],
            'Healthcare': ['healthcare', 'medical', 'hospital', 'pharmaceutical', 'biotech'],
            'Education': ['education', 'academic', 'school', 'university', 'learning'],
            'Manufacturing': ['manufacturing', 'production', 'industrial', 'factory'],
            'Construction': ['construction', 'building', 'real estate', 'property'],
            'Retail': ['retail', 'e-commerce', 'consumer goods', 'merchandise'],
            'Consulting': ['consulting', 'professional services', 'advisory'],
            'Government': ['government', 'public sector', 'federal', 'state', 'municipal'],
            'Non-profit': ['non-profit', 'nonprofit', 'charity', 'ngo'],
            'Hospitality': ['hospitality', 'hotel', 'restaurant', 'tourism'],
            'Transportation': ['transportation', 'logistics', 'shipping', 'supply chain'],
            'Energy': ['energy', 'utilities', 'oil', 'gas', 'renewable'],
            'Media': ['media', 'entertainment', 'publishing', 'broadcast'],
            'Legal': ['legal', 'law firm', 'attorney', 'courthouse']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                industries.add(industry)
        
        return list(industries)
    
    def _extract_technical_skills_universal(self, text_lower: str) -> List[str]:
        """Extract technical skills for any profession (not just IT)"""
        technical_skills = set()
        
        # Software & IT (for all professions)
        software_skills = [
            'microsoft office', 'excel', 'word', 'powerpoint', 'outlook',
            'google workspace', 'sheets', 'docs', 'slides',
            'quickbooks', 'salesforce', 'sap', 'oracle'
        ]
        
        # Engineering tools
        engineering_tools = ['autocad', 'revit', 'solidworks', 'matlab', 'ansys', 'catia']
        
        # Design tools
        design_tools = ['photoshop', 'illustrator', 'indesign', 'figma', 'sketch', 'canva']
        
        # Healthcare systems
        healthcare_systems = ['epic', 'cerner', 'meditech', 'ehr', 'electronic health records']
        
        # Add relevant technical skills based on content
        all_technical = software_skills + engineering_tools + design_tools + healthcare_systems
        for skill in all_technical:
            if skill in text_lower:
                technical_skills.add(skill.title())
        
        return list(technical_skills)[:10]
    
    def _extract_soft_skills_universal(self, text_lower: str) -> List[str]:
        """Extract soft skills applicable to all professions"""
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
            'adaptability', 'time management', 'creativity', 'collaboration', 'negotiation',
            'presentation', 'public speaking', 'interpersonal', 'emotional intelligence',
            'conflict resolution', 'decision making', 'strategic thinking', 'coaching',
            'mentoring', 'customer service', 'client management', 'stakeholder management'
        ]
        
        return [skill.title() for skill in soft_skills if skill in text_lower]
    
    def _extract_tools_universal(self, text_lower: str) -> List[str]:
        """Extract tools and technologies for any profession"""
        tools = set()
        
        # Universal office tools
        office_tools = [
            'microsoft office', 'google workspace', 'slack', 'teams', 'zoom',
            'sharepoint', 'onedrive', 'dropbox', 'asana', 'trello', 'jira'
        ]
        
        # Industry-specific tools
        industry_tools = {
            'engineering': ['autocad', 'revit', 'solidworks', 'matlab', 'ansys', 'arcgis'],
            'design': ['photoshop', 'illustrator', 'indesign', 'figma', 'sketch', 'canva'],
            'healthcare': ['epic', 'cerner', 'meditech', 'ehr', 'pharmacy software'],
            'finance': ['quickbooks', 'sage', 'xero', 'bloomberg', 'reuters'],
            'education': ['blackboard', 'canvas', 'moodle', 'learning management system']
        }
        
        # Add office tools
        for tool in office_tools:
            if tool in text_lower:
                tools.add(tool.title())
        
        # Add industry-specific tools
        for industry, tool_list in industry_tools.items():
            if industry in text_lower:
                for tool in tool_list:
                    if tool in text_lower:
                        tools.add(tool.title())
        
        return list(tools)
    
    def _extract_certifications_universal(self, lines: List[str]) -> List[str]:
        """Extract certifications for any profession"""
        certs = set()
        cert_keywords = [
            'certified', 'certification', 'license', 'licensed', 'accredited',
            'pmp', 'cpa', 'pe', 'cpr', 'aed', 'first aid', 'six sigma',
            'lean', 'scrum', 'agile', 'aws certified', 'google certified'
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                cert_text = line.strip()
                if len(cert_text) < 100:
                    certs.add(cert_text)
        
        return list(certs)[:5]
    
    def _extract_languages_universal(self, text_lower: str) -> List[str]:
        """Extract languages"""
        languages = set()
        common_langs = [
            'english', 'spanish', 'french', 'german', 'chinese', 'hindi',
            'arabic', 'portuguese', 'russian', 'japanese', 'korean', 'italian'
        ]
        
        for lang in common_langs:
            if lang in text_lower:
                languages.add(lang.title())
        
        return list(languages)
    
    def _extract_achievements_universal(self, lines: List[str]) -> List[str]:
        """Extract key achievements for any profession"""
        achievements = []
        achievement_indicators = [
            'achieved', 'implemented', 'led', 'managed', 'increased', 'reduced',
            'improved', 'developed', 'created', 'established', 'launched',
            'won', 'awarded', 'recognized', 'completed', 'delivered'
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in achievement_indicators):
                if 15 < len(line.strip()) < 250:  # Reasonable achievement length
                    achievements.append(line.strip())
        
        return achievements[:5]
    
    def _extract_education_level_universal(self, text_lower: str) -> str:
        """Extract highest education level"""
        if 'phd' in text_lower or 'doctorate' in text_lower:
            return "PhD"
        elif 'master' in text_lower or 'ms' in text_lower or 'mba' in text_lower or 'm.a' in text_lower:
            return "Master's"
        elif 'bachelor' in text_lower or 'bs' in text_lower or 'ba' in text_lower or 'b.a' in text_lower:
            return "Bachelor's"
        elif 'associate' in text_lower or 'a.a' in text_lower or 'a.s' in text_lower:
            return "Associate's"
        elif 'diploma' in text_lower:
            return "Diploma"
        elif 'certificate' in text_lower:
            return "Certificate"
        else:
            return "Unknown"
    
    def _extract_field_universal(self, line: str) -> str:
        """Extract field of study for any profession"""
        fields = {
            'Computer Science': ['computer science', 'cs', 'software engineering', 'information technology'],
            'Engineering': ['engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'aerospace'],
            'Business': ['business', 'business administration', 'mba', 'management', 'marketing'],
            'Finance': ['finance', 'accounting', 'economics', 'banking', 'investment'],
            'Mathematics': ['mathematics', 'math', 'statistics', 'applied math'],
            'Science': ['physics', 'chemistry', 'biology', 'environmental science', 'geology'],
            'Healthcare': ['medicine', 'nursing', 'pharmacy', 'public health', 'health sciences'],
            'Education': ['education', 'teaching', 'curriculum', 'educational leadership'],
            'Arts': ['arts', 'fine arts', 'design', 'music', 'theater', 'drama'],
            'Social Sciences': ['psychology', 'sociology', 'political science', 'anthropology'],
            'Humanities': ['history', 'english', 'literature', 'philosophy', 'languages']
        }
        
        line_lower = line.lower()
        for field, keywords in fields.items():
            if any(keyword in line_lower for keyword in keywords):
                return field
        
        return "General Studies"
    
    def _generate_summary_universal(self, cv_text: str) -> str:
        """Generate a professional summary for any field"""
        lines = [line.strip() for line in cv_text.split('\n') if line.strip() and len(line.strip()) > 15]
        if lines:
            # Use the first meaningful lines as summary
            summary = " ".join(lines[:2])
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary
        return "Experienced professional with demonstrated skills and accomplishments."