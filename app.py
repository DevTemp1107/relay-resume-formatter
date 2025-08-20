import streamlit as st
import base64
import requests
from jinja2 import Environment, BaseLoader, FileSystemLoader
import os
import tempfile
import re
import json
import zipfile
from pathlib import Path
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Formatter",
    page_icon="📄",
    layout="wide"
)

# Initialize session state for templates
if 'available_templates' not in st.session_state:
    st.session_state['available_templates'] = {}
if 'template_content' not in st.session_state:
    st.session_state['template_content'] = ""

def load_available_templates():
    """Load all available templates from the templates directory"""
    templates = {}
    template_dir = "template"
    
    if os.path.exists(template_dir):
        for file in os.listdir(template_dir):
            if file.endswith(('.html', '.htm')):
                template_path = os.path.join(template_dir, file)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        templates[file] = f.read()
                except Exception as e:
                    st.warning(f"Could not load template {file}: {str(e)}")
    
    return templates

def save_template(name, content):
    """Save a template to the templates directory"""
    template_dir = "templates"
    os.makedirs(template_dir, exist_ok=True)
    
    # Ensure the filename has .html extension
    if not name.endswith(('.html', '.htm')):
        name += '.html'
    
    template_path = os.path.join(template_dir, name)
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, template_path
    except Exception as e:
        return False, str(e)

def extract_template_from_zip(zip_file):
    """Extract templates from uploaded ZIP file"""
    templates = {}
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(('.html', '.htm')) and not file_info.is_dir():
                    content = zip_ref.read(file_info.filename).decode('utf-8')
                    templates[os.path.basename(file_info.filename)] = content
    except Exception as e:
        st.error(f"Error extracting ZIP file: {str(e)}")
    
    return templates

def clean_html_for_display(html_content):
    """Clean HTML content to handle non-ASCII characters"""
    def replace_char(match):
        char = match.group(0)
        return f'&#{ord(char)};'
    
    return re.sub(r'[^\x00-\x7F]', replace_char, html_content)

def process_resume(uploaded_file, api_endpoint, api_key, template_content):
    """Process the uploaded resume file"""
    try:
        # Read and encode the file
        file_bytes = uploaded_file.read()
        encoded = base64.b64encode(file_bytes).decode('utf-8')
        
        # Prepare API request
        body = {
            "resume_filename": uploaded_file.name,
            "resume_base64_encoded": encoded
        }
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            # Alternative header formats (uncomment if needed)
            # headers["X-API-Key"] = api_key
            # headers["Ocp-Apim-Subscription-Key"] = api_key
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Make API request
        status_text.text("📄 Processing resume with AI...")
        progress_bar.progress(25)
        
        response = requests.post(api_endpoint, json=body, headers=headers, timeout=60)
        progress_bar.progress(50)
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None, None, None
        
        # Parse response
        output = response.json().get('data', {})
        progress_bar.progress(75)
        
        # Render template
        status_text.text("🎨 Rendering template...")
        
        if template_content:
            env = Environment(loader=BaseLoader())
            template = env.from_string(template_content)
            rendered_html = template.render(output)
            
            # Clean HTML for display
            cleaned_html = clean_html_for_display(rendered_html)
        else:
            rendered_html = cleaned_html = "<p>No template selected</p>"
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        return output, rendered_html, cleaned_html
        
    except requests.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None, None, None
    except Exception as e:
        st.error(f"Processing Error: {str(e)}")
        return None, None, None

# Title and description
st.title("📄 Resume Formatter")
st.markdown("Upload a PDF resume to format it using AI processing")

# Load available templates
st.session_state['available_templates'] = load_available_templates()

# Sidebar for configuration
st.sidebar.header("🔧 Configuration")

# API Configuration
api_endpoint = os.getenv("PROMPTFLOW_ENDPOINT", "")
api_key = os.getenv("PROMPTFLOW_API_KEY", "")

# Template Management Section
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Template Management")

# Template selection
template_options = ["Select a template..."] + list(st.session_state['available_templates'].keys())
selected_template = st.sidebar.selectbox(
    "Choose Template",
    options=template_options,
    help="Select an existing template"
)

# Load selected template
if selected_template != "Select a template..." and selected_template in st.session_state['available_templates']:
    st.session_state['template_content'] = st.session_state['available_templates'][selected_template]

