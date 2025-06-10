# Business Idea Generation Agent

This Python agent uses the OpenAI API to generate, validate, and detail innovative business ideas within a specified domain. It also performs a basic check for business name availability.

## Features

- **Idea Generation**: Creates a business name, description, and tagline based on a given domain.
- **Idea Validation**: Provides a qualitative assessment of the generated idea's potential.
- **Business Element Definition**: Outlines core value proposition, target audience, demographics, USPs, and initial revenue model.
- **Name Availability Check**: Checks if the generated business name is available as a `.com` domain using WHOIS lookups.
- **Retry Mechanism**: Attempts to find an available business name multiple times if the first one is taken.
- **Configurable**: Accepts business domain and OpenAI API key via command-line arguments.

## Project Structure

```
.
├── business_idea_agent.py  # Main script for the agent
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup

1.  **Clone the repository (if applicable) or download the files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up OpenAI API Key:**
    You need an OpenAI API key to use this agent. You can either:
    *   Set it as an environment variable:
        ```bash
        export OPENAI_API_KEY="your_openai_api_key_here"
        ```
    *   Pass it as a command-line argument when running the script (see below).

## Usage

Run the agent from the command line, providing the business domain as an argument.

**Basic usage (with API key as environment variable):**
```bash
python business_idea_agent.py "health and fitness using AI"
```

**Providing API key as an argument:**
```bash
python business_idea_agent.py "sustainable urban farming using IoT" --api_key "your_openai_api_key_here"
```

**Specifying maximum name check retries:**
```bash
python business_idea_agent.py "personalized education platforms for K-12" --max_retries 5
```

### Command-line Arguments:
*   `domain` (required): The business domain you want to explore (e.g., "renewable energy solutions for smart cities").
*   `--api_key` (optional): Your OpenAI API key. If not provided, the script will look for the `OPENAI_API_KEY` environment variable.
*   `--max_retries` (optional): The maximum number of times the agent should try to find an available business name. Defaults to 3.

## Output

The script will log its progress to the console and print the final business idea details as a JSON object. The output includes:

```json
{
  "businessName": "SynapseAI", // Example
  "BusinessDescription": "An AI-driven platform...", // Example
  "tagline": "BIA-generated tagline", // Example
  "coreValueProposition": "Generated core value prop", // Example
  "primaryTargetAudience": "Specific audience", // Example
  "demographics": "Audience demographics", // Example
  "uniqueSellingPoints": ["USP1", "USP2"], // Example
  "initialRevenueModel": "Subscription based", // Example
  "validationSummary": "The idea shows promise...", // Example
  "nameAvailability": { // Example
    "domain_name": "synapseai.com",
    "status": "unavailable", // or "available", "unknown", "error_checking"
    "details": "WHOIS details or error message"
  }
}
```
(Note: The exact fields and content will vary based on the OpenAI generation.)

## How it Works

The agent follows these steps:
1.  **Idea Generation**: Takes the input domain and uses OpenAI to brainstorm a business name, description, and tagline.
2.  **Name Availability Check**: Checks if the `.com` domain for the generated name is available. If not, and if retries are allowed, it loops back to step 1 to generate a new name.
3.  **Idea Validation**: Once a potentially available name is found (or retries are exhausted), OpenAI validates the core idea.
4.  **Business Elements Definition**: OpenAI defines key business elements like USPs, target audience, etc.
5.  **Output**: The consolidated information is presented as a JSON object.

## Libraries Used
*   [openai](https://pypi.org/project/openai/): For interacting with the OpenAI API.
*   [python-whois](https://pypi.org/project/python-whois/): For checking domain name availability.
*   `argparse`: For command-line argument parsing.
*   `logging`: For application logging.
