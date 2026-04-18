# AI Multi-Agent Code Generator

A sophisticated **multi-agent AI system** that automatically generates complete applications from natural language descriptions. Using LangGraph, Groq LLM, and a ReAct architecture, the system breaks down project requirements into planning, architecture, and implementation phases.

## 🎯 How It Works

The system uses three specialized AI agents working in sequence:

1. **Planner Agent** - Converts user prompts into comprehensive engineering project plans
2. **Architect Agent** - Breaks down plans into explicit, ordered implementation tasks with dependencies
3. **Coder Agent** - Implements tasks iteratively, writing and reading files with full context

### Architecture Overview

```
User Prompt 
    ↓
[Planner Agent] → Creates Project Plan
    ↓
[Architect Agent] → Creates Task Plan with dependencies
    ↓
[Coder Agent] → Implements tasks iteratively (loop until DONE)
```

## 🚀 Features

- **Multi-Agent System**: Specialized agents for planning, architecture, and coding
- **LangGraph Integration**: State graph-based workflow orchestration
- **ReAct Pattern**: Coder agent uses reasoning and tool-use with file operations
- **File Safety**: Sandboxed file operations within project root
- **Context Awareness**: Each task includes full file context for consistency
- **Dependency Management**: Tasks ordered by implementation dependencies
- **Groq Integration**: Fast LLM inference with Llama models

## 📋 Prerequisites

- Python 3.8+
- Groq API Key
- Required Python packages (see installation)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-code-generator.git
   cd ai-code-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## 📖 Usage

### Basic Example

```python
from main import agent

user_prompt = "Create a simple calculator web application"
result = agent.invoke({"user_prompt": user_prompt})
print(result)
```

### What Happens

1. The system analyzes your prompt
2. Planner creates a complete project plan with files and features
3. Architect breaks it into implementation tasks with dependencies
4. Coder implements each task sequentially, writing files to `./generated_project/`

### Generated Output

All files are created in the `./generated_project/` directory with the following structure:
```
generated_project/
├── [frontend files]
├── [backend files]
├── [config files]
└── [other modules]
```

## 📁 Project Structure

```
.
├── main.py                 # Main entry point and graph setup
├── states.py               # Pydantic models for state management
├── prompts.py              # Agent system and context prompts
├── tools.py                # File operations and utilities
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
└── README.md               # This file
```

## 🔑 Key Components

### States (`states.py`)
- **File**: File path and purpose definition
- **Plan**: Project plan with name, description, tech stack, features
- **ImplementationTask**: Individual coding task with description and filepath
- **TaskPlan**: Ordered list of implementation tasks
- **CoderState**: Tracks coder agent progress through tasks

### Prompts (`prompts.py`)
- **planner_prompt()**: Generates project plans
- **architect_prompt()**: Creates task plans with dependencies
- **coder_system_prompt()**: System instructions for coder agent

### Tools (`tools.py`)
- **write_file()**: Safely write files to project root
- **read_file()**: Read file content with context
- **list_files()**: List files in directory
- **get_current_directory()**: Get project root
- **run_cmd()**: Execute shell commands safely
- **init_project_root()**: Initialize project directory

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_DEBUG=false
LANGCHAIN_VERBOSE=false
```

### LLM Model

Currently configured to use `meta-llama/llama-4-scout-17b-16e-instruct`. You can change this in `main.py`:

```python
llm = ChatGroq(model="your_preferred_model")
```

## 🛠️ Development

### Debug Mode

Enable detailed logging in `main.py`:
```python
set_debug(True)
set_verbose(True)
```

### Testing with Different Prompts

```python
test_prompts = [
    "Create a todo list application",
    "Build a weather API with Flask",
    "Make a markdown blog generator"
]

for prompt in test_prompts:
    result = agent.invoke({"user_prompt": prompt})
```

## 📦 Dependencies

- **langchain-groq**: Groq LLM integration
- **langgraph**: Agentic workflow orchestration
- **pydantic**: Data validation and settings
- **python-dotenv**: Environment variable management
- **langchain-core**: Core LangChain utilities

See `requirements.txt` for full list with versions.

## 🤖 How the Coder Agent Works

The Coder Agent uses a ReAct (Reasoning + Acting) pattern:

1. **Reads** the current task and existing file content
2. **Reasons** about the implementation approach
3. **Uses tools** to read/write files as needed
4. **Iterates** through all tasks until complete

Example task flow:
```
Task: Implement user authentication with password hashing
File: src/auth.py
Existing content: [empty or partial]
→ Coder reads any dependencies
→ Coder writes complete implementation
→ Moves to next task
```

## 🔒 Security Considerations

- **File Sandboxing**: All file operations restricted to `./generated_project/`
- **Path Validation**: `safe_path_for_project()` prevents directory traversal
- **Timeout Protection**: Shell commands have 30-second timeout
- **No Arbitrary Execution**: Only predefined tools available to LLM

## 🚧 Limitations & Future Improvements

### Current Limitations
- Coder agent iterates sequentially (no parallelization)
- No built-in testing or validation of generated code
- LLM may occasionally generate incomplete files

### Future Enhancements
- [ ] Add code validation and testing pipeline
- [ ] Parallel task execution
- [ ] Generated code review by QA agent
- [ ] Support for multiple programming languages
- [ ] Interactive refinement prompts
- [ ] Cache task plans for similar prompts

## 🐛 Troubleshooting

### "Groq API Key not found"
- Ensure `.env` file exists with `GROQ_API_KEY=your_key`
- Check that dotenv loads before LLM initialization

### "Planner did not give a valid response"
- Increase prompt clarity in user input
- Check LLM model availability on Groq
- Verify API quota limits

### "Attempt to write outside project root"
- This is a security feature - only files under `./generated_project/` are created
- Verify file paths in architect prompt

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Docs](https://console.groq.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 👨‍💼 Author

Mian Muhammad Hassan

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an GitHub Issue
- Email: mmh427726@gmail.com

---

**Happy Code Generation! 🎉**