# Template upload options
upload_option = st.sidebar.radio(
    "Upload New Template",
    ["Single HTML File", "ZIP Archive", "Manual Entry"]
)

if upload_option == "Single HTML File":
    uploaded_template = st.sidebar.file_uploader(
        "Upload HTML Template",
        type=['html', 'htm'],
        help="Upload a single HTML template file"
    )
    
    if uploaded_template is not None:
        template_content = uploaded_template.read().decode('utf-8')
        template_name = uploaded_template.name
        
        if st.sidebar.button("💾 Save Template"):
            success, result = save_template(template_name, template_content)
            if success:
                st.sidebar.success(f"Template saved: {result}")
                st.session_state['available_templates'] = load_available_templates()
                st.session_state['template_content'] = template_content
                st.rerun()
            else:
                st.sidebar.error(f"Error saving template: {result}")

elif upload_option == "ZIP Archive":
    uploaded_zip = st.sidebar.file_uploader(
        "Upload ZIP with Templates",
        type=['zip'],
        help="Upload a ZIP file containing multiple HTML templates"
    )
    
    if uploaded_zip is not None:
        extracted_templates = extract_template_from_zip(uploaded_zip)
        
        if extracted_templates:
            st.sidebar.write(f"Found {len(extracted_templates)} templates:")
            for name in extracted_templates.keys():
                st.sidebar.write(f"- {name}")
            
            if st.sidebar.button("💾 Save All Templates"):
                saved_count = 0
                for name, content in extracted_templates.items():
                    success, result = save_template(name, content)
                    if success:
                        saved_count += 1
                
                if saved_count > 0:
                    st.sidebar.success(f"Saved {saved_count} templates")
                    st.session_state['available_templates'] = load_available_templates()
                    st.rerun()

elif upload_option == "Manual Entry":
    with st.sidebar.expander("✏️ Create/Edit Template"):
        new_template_name = st.text_input("Template Name", value="custom_template.html")
        new_template_content = st.text_area(
            "Template Content (Jinja2/HTML)",
            value=st.session_state.get('template_content', ''),
            height=200,
            help="Enter your Jinja2 template content"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save"):
                if new_template_name and new_template_content:
                    success, result = save_template(new_template_name, new_template_content)
                    if success:
                        st.success(f"Template saved!")
                        st.session_state['available_templates'] = load_available_templates()
                        st.session_state['template_content'] = new_template_content
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
        
        with col2:
            if st.button("📝 Load"):
                st.session_state['template_content'] = new_template_content

# Template preview
if st.session_state.get('template_content'):
    with st.sidebar.expander("👀 Template Preview"):
        st.code(st.session_state['template_content'][:500] + "..." if len(st.session_state['template_content']) > 500 else st.session_state['template_content'], language='html')

# Main interface
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📤 Upload Resume")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF resume to process"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"📊 File size: {len(uploaded_file.getvalue())} bytes")
        
        # Template validation
        if not st.session_state.get('template_content'):
            st.warning("⚠️ Please select or upload a template first")
        
        # Process button
        if st.button("🚀 Process Resume", type="primary", disabled=not st.session_state.get('template_content')):
            if not api_endpoint:
                st.error("Please configure API endpoint")
            else:
                with st.spinner("Processing..."):
                    output_data, raw_html, cleaned_html = process_resume(
                        uploaded_file, api_endpoint, api_key, st.session_state['template_content']
                    )
                    
                    if output_data and cleaned_html:
                        # Store results in session state
                        st.session_state['output_data'] = output_data
                        st.session_state['raw_html'] = raw_html
                        st.session_state['cleaned_html'] = cleaned_html
                        st.session_state['filename'] = uploaded_file.name

