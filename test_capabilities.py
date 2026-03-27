#!/usr/bin/env python3
"""
Test script for Kai Capabilities
Verifies all new features work correctly.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from kai_capabilities import KaiCapabilities


def test_code_analysis():
    """Test code analysis capabilities."""
    print("\n" + "=" * 60)
    print("TEST: Code Analysis")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # Test Python analysis
    python_code = """
import os
import sys
from pathlib import Path

def process_data(data: dict, config: dict) -> dict:
    '''Process data with configuration.'''
    result = {}
    for key, value in data.items():
        if key in config.get('allowed_keys', []):
            result[key] = value * 2
    return result

class DataProcessor:
    def __init__(self, name: str):
        self.name = name
        self.data = {}
    
    def load(self, file_path: str) -> bool:
        '''Load data from file.'''
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def save(self, file_path: str) -> bool:
        '''Save data to file.'''
        try:
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
"""
    
    analysis = kai.analyze_code(python_code, 'python')
    print(f"Language: {analysis['language']}")
    print(f"Lines: {analysis['lines']}")
    print(f"Functions: {analysis['functions']}")
    print(f"Classes: {analysis['classes']}")
    print(f"Imports: {analysis['imports']}")
    print(f"Complexity: {analysis['complexity']}")
    print(f"Issues: {analysis['issues']}")
    
    assert analysis['language'] == 'python'
    assert analysis['lines'] > 0
    assert 'process_data' in analysis['functions']
    assert 'DataProcessor' in analysis['classes']
    print("[PASS] Python analysis test passed")
    
    # Test JavaScript analysis
    js_code = """
import React from 'react';
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    const increment = () => setCount(count + 1);
    const decrement = () => setCount(count - 1);
    
    return (
        <div>
            <h1>Count: {count}</h1>
            <button onClick={increment}>+</button>
            <button onClick={decrement}>-</button>
        </div>
    );
}

export default Counter;
"""
    
    analysis = kai.analyze_code(js_code, 'javascript')
    print(f"\nJavaScript Analysis:")
    print(f"Language: {analysis['language']}")
    print(f"Lines: {analysis['lines']}")
    print(f"Functions: {analysis['functions']}")
    
    assert analysis['language'] == 'javascript'
    assert 'Counter' in analysis['functions']
    print("[PASS] JavaScript analysis test passed")


def test_code_generation():
    """Test code generation capabilities."""
    print("\n" + "=" * 60)
    print("TEST: Code Generation")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # Test function generation
    func = kai.generate_function(
        'calculate_average',
        ['numbers: List[float]'],
        'float',
        'Calculate the average of a list of numbers',
        'python'
    )
    print("Generated Function:")
    print(func)
    assert 'def calculate_average' in func
    assert 'numbers: List[float]' in func
    print("[PASS] Function generation test passed")
    
    # Test class generation
    cls = kai.generate_class(
        'DatabaseManager',
        ['connect', 'disconnect', 'execute_query'],
        'BaseManager',
        'python'
    )
    print("\nGenerated Class:")
    print(cls)
    assert 'class DatabaseManager' in cls
    assert 'def connect(self)' in cls
    print("[PASS] Class generation test passed")
    
    # Test test generation
    test = kai.generate_test(
        'calculate_average',
        [
            {'input': [[1, 2, 3]], 'expected': 2.0},
            {'input': [[10, 20, 30]], 'expected': 20.0}
        ],
        'python'
    )
    print("\nGenerated Test:")
    print(test)
    assert 'class TestCalculate_Average' in test
    assert 'test_calculate_average_1' in test
    print("[PASS] Test generation test passed")


def test_file_operations():
    """Test file operation capabilities."""
    print("\n" + "=" * 60)
    print("TEST: File Operations")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # Test write file
    test_content = """# Test File
def hello():
    print("Hello, World!")
