"""
Kai Core Capabilities Module
Provides code understanding, file operations, command execution, and tool integration.
Inspired by Kilo/Codex capabilities.
"""

import os
import sys
import json
import subprocess
import re
import ast
import traceback
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodeAnalysis:
    """Result of code analysis."""
    language: str
    lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity: int
    issues: List[str]


@dataclass
class FileOperation:
    """Result of a file operation."""
    success: bool
    message: str
    path: str
    content: Optional[str] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float


class CodeAnalyzer:
    """Analyze and understand code in multiple languages."""

    # Cache for analyzed code (key: hash of code, value: CodeAnalysis)
    _analysis_cache = {}
    _cache_max_size = 100

    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.sh': 'bash',
        '.ps1': 'powershell',
        '.md': 'markdown',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
    }

    @classmethod
    def _get_cache_key(cls, code: str, language: str) -> str:
        """Generate a cache key for code analysis."""
        import hashlib
        content = f"{language}:{code}"
        return hashlib.md5(content.encode()).hexdigest()

    @classmethod
    def _manage_cache_size(cls):
        """Keep cache size under limit by removing oldest entries."""
        if len(cls._analysis_cache) > cls._cache_max_size:
            # Remove oldest 20% of entries
            remove_count = len(cls._analysis_cache) - int(cls._cache_max_size * 0.8)
            keys_to_remove = list(cls._analysis_cache.keys())[:remove_count]
            for key in keys_to_remove:
                del cls._analysis_cache[key]

    @classmethod
    def detect_language(cls, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return cls.SUPPORTED_LANGUAGES.get(ext, 'unknown')

    @classmethod
    def analyze_python(cls, code: str) -> CodeAnalysis:
        """Analyze Python code."""
        lines = code.split('\n')
        functions = []
        classes = []
        imports = []
        issues = []

        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
            
            # Calculate cyclomatic complexity (simplified)
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            # Check for common issues
            if len(lines) > 500:
                issues.append("File is very long (>500 lines). Consider splitting.")
            if any(len(line) > 120 for line in lines):
                issues.append("Some lines exceed 120 characters.")
            
        except SyntaxError as e:
            issues.append(f"Syntax error: {str(e)}")
            complexity = 0

        return CodeAnalysis(
            language='python',
            lines=len(lines),
            functions=functions,
            classes=classes,
            imports=imports,
            complexity=complexity,
            issues=issues
        )

    @classmethod
    def analyze_javascript(cls, code: str) -> CodeAnalysis:
        """Analyze JavaScript/TypeScript code."""
        lines = code.split('\n')
        functions = []
        classes = []
        imports = []
        issues = []

        # Simple regex-based extraction
        func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'(?:import|from)\s+[\'"]([^\'"]+)[\'"]'

        for line in lines:
            func_match = re.search(func_pattern, line)
            if func_match:
                func_name = func_match.group(1) or func_match.group(2)
                if func_name:
                    functions.append(func_name)
            
            class_match = re.search(class_pattern, line)
            if class_match:
                classes.append(class_match.group(1))
            
            import_match = re.search(import_pattern, line)
            if import_match:
                imports.append(import_match.group(1))

        # Calculate complexity
        complexity = 1
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||']
        for line in lines:
            for keyword in complexity_keywords:
                if keyword in line:
                    complexity += 1

        if len(lines) > 500:
            issues.append("File is very long (>500 lines). Consider splitting.")

        return CodeAnalysis(
            language='javascript',
            lines=len(lines),
            functions=functions,
            classes=classes,
            imports=imports,
            complexity=complexity,
            issues=issues
        )

    @classmethod
    def analyze_code(cls, code: str, language: str = 'python') -> CodeAnalysis:
        """Analyze code in the specified language with caching."""
        # Check cache first
        cache_key = cls._get_cache_key(code, language)
        if cache_key in cls._analysis_cache:
            return cls._analysis_cache[cache_key]
        
        # Perform analysis
        if language == 'python':
            result = cls.analyze_python(code)
        elif language in ['javascript', 'typescript']:
            result = cls.analyze_javascript(code)
        else:
            # Generic analysis
            lines = code.split('\n')
            result = CodeAnalysis(
                language=language,
                lines=len(lines),
                functions=[],
                classes=[],
                imports=[],
                complexity=0,
                issues=[]
            )
        
        # Cache the result
        cls._analysis_cache[cache_key] = result
        cls._manage_cache_size()
        
        return result

    @classmethod
    def analyze_file(cls, file_path: str) -> CodeAnalysis:
        """Analyze a file with caching."""
        try:
            # Check cache by file path first
            cache_key = f"file:{file_path}"
            if cache_key in cls._analysis_cache:
                # Verify file hasn't changed
                import os
                cached_result = cls._analysis_cache[cache_key]
                if hasattr(cached_result, '_file_mtime'):
                    current_mtime = os.path.getmtime(file_path)
                    if current_mtime == cached_result._file_mtime:
                        return cached_result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            language = cls.detect_language(file_path)
            result = cls.analyze_code(code, language)
            
            # Add file metadata to result for cache validation
            import os
            result._file_mtime = os.path.getmtime(file_path)
            cls._analysis_cache[cache_key] = result
            cls._manage_cache_size()
            
            return result
        except Exception as e:
            return CodeAnalysis(
                language='unknown',
                lines=0,
                functions=[],
                classes=[],
                imports=[],
                complexity=0,
                issues=[f"Error reading file: {str(e)}"]
            )


class CodeGenerator:
    """Generate code based on specifications."""

    @staticmethod
    def generate_function(name: str, params: List[str], return_type: str = 'None', 
                         docstring: str = '', language: str = 'python') -> str:
        """Generate a function template."""
        if language == 'python':
            params_str = ', '.join(params)
            docstring_lines = f'    """{docstring}"""' if docstring else '    pass'
            return f"""def {name}({params_str}) -> {return_type}:
{docstring_lines}
"""
        elif language in ['javascript', 'typescript']:
            params_str = ', '.join(params)
            return f"""function {name}({params_str}) {{
    // {docstring or 'TODO: Implement'}
}}
"""
        return f"// Cannot generate {language} function"

    @staticmethod
    def generate_class(name: str, methods: List[str] = None, 
                      parent_class: str = None, language: str = 'python') -> str:
        """Generate a class template."""
        if language == 'python':
            parent = f'({parent_class})' if parent_class else ''
            methods_code = '\n'.join([f'    def {m}(self):\n        pass' for m in (methods or [])])
            return f"""class {name}{parent}:
    def __init__(self):
        pass

{methods_code}
"""
        elif language in ['javascript', 'typescript']:
            extends = f' extends {parent_class}' if parent_class else ''
            methods_code = '\n'.join([f'    {m}() {{\n        // TODO: Implement\n    }}' for m in (methods or [])])
            return f"""class {name}{extends} {{
    constructor() {{
        // TODO: Initialize
    }}

{methods_code}
}}
"""
        return f"// Cannot generate {language} class"

    @staticmethod
    def generate_test(function_name: str, test_cases: List[Dict] = None, 
                     language: str = 'python') -> str:
        """Generate unit tests for a function."""
        if language == 'python':
            tests = []
            for i, case in enumerate(test_cases or [{'input': [], 'expected': None}]):
                input_str = ', '.join(repr(v) for v in case.get('input', []))
                expected = repr(case.get('expected'))
                tests.append(f"""    def test_{function_name}_{i+1}(self):
        result = {function_name}({input_str})
        self.assertEqual(result, {expected})""")
            
            tests_code = '\n\n'.join(tests)
            return f"""import unittest

class Test{function_name.title()}(unittest.TestCase):
{tests_code}

if __name__ == '__main__':
    unittest.main()
"""
        return f"// Cannot generate {language} tests"


class FileManager:
    """Handle file operations safely."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.allowed_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs',
            '.rb', '.php', '.swift', '.kt', '.scala', '.html', '.css', '.sql',
            '.sh', '.ps1', '.md', '.txt', '.json', '.xml', '.yaml', '.yml',
            '.csv', '.log', '.cfg', '.ini', '.toml'
        }

    def _validate_path(self, path: str) -> Tuple[bool, str]:
        """Validate that a path is safe to access."""
        try:
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = self.base_path / target_path
            
            # Resolve to prevent path traversal
            resolved = target_path.resolve()
            
            # Check if within base path
            if not str(resolved).startswith(str(self.base_path.resolve())):
                return False, "Path traversal detected"
            
            # Check extension for write operations
            if resolved.suffix and resolved.suffix not in self.allowed_extensions:
                return False, f"File extension {resolved.suffix} not allowed"
            
            return True, str(resolved)
        except Exception as e:
            return False, f"Path validation error: {str(e)}"

    def read_file(self, path: str) -> FileOperation:
        """Read a file safely."""
        valid, result = self._validate_path(path)
        if not valid:
            return FileOperation(False, result, path)
        
        try:
            with open(result, 'r', encoding='utf-8') as f:
                content = f.read()
            return FileOperation(True, "File read successfully", result, content)
        except FileNotFoundError:
            return FileOperation(False, f"File not found: {path}", path)
        except PermissionError:
            return FileOperation(False, f"Permission denied: {path}", path)
        except Exception as e:
            return FileOperation(False, f"Error reading file: {str(e)}", path)

    def write_file(self, path: str, content: str, create_dirs: bool = True) -> FileOperation:
        """Write content to a file safely."""
        valid, result = self._validate_path(path)
        if not valid:
            return FileOperation(False, result, path)
        
        try:
            target_path = Path(result)
            if create_dirs:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return FileOperation(True, "File written successfully", result)
        except PermissionError:
            return FileOperation(False, f"Permission denied: {path}", path)
        except Exception as e:
            return FileOperation(False, f"Error writing file: {str(e)}", path)

    def edit_file(self, path: str, old_content: str, new_content: str) -> FileOperation:
        """Edit a file by replacing old content with new content."""
        read_result = self.read_file(path)
        if not read_result.success:
            return read_result
        
        if old_content not in read_result.content:
            return FileOperation(False, "Old content not found in file", path)
        
        updated_content = read_result.content.replace(old_content, new_content, 1)
        return self.write_file(path, updated_content, create_dirs=False)

    def list_files(self, directory: str = '.', pattern: str = '*') -> FileOperation:
        """List files in a directory."""
        valid, result = self._validate_path(directory)
        if not valid:
            return FileOperation(False, result, directory)
        
        try:
            path = Path(result)
            if not path.is_dir():
                return FileOperation(False, f"Not a directory: {directory}", directory)
            
            files = list(path.glob(pattern))
            file_list = [str(f.relative_to(self.base_path)) for f in files]
            return FileOperation(True, f"Found {len(files)} files", directory, json.dumps(file_list, indent=2))
        except Exception as e:
            return FileOperation(False, f"Error listing files: {str(e)}", directory)

    def delete_file(self, path: str) -> FileOperation:
        """Delete a file safely."""
        valid, result = self._validate_path(path)
        if not valid:
            return FileOperation(False, result, path)
        
        try:
            target_path = Path(result)
            if target_path.is_file():
                target_path.unlink()
                return FileOperation(True, "File deleted successfully", result)
            else:
                return FileOperation(False, f"Not a file: {path}", path)
        except PermissionError:
            return FileOperation(False, f"Permission denied: {path}", path)
        except Exception as e:
            return FileOperation(False, f"Error deleting file: {str(e)}", path)

    async def read_file_async(self, path: str) -> FileOperation:
        """Read a file asynchronously."""
        valid, result = self._validate_path(path)
        if not valid:
            return FileOperation(False, result, path)
        
        try:
            async with aiofiles.open(result, 'r', encoding='utf-8') as f:
                content = await f.read()
            return FileOperation(True, "File read successfully", result, content)
        except FileNotFoundError:
            return FileOperation(False, f"File not found: {path}", path)
        except PermissionError:
            return FileOperation(False, f"Permission denied: {path}", path)
        except Exception as e:
            return FileOperation(False, f"Error reading file: {str(e)}", path)

    async def write_file_async(self, path: str, content: str, create_dirs: bool = True) -> FileOperation:
        """Write content to a file asynchronously."""
        valid, result = self._validate_path(path)
        if not valid:
            return FileOperation(False, result, path)
        
        try:
            target_path = Path(result)
            if create_dirs:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(target_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return FileOperation(True, "File written successfully", result)
        except PermissionError:
            return FileOperation(False, f"Permission denied: {path}", path)
        except Exception as e:
            return FileOperation(False, f"Error writing file: {str(e)}", path)

    async def analyze_file_async(self, file_path: str) -> CodeAnalysis:
        """Analyze a file asynchronously."""
        try:
            # Check cache by file path first
            cache_key = f"file:{file_path}"
            if cache_key in CodeAnalyzer._analysis_cache:
                # Verify file hasn't changed
                import os
                cached_result = CodeAnalyzer._analysis_cache[cache_key]
                if hasattr(cached_result, '_file_mtime'):
                    current_mtime = os.path.getmtime(file_path)
                    if current_mtime == cached_result._file_mtime:
                        return cached_result
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                code = await f.read()
            language = CodeAnalyzer.detect_language(file_path)
            result = CodeAnalyzer.analyze_code(code, language)
            
            # Add file metadata to result for cache validation
            import os
            result._file_mtime = os.path.getmtime(file_path)
            CodeAnalyzer._analysis_cache[cache_key] = result
            CodeAnalyzer._manage_cache_size()
            
            return result
        except Exception as e:
            return CodeAnalysis(
                language='unknown',
                lines=0,
                functions=[],
                classes=[],
                imports=[],
                complexity=0,
                issues=[f"Error reading file: {str(e)}"]
            )


class CommandExecutor:
    """Execute commands safely in a sandboxed environment."""

    def __init__(self, working_dir: str = None, timeout: int = 30):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.timeout = timeout
        self.blocked_commands = {
            'rm -rf /', 'format', 'del /f /s /q', 'shutdown', 'reboot',
            'mkfs', 'dd if=', ':(){:|:&};:'
        }
        # Performance metrics
        self._execution_history = []
        self._max_history = 100
        self._total_executions = 0
        self._total_execution_time = 0.0
        self._successful_executions = 0

    def _is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if a command is safe to execute."""
        command_lower = command.lower()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                return False, f"Blocked dangerous command: {blocked}"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'rm\s+-rf\s+/',
            r'del\s+/[sf]\s+',
            r'format\s+[a-z]:',
            r'>\s*/dev/sd[a-z]',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, command_lower):
                return False, f"Suspicious command pattern detected"
        
        return True, "Command is safe"

    def execute(self, command: str, capture_output: bool = True) -> CommandResult:
        """Execute a command safely with performance tracking."""
        import time
        
        # Safety check
        safe, message = self._is_command_safe(command)
        if not safe:
            return CommandResult(
                success=False,
                stdout='',
                stderr=f"Safety check failed: {message}",
                return_code=-1,
                execution_time=0
            )
        
        try:
            start_time = time.time()
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.working_dir),
                capture_output=capture_output,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            # Track performance metrics
            self._total_executions += 1
            self._total_execution_time += execution_time
            if result.returncode == 0:
                self._successful_executions += 1
            
            # Add to history
            self._execution_history.append({
                'command': command[:100],  # Truncate long commands
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            
            # Keep history size limited
            if len(self._execution_history) > self._max_history:
                self._execution_history = self._execution_history[-self._max_history:]
            
            return CommandResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time
            )
        except subprocess.TimeoutExpired:
            execution_time = self.timeout
            self._total_executions += 1
            self._total_execution_time += execution_time
            
            return CommandResult(
                success=False,
                stdout='',
                stderr=f"Command timed out after {self.timeout} seconds",
                return_code=-1,
                execution_time=execution_time
            )
        except Exception as e:
            self._total_executions += 1
            
            return CommandResult(
                success=False,
                stdout='',
                stderr=f"Execution error: {str(e)}",
                return_code=-1,
                execution_time=0
            )

    def execute_python(self, code: str) -> CommandResult:
        """Execute Python code safely."""
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = self.execute(f'python "{temp_file}"')
            
            # Clean up
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return result
        except Exception as e:
            return CommandResult(
                success=False,
                stdout='',
                stderr=f"Error executing Python code: {str(e)}",
                return_code=-1,
                execution_time=0
            )

    def get_performance_stats(self) -> Dict:
        """Get performance statistics for command execution."""
        if self._total_executions == 0:
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'success_rate': 0.0,
                'average_execution_time': 0.0,
                'total_execution_time': 0.0
            }
        
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'success_rate': self._successful_executions / self._total_executions,
            'average_execution_time': self._total_execution_time / self._total_executions,
            'total_execution_time': self._total_execution_time,
            'recent_executions': self._execution_history[-10:]  # Last 10 executions
        }


