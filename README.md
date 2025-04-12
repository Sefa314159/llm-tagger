# Language, Sentiment and Intent Analysis

A comprehensive text analysis tool that leverages OpenAI's language models to detect sentiment, identify language, and classify intent in text inputs.

## Project Overview

This project provides a modular system for analyzing text through several components:

1. **Core Analysis Engine**: Uses OpenAI's language models to perform sentiment, language, and intent analysis
2. **Conversation Analysis**: Breaks down multi-sentence text for individual sentence analysis
3. **Logging Service**: Stores analysis results in MongoDB for future reference
4. **Web Interface**: Streamlit-based UI for easy interaction with the analysis tools

## Components

### app.py

Contains the core functionality:
- `Tagging` - Pydantic model that defines the structure for text analysis (sentiment, language, intent)
- `LLMTagger` - Class that leverages OpenAI models to analyze text based on the Tagging schema

### conversation_analysis.py

Handles multi-sentence text analysis:
- Splits text into individual sentences
- Processes each sentence through the LLMTagger
- Sends results to the logging service

### log_service.py

FastAPI-based logging service:
- Stores analysis results in MongoDB
- Uses background tasks for non-blocking operations
- Provides structured logging with Python's logging module

### stapp.py

Streamlit-based web interface:
- Provides a user-friendly UI for text analysis
- Supports both single-sentence and conversation modes
- Displays analysis results in a readable JSON format

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- OpenAI API key

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
OPEN_AI_MODEL_NAME=gpt-4-turbo
OPENAI_MODEL_TEMPERATURE=0.1
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=text_analysis
MONGO_COLLECTION_NAME=analysis_logs
```

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd llm-sentiment
   ```

2. Install dependencies
   ```bash
   pip3 install -r requirements.txt
   ```

3. Start the logging service
   ```bash
   uvicorn log_service:app --reload
   ```

4. Run the Streamlit app (in a separate terminal)
   ```bash
   streamlit run stapp.py
   ```

## Usage Example

### Using LLMTagger directly in your code

```python
from app import LLMTagger

# Initialize the tagger
tagger = LLMTagger()

# Analyze a single sentence
text = "I'm really excited about this new product - it's exactly what I've been looking for!"
result = tagger.tag(text)

print(f"Sentiment: {result['sentiment']}")
print(f"Language: {result['language']}")
print(f"Intent: {result['intent']}")

# Example output:
# Sentiment: positive
# Language: en
# Intent: appreciation
```

### Analyzing a Conversation

```python
from conversation_analysis import analyze_conversation

# Analyze a multi-sentence conversation
conversation = "Hello there! I was wondering if you could help me. I ordered your premium package last week but haven't received it yet."
results = analyze_conversation(conversation)

for idx, result in enumerate(results):
    print(f"\nSentence {idx+1}: {result['sentence']}")
    print(f"Sentiment: {result['analysis']['sentiment']}")
    print(f"Language: {result['analysis']['language']}")
    print(f"Intent: {result['analysis']['intent']}")

# Example output:
# Sentence 1: Hello there!
# Sentiment: positive
# Language: en
# Intent: greeting
# 
# Sentence 2: I was wondering if you could help me.
# Sentiment: neutral
# Language: en
# Intent: information_request
# 
# Sentence 3: I ordered your premium package last week but haven't received it yet.
# Sentiment: negative
# Language: en
# Intent: complaint
```

## Web Interface

The Streamlit-based web interface provides two modes:

1. **Single Sentence Mode**: Analyze one text input at a time
2. **Conversation Mode**: Break down and analyze multi-sentence text

Results are displayed in real-time with formatted JSON output.

## Data Storage

All analysis results are automatically stored in MongoDB through the logging service. This allows for:
- Historical analysis of user interactions
- Building a dataset for future model training
- Tracking sentiment trends over time

## Docker Deployment

You can easily run this application using Docker. Here are the commands to build and run the application:

### Building the Docker Image

Build the Docker image for the application:

```bash
docker build -t llm-sentiment .
```

### Starting MongoDB Container

Start a MongoDB container for data storage:

```bash
docker run --name mongodb -d -p 27018:27017 mongo:latest
```

This command starts a MongoDB container named "mongodb", running in detached mode (-d), and maps port 27018 on your local machine to port 27017 inside the container.

### Running the Application Container

Start the application container with access to MongoDB:

```bash
docker run --name llm-app --network llm-network -p 8000:8000 -p 8501:8501 llm-sentiment
```

This command:
- Creates a container named "llm-app"
- Connects it to the "llm-network" Docker network (make sure this network exists or create it with `docker network create llm-network`)
- Maps ports 8000 (FastAPI service) and 8501 (Streamlit interface) to your local machine

### Checking Stored Data

You can check the data stored in MongoDB using these commands:

```bash
docker exec -it mongodb mongosh
use analysis_db
db.analysis_logs.find().pretty()
```

These commands:
1. Open an interactive MongoDB shell in the running MongoDB container
2. Switch to the "analysis_db" database where analysis results are stored
3. Display all stored analysis logs in a readable format

## License

[MIT License](LICENSE)
