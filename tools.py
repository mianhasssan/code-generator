"""
File operation tools for the AI Code Generator.

Provides safe, sandboxed file operations that are restricted to a project root directory.
All paths are validated to prevent directory traversal attacks.
"""

import pathlib
import subprocess
from typing import Tuple

from langchain_core.tools import tool


# ==================== PROJECT ROOT SECURITY ====================

# All file operations are confined to this directory
PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"


def safe_path_for_project(path: str) -> pathlib.Path:
    """
    Validates that a file path is within the project root.
    
    Prevents directory traversal attacks by ensuring all operations
    stay within the generated_project/ directory.
    
    Args:
        path: Requested file path
        
    Returns:
        Resolved pathlib.Path object
        
    Raises:
        ValueError: If path attempts to escape project root
    """
    p = (PROJECT_ROOT / path).resolve()
    
    # Check if resolved path is within project root
    if not (PROJECT_ROOT.resolve() in p.parents or PROJECT_ROOT.resolve() == p.parent or PROJECT_ROOT.resolve() == p):
        raise ValueError(f"Attempt to write outside project root: {path}")
    
    return p


# ==================== FILE OPERATIONS ====================

@tool
def write_file(path: str, content: str) -> str:
    """
    Write content to a file at the specified path.
    
    Creates directories as needed. All operations are sandboxed
    within the project root directory.
    
    Args:
        path: Relative file path (e.g., 'app.py', 'src/utils.py')
        content: File content to write
        
    Returns:
        Confirmation message with full path
    """
    p = safe_path_for_project(path)
    
    # Create parent directories if they don't exist
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file with UTF-8 encoding
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"✓ Written: {p}"


@tool
def read_file(path: str) -> str:
    """
    Read content from a file at the specified path.
    
    Returns empty string if file doesn't exist (useful for new files).
    
    Args:
        path: Relative file path (e.g., 'app.py', 'src/utils.py')
        
    Returns:
        File content, or empty string if file doesn't exist
    """
    p = safe_path_for_project(path)
    
    if not p.exists():
        return ""
    
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


@tool
def list_files(directory: str = ".") -> str:
    """
    List all files in a directory within the project.
    
    Useful for understanding project structure and existing files.
    
    Args:
        directory: Directory path relative to project root (default: '.')
        
    Returns:
        Newline-separated list of file paths, or error message
    """
    p = safe_path_for_project(directory)
    
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    
    # Get all files recursively
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    
    return "\n".join(files) if files else "No files found."


@tool
def get_current_directory() -> str:
    """
    Get the current project root directory.
    
    Returns:
        Full path to the project root directory
    """
    return str(PROJECT_ROOT)


@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a shell command within the project directory.
    
    Useful for running tests, installing dependencies, etc.
    
    Args:
        cmd: Shell command to execute
        cwd: Working directory (relative to project root, optional)
        timeout: Maximum execution time in seconds (default: 30)
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
    
    res = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd_dir),
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return res.returncode, res.stdout, res.stderr


# ==================== INITIALIZATION ====================

def init_project_root() -> str:
    """
    Initialize the project root directory.
    
    Creates the generated_project/ directory if it doesn't exist.
    
    Returns:
        Path to the project root
    """
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)


# Initialize on import
init_project_root()