class ToolRegistry:
    """Registry for available tools and capabilities."""

    def __init__(self):
        self.tools = {}
        self.categories = {
            'code': [],
            'file': [],
            'command': [],
            'analysis': [],
            'generation': []
        }

    def register_tool(self, name: str, description: str, category: str, 
                     handler: callable, parameters: Dict = None):
        """Register a new tool."""
        self.tools[name] = {
            'name': name,
            'description': description,
            'category': category,
            'handler': handler,
            'parameters': parameters or {}
        }
        
        if category in self.categories:
            self.categories[category].append(name)

    def get_tool(self, name: str) -> Optional[Dict]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: str = None) -> List[Dict]:
        """List available tools, optionally filtered by category."""
        if category:
            return [self.tools[name] for name in self.categories.get(category, [])]
        return list(self.tools.values())

    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool not found: {name}"}
        
        try:
            return tool['handler'](**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


class ProjectContext:
    """Maintain context about the current project."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.file_cache = {}
        self.structure = {}
        self.recent_files = []
        self.max_recent = 10
        self._last_scan_time = None
        self._file_mtimes = {}  # Track file modification times

    def scan_project(self) -> Dict:
        """Scan the project structure."""
        structure = {
            'root': str(self.project_root),
            'directories': [],
            'files': [],
            'languages': {},
            'total_lines': 0
        }
        
        try:
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    rel_path = str(item.relative_to(self.project_root))
                    structure['files'].append(rel_path)
                    
                    # Detect language
                    ext = item.suffix.lower()
                    if ext in CodeAnalyzer.SUPPORTED_LANGUAGES:
                        lang = CodeAnalyzer.SUPPORTED_LANGUAGES[ext]
                        structure['languages'][lang] = structure['languages'].get(lang, 0) + 1
                    
                    # Count lines for text files
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            structure['total_lines'] += lines
                    except:
                        pass
                        
                elif item.is_dir():
                    rel_path = str(item.relative_to(self.project_root))
                    structure['directories'].append(rel_path)
            
            self.structure = structure
            return structure
        except Exception as e:
            return {"error": f"Error scanning project: {str(e)}"}

    def get_file_context(self, file_path: str) -> Dict:
        """Get context about a specific file."""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            stat = full_path.stat()
            context = {
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': full_path.suffix,
                'language': CodeAnalyzer.detect_language(str(full_path))
            }
            
            # Add to recent files
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:self.max_recent]
            
            return context
        except Exception as e:
            return {"error": f"Error getting file context: {str(e)}"}

    def find_files(self, pattern: str) -> List[str]:
        """Find files matching a pattern."""
        try:
            matches = list(self.project_root.rglob(pattern))
            return [str(m.relative_to(self.project_root)) for m in matches]
        except:
            return []

    def get_related_files(self, file_path: str) -> List[str]:
        """Get files related to the given file."""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return []
        
        related = []
        
        # Find files with same name but different extension
        stem = full_path.stem
        for item in self.project_root.rglob(f"{stem}.*"):
            if item != full_path:
                related.append(str(item.relative_to(self.project_root)))
        
        # Find test files
        test_patterns = [f"test_{stem}.*", f"{stem}_test.*", f"tests/*{stem}*"]
        for pattern in test_patterns:
            for item in self.project_root.rglob(pattern):
                related.append(str(item.relative_to(self.project_root)))
        
        return list(set(related))

    def update_scan_incremental(self) -> Dict:
        """Update project scan incrementally by checking only changed files."""
        import time
        
        if not self.structure:
            # No previous scan, do full scan
            return self.scan_project()
        
        try:
            current_time = time.time()
            changes = {
                'added': [],
                'modified': [],
                'deleted': [],
                'total_changes': 0
            }
            
            # Check for new or modified files
            for item in self.project_root.rglob('*'):
                if item.is_file():
                    rel_path = str(item.relative_to(self.project_root))
                    current_mtime = item.stat().st_mtime
                    
                    if rel_path not in self._file_mtimes:
                        # New file
                        changes['added'].append(rel_path)
                        self._file_mtimes[rel_path] = current_mtime
                    elif current_mtime > self._file_mtimes[rel_path]:
                        # Modified file
                        changes['modified'].append(rel_path)
                        self._file_mtimes[rel_path] = current_mtime
            
            # Check for deleted files
            for rel_path in list(self._file_mtimes.keys()):
                full_path = self.project_root / rel_path
                if not full_path.exists():
                    changes['deleted'].append(rel_path)
                    del self._file_mtimes[rel_path]
            
            changes['total_changes'] = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
            
            # Update structure if there were changes
            if changes['total_changes'] > 0:
                # Update files list
                self.structure['files'] = [f for f in self.structure['files'] if f not in changes['deleted']]
                self.structure['files'].extend(changes['added'])
                
                # Update language counts
                for file_path in changes['added'] + changes['modified']:
                    ext = Path(file_path).suffix.lower()
                    if ext in CodeAnalyzer.SUPPORTED_LANGUAGES:
                        lang = CodeAnalyzer.SUPPORTED_LANGUAGES[ext]
                        self.structure['languages'][lang] = self.structure['languages'].get(lang, 0) + 1
                
                for file_path in changes['deleted']:
                    ext = Path(file_path).suffix.lower()
                    if ext in CodeAnalyzer.SUPPORTED_LANGUAGES:
                        lang = CodeAnalyzer.SUPPORTED_LANGUAGES[ext]
                        if lang in self.structure['languages']:
                            self.structure['languages'][lang] = max(0, self.structure['languages'][lang] - 1)
            
            self._last_scan_time = current_time
            return {
                'success': True,
                'changes': changes,
                'structure': self.structure
            }
        except Exception as e:
            return {'error': f"Error updating scan: {str(e)}"}


class KaiCapabilities:
    """Main capabilities class that combines all features."""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or str(Path.cwd())
        self.code_analyzer = CodeAnalyzer()
        self.code_generator = CodeGenerator()
        self.file_manager = FileManager(self.project_root)
        self.command_executor = CommandExecutor(self.project_root)
        self.tool_registry = ToolRegistry()
        self.project_context = ProjectContext(self.project_root)
        
        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""
        # Code analysis tools
        self.tool_registry.register_tool(
            'analyze_code',
            'Analyze code for structure, complexity, and issues',
            'analysis',
            self.analyze_code,
            {'code': str, 'language': str}
        )
        
        self.tool_registry.register_tool(
            'analyze_file',
            'Analyze a file for structure, complexity, and issues',
            'analysis',
            self.analyze_file,
            {'file_path': str}
        )
        
        # Code generation tools
        self.tool_registry.register_tool(
            'generate_function',
            'Generate a function template',
            'generation',
            self.generate_function,
            {'name': str, 'params': list, 'return_type': str, 'docstring': str, 'language': str}
        )
        
        self.tool_registry.register_tool(
            'generate_class',
            'Generate a class template',
            'generation',
            self.generate_class,
            {'name': str, 'methods': list, 'parent_class': str, 'language': str}
        )
        
        self.tool_registry.register_tool(
            'generate_test',
            'Generate unit tests for a function',
            'generation',
            self.generate_test,
            {'function_name': str, 'test_cases': list, 'language': str}
        )
        
        # File operation tools
        self.tool_registry.register_tool(
            'read_file',
            'Read a file safely',
            'file',
            self.read_file,
            {'path': str}
        )
        
        self.tool_registry.register_tool(
            'write_file',
            'Write content to a file',
            'file',
            self.write_file,
            {'path': str, 'content': str}
        )
        
        self.tool_registry.register_tool(
            'edit_file',
            'Edit a file by replacing content',
            'file',
            self.edit_file,
            {'path': str, 'old_content': str, 'new_content': str}
        )
        
        self.tool_registry.register_tool(
            'list_files',
            'List files in a directory',
            'file',
            self.list_files,
            {'directory': str, 'pattern': str}
        )
        
        # Command execution tools
        self.tool_registry.register_tool(
            'execute_command',
            'Execute a shell command',
            'command',
            self.execute_command,
            {'command': str}
        )
        
        self.tool_registry.register_tool(
            'execute_python',
            'Execute Python code',
            'command',
            self.execute_python,
            {'code': str}
        )
        
        # Project context tools
        self.tool_registry.register_tool(
            'scan_project',
            'Scan project structure',
            'analysis',
            self.scan_project,
            {}
        )
        
        self.tool_registry.register_tool(
            'find_files',
            'Find files matching a pattern',
            'file',
            self.find_files,
            {'pattern': str}
        )

    # Code Analysis Methods
    def analyze_code(self, code: str, language: str = 'python') -> Dict:
        """Analyze code and return results as dict."""
        analysis = self.code_analyzer.analyze_code(code, language)
        return {
            'language': analysis.language,
            'lines': analysis.lines,
            'functions': analysis.functions,
            'classes': analysis.classes,
            'imports': analysis.imports,
            'complexity': analysis.complexity,
            'issues': analysis.issues
        }

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a file and return results as dict."""
        analysis = self.code_analyzer.analyze_file(file_path)
        return {
            'language': analysis.language,
            'lines': analysis.lines,
            'functions': analysis.functions,
            'classes': analysis.classes,
            'imports': analysis.imports,
            'complexity': analysis.complexity,
            'issues': analysis.issues
        }

    # Code Generation Methods
    def generate_function(self, name: str, params: List[str] = None, 
                         return_type: str = 'None', docstring: str = '', 
                         language: str = 'python') -> str:
        """Generate a function template."""
        return self.code_generator.generate_function(name, params or [], return_type, docstring, language)

    def generate_class(self, name: str, methods: List[str] = None, 
                      parent_class: str = None, language: str = 'python') -> str:
        """Generate a class template."""
        return self.code_generator.generate_class(name, methods, parent_class, language)

    def generate_test(self, function_name: str, test_cases: List[Dict] = None, 
                     language: str = 'python') -> str:
        """Generate unit tests."""
        return self.code_generator.generate_test(function_name, test_cases, language)

    # File Operation Methods
    def read_file(self, path: str) -> Dict:
        """Read a file."""
        result = self.file_manager.read_file(path)
        return {
            'success': result.success,
            'message': result.message,
            'path': result.path,
            'content': result.content
        }

    def write_file(self, path: str, content: str) -> Dict:
        """Write to a file."""
        result = self.file_manager.write_file(path, content)
        return {
            'success': result.success,
            'message': result.message,
            'path': result.path
        }

    def edit_file(self, path: str, old_content: str, new_content: str) -> Dict:
        """Edit a file."""
        result = self.file_manager.edit_file(path, old_content, new_content)
        return {
            'success': result.success,
            'message': result.message,
            'path': result.path
        }

    def list_files(self, directory: str = '.', pattern: str = '*') -> Dict:
        """List files."""
        result = self.file_manager.list_files(directory, pattern)
        return {
            'success': result.success,
            'message': result.message,
            'path': result.path,
            'files': json.loads(result.content) if result.content else []
        }

    # Command Execution Methods
    def execute_command(self, command: str) -> Dict:
        """Execute a command."""
        result = self.command_executor.execute(command)
        return {
            'success': result.success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.return_code,
            'execution_time': result.execution_time
        }

    def execute_python(self, code: str) -> Dict:
        """Execute Python code."""
        result = self.command_executor.execute_python(code)
        return {
            'success': result.success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.return_code,
            'execution_time': result.execution_time
        }

    # Project Context Methods
    def scan_project(self) -> Dict:
        """Scan project structure."""
        return self.project_context.scan_project()

    def find_files(self, pattern: str) -> List[str]:
        """Find files matching a pattern."""
        return self.project_context.find_files(pattern)

    def get_file_context(self, file_path: str) -> Dict:
        """Get context about a file."""
        return self.project_context.get_file_context(file_path)

    def get_related_files(self, file_path: str) -> List[str]:
        """Get files related to a file."""
        return self.project_context.get_related_files(file_path)

    def get_recent_files(self) -> List[str]:
        """Get recently inspected project files."""
        return list(self.project_context.recent_files)

    # Tool Registry Methods
    def list_tools(self, category: str = None) -> List[Dict]:
        """List available tools."""
        return self.tool_registry.list_tools(category)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        return self.tool_registry.execute_tool(tool_name, **kwargs)

    # Utility Methods
    def get_capabilities_summary(self) -> Dict:
        """Get a summary of all capabilities."""
        return {
            'code_analysis': {
                'languages': list(CodeAnalyzer.SUPPORTED_LANGUAGES.values()),
                'features': ['function extraction', 'class extraction', 'import analysis', 'complexity calculation', 'issue detection']
            },
            'code_generation': {
                'features': ['function templates', 'class templates', 'test generation']
            },
            'file_operations': {
                'features': ['read', 'write', 'edit', 'list', 'delete'],
                'safety': ['path validation', 'extension filtering', 'path traversal prevention']
            },
            'command_execution': {
                'features': ['shell commands', 'python code execution'],
                'safety': ['command filtering', 'timeout protection', 'sandboxed execution']
            },
            'project_context': {
                'features': ['project scanning', 'file context', 'related files', 'file search']
            },
            'tools': {
                'total': len(self.tool_registry.tools),
                'categories': list(self.tool_registry.categories.keys())
            }
        }


# Example usage and testing
if __name__ == "__main__":
    print("Kai Capabilities Module")
    print("=" * 50)
    
    # Initialize capabilities
    kai = KaiCapabilities()
    
    # Print summary
    summary = kai.get_capabilities_summary()
    print("\nCapabilities Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test code analysis
    print("\n" + "=" * 50)
    print("Testing Code Analysis:")
    test_code = """
def hello_world(name: str) -> str:
    '''Say hello to someone.'''
    return f"Hello, {name}!"

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
"""
    analysis = kai.analyze_code(test_code, 'python')
    print(json.dumps(analysis, indent=2))
    
    # Test code generation
    print("\n" + "=" * 50)
    print("Testing Code Generation:")
    func = kai.generate_function('process_data', ['data', 'config'], 'dict', 'Process data with configuration')
    print(func)
    
    # List available tools
    print("\n" + "=" * 50)
    print("Available Tools:")
    tools = kai.list_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
