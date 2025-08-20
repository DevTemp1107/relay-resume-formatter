# 📄 Resume Formatter

A powerful Streamlit application that processes PDF resumes using AI and formats them using customizable Jinja2 templates. Perfect for standardizing resumes across organizations or creating consistent formatting for recruitment processes.

## ✨ Features

- **📤 PDF Resume Upload** - Support for PDF resume files
- **🤖 AI Processing** - Integration with PromptFlow API for resume parsing
- **📋 Template Management** - Upload, save, and manage Jinja2 templates
- **🎨 Live Preview** - Real-time HTML preview of formatted resumes
- **💾 Multiple Export Formats** - Download as HTML, JSON, or Base64
- **🔧 Environment Configuration** - Secure API settings via .env file
- **📦 Bulk Template Upload** - ZIP file support for multiple templates
- **👀 Template Preview** - View and edit templates before processing
- **🛠️ Debug Mode** - Development tools and diagnostics

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd resume-formatter
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:
```env
PROMPTFLOW_ENDPOINT=https://your-promptflow-endpoint.com/score
PROMPTFLOW_API_KEY=your-api-key-here
```

### 4. Run the Application
```bash
streamlit run main.py
```

The app will be available at `http://localhost:8501`

## 📋 Requirements

Create a `requirements.txt` file with:
```txt
streamlit>=1.28.0
requests>=2.31.0
jinja2>=3.1.0
python-dotenv>=1.0.0
```

## 📁 Project Structure

```
resume-formatter/
├── app.py              # Main Streamlit application
├── .env                 # Environment variables (create this)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── template/          # Template storage (auto-created)
    ├── basic.html
    ├── modern.html
    └── corporate.html
```

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `PROMPTFLOW_ENDPOINT` | Your PromptFlow API endpoint URL | Yes |
| `PROMPTFLOW_API_KEY` | API key for authentication | Yes |

### API Endpoint Requirements

Your API endpoint should:
- Accept POST requests
- Receive JSON payload with:
  ```json
  {
    "resume_filename": "resume.pdf",
    "resume_base64_encoded": "base64_string_here"
  }
  ```
- Return JSON response with:
  ```json
  {
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "experience": [...],
      // ... other parsed data
    }
  }
  ```

## 📋 Template Management

### Creating Templates

Templates use Jinja2 syntax and should reference variables from your API response:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Resume - {{ name }}</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #f0f0f0; padding: 20px; }
        .section { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ name }}</h1>
        <p>{{ email }} | {{ phone }}</p>
    </div>
    
    {% if summary %}
    <div class="section">
        <h2>Summary</h2>
        <p>{{ summary }}</p>
    </div>
    {% endif %}
    
    {% if experience %}
    <div class="section">
        <h2>Experience</h2>
        {% for job in experience %}
        <div class="job">
            <h3>{{ job.title }} - {{ job.company }}</h3>
            <p><em>{{ job.duration }}</em></p>
            <p>{{ job.description }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if skills %}
    <div class="section">
        <h2>Skills</h2>
        <ul>
        {% for skill in skills %}
            <li>{{ skill }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>
```

### Template Upload Options

1. **Single HTML File** - Upload individual template files
2. **ZIP Archive** - Upload multiple templates at once
3. **Manual Entry** - Create/edit templates directly in the UI

## 🔧 Usage Guide

### Step 1: Configure API Settings
- Set your PromptFlow endpoint and API key in the sidebar
- Or use the `.env` file for persistent configuration

### Step 2: Select or Upload Template
- Choose from existing templates in the dropdown
- Upload new templates via file upload or ZIP archive
- Create custom templates using the manual entry option

### Step 3: Upload Resume
- Click "Choose a PDF file" to upload your resume
- Supported format: PDF files only
- File size should be reasonable for API processing

### Step 4: Process Resume
- Click "🚀 Process Resume" to start processing
- Wait for AI processing and template rendering
- View results in the tabs on the right

### Step 5: Download Results
- **HTML**: Formatted resume ready for viewing/printing
- **JSON**: Raw extracted data for further processing
- **Base64**: Encoded resume file for storage

## 🛠️ Troubleshooting

### Common Issues

#### API Connection Problems
```
Error: API Error: 401 - Unauthorized
```
**Solution**: Check your API key and endpoint URL in `.env` file

#### Template Errors
```
Error: Template syntax error
```
**Solution**: Validate your Jinja2 template syntax, ensure variables match API response

#### File Upload Issues
```
Error: File upload failed
```
**Solution**: Ensure PDF file is not corrupted and within size limits

### Debug Mode
Enable debug mode in the sidebar to see:
- Current configuration
- Available template
- API response structure
- Template variables

## 🔒 Security Notes

- API keys are stored in `.env` file (never commit to version control)
- Add `.env` to your `.gitignore` file
- Use HTTPS endpoints for production
- Validate all template content before use

## 📚 API Integration Examples

### Azure AI Services
```env
PROMPTFLOW_ENDPOINT=https://your-resource.cognitiveservices.azure.com/formrecognizer/documentModels/prebuilt-document:analyze
PROMPTFLOW_API_KEY=your-azure-key
```

### Custom API
```env
PROMPTFLOW_ENDPOINT=https://your-api.com/parse-resume
PROMPTFLOW_API_KEY=your-custom-key
```

### Local Development
```env
PROMPTFLOW_ENDPOINT=http://localhost:8080/score
PROMPTFLOW_API_KEY=development-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Enable debug mode for more information
3. Check the Streamlit logs for error details
4. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your configuration (without API keys)

## 🔄 Version History

- **v1.0.0** - Initial release with basic functionality

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)

---

## 📞 Contact

For questions or support, please reach out through:
- GitHub Issues
- Email: sumant.pujari@relayhumancloud.com

**Happy Resume Formatting! 🎉**