with col2:
    st.header("📋 Results")
    
    # Display results if available
    if 'output_data' in st.session_state:
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Parsed Data", "🎨 HTML Preview", "💾 Downloads", "🔧 Raw HTML"])
        
        with tab1:
            st.subheader("Extracted Data")
            
            # Display the parsed data in a nice format
            if st.session_state['output_data']:
                # Create expandable sections for different data types
                for key, value in st.session_state['output_data'].items():
                    with st.expander(f"📝 {key.title()}"):
                        if isinstance(value, dict):
                            st.json(value)
                        elif isinstance(value, list):
                            for i, item in enumerate(value):
                                st.write(f"**Item {i+1}:**", item)
                        else:
                            st.write(value)
            else:
                st.info("No data available")
        
        with tab2:
            st.subheader("HTML Preview")
            
            # Display HTML preview
            if st.session_state['cleaned_html']:
                # Show HTML in a container
                st.components.v1.html(
                    st.session_state['cleaned_html'], 
                    height=600, 
                    scrolling=True
                )
            else:
                st.info("No HTML available")
        
        with tab3:
            st.subheader("Download Files")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Download HTML file
                if 'raw_html' in st.session_state:
                    st.download_button(
                        label="📄 Download HTML",
                        data=st.session_state['raw_html'],
                        file_name=f"{Path(st.session_state['filename']).stem}_formatted.html",
                        mime="text/html",
                        help="Download the formatted HTML file"
                    )
            
            with col4:
                # Download JSON data
                if 'output_data' in st.session_state:
                    json_data = json.dumps(st.session_state['output_data'], indent=2)
                    st.download_button(
                        label="📊 Download JSON",
                        data=json_data,
                        file_name=f"{Path(st.session_state['filename']).stem}_data.json",
                        mime="application/json",
                        help="Download the extracted data as JSON"
                    )
            
            # Download base64 encoded file
            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                encoded = base64.b64encode(file_bytes).decode('utf-8')
                st.download_button(
                    label="🔗 Download Base64",
                    data=encoded,
                    file_name=f"{Path(uploaded_file.name).stem}_base64.txt",
                    mime="text/plain",
                    help="Download the base64 encoded version"
                )
        
        with tab4:
            st.subheader("Raw HTML Code")
            
            if 'raw_html' in st.session_state:
                st.code(st.session_state['raw_html'], language='html')
            else:
                st.info("No HTML code available")
    
    else:
        st.info("👆 Upload a PDF file and click 'Process Resume' to see results")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🚀 Resume Formatter App | Built by Sumant</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Additional features in sidebar
st.sidebar.markdown("---")
st.sidebar.header("📋 Features")
st.sidebar.markdown("""
- 📤 **Upload PDF**: Support for PDF resume files
- 🤖 **AI Processing**: Connect to your PromptFlow API
- 📋 **Template Management**: Upload, save, and manage templates
- 🎨 **Live Preview**: See results in real-time
- 💾 **Multiple Downloads**: HTML, JSON, and Base64 formats
- 🔧 **Environment Config**: Use .env file for API settings
- 📦 **ZIP Support**: Upload multiple templates at once
""")

# Environment setup info
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Environment Setup")
with st.sidebar.expander("📝 .env Configuration"):
    st.markdown("""
    Create a `.env` file in your project root:
    
    ```
    PROMPTFLOW_ENDPOINT=https://your-endpoint.com/score
    PROMPTFLOW_API_KEY=your-api-key-here
    ```
    
    **Supported Authentication:**
    - Bearer Token (default)
    - API Key headers
    - Azure subscription keys
    """)

# Error handling info
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Troubleshooting")
with st.sidebar.expander("Common Issues"):
    st.markdown("""
    **API Connection Issues:**
    - Check if your API endpoint is running
    - Verify the URL format (include https://)
    - Ensure API key is correct
    
    **Template Issues:**
    - Check Jinja2 template syntax
    - Ensure variables match API response
    - Test with simple template first
    
    **File Upload Issues:**
    - Only PDF files are supported
    - Check file size limits
    - Ensure file is not corrupted
    """)

# Development mode toggle
if st.sidebar.checkbox("🔧 Development Mode"):
    st.sidebar.markdown("### Debug Info")
    debug_info = {
        "API Endpoint": api_endpoint,
        "API Key Set": bool(api_key),
        "Template Selected": bool(st.session_state.get('template_content')),
        "Available Templates": len(st.session_state['available_templates']),
        "Template Names": list(st.session_state['available_templates'].keys())
    }
    
    if 'output_data' in st.session_state:
        debug_info["Data Keys"] = list(st.session_state['output_data'].keys()) if st.session_state['output_data'] else []
    
    st.sidebar.json(debug_info)