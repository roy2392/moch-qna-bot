# Knowledge Base Integration Guide

This guide explains how to integrate JSON data into your system prompt using the knowledge base feature.

## Overview

The chatbot uses a two-file approach for system prompts:
1. **System Prompt File** (`prompts/system_prompt.txt`) - Contains the instructions and behavior guidelines
2. **Knowledge Base File** (`prompts/knowledge_base.json`) - Contains structured data that gets injected into the prompt

## How It Works

When the system loads the prompt, it:
1. Reads the system prompt file
2. Reads the knowledge base JSON file
3. Finds the `<knowledge_base>` tag in the prompt
4. Replaces the content between `<knowledge_base>` and `</knowledge_base>` with the JSON data
5. Sends the complete prompt to AWS Bedrock

## File Structure

```
prompts/
├── system_prompt.txt           # Your system prompt with <knowledge_base> placeholder
├── system_prompt.example.txt   # Example template
├── knowledge_base.json         # Your actual data (gitignored)
└── knowledge_base.example.json # Example structure
```

## Setting Up Knowledge Base

### 1. Create Your Knowledge Base JSON

```bash
# Copy the example file
cp prompts/knowledge_base.example.json prompts/knowledge_base.json

# Edit with your data
nano prompts/knowledge_base.json
```

### 2. Structure Your JSON

Your JSON can have any structure. Example:

```json
{
  "knowledge_base": {
    "categories": [
      {
        "main_topic": "Topic Name",
        "main_topic_code": "123",
        "sub_topics": [
          {
            "sub_topic": "Subtopic Name",
            "description": "Description here",
            "common_queries": ["Query 1", "Query 2"],
            "info_links": ["https://example.com"],
            "form_link": "https://example.com/form"
          }
        ]
      }
    ],
    "metadata": {
      "last_updated": "2024-11-11",
      "version": "1.0"
    }
  }
}
```

### 3. Reference in System Prompt

In your `prompts/system_prompt.txt`, use the `<knowledge_base>` tag:

```xml
<system_prompt>
<role>
You are a helpful assistant.
</role>

<knowledge_base>
This section will be automatically replaced with the JSON data from knowledge_base.json
</knowledge_base>

<response_guidelines>
- Follow the data in the knowledge base
- Provide accurate information
</response_guidelines>
</system_prompt>
```

## Configuration

### Environment Variable (Optional)

You can change the knowledge base file path in your `.env`:

```bash
KNOWLEDGE_BASE_FILE=prompts/custom_knowledge.json
```

### Default Path

If not specified, the default is `prompts/knowledge_base.json`

## Multiple Knowledge Bases

You can maintain different knowledge bases for different environments:

```bash
prompts/
├── knowledge_base.json              # Production data
├── knowledge_base.dev.json         # Development data
├── knowledge_base.staging.json     # Staging data
└── knowledge_base.example.json     # Template
```

Switch between them using environment variables:

```bash
# .env.production
KNOWLEDGE_BASE_FILE=prompts/knowledge_base.json

# .env.development
KNOWLEDGE_BASE_FILE=prompts/knowledge_base.dev.json
```

## Best Practices

### 1. Keep JSON Clean and Organized

```json
{
  "knowledge_base": {
    "categories": [...],
    "metadata": {
      "last_updated": "2024-11-11",
      "version": "1.0"
    }
  }
}
```

### 2. Use Meaningful Keys

Make your JSON self-documenting:

```json
{
  "categories": [
    {
      "id": "housing_assistance",
      "name": "Housing Assistance Programs",
      "description": "Programs for rental assistance"
    }
  ]
}
```

### 3. Include Metadata

Track versions and updates:

```json
{
  "metadata": {
    "last_updated": "2024-11-11",
    "version": "1.0",
    "author": "Your Name",
    "notes": "Added new categories"
  }
}
```

### 4. Validate Your JSON

Before using, ensure your JSON is valid:

```bash
# Using Python
python -m json.tool prompts/knowledge_base.json

# Using jq
jq . prompts/knowledge_base.json
```

### 5. Keep Data Updated

Regularly review and update your knowledge base:
- Remove outdated information
- Add new categories as needed
- Update links and contact information
- Track changes in the metadata section

## Unicode and Special Characters

The system supports full Unicode (including Hebrew, Arabic, etc.):

```json
{
  "categories": [
    {
      "name": "סיוע בשכר דירה",
      "description": "מידע על סיוע בשכר דירה"
    }
  ]
}
```

The JSON loader uses `ensure_ascii=False` to preserve all characters correctly.

