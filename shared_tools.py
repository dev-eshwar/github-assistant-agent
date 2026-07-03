import subprocess
import os
import urllib.request
import urllib.error
import json

def run_shell_command(command: str) -> str:
    """Runs a shell command and returns its stdout and stderr combined.
    
    Args:
        command: The shell command line string to run.
    """
    try:
        res = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        output = res.stdout
        if res.stderr:
            output += "\n" + res.stderr
        return output
    except Exception as e:
        return f"Error executing command: {e}"

def read_file_content(path: str) -> str:
    """Reads and returns the content of a file.
    
    Args:
        path: The absolute or relative path to the file.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file_content(path: str, content: str) -> str:
    """Writes or overwrites content to a file.
    
    Args:
        path: The path to the file.
        content: The text content to write.
    """
    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file: {e}"

def list_directory(path: str) -> str:
    """Lists files and directories inside a directory.
    
    Args:
        path: The directory path.
    """
    try:
        if not os.path.exists(path):
            return f"Directory {path} does not exist"
        items = os.listdir(path)
        return json.dumps(items)
    except Exception as e:
        return f"Error listing directory: {e}"

def path_exists(path: str) -> bool:
    """Checks if a file or directory exists.
    
    Args:
        path: The path to check.
    """
    return os.path.exists(path)

def make_directory(path: str) -> str:
    """Creates a directory recursively if it doesn't exist.
    
    Args:
        path: The directory path to create.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created/verified directory: {path}"
    except Exception as e:
        return f"Error creating directory: {e}"

def http_get_request(url: str, headers_json: str = "{}") -> str:
    """Performs an HTTP GET request and returns the response body as text.
    
    Args:
        url: The API endpoint or page URL.
        headers_json: Optional JSON string of request headers (e.g. for Authorization).
    """
    try:
        headers = json.loads(headers_json)
        req = urllib.request.Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.read().decode('utf-8', errors='ignore')}"
    except Exception as e:
        return f"Request Error: {e}"
