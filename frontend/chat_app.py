#!/usr/bin/env python3
"""
Chat App that interfaces with print_params.py script
This application provides a web-based chat interface where users can send messages
that get processed by the print_params.py script and the output is displayed.
"""

import gradio as gr
import subprocess
import shlex
import os
from datetime import datetime


def execute_print_params(user_message, history):
    """
    Execute the print_params.py script with user input and return the output.
    
    Args:
        user_message (str): The message from the user
        history (list): Chat history (not used in this simple implementation)
    
    Returns:
        tuple: (updated_history, empty_string_for_user_input)
    """
    try:
        # Get the directory of this script to find print_params.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print_params_path = os.path.join(script_dir, "print_params.py")
        
        # Parse the user message to extract arguments
        # Simple parsing: split by spaces but handle quoted strings
        try:
            args = shlex.split(user_message)
        except ValueError:
            # If shlex fails, just split by spaces
            args = user_message.split()
        
        # Construct the command
        cmd = ["python", print_params_path] + args
        
        # Execute the script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Format the response
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if result.returncode == 0:
            # Success
            bot_response = f"**[{timestamp}] Command executed successfully:**\n\n"
            bot_response += f"**Command:** `{' '.join(cmd)}`\n\n"
            bot_response += f"**Output:**\n```\n{result.stdout}\n```"
            
            if result.stderr:
                bot_response += f"\n\n**Warnings:**\n```\n{result.stderr}\n```"
        else:
            # Error
            bot_response = f"**[{timestamp}] Command failed:**\n\n"
            bot_response += f"**Command:** `{' '.join(cmd)}`\n\n"
            bot_response += f"**Error (Exit Code {result.returncode}):**\n```\n{result.stderr}\n```"
            
            if result.stdout:
                bot_response += f"\n\n**Partial Output:**\n```\n{result.stdout}\n```"
                
    except subprocess.TimeoutExpired:
        bot_response = f"**[{timestamp}] Command timed out:**\n\nThe script took too long to execute (>30 seconds)."
        
    except FileNotFoundError:
        bot_response = f"**[{timestamp}] Error:**\n\nCould not find print_params.py script in {script_dir}"
        
    except Exception as e:
        bot_response = f"**[{timestamp}] Unexpected error:**\n\n```\n{str(e)}\n```"
    
    # Update history
    history.append([user_message, bot_response])
    
    return history, ""


def get_examples():
    """Return example commands that users can try."""
    return [
        "hello world",
        "--name John --age 25",
        "item1 item2 item3 --verbose",
        "--name 'Jane Doe' --city 'New York' --debug",
        "test --output results.txt --verbose"
    ]


def clear_chat():
    """Clear the chat history."""
    return [], ""


# Custom CSS for better styling
custom_css = """
#chatbot {
    height: 500px;
}
.gradio-container {
    max-width: 800px;
    margin: auto;
}
"""

# Create the Gradio interface
with gr.Blocks(css=custom_css, title="Print Params Chat App") as app:
    gr.Markdown(
        """
        # 🤖 Print Params Chat App
        
        This chat interface allows you to interact with the `print_params.py` script.
        Send commands and see the script output in real-time!
        
        ## How to use:
        - Type your command arguments in the message box
        - The app will execute `python print_params.py [your_arguments]`
        - See the output displayed in the chat
        
        ## Example commands:
        - `hello world` - Simple positional arguments
        - `--name John --age 25` - Named arguments
        - `item1 item2 --verbose` - Mixed arguments with flags
        - `--help` - Show script help
        """
    )
    
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        value=[],
        label="Chat with Print Params Script",
        show_label=True,
        container=True,
        scale=1
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Enter your command arguments here (e.g., 'hello world' or '--name John --age 25')",
            label="Command Arguments",
            scale=4,
            lines=1
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)
    
    with gr.Row():
        clear_btn = gr.Button("Clear Chat", variant="secondary")
        
    with gr.Row():
        gr.Examples(
            examples=get_examples(),
            inputs=msg,
            label="Try these examples:"
        )
    
    # Event handlers
    msg.submit(
        execute_print_params,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    
    send_btn.click(
        execute_print_params,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    
    clear_btn.click(
        clear_chat,
        outputs=[chatbot, msg]
    )
    
    gr.Markdown(
        """
        ---
        **Note:** This app executes the `print_params.py` script with your input. 
        The script is safe and only prints information about the parameters you provide.
        """
    )


if __name__ == "__main__":
    print("Starting Print Params Chat App...")
    print("The app will be available at: http://localhost:7860")
    print("Press Ctrl+C to stop the server")
    
    # Launch the app
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=True,  # Set to True if you want a public link
        show_error=True,
        debug=False
    )
