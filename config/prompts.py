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