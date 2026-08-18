# Scenario: AI Agent Chatbot

Webhook receives chat messages → AI Agent processes with tools and memory → returns response.

## Architecture

```
Webhook (POST /chat)
  → AI Agent
    ├── OpenAI Chat Model (ai_languageModel)
    ├── HTTP Request Tool (ai_tool)
    ├── Calculator Tool (ai_tool)
    └── Window Buffer Memory (ai_memory)
  → Respond to Webhook (reply)
```

## AI Connection Types

AI Agent workflows use special connection types — not the standard `main` type:

| Connection Type | Purpose | Example Node |
|----------------|---------|-------------|
| `ai_languageModel` | LLM provider | OpenAI, Anthropic, Google |
| `ai_tool` | Tools the agent can use | HTTP Request, Calculator, Code |
| `ai_memory` | Conversation memory | Window Buffer, Postgres Chat Memory |
| `ai_outputParser` | Parse agent output | Structured Output Parser |
| `ai_retriever` | RAG retrieval | Vector Store Retriever |
| `ai_textSplitter` | Split documents | Recursive Text Splitter |
| `ai_document` | Load documents | PDF, CSV, JSON loaders |
| `ai_embedding` | Embedding models | OpenAI Embeddings |

## Step 1: Discover Nodes

```javascript
search_nodes({query: "agent"})
// → nodes-langchain.agent

search_nodes({query: "openai chat"})
// → nodes-langchain.lmChatOpenAi

search_nodes({query: "http request tool"})
// → nodes-langchain.toolHttpRequest

search_nodes({query: "calculator"})
// → nodes-langchain.toolCalculator

search_nodes({query: "window buffer memory"})
// → nodes-langchain.memoryBufferWindow
```

## Step 2: Get Node Details

```javascript
// Check AI Agent configuration
get_node({nodeType: "nodes-langchain.agent", detail: "standard"})

// Check OpenAI model options
get_node({nodeType: "nodes-langchain.lmChatOpenAi", detail: "standard"})
```

## Step 3: Create Workflow

```javascript
n8n_create_workflow({
  name: "AI Chat Agent",
  nodes: [
    {
      id: "webhook-1",
      name: "Chat Input",
      type: "n8n-nodes-base.webhook",
      typeVersion: 2,
      position: [250, 300],
      parameters: {
        path: "chat",
        httpMethod: "POST",
        responseMode: "responseNode"
      }
    },
    {
      id: "agent-1",
      name: "AI Agent",
      type: "@n8n/n8n-nodes-langchain.agent",
      typeVersion: 1.7,
      position: [500, 300],
      parameters: {
        text: "={{$json.body.message}}",
        options: {
          systemMessage: "You are a helpful assistant. Answer questions clearly and concisely."
        }
      }
    },
    {
      id: "openai-1",
      name: "OpenAI Model",
      type: "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      typeVersion: 1.2,
      position: [500, 100],
      parameters: {
        model: "gpt-4o-mini",
        options: {
          temperature: 0.7
        }
      }
    },
    {
      id: "http-tool-1",
      name: "Web Search Tool",
      type: "@n8n/n8n-nodes-langchain.toolHttpRequest",
      typeVersion: 1.1,
      position: [650, 100],
      parameters: {
        name: "web_search",
        description: "Search the web for current information",
        method: "GET",
        url: "https://api.example.com/search?q={query}",
        placeholderDefinitions: {
          values: [{
            name: "query",
            description: "Search query"
          }]
        }
      }
    },
    {
      id: "calc-1",
      name: "Calculator",
      type: "@n8n/n8n-nodes-langchain.toolCalculator",
      typeVersion: 1,
      position: [800, 100],
      parameters: {}
    },
    {
      id: "memory-1",
      name: "Chat Memory",
      type: "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      typeVersion: 1.3,
      position: [500, 500],
      parameters: {
        sessionIdType: "customKey",
        sessionKey: "={{$json.body.session_id}}",
        contextWindowLength: 10
      }
    },
    {
      id: "respond-1",
      name: "Reply",
      type: "n8n-nodes-base.respondToWebhook",
      typeVersion: 1.1,
      position: [750, 300],
      parameters: {
        respondWith: "json",
        responseBody: "={\"response\": \"{{$json.output}}\", \"session_id\": \"{{$json.body.session_id}}\"}"
      }
    }
  ],
  connections: {
    "Chat Input": {
      "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    },
    "AI Agent": {
      "main": [[{"node": "Reply", "type": "main", "index": 0}]]
    },
    "OpenAI Model": {
      "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
    },
    "Web Search Tool": {
      "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
    },
    "Calculator": {
      "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
    },
    "Chat Memory": {
      "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
    }
  }
})
```

## Step 4: Test

```javascript
n8n_test_workflow({
  workflowId: "<workflow-id>",
  triggerType: "webhook",
  data: {
    message: "What is 42 * 17?",
    session_id: "test-session-1"
  }
})
```

## Step 5: Validate and Activate

```javascript
n8n_validate_workflow({id: "<workflow-id>"})
n8n_update_partial_workflow({
  id: "<workflow-id>",
  operations: [{type: "activateWorkflow"}]
})
```

## Key Learnings

- AI nodes use `@n8n/n8n-nodes-langchain.*` prefix (not `n8n-nodes-base.*`)
- AI connections use special types: `ai_languageModel`, `ai_tool`, `ai_memory`
- AI connection direction is FROM the sub-node TO the agent (reversed from main flow)
- Webhook data for chat message: `$json.body.message`
- Memory `sessionKey` enables per-user conversation tracking
- Agent `text` parameter is the user's input message
- Agent output is in `$json.output`
- LLM credentials (OpenAI key) are configured via n8n credential system, not in node parameters
- Use `get_node({nodeType: "nodes-langchain.agent", mode: "docs"})` for comprehensive AI Agent documentation
