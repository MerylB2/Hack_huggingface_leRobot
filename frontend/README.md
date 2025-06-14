# Print Params Chat App

A web-based chat application built with Gradio that interfaces with the `print_params.py` script.

## Features

- 🌐 Web-based chat interface
- 🤖 Interactive communication with the print_params.py script
- 📝 Real-time output display
- 🎯 Example commands for easy testing
- 🧹 Clear chat functionality
- ⚡ Fast and responsive UI

## Files

- `print_params.py` - The main parameter processing script
- `chat_app.py` - The Gradio web application
- `pyproject.toml` - Poetry configuration file
- `README.md` - This file

## Installation

### Option 1: Using Poetry (Recommended)

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run the chat app
poetry run python chat_app.py
```

### Option 2: Using pip

```bash
# Install Gradio
pip install gradio

# Run the chat app
python chat_app.py
```

## Usage

1. Start the application:
   ```bash
   python chat_app.py
   ```

2. Open your browser to: `http://localhost:7860`

3. Enter command arguments in the chat input field

4. See the output from the `print_params.py` script displayed in the chat

## Example Commands

Try these commands in the chat interface:

- `hello world` - Simple positional arguments
- `--name John --age 25` - Named arguments
- `item1 item2 item3 --verbose` - Mixed arguments with flags
- `--name "Jane Doe" --city "New York" --debug` - Arguments with spaces
- `--help` - Show script help

## How It Works

1. User enters command arguments in the web interface
2. The chat app executes: `python print_params.py [user_arguments]`
3. The script output is captured and displayed in the chat
4. Both successful outputs and errors are handled gracefully

## Architecture

```
User Input → Gradio Interface → subprocess.run() → print_params.py → Output Display
```

The application uses:
- **Gradio**: For the web interface and chat functionality
- **subprocess**: To execute the print_params.py script
- **shlex**: For proper argument parsing

## Security Notes

- The application only executes the local `print_params.py` script
- Input is properly sanitized using `shlex.split()`
- Script execution has a 30-second timeout
- No arbitrary code execution is allowed

## Customization

You can modify the chat app by:
- Changing the port in `chat_app.py` (default: 7860)
- Adding more example commands in the `get_examples()` function
- Customizing the CSS styling
- Adding more parameter options to the print_params.py script

## Troubleshooting

**Port already in use:**
```bash
# Kill process using port 7860
sudo lsof -ti:7860 | xargs kill -9
```

**Permission denied:**
```bash
# Make scripts executable
chmod +x print_params.py chat_app.py
```

**Module not found:**
```bash
# Install missing dependencies
pip install gradio
```
