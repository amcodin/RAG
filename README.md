# Internet Plan Price Retriever

A Python application using AutoGen v0.4 to create a multi-agent system for retrieving and verifying internet plan prices.

## Setup Instructions

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate virtual environment:

### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# If using PowerShell
# venv\Scripts\Activate.ps1
```

### macOS/Linux
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the variables in `.env` with your settings:
  - `GOOGLE_API_KEY`: Your Gemini API key
  - `MODEL_NAME`: Set to "gemini-2.0-flash"
  - Other configuration as needed

## Project Structure

```
.
├── memory-bank/          # Project documentation
├── src/                  # Source code
│   ├── agents/          # Agent implementations
│   ├── config.py        # Configuration management
│   └── main.py         # Application entry point
├── tests/               # Test files
├── .env                # Environment variables (not in git)
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── requirements.txt   # Project dependencies
```

## Development

1. Activate virtual environment (see Setup Instructions)
2. Run tests:
```bash
pytest
```

3. Run the application:
```bash
python src/main.py <url> <download_speed> [plan_name]
```

## Documentation

See the `memory-bank` directory for detailed documentation:
- Project brief and requirements
- System architecture
- Technical specifications
- Development progress
