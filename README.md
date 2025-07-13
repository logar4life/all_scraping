# Unified County Scraping API

A FastAPI-based unified scraping system for three counties: Fairfax, Loudoun, and PWCBA. Each endpoint runs a complete workflow: **scrape → process PDFs → analyze**.

## 🏗️ Architecture

The API provides 3 main endpoints, one for each county:

- **Fairfax**: `/fairfax/run-complete-workflow`
- **Loudoun**: `/loudoun/run-complete-workflow`  
- **PWCBA**: `/pwcba/run-complete-workflow`

Each endpoint follows the same workflow:
1. **Scrape**: Run the county-specific scraper to download PDFs
2. **Process PDFs**: Use OCR to make PDFs searchable
3. **Analyze**: Extract key information using AI analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test the API

```bash
# Run the test script
python test_api.py
```

## 📋 API Endpoints

### Root Endpoint
- **GET** `/` - Get API information and available endpoints

### County Endpoints

#### Fairfax County
- **POST** `/fairfax/run-complete-workflow`
  - Runs Fairfax scraper
  - Processes Fairfax PDFs with OCR
  - Analyzes Fairfax images

#### Loudoun County  
- **POST** `/loudoun/run-complete-workflow`
  - Runs Loudoun scraper
  - Processes Loudoun PDFs with OCR
  - Analyzes Loudoun PDFs

#### PWCBA County
- **POST** `/pwcba/run-complete-workflow`
  - Runs PWCBA scraper
  - Processes PWCBA PDFs with OCR
  - Analyzes PWCBA PDFs

## 📊 Response Format

Each endpoint returns a JSON response with the following structure:

```json
{
  "status": "success|error|partial_success",
  "steps": {
    "scraping": {
      "status": "success|error",
      "result": {...}
    },
    "pdf_processing": {
      "status": "success|error", 
      "result": {...}
    },
    "analysis": {
      "status": "success|error",
      "result": {...}
    }
  },
  "errors": ["error1", "error2"]
}
```

## 🔧 Usage Examples

### Using curl

```bash
# Test Fairfax workflow
curl -X POST "http://localhost:8000/fairfax/run-complete-workflow"

# Test Loudoun workflow  
curl -X POST "http://localhost:8000/loudoun/run-complete-workflow"

# Test PWCBA workflow
curl -X POST "http://localhost:8000/pwcba/run-complete-workflow"
```

### Using Python requests

```python
import requests

# Run Fairfax workflow
response = requests.post("http://localhost:8000/fairfax/run-complete-workflow")
data = response.json()
print(f"Status: {data['status']}")

# Check individual steps
for step, step_data in data['steps'].items():
    print(f"{step}: {step_data['status']}")
```

## 📁 Project Structure

```
final_scraping/
├── main.py                 # FastAPI application
├── test_api.py            # API testing script
├── requirements.txt        # Python dependencies
├── fairfax/
│   └── fairfax.py        # Fairfax scraper
├── loudoun/
│   └── loudoun.py        # Loudoun scraper  
├── pwcba/
│   └── pwcba.py          # PWCBA scraper
└── shared/
    ├── unified_pdf_processor.py  # PDF processing utilities
    └── unified_analyzer.py       # AI analysis utilities
```

## 🔍 Workflow Details

### Step 1: Scraping
- Each county has its own scraper that:
  - Logs into the county website
  - Searches for documents
  - Downloads PDFs to county-specific folders

### Step 2: PDF Processing  
- Uses EasyOCR to extract text from PDFs
- Creates searchable PDF versions
- Removes duplicates (optional)
- Organizes files by county

### Step 3: Analysis
- Uses OpenAI GPT-4 to extract key information:
  - Owner names
  - Property addresses  
  - Tax IDs/APNs
  - Document dates
- Saves results to CSV files

## ⚙️ Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for analysis

### PDF Processing Options
- Duplicate removal: Enabled by default
- OCR DPI: 300 (configurable)
- Output format: Searchable PDFs

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - Ensure Chrome is installed
   - Check webdriver-manager installation

2. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API quota and billing

3. **PDF Processing Failures**
   - Ensure EasyOCR is installed
   - Check available disk space

4. **Scraping Timeouts**
   - County websites may be slow
   - Try running during off-peak hours

### Debug Mode

Enable detailed logging by setting environment variables:
```bash
export PYTHONPATH=.
export DEBUG=1
```

## 📈 Monitoring

The API provides detailed status information for each step:
- Success/failure status
- Error messages
- Processing statistics
- File counts and locations

## 🔒 Security Notes

- Credentials are hardcoded in scraper files
- Consider using environment variables for production
- API runs on localhost by default
- Add authentication for production deployment

## 📝 License

This project is for educational and research purposes. Please respect the terms of service of the county websites being scraped. 