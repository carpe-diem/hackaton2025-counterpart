# PDF Data Extraction Tool

This tool is designed to extract and process data from PDF documents using Python.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```

2. Install dependencies:

```bash
uv sync
```

3. Create a .env file in the project root with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key
LINEAR_API_KEY=your_linear_api_key
LINEAR_TEAM_ID=your_linear_team_id
```


## Usage

### Process a local PDF file

```bash
python main.py
```