"""
    
    result = kai.write_file('test_output.py', test_content)
    print(f"Write result: {result['message']}")
    assert result['success'] == True
    print("[PASS] Write file test passed")
    
    # Test read file
    result = kai.read_file('test_output.py')
    print(f"Read result: {result['message']}")
    assert result['success'] == True
    assert 'def hello' in result['content']
    print("[PASS] Read file test passed")
    
    # Test edit file
    result = kai.edit_file(
        'test_output.py',
        'print("Hello, World!")',
        'print("Hello, Kai!")'
    )
    print(f"Edit result: {result['message']}")
    assert result['success'] == True
    
    # Verify edit
    result = kai.read_file('test_output.py')
    assert 'Hello, Kai!' in result['content']
    print("[PASS] Edit file test passed")
    
    # Test list files
    result = kai.list_files('.', '*.py')
    print(f"List result: Found {len(result['files'])} Python files")
    assert result['success'] == True
    assert 'test_output.py' in result['files']
    print("[PASS] List files test passed")
    
    # Cleanup
    import os
    try:
        os.remove('test_output.py')
        print("[PASS] Cleanup successful")
    except:
        pass


def test_command_execution():
    """Test command execution capabilities."""
    print("\n" + "=" * 60)
    print("TEST: Command Execution")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # Test simple command
    result = kai.execute_command('echo "Hello from Kai!"')
    print(f"Command output: {result['stdout'].strip()}")
    assert result['success'] == True
    assert 'Hello from Kai!' in result['stdout']
    print("[PASS] Simple command test passed")
    
    # Test Python execution
    python_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"Factorial of 5: {factorial(5)}")
"""
    
    result = kai.execute_python(python_code)
    print(f"Python output: {result['stdout'].strip()}")
    assert result['success'] == True
    assert 'Factorial of 5: 120' in result['stdout']
    print("[PASS] Python execution test passed")
    
    # Test safety check
    result = kai.execute_command('rm -rf /')
    print(f"Safety check result: {result['stderr']}")
    assert result['success'] == False
    assert 'Safety check failed' in result['stderr']
    print("[PASS] Safety check test passed")


def test_project_context():
    """Test project context capabilities."""
    print("\n" + "=" * 60)
    print("TEST: Project Context")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # Test scan project
    structure = kai.scan_project()
    print(f"Project root: {structure['root']}")
    print(f"Total files: {len(structure['files'])}")
    print(f"Total lines: {structure['total_lines']}")
    print(f"Languages: {structure['languages']}")
    
    assert 'root' in structure
    assert 'files' in structure
    print("[PASS] Project scan test passed")
    
    # Test find files
    py_files = kai.find_files('*.py')
    print(f"\nFound {len(py_files)} Python files")
    assert len(py_files) > 0
    print("[PASS] Find files test passed")
    
    # Test file context
    if py_files:
        context = kai.get_file_context(py_files[0])
        print(f"\nFile context for {py_files[0]}:")
        print(f"  Language: {context.get('language')}")
        print(f"  Size: {context.get('size')} bytes")
        assert 'language' in context
        print("[PASS] File context test passed")


def test_tool_registry():
    """Test tool registry capabilities."""
    print("\n" + "=" * 60)
    print("TEST: Tool Registry")
    print("=" * 60)
    
    kai = KaiCapabilities()
    
    # List all tools
    tools = kai.list_tools()
    print(f"Total tools: {len(tools)}")
    
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    assert len(tools) > 0
    print("[PASS] Tool listing test passed")
    
    # List tools by category
    code_tools = kai.list_tools('code')
    file_tools = kai.list_tools('file')
    command_tools = kai.list_tools('command')
    
    print(f"\nCode tools: {len(code_tools)}")
    print(f"File tools: {len(file_tools)}")
    print(f"Command tools: {len(command_tools)}")
    
    assert len(file_tools) > 0
    print("[PASS] Tool category test passed")
    
    # Execute a tool
    result = kai.execute_tool('analyze_code', code='print("test")', language='python')
    print(f"\nTool execution result: {result}")
    assert 'language' in result
    print("[PASS] Tool execution test passed")


def test_capabilities_summary():
    """Test capabilities summary."""
    print("\n" + "=" * 60)
    print("TEST: Capabilities Summary")
    print("=" * 60)
    
    kai = KaiCapabilities()
    summary = kai.get_capabilities_summary()
    
    print("Capabilities Summary:")
    print(f"  Code Analysis: {len(summary['code_analysis']['languages'])} languages")
    print(f"  Code Generation: {len(summary['code_generation']['features'])} features")
    print(f"  File Operations: {len(summary['file_operations']['features'])} features")
    print(f"  Command Execution: {len(summary['command_execution']['features'])} features")
    print(f"  Project Context: {len(summary['project_context']['features'])} features")
    print(f"  Tools: {summary['tools']['total']} registered")
    
    assert 'code_analysis' in summary
    assert 'code_generation' in summary
    assert 'file_operations' in summary
    assert 'command_execution' in summary
    assert 'project_context' in summary
    assert 'tools' in summary
    print("[PASS] Capabilities summary test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("KAI CAPABILITIES TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_code_analysis,
        test_code_generation,
        test_file_operations,
        test_command_execution,
        test_project_context,
        test_tool_registry,
        test_capabilities_summary
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] Test failed: {test.__name__}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARN] {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
