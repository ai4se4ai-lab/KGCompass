# KGCompass Configuration Guide

## Environment Variable Configuration

Create a `.env` file in the project root directory and set the following environment variables:

```bash
# GitHub Token (for accessing GitHub API)
GITHUB_TOKEN=your_github_token_here

# Bailian API Key (Alibaba Cloud Bailian Large Model)
BAILIAN_API_KEY=your_bailian_api_key_here

# Claude API Key (Anthropic Claude)
CLAUDE_API_KEY=your_claude_api_key_here

# OpenAI API Key (GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Qwen API Key
QWEN_API_KEY=your_qwen_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Proxy Settings (if needed)
# http_proxy=http://172.27.16.1:7890
# https_proxy=http://172.27.16.1:7890
# no_proxy=localhost,127.0.0.1

# Debug Settings
DEBUG=0
FLASK_DEBUG=0
```

## API Key Acquisition

### GitHub Token
1. Visit https://github.com/settings/tokens
2. Click "Generate new token"
3. Select appropriate permissions (repo, read:org)
4. Copy the generated token

### Anthropic Claude
1. Visit https://console.anthropic.com/
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Log in to your account
3. Click "Create new secret key"
4. Copy the API key

### DeepSeek
1. Visit https://platform.deepseek.com/
2. Register or log in
3. Navigate to API Keys section
4. Create and copy the API key

### Qwen
1. Visit Alibaba Cloud Qwen API platform
2. Register or log in
3. Create an API key
4. Copy the API key

## Configuration Notes

- All API keys should be kept secure and not committed to version control
- The `.env` file is already in `.gitignore` to prevent accidental commits
- For production environments, use environment variables or secure secret management systems
- Neo4j configuration should match your Docker Compose setup

## Testing Configuration

After setting up the `.env` file, you can test the configuration by running:

```bash
python3 -c "from kgcompass.config import *; print('Configuration loaded successfully')"
```

If there are any missing or invalid API keys, the system will report errors during initialization.