## Troubleshooting

### Knowledge Base Not Loading

Check the logs for warnings:
```
Warning: Knowledge base file not found at /path/to/knowledge_base.json
Warning: Could not load knowledge base from file: <error>
```

**Solution:**
1. Verify the file exists at the correct path
2. Check file permissions
3. Validate JSON syntax

### Invalid JSON

If your JSON is malformed, the system will log an error and continue with an empty knowledge base.

**Solution:**
```bash
# Validate JSON syntax
python -m json.tool prompts/knowledge_base.json
```

### Knowledge Base Not Appearing in Prompt

**Check:**
1. Your system prompt has `<knowledge_base>` and `</knowledge_base>` tags
2. The tags are properly formatted (case-sensitive)
3. The knowledge base JSON is loading without errors

### Large Knowledge Bases

If your knowledge base is very large (>50KB), consider:
1. Splitting into multiple smaller files
2. Removing unnecessary data
3. Compressing the JSON (remove whitespace)
4. Increasing `max_tokens` if needed

## Example: Complete Setup

### 1. System Prompt (`prompts/system_prompt.txt`)

```xml
<system_prompt>
<role>
You are a virtual assistant for housing services.
</role>

<knowledge_base>
Data will be injected here automatically
</knowledge_base>

<response_guidelines>
- Use the knowledge base to answer questions
- Provide relevant links from the data
- Be helpful and accurate
</response_guidelines>
</system_prompt>
```

### 2. Knowledge Base (`prompts/knowledge_base.json`)

```json
{
  "knowledge_base": {
    "programs": [
      {
        "id": "rental_assistance",
        "name": "Rental Assistance",
        "description": "Monthly assistance for rent",
        "eligibility": ["Low income", "No property ownership"],
        "info_link": "https://example.com/rental"
      }
    ],
    "metadata": {
      "last_updated": "2024-11-11",
      "version": "1.0"
    }
  }
}
```

### 3. Result

The final prompt sent to AWS Bedrock will be:

```xml
<system_prompt>
<role>
You are a virtual assistant for housing services.
</role>

<knowledge_base>
{
  "knowledge_base": {
    "programs": [
      {
        "id": "rental_assistance",
        "name": "Rental Assistance",
        "description": "Monthly assistance for rent",
        "eligibility": ["Low income", "No property ownership"],
        "info_link": "https://example.com/rental"
      }
    ],
    "metadata": {
      "last_updated": "2024-11-11",
      "version": "1.0"
    }
  }
}
</knowledge_base>

<response_guidelines>
- Use the knowledge base to answer questions
- Provide relevant links from the data
- Be helpful and accurate
</response_guidelines>
</system_prompt>
```

## Version Control

### What to Commit

✅ Commit:
- `prompts/knowledge_base.example.json`
- `prompts/system_prompt.example.txt`

❌ Don't Commit:
- `prompts/knowledge_base.json` (gitignored)
- `prompts/system_prompt.txt` (gitignored)

### Sharing Knowledge Base

To share your knowledge base structure without exposing sensitive data:

1. Copy to example file:
```bash
cp prompts/knowledge_base.json prompts/knowledge_base.example.json
```

2. Remove sensitive data from example
3. Commit the example file
4. Document the structure in this guide

## Performance Considerations

### Token Usage

Remember that the knowledge base is sent with every request:
- Monitor token usage in AWS Bedrock
- Keep knowledge base concise
- Remove unused data
- Consider pagination for large datasets

### Caching

The prompt is loaded once when the application starts. To reload:
1. Restart the application
2. Or implement hot-reload functionality

## Security

### Sensitive Data

Never include sensitive information in the knowledge base:
- API keys
- Passwords
- Personal identifiable information (PII)
- Internal system details

### Access Control

The knowledge base file should have appropriate permissions:
```bash
chmod 600 prompts/knowledge_base.json
```

## Advanced Usage

### Dynamic Knowledge Base

For dynamic data that changes frequently, consider:
1. Loading from a database
2. Using an external API
3. Implementing a cache with TTL
4. Creating a management interface

### Multiple Data Sources

Combine multiple JSON files:

```python
# Custom implementation in settings.py
def load_knowledge_base(self) -> Dict[str, Any]:
    kb = {}
    for file in ['kb1.json', 'kb2.json', 'kb3.json']:
        data = load_json(file)
        kb.update(data)
    return kb
```

## Support

For issues or questions:
- Check the logs for warnings
- Validate your JSON syntax
- Review this documentation
- Open an issue on GitHub
