


import google.generativeai as genai
import os
from typing import Dict, Any, List

class UniversalQueryBuilder:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def build_job_query(self, cv_data: Dict[str, Any]) -> str:
        """Build optimized job query for ANY profession"""
        
        # Prepare the data for the prompt
        prompt_data = self._prepare_prompt_data(cv_data)
        
        if self.model:
            try:
                return self._build_query_with_llm(prompt_data)
            except Exception as e:
                print(f"LLM query generation failed: {e}")
        
        # Fallback to universal rule-based query building
        return self._build_universal_query(prompt_data)
    
    def _prepare_prompt_data(self, cv_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare and format data for query generation"""
        # Calculate actual experience
        experience_years = self._calculate_real_experience(cv_data)
        
        # Extract and format lists
        skills = cv_data.get('skills', [])[:8]
        technical_skills = cv_data.get('technical_skills', [])[:10]
        job_titles = cv_data.get('job_titles', [])[:5]
        tools = cv_data.get('tools_technologies', [])[:8]
        industries = cv_data.get('industries', [])[:3]
        
        return {
            'profession': cv_data.get('profession_field', 'Professional'),
            'experience': experience_years,
            'education_level': cv_data.get('education_level', ''),
            'job_titles': ", ".join(job_titles) if job_titles else "",
            'skills': ", ".join(skills) if skills else "",
            'technical_skills': ", ".join(technical_skills) if technical_skills else "",
            'tools': ", ".join(tools) if tools else "",
            'industries': ", ".join(industries) if industries else "",
            'summary': cv_data.get('summary', '')[:200]
        }
    
    def _calculate_real_experience(self, cv_data: Dict[str, Any]) -> float:
        """Calculate real experience from work history"""
        base_experience = cv_data.get('experience_years', 0)
        
        # If experience is 0 but has work history, calculate real experience
        if base_experience == 0:
            job_titles = cv_data.get('job_titles', [])
            achievements = cv_data.get('key_achievements', [])
            
            # Check for professional experience indicators
            experience_indicators = [
                'intern', 'fellow', 'trainee', 'assistant', 'associate',
                'worked', 'employed', 'position', 'role'
            ]
            
            has_professional_experience = any(
                any(indicator in title.lower() for indicator in experience_indicators)
                for title in job_titles
            )
            
            # Estimate based on role types
            if any('fellow' in title.lower() for title in job_titles):
                return 0.5  # 6-month fellowship
            elif any('intern' in title.lower() for title in job_titles):
                return 0.3  # 3-month internship
            elif has_professional_experience:
                return 0.5  # General professional experience
            
            # Check for substantial project experience
            project_keywords = ['developed', 'managed', 'led', 'created', 'implemented']
            project_count = sum(1 for achievement in achievements 
                              if any(keyword in achievement.lower() for keyword in project_keywords))
            
            if project_count >= 2:
                return 0.3  # Project-based experience
        
        return base_experience
    
    def _build_query_with_llm(self, prompt_data: Dict[str, str]) -> str:
        """Build query using Gemini LLM for any profession"""
        prompt = f"""
        Create a clean, effective job search query for this professional:

        Profession: {prompt_data['profession']}
        Experience: {prompt_data['experience']} years
        Education: {prompt_data['education_level']}
        Previous Roles: {prompt_data['job_titles']}
        Key Skills: {prompt_data['skills']}
        Technical Skills: {prompt_data['technical_skills']}
        Tools: {prompt_data['tools']}
        Industries: {prompt_data['industries']}
        Summary: {prompt_data['summary']}

        Create a natural job search query that:
        - Uses plain language (NO parentheses, OR operators, or excessive quotes)
        - Includes appropriate experience level
        - Mentions key skills and qualifications relevant to the profession
        - Is optimized for job platforms like LinkedIn, Indeed, etc.
        - Works for ANY profession (engineering, healthcare, business, education, etc.)

        Return ONLY the query text, nothing else.
        """
        
        response = self.model.generate_content(prompt)
        query = response.text.strip()
        
        # Clean up the query
        query = self._clean_query(query)
        return query
    
    def _build_universal_query(self, data: Dict[str, Any]) -> str:
        """Build professional query for ANY field without tech bias"""
        query_parts = []
        
        # 1. Experience level (universal across all professions)
        experience = data['experience']
        if experience >= 5:
            exp_level = "Senior"
        elif experience >= 2:
            exp_level = ""
        elif experience >= 1:
            exp_level = "Junior"
        else:
            exp_level = "Entry-level"
        
        # 2. Primary profession/role
        profession = data['profession']
        if exp_level:
            query_parts.append(f"{exp_level} {profession}")
        else:
            query_parts.append(profession)
        
        # 3. Add specific role types if available
        job_titles = [title for title in data['job_titles'].split(', ') if title]
        if job_titles and len(job_titles[0].split()) <= 4:  # Reasonable title length
            query_parts.append(job_titles[0])
        
        # 4. Add key skills (profession-agnostic)
        key_skills = self._extract_universal_skills(data)
        query_parts.extend(key_skills[:3])
        
        # 5. Add industries if relevant
        industries = [ind for ind in data['industries'].split(', ') if ind]
        if industries and industries[0].lower() not in profession.lower():
            query_parts.append(industries[0])
        
        # 6. Add education for entry-level positions
        if experience < 1 and data['education_level']:
            query_parts.append(f"{data['education_level']}")
        
        # Remove duplicates and clean
        unique_parts = []
        for part in query_parts:
            if part and part not in unique_parts and len(part) > 2:
                unique_parts.append(part)
        
        return " ".join(unique_parts)
    
    def _extract_universal_skills(self, data: Dict[str, Any]) -> List[str]:
        """Extract relevant skills for any profession"""
        all_skills = []
        
        # Add technical skills (relevant to any profession)
        tech_skills = [skill for skill in data['technical_skills'].split(', ') if skill]
        all_skills.extend(tech_skills[:4])
        
        # Add general skills
        general_skills = [skill for skill in data['skills'].split(', ') if skill]
        all_skills.extend(general_skills[:3])
        
        # Add tools (relevant to any profession)
        tools = [tool for tool in data['tools'].split(', ') if tool]
        all_skills.extend(tools[:2])
        
        return all_skills
    
    def _clean_query(self, query: str) -> str:
        """Clean up the query - remove operators, quotes, etc."""
        # Remove common problematic patterns
        query = query.replace('"', '').replace('(', '').replace(')', '')
        query = query.replace(' OR ', ' ').replace(' AND ', ' ')
        query = query.replace('|', ' ')
        query = ' '.join(query.split())  # Normalize whitespace
        
        return query