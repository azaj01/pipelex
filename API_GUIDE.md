# Pipelex API Guide

This guide covers everything you need to know about using the Pipelex API to execute pipelines with flexible input formats.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Execute Pipeline](#execute-pipeline)
3. [Input Format: ImplicitMemory](#input-format-implicitmemory)
   - [Case 1: Direct Content Format](#case-1-direct-content-format)
   - [Case 2: Explicit Format](#case-2-explicit-format-concept--content)
4. [Search Domains Explained](#search-domains-explained)
5. [PLX Content: Execute Pipelines Inline](#plx-content-execute-pipelines-inline)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Client Libraries](#client-libraries)

---

## Base URL

```
https://api.pipelex.ai/api/v1
```

## Authentication

Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

---

## Quick Reference

### Input Formats at a Glance

```json
// 1. Simple text (Case 1.1)
{ "text": "Hello, world!" }

// 2. List of text (Case 1.2)
{ "documents": ["text1", "text2", "text3"] }

// 3. Explicit format (Case 2.1)
{ "text": { "concept": "Text", "content": "Hello!" } }

// 4. Structured data (Case 2.5)
{ "invoice": { "concept": "Invoice", "content": { "number": "001", "amount": 100 } } }

// 5. Domain-prefixed concept (Case 2.5)
{ "data": { "concept": "accounting.Invoice", "content": { ... } } }
```

### Key Points

✅ **DO:** Use direct strings for text: `{"text": "Hello"}`  
❌ **DON'T:** Over-complicate text: `{"text": {"concept": "Text", "content": "Hello"}}`

✅ **DO:** Specify domain when ambiguous: `"accounting.Invoice"`  
❌ **DON'T:** Use generic names when you have duplicates: `"Invoice"`

✅ **DO:** Use `plx_content` for dynamic pipelines  
❌ **DON'T:** Use both `pipe_code` and `plx_content` together

---

## Execute Pipeline

Execute a Pipelex pipeline with flexible inputs.

**Endpoint:** `POST /pipeline/{pipe_code}/execute`

**Path Parameters:**
- `pipe_code` (string, required): The code identifying the pipeline to execute

**Request Body:**

```json
{
  "inputs": {
    "input_name": "simple text or object"
  },
  "output_name": null,
  "output_multiplicity": null,
  "dynamic_output_concept_code": null,
  "plx_content": null
}
```

**Request Fields:**
- `inputs` (ImplicitMemory): Flexible input format - see [Input Format](#input-format-implicitmemory) below
- `output_name` (string, optional): Name for the output slot
- `output_multiplicity` (string, optional): Output multiplicity setting
- `dynamic_output_concept_code` (string, optional): Override output concept
- `plx_content` (string, optional): Inline pipeline definition - see [PLX Content](#plx-content-execute-pipelines-inline)

**Response:**

```json
{
  "status": "success",
  "message": null,
  "error": null,
  "pipeline_run_id": "abc123...",
  "created_at": "2025-10-20T12:00:00Z",
  "pipeline_state": "COMPLETED",
  "finished_at": "2025-10-20T12:00:05Z",
  "pipe_output": {
    "working_memory": {
      "root": { ... },
      "aliases": { ... }
    },
    "pipeline_run_id": "abc123..."
  },
  "main_stuff_name": "result"
}
```

---

## Input Format: ImplicitMemory

Run your pipeline with flexible inputs that adapt to your needs. Pipelex supports multiple formats for providing inputs, making it easy to work with simple text, structured data, or complex objects. 

### What is ImplicitMemory?

The `inputs` field uses **ImplicitMemory** format - a smart, flexible way to provide data to your pipelines. Instead of forcing you into a rigid structure, ImplicitMemory intelligently interprets your data based on how you provide it.

### How Input Formatting Works

**Case 1: Direct Content** - Provide the value directly (simplest)
- 1.1: String → `"my text"`
- 1.2: List of strings → `["text1", "text2"]`
- 1.3: StuffContent object → `MyClass(arg1="value")`
- 1.4: List of StuffContent objects → `[MyClass(...), MyClass(...)]`

**Case 2: Explicit Format** - Use `{"concept": "...", "content": "..."}` for control
- 2.1: String with concept → `{"concept": "Text", "content": "my text"}`
- 2.2: List of strings with concept → `{"concept": "Text", "content": ["text1", "text2"]}`
- 2.3: StuffContent object with concept → `{"concept": "Invoice", "content": InvoiceObject}`
- 2.4: List of StuffContent objects with concept → `{"concept": "Invoice", "content": [...]}`
- 2.5: Dictionary (structured data) → `{"concept": "Invoice", "content": {"field": "value"}}`
- 2.6: List of dictionaries → `{"concept": "Invoice", "content": [{...}, {...}]}`

**Pro Tip:** For **text inputs specifically**, skip the verbose format. Just provide the string directly: `"text": "Hello"` instead of `"text": {"concept": "Text", "content": "Hello"}`

---

## Case 1: Direct Content Format

When you provide content directly (without the `concept` key), Pipelex intelligently infers the type.

### 1.1: Simple String (Text)

The simplest case - just provide a string directly:

```json
{
  "inputs": {
    "my_text": "my text"
  }
}
```

**Result:** Automatically becomes `TextContent` with concept `native.Text`

### 1.2: List of Strings (Text List)

Provide multiple text items as a list:

```json
{
  "inputs": {
    "my_texts": ["my text1", "my text2", "my text3"]
  }
}
```

**Result:** Becomes a `ListContent` containing multiple `TextContent` items

**Note:** The concept must be compatible with `native.Text` or an error will be raised.

### 1.3: StuffContent Object

Provide a structured object directly (for Python clients):

```python
# Python client example
inputs = {
    "invoice_data": MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))
}
```

**Concept Resolution:**
- The system searches all available domains for a concept matching the class name
- If multiple concepts with the same name exist in different domains → **Error**: Must specify domain
- If no concept is found → **Error**

### 1.4: List of StuffContent Objects

Provide multiple structured objects:

```python
# Python client example
inputs = {
    "invoice_list": [
        MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4")),
        MyConcept(arg1="arg1", arg2=1, arg3=MySubClass(arg4="arg4"))
    ]
}
```

**Requirements:**
- All items must be of the same type
- Concept resolution follows the same rules as 1.3

---

## Case 2: Explicit Format (Concept + Content)

Use the explicit format `{"concept": "...", "content": "..."}` when you need precise control over concept selection or when working with domain-specific concepts.

### 2.1: Explicit String Input

```json
{
  "inputs": {
    "text": {
      "concept": "Text",
      "content": "my text"
    }
  }
}
```

**Concept Options:**
- `"Text"` or `"native.Text"` for native text
- Any custom concept that is strictly compatible with `native.Text`

### 2.2: Explicit List of Strings

```json
{
  "inputs": {
    "documents": {
      "concept": "Text",
      "content": ["text1", "text2", "text3"]
    }
  }
}
```

**Result:** `ListContent` with multiple `TextContent` items

### 2.3: StuffContent Object with Concept

```json
{
  "inputs": {
    "invoice_data": {
      "concept": "Invoice",
      "content": {
        "invoice_number": "INV-001",
        "amount": 1250.00,
        "date": "2025-10-20"
      }
    }
  }
}
```

**Concept Resolution with Search Domains:**

When you specify a concept name without a domain prefix:
- ✅ If the concept exists in only one domain → Automatically found
- ❌ If the concept exists in multiple domains → **Error**: "Multiple concepts found. Please specify domain as 'domain.Concept'"
- ❌ If the concept doesn't exist → **Error**: "Concept not found"

**Using Domain Prefix:**
```json
{
  "concept": "accounting.Invoice"
}
```

This explicitly tells Pipelex to use the `Invoice` concept from the `accounting` domain.

### 2.4: List of StuffContent Objects

```json
{
  "inputs": {
    "invoices": {
      "concept": "Invoice",
      "content": [
        {
          "invoice_number": "INV-001",
          "amount": 1250.00
        },
        {
          "invoice_number": "INV-002",
          "amount": 890.00
        }
      ]
    }
  }
}
```

**Result:** `ListContent` with multiple structured content items

### 2.5: Dictionary Content

Provide structured data as a dictionary:

```json
{
  "inputs": {
    "person": {
      "concept": "PersonInfo",
      "content": {
        "arg1": "something",
        "arg2": 1,
        "arg3": {
          "arg4": "something else"
        }
      }
    }
  }
}
```

The system will:
1. Find the concept structure (with domain resolution as explained above)
2. Validate the dictionary against the concept's structure
3. Create the appropriate content object

### 2.6: List of Dictionaries

```json
{
  "inputs": {
    "people": {
      "concept": "PersonInfo",
      "content": [
        {
          "arg1": "something",
          "arg2": 1,
          "arg3": {"arg4": "something else"}
        },
        {
          "arg1": "something else",
          "arg2": 2,
          "arg3": {"arg4": "something else else"}
        }
      ]
    }
  }
}
```

---

## Search Domains Explained

When you reference a concept by name (like `"Invoice"` or `"PersonInfo"`), Pipelex needs to find it in your loaded domains.

### Automatic Search

```json
{
  "concept": "Invoice"
}
```

**What happens:**
1. Pipelex searches all available domains for a concept named `"Invoice"`
2. If found in **exactly one domain** → ✅ Uses that concept
3. If found in **multiple domains** → ❌ Error: "Ambiguous concept: Found 'Invoice' in domains: accounting, billing. Use 'domain.Invoice' format."
4. If **not found** → ❌ Error: "Concept 'Invoice' not found in any domain"

### Explicit Domain Specification

To avoid ambiguity, specify the domain explicitly:

```json
{
  "concept": "accounting.Invoice"
}
```

**Format:** `"domain_name.ConceptName"`

This tells Pipelex exactly which concept to use, bypassing the search.

### Best Practices

- Use simple names (`"Invoice"`) when you have unique concept names across domains
- Use domain-prefixed names (`"accounting.Invoice"`) when:
  - You have concepts with the same name in different domains
  - You want to be explicit about which concept to use
  - You're building APIs that need to be unambiguous

---

## Multiple Input Combinations

Combine different input types in a single request:

```json
{
  "inputs": {
    "text": "Analyze this contract for risks.",
    "category": {
      "concept": "Category",
      "content": {"name": "legal", "priority": "high"}
    },
    "options": ["option1", "option2", "option3"],
    "invoice": {
      "concept": "accounting.Invoice",
      "content": {
        "invoice_number": "INV-001",
        "amount": 1250.00
      }
    }
  }
}
```

In this example:
- `text` uses direct string format (Case 1.1)
- `category` uses explicit format with structured content (Case 2.5)
- `options` uses direct list format (Case 1.2)
- `invoice` uses explicit format with domain prefix and structured content (Case 2.5)

---

## PLX Content: Execute Pipelines Inline

The `plx_content` field allows you to execute pipelines by providing their `.plx` definition directly in the request, without needing to reference a pre-existing `pipe_code`.

### When to Use PLX Content

Use `plx_content` when you want to:
- Execute a dynamically generated pipeline
- Test a pipeline without deploying it
- Run one-off pipelines that don't need to be stored
- Prototype new pipelines quickly

### Basic Usage

Instead of referencing a `pipe_code`, provide the complete pipeline definition:

```bash
curl -X POST https://api.pipelex.ai/api/v1/pipeline/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "plx_content": "domain = \"my_domain\"\n\n[concept]\nGreeting = \"A greeting message\"\n\n[pipe.hello]\ntype = \"PipeLLM\"\ndescription = \"Generate a greeting\"\noutput = \"Greeting\"\nprompt = \"Generate a friendly greeting\"",
    "inputs": {
      "name": "Alice"
    }
  }'
```

### PLX Content Structure

The `plx_content` should contain a valid `.plx` file as a string:

```json
{
  "plx_content": "domain = \"example\"\n\n[concept]\nResult = \"A result\"\n\n[pipe.my_pipe]\ntype = \"PipeLLM\"\ndescription = \"Process input\"\ninputs = { text = \"Text\" }\noutput = \"Result\"\nprompt = \"Process this: @text\""
}
```

**Key Points:**
- The `plx_content` must be a valid Pipelex pipeline definition
- Include newlines (`\n`) to properly format the pipeline
- The pipeline will be validated before execution
- All concepts and pipes must be properly defined within the content

### Example: Dynamic Pipeline

```python
from pipelex.client import PipelexClient

client = PipelexClient(api_token="YOUR_API_KEY")

# Define a pipeline inline
plx_pipeline = """
domain = "sentiment_analysis"

[concept]
SentimentScore = "A sentiment score"

[concept.SentimentScore.structure]
score = { type = "number", description = "Sentiment score from -1 to 1", required = true }
label = { type = "text", description = "Sentiment label", required = true }

[pipe.analyze]
type = "PipeLLM"
description = "Analyze sentiment of text"
inputs = { text = "Text" }
output = "SentimentScore"
model = { model = "gpt-4o-mini", temperature = 0.3 }
prompt = \"\"\"
Analyze the sentiment of this text and provide a score from -1 (negative) to 1 (positive):

@text
\"\"\"
"""

# Execute the pipeline
response = await client.execute_pipeline(
    pipe_code="analyze",
    plx_content=plx_pipeline,
    inputs={
        "text": "This product exceeded all my expectations!"
    }
)

print(response.pipe_output)
```

### Combining PLX Content with Inputs

You can use all the ImplicitMemory input formats described above with `plx_content`:

```json
{
  "plx_content": "domain = \"processing\"...",
  "inputs": {
    "text": "Simple direct input",
    "data": {
      "concept": "DataRecord",
      "content": {
        "id": 123,
        "values": [1, 2, 3]
      }
    }
  }
}
```

### Validation

When you provide `plx_content`:
1. The pipeline definition is parsed and validated
2. All concepts and structures are verified
3. The pipeline is executed if valid
4. Errors are returned if the pipeline definition is invalid

**Important:** `plx_content` and `pipe_code` are mutually exclusive. Use one or the other, not both.

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "message": "Pipeline execution failed",
  "error": "Invalid concept: UnknownConcept",
  "pipeline_run_id": "abc123",
  "pipeline_state": "FAILED"
}
```

### HTTP Status Codes

- `200 OK`: Pipeline executed successfully
- `400 Bad Request`: Invalid input format
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Pipeline not found
- `500 Internal Server Error`: Server error

-

For questions or issues:
- Discord: https://go.pipelex.com/discord
- GitHub: https://github.com/pipelex/pipelex
- Email: support@pipelex.ai

