# project-files-feature 

**DOCX & PDF Parser with AI Function Calling**

A modular Python project that ingests Word and PDF documents, extracts structured data, and leverages OpenAI's function calling capabilities to transform and analyze text. It provides configurable transformation modes, language settings, and a clear architecture for building document-centric AI pipelines.

---

## Key Features

- **Multi-format parsing**: Handles DOCX and PDF inputs using custom parsers.
- **Function calling integration**: Interacts with OpenAI functions to process extracted content.
- **Configurable transformation modes**: Supports different output styles (e.g., bullet list, JSON, etc.).
- **Language modes**: Ability to process text in multiple languages (English, Hebrew, etc.).
- **Modular architecture**: Clean separation between parsing, transformation, and orchestration logic.
- **Extensible parameters**: Easily adjust behavior through parameters and Pydantic models.

## Tech Stack

- **Python 3.10+**
- **Pydantic** for data modelling and validation
- **OpenAI API** for language models and function calling
- **python-docx**, **PyPDF2**, or similar for document parsing (in parsers)
- **logging** utilities for audit trails

## Architecture Overview

The system is organized into three main layers:

1. **Parsers** (`/parsers`): Contains handlers for different document formats (`docx_handler.py`, `pdf_handler.py`, etc.). These extract raw text and metadata from files.
2. **Transformation / LLM integration** (`/src/models/document_models.py`, `/openai/*`): Defines Pydantic models, parameter loading, and the logic for invoking OpenAI functions based on transformation modes and languages.
3. **Orchestration & CLI** (`main.py`, `reading_json.py`): Entry points that load configuration, parse inputs, and execute the transformation processes.

Each document first flows through a parser to produce an intermediate representation. That data is then fed to the OpenAI manager which constructs and calls functions according to the selected mode, returning structured output that is saved or streamed to the console.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key
- Git (to clone the repository)
- Virtual environment tooling (venv, pipenv, etc.)

### Installation

```bash
# clone the repo
git clone https://github.com/aharonshamsi/project-files-feature
cd project-files-feature

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # macOS / Linux
# or `venv\Scripts\activate` on Windows

# install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or export the following keys in your shell:

```
OPENAI_API_KEY
# (optional) other keys used by config_model or parameters
```

### Usage

Basic invocation via Python script:

```bash
# parse and transform a document
python main.py --input path/to/file.docx --mode bullet --lang en

# alternatively, load a JSON input and process
python reading_json.py --json data/inputs/input.json
```

Command-line options mirror the parameters defined in `parameters/config_model.py`.

## Configuration

### Transformation Modes

The project supports multiple transformation modes that dictate output formatting:

- `bullet`: Convert document text into a bulleted list.
- `json`: Produce a JSON representation of the extracted content.
- `summary`: Generate a concise summary of the document.
- `full-text`: Return the complete parsed text.

(More modes can be added by extending the transformation logic in `openai/functions.py` and updating the parameter loader.)

### Language Modes

Supported language codes determine the LLM prompt and function behaviour:

- `en` – English
- `he` – Hebrew
- additional languages defined in `parameters/loader.py` or locale mapping.

These flags adjust both the parsing heuristics and the OpenAI requests.

## 📁 Project Structure

```
project-files-feature/
├── config.py                     # global configuration helpers
├── main.py                       # primary CLI entry point
├── reading_json.py               # alternate entry for JSON-based input
├── requirements.txt              # Python dependencies
├── src/                          # core application code
│   └── models/
│       └── document_models.py    # Pydantic models & transformation logic
├── openai/                       # modules wrapping OpenAI calls
│   ├── functions.py              # function calling utilities
│   ├── manager.py                # orchestrates LLM interactions
│   └── prompts.py                # prompt templates
├── parameters/                   # configuration & parameter definitions
│   ├── config_model.py           # Pydantic config models
│   └── loader.py                 # loads parameters from JSON
├── parsers/                      # document parsers by format
│   ├── docx_handler.py
│   ├── pdf_handler.py
│   ├── pptx_handler.py
│   └── utils.py                  # common parser helpers
├── utils/
│   └── logger.py                 # logging setup
└── data/                         # sample/processed data
    ├── inputs/
    └── outputs/
```

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. Ensure you follow the existing coding style and include tests where appropriate.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

---

*Developed with and by the engineering team.*
