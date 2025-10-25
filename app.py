

import streamlit as st
import os
import tempfile
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.main import ResumeQueryBuilder
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please check that all required files exist in the correct locations.")
    st.stop()

def main():
    st.set_page_config(
        page_title="Universal Resume Query Builder",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🌍 Universal Resume Query Builder")
    st.markdown("Upload any profession's resume to generate optimized job search queries")
    
    # Load environment variables
    load_dotenv()
    
    # API key input
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password", 
                                   value=os.getenv('GOOGLE_API_KEY', ''))
    
    if not api_key:
        st.info("Please enter your Google Gemini API key in the sidebar to continue")
        st.info("You can also create a .env file with GOOGLE_API_KEY=your_key_here")
        return
    
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Supports resumes from any profession: engineering, finance, healthcare, management, etc."
    )
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, 
                                       suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            file_type = os.path.splitext(uploaded_file.name)[1].lower()[1:]
            
            with st.spinner("Processing resume..."):
                processor = ResumeQueryBuilder(api_key)
                result = processor.process_resume(tmp_path, file_type)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Extracted Profile")
                data = result['parsed_data']
                
                st.metric("Profession", data.profession_field)
                st.metric("Experience", f"{data.experience_years} years")
                st.metric("Education Level", data.education_level)
                
                st.write("**Skills:**")
                for skill in data.skills[:10]:
                    st.write(f"• {skill}")
                
                st.write("**Job Titles:**")
                for title in data.job_titles[:5]:
                    st.write(f"• {title}")
            
            with col2:
                st.subheader("🛠️ Technical Profile")
                
                if data.technical_skills:
                    st.write("**Technical Skills:**")
                    for skill in data.technical_skills[:8]:
                        st.write(f"• {skill}")
                
                if data.tools_technologies:
                    st.write("**Tools & Technologies:**")
                    for tool in data.tools_technologies[:8]:
                        st.write(f"• {tool}")
                
                if data.certifications:
                    st.write("**Certifications:**")
                    for cert in data.certifications[:5]:
                        st.write(f"• {cert}")
            
            # Generated query
            st.subheader("🚀 Generated Job Search Query")
            st.code(result['job_query'], language="text")
            
            # Debug information
            with st.expander("🔍 Query Generation Details"):
                st.write("**Data used for query generation:**")
                st.json({
                    'profession': data.profession_field,
                    'experience_years': data.experience_years,
                    'job_titles': data.job_titles,
                    'skills': data.skills[:5],
                    'technical_skills': data.technical_skills[:5],
                    'tools': data.tools_technologies[:5]
                })
            
            # Raw data
            with st.expander("View Raw Data"):
                st.json(result['parsed_data'].dict())
        
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

if __name__ == "__main__":
    main()