import os
import json
import os
import json
from langchain_core.tools import tool

BASE_PATH = "/Users/sureshkumars/Documents/AI_learnings/agentic-workflows/project"

def get_full_path(relative_path):
    """Joins the base path with a relative path."""
    return os.path.join(BASE_PATH, relative_path)

@tool
def list_files_and_directories(path):
    """
    Recursively lists all files and directories starting from the given path.

    @function list_files_and_directories
    @param {str} path - The absolute path from which to start the recursive traversal.
    @returns {dict} A nested dictionary representing the directory tree structure:
        {
            "name": <directory_or_file_name>,
            "path": <full_path>,
            "type": "directory" | "file",
            "contents": [<nested entries>]   # Only for directories
        }

    @throws {PermissionError} If the program lacks permission to access any directory.
    @throws {Exception} For any other unexpected errors.

    @example
    >>> list_files_and_directories("/Users/sureshkumars/Documents/myproject")
    {
        "name": "myproject",
        "path": "/Users/sureshkumars/Documents/myproject",
        "type": "directory",
        "contents": [
            {
                "name": "index.html",
                "path": "...",
                "type": "file"
            },
            {
                "name": "css",
                "path": "...",
                "type": "directory",
                "contents": [ ... ]
            }
        ]
    }
    """
    path = get_full_path(path)
    result = {
        "name": os.path.basename(path),
        "path": path,
        "type": "directory",
        "contents": []
    }

    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                result["contents"].append(list_files_and_directories(full_path))
            else:
                result["contents"].append({
                    "name": entry,
                    "path": full_path,
                    "type": "file"
                })
    except PermissionError:
        result["contents"].append({
            "name": "Permission Denied",
            "path": path,
            "type": "error"
        })
    except FileNotFoundError:
        return {
            "error": f"The path '{path}' does not exist."
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }
    return result

@tool
def create_file_with_content(file_path, content=""):
    """
    Creates a file at the given path.
    Creates any missing parent directories automatically.

    @function create_file_with_content
    @param {str} file_path - The file path relative to BASE_PATH.
    @param {str} content - Optional text content to write into the file. Default is empty string.
    @returns {void}

    @example
    >>> create_file_with_folders("logs/test.txt", "Hello, world!")
    # Creates /.../project/logs/test.txt with "Hello, world!" inside.
    """
    file_path = get_full_path(file_path)
    try:
        # Extract the directory part from the full file path
        folder = os.path.dirname(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folders: {folder}")

        # Create the file and write initial content
        with open(file_path, "w") as f:
            f.write(content)
            print(f"File created at: {file_path}")

    except Exception as e:
        print(f"Error: {e}")

@tool
def read_file(file_path):
    """
    Reads and returns the content of a file located under BASE_PATH.

    @function read_file
    @param {str} relative_file_path - The file path relative to BASE_PATH.
    @returns {str} The content of the file if found.

    @throws {FileNotFoundError} If the file does not exist.
    @throws {Exception} For any other read errors.

    @example
    >>> read_file("logs/test.txt")
    "Hello, world!\nMore info..."
    """
    file_path = get_full_path(file_path)
    try:
        with open(file_path, "r") as f:
            content = f.read()
            print(f"\nContents of '{file_path}':\n")
            print(content)
            return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

@tool     
def write_file(file_path, new_content, mode='w'):
    """
    Edits a file by either overwriting or appending content.

    @function edit_file
    @param {str} file_path - The file path relative to BASE_PATH.
    @param {str} new_content - The content to write or append to the file.
    @param {str} mode - Write mode: 'w' for overwrite, 'a' for append. Default is 'w'.
    @returns {void}

    @example
    >>> edit_file("logs/test.txt", "More info...", mode='a')
    # Appends content to the file
    """
    file_path = get_full_path(file_path)
    try:
        with open(file_path, mode) as f:
            f.write(new_content)
            action = "Appended to" if mode == 'a' else "Overwritten"
            print(f"{action} file: {file_path}")
    except Exception as e:
        print(f"Error editing file: {e}")
        

file_tool_list = [list_files_and_directories, create_file_with_content, write_file, read_file]