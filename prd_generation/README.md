# BRD/PRD Generation Tool

This tool automatically generates Business Requirements Documents (BRD) and Product Requirements Documents (PRD) using AI. It leverages Groq's LLama-3 model through the Agno platform to create detailed, professionally structured documents that follow industry standards.

## Features

- **Interactive Project Information Collection**: Gather detailed information about your project through guided prompts
- **BRD Generation**: Create comprehensive Business Requirements Documents from project details
- **PRD Generation**: Generate detailed Product Requirements Documents based on the BRD
- **Task Hierarchy**: Produce a structured implementation plan with epics, features, and tasks in JSON format
- **Template-Based**: Uses existing templates to ensure industry-standard document formats
- **Command-Line Interface**: Supports both interactive and command-line usage

## Prerequisites

- Python 3.7+
- Groq API key
- Required Python packages:
  - `agno`
  - `groq`
  - `tenacity`

## Installation

1. Clone this repository:

   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:

   ```
   pip install agno groq tenacity
   ```

3. Set up your Groq API key:

   ```
   export GROQ_API_KEY="your-api-key-here"
   ```

   Alternatively, you can add it directly to the script by uncommenting and modifying this line in `brd_generation.py`:

   ```python
   # os.environ["GROQ_API_KEY"] = "your-api-key-here"
   ```

## Usage

### Interactive Mode

Run the script without arguments to use interactive mode:

```
python brd_generation.py
```

You will be prompted to enter:

- Project name
- Project description
- Business objectives
- Target audience
- Key features
- Budget
- Timeline
- Industry sector
- Known competitors
- Project constraints

### Command-Line Mode

You can also use command-line arguments for non-interactive use:

```
python brd_generation.py --skip-input --name "ProjectName" --description "Project description"
```

Additional optional arguments:

- `--brd-file`: Specify the output file for the BRD (default: brd.md)
- `--prd-file`: Specify the output file for the PRD (default: prd.md)

### Example

```
python brd_generation.py --skip-input --name "HealthAssistant" --description "A retrieval-augmented generation (RAG) chatbot that provides personalized health information and guidance using Groq's LLM capabilities"
```

## Output Files

The tool generates the following files:

1. `brd.md` - Business Requirements Document
2. `prd.md` - Product Requirements Document
3. `task_hierarchy.json` - Task breakdown in JSON format

## Templates

The tool uses template files for generating documents:

- `BRD_toko_kita.md` - Template for BRD structure
- `PRD_toko_kita.md` - Template for PRD structure

If these files are not found, the tool will proceed without them but may produce less structured documents.

## Customization

You can customize the document structure by modifying:

1. The template files
2. The prompt instructions in the code

## Troubleshooting

### API Key Issues

If you encounter an error about missing API key:

- Make sure your Groq API key is properly set as an environment variable
- Or uncomment and update the API key line in the script

### Connection Problems

If you experience connection issues with Groq:

- Check your internet connection
- Verify that your API key is valid and has not exceeded usage limits

### Format Issues

If the output documents don't match your expectations:

- Make sure the template files are properly formatted
- Check that your input information is complete and detailed

## License

[Specify your license information here]

## Credits

This tool was developed by [Your Name/Organization] and uses the following:

- Groq's LLama-3 model
- Agno platform for agent interactions
