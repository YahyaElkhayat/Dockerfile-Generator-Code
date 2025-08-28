import os
import glob
import shutil
import re

def analyze_project_files(dest_path):
    """Analyze all file types in the project"""
    file_analysis = {}
    
    # Python files
    py_files = [f for f in glob.glob(os.path.join(dest_path,"**", "*.py"), recursive=True) if "node_modules" not in f ]
    py_requirements = glob.glob(os.path.join(dest_path, "**", "requirements.txt"), recursive=True)
    file_analysis['python'] = {
        'files': [os.path.basename(f) for f in py_files] if py_files else [],
        'has_requirements': bool(py_requirements),
        'count': len(py_files)
    }
    
    # Java files
    java_files = glob.glob(os.path.join(dest_path, "**","*.java"), recursive=True)
    file_analysis['java'] = {
        'files': [os.path.basename(f) for f in java_files] if java_files else [],
        'count': len(java_files)
    }
    
    # JavaScript files
    js_files = [f for f in glob.glob(os.path.join(dest_path, "**","*.js"), recursive=True) if "node_modules" not in f]
    js_config = glob.glob(os.path.join(dest_path, "**", "package.json"), recursive=True)
    file_analysis['javascript'] = {
        'files': [os.path.basename(f) for f in js_files] if js_files else [],
        'has_package_json': bool(js_config),
        'count': len(js_files)
    }
    
    # TypeScript files
    ts_files = [f for f in glob.glob(os.path.join(dest_path, "**", "*.ts"), recursive=True) if "node_modules" not in f]
    ts_config = glob.glob(os.path.join(dest_path, "**", "tsconfig.json"), recursive=True)
    file_analysis['typescript'] = {
        'files': [os.path.basename(f) for f in ts_files] if ts_files else [],
        'has_tsconfig': bool(ts_config),
        'count': len(ts_files)
    }
    
    # C files
    c_files = [f for f in glob.glob(os.path.join(dest_path,"**", "*.c"), recursive=True) if "node_modules" not in f]
    file_analysis['c'] = {
        'files': [os.path.basename(f) for f in c_files] if c_files else [],
        'count': len(c_files)
    }
    
    # C++ files
    cpp_files = [f for f in glob.glob(os.path.join(dest_path,"**" ,"*.cpp"), recursive=True) if "node_modules" not in f]
    file_analysis['cpp'] = {
        'files': [os.path.basename(f) for f in cpp_files] if cpp_files else [],
        'count': len(cpp_files)
    }
    
    # Go files
    go_files = glob.glob(os.path.join(dest_path,"**", "*.go"), recursive=True)
    file_analysis['go'] = {
        'files': [os.path.basename(f) for f in go_files] if go_files else [],
        'count': len(go_files)
    }
    
    # Rust files
    rust_files = glob.glob(os.path.join(dest_path,"**", "*.rs"), recursive=True)
    file_analysis['rust'] = {
        'files': [os.path.basename(f) for f in rust_files] if rust_files else [],
        'count': len(rust_files)
    }
    
    # Build systems
    file_analysis['build_system'] = {
        'has_makefile': os.path.exists(os.path.join(dest_path, "Makefile")),
        'has_package_json': bool(js_config),
        'has_requirements': bool(py_requirements),
        'has_tsconfig': bool(ts_config)
    }
    
    return file_analysis

def determine_project_type(project_name, file_analysis):
    """Determine project type and generate description for LLM"""
    build_system = file_analysis['build_system']
    
    # Priority order for determining primary language
    if file_analysis['python']['count'] > 0:
        files_str = ", ".join(file_analysis['python']['files'])
        if file_analysis['python']['has_requirements']:
            return {
                'type': 'python',
                'description': f"{project_name}: Python project with requirements.txt",
                'files': files_str,
                'has_dependencies': True,
                'dependency_file': 'requirements.txt'
            }
        else:
            return {
                'type': 'python', 
                'description': f"{project_name}: Python project",
                'files': files_str,
                'has_dependencies': False,
                'dependency_file': None
            }
    
    elif file_analysis['javascript']['count'] > 0:
        files_str = ", ".join(file_analysis['javascript']['files'])
        if file_analysis['javascript']['has_package_json']:
            return {
                'type': 'javascript',
                'description': f"{project_name}: JavaScript project with package.json",
                'files': files_str,
                'has_dependencies': True,
                'dependency_file': 'package.json'
            }
        else:
            return {
                'type': 'javascript', 
                'description': f"{project_name}: Javascript project",
                'files': files_str,
                'has_dependencies': False,
                'dependency_file': None
            }
    
    elif file_analysis['typescript']['count'] > 0:
        files_str = ", ".join(file_analysis['typescript']['files'])
        if file_analysis['typescript']['has_tsconfig']:
            return {
                'type': 'typescript',
                'description': f"{project_name}: TypeScript project with tsconfig.json",
                'files': files_str,
                'has_dependencies': file_analysis['javascript']['has_package_json'],
                'dependency_file': 'package.json' if file_analysis['javascript']['has_package_json'] else None
            }
    
    elif file_analysis['java']['count'] > 0:
        files_str = ", ".join(file_analysis['java']['files'])
        return {
            'type': 'java',
            'description': f"{project_name}: Java project",
            'files': files_str,
            'has_dependencies': False,
            'dependency_file': None
        }
    
    elif file_analysis['c']['count'] > 0:
        files_str = ", ".join(file_analysis['c']['files'])
        if build_system['has_makefile']:
            return {
                'type': 'c',
                'description': f"{project_name}: C project with Makefile",
                'files': files_str,
                'has_dependencies': False,
                'build_system': 'Makefile'
            }
        else:
            return {
                'type': 'c',
                'description': f"{project_name}: C project",
                'files': files_str,
                'has_dependencies': False,
                'build_system': None
            }
    
    elif file_analysis['cpp']['count'] > 0:
        files_str = ", ".join(file_analysis['cpp']['files'])
        if build_system['has_makefile']:
            return {
                'type': 'cpp',
                'description': f"{project_name}: C++ project with Makefile",
                'files': files_str,
                'has_dependencies': False,
                'build_system': 'Makefile'
            }
        else:
            return {
                'type': 'cpp',
                'description': f"{project_name}: C++ project",
                'files': files_str,
                'has_dependencies': False,
                'build_system': None
            }
    
    elif file_analysis['go']['count'] > 0:
        files_str = ", ".join(file_analysis['go']['files'])
        if build_system['has_makefile']:
            return {
                'type': 'go',
                'description': f"{project_name}: Go project with Makefile",
                'files': files_str,
                'has_dependencies': False,
                'build_system': 'Makefile'
            }
        else:
            return {
                'type': 'go',
                'description': f"{project_name}: Go project",
                'files': files_str,
                'has_dependencies': False,
                'build_system': None
            }
    
    elif file_analysis['rust']['count'] > 0:
        files_str = ", ".join(file_analysis['rust']['files'])
        return {
            'type': 'rust',
            'description': f"{project_name}: Rust project",
            'files': files_str,
            'has_dependencies': False,
            'dependency_file': None
        }
    
    else:
        return {
            'type': 'unknown',
            'description': f"{project_name}: Unknown project type",
            'files': '',
            'has_dependencies': False,
            'dependency_file': None
        }

def parse_makefile_target(dest_path):
    """Parse Makefile to find the main target - COMPREHENSIVE"""
    makefile_path = os.path.join(dest_path, "Makefile")
    
    try:
        with open(makefile_path, 'r') as f:
            content = f.read()
            
        # Method 1: Look for TARGET variable (like your example)
        target_match = re.search(r'^TARGET\s*=\s*(\w+)', content, re.MULTILINE)
        if target_match:
            return target_match.group(1)
        
        # Method 2: Look for variables that might be executables
        exe_patterns = [
            r'^PROGRAM\s*=\s*(\w+)',
            r'^EXECUTABLE\s*=\s*(\w+)',
            r'^BINARY\s*=\s*(\w+)',
            r'^OUTPUT\s*=\s*(\w+)',
        ]
        for pattern in exe_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1)
        
        # Method 3: Look for -o flag in compilation commands
        output_match = re.search(r'-o\s+(\$\((\w+)\)|\w+)', content)
        if output_match:
            if output_match.group(2):  # Variable like $(TARGET)
                # Find what this variable equals
                var_name = output_match.group(2)
                var_match = re.search(rf'^{var_name}\s*=\s*(\w+)', content, re.MULTILINE)
                if var_match:
                    return var_match.group(1)
            else:  # Direct name
                return output_match.group(1)
        
        # Method 4: Look for first meaningful target (original logic)
        lines = content.split('\n')
        skip_targets = {'clean', 'install', 'all', 'run', 'help', 'test', 'distclean', 'check'}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line and not line.startswith('\t'):
                target = line.split(':')[0].strip()
                
                # Skip special targets and variables
                if target.startswith('.') or target in skip_targets:
                    continue
                
                # Skip if it looks like a variable assignment
                if '=' in target:
                    continue
                
                # This is probably our main executable target
                return target
                
    except Exception:
        pass
    
    return None

def determine_project_is_interactive(dest_path):
    """Determine if the project is interactive based on code inside each file"""
    
    # Interactive patterns for each language
    interactive_patterns = {
        'python': [
            r'input\s*\(',
            r'raw_input\s*\(',
            r'sys\.stdin\.read',
            r'getpass\.getpass',
            r'click\.prompt',
        ],
        'javascript': [
            r'readline\.',
            r'process\.stdin',
            r'prompt\s*\(',
            r'confirm\s*\(',
            r'inquirer\.',
            r'\.question\s*\(',
        ],
        'typescript': [
            r'readline\.',
            r'process\.stdin',
            r'prompt\s*\(',
            r'confirm\s*\(',
            r'inquirer\.',
            r'\.question\s*\(',
        ],
        'c': [
            r'scanf\s*\(',
            r'getchar\s*\(',
            r'gets\s*\(',
            r'fgets\s*\(',
            r'getc\s*\(',
        ],
        'cpp': [
            r'cin\s*>>',
            r'getline\s*\(',
            r'scanf\s*\(',
            r'getchar\s*\(',
            r'std::cin',
            r'gets\s*\(',
        ],
        'java': [
            r'Scanner\s*\(',
            r'\.nextLine\s*\(',
            r'\.next\s*\(',
            r'\.nextInt\s*\(',
            r'System\.in',
            r'BufferedReader',
            r'Console\.readLine',
        ],
        'go': [
            r'fmt\.Scan',
            r'bufio\.NewReader',
            r'os\.Stdin',
            r'fmt\.Scanf',
            r'reader\.ReadString',
        ],
        'rust': [
            r'stdin\s*\(',
            r'read_line\s*\(',
            r'io::stdin',
            r'stdin\.read_line',
        ]
    }
    
    # File extensions mapping
    file_extensions = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust'
    }
    
    # Search through all source files
    for root, dirs, files in os.walk(dest_path):
        # Skip node_modules and other irrelevant directories
        if 'node_modules' in root or '.git' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Skip if not a source file we care about
            if file_ext not in file_extensions:
                continue
                
            language = file_extensions[file_ext]
            patterns = interactive_patterns.get(language, [])
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for interactive patterns
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            return {
                                'is_interactive': True,
                                'reason': f'Found interactive pattern "{pattern}" in {file}',
                                'file': file,
                                'language': language
                            }
                            
            except Exception as e:
                # Skip files that can't be read
                continue
    
    return {
        'is_interactive': False,
        'reason': 'No interactive patterns found',
        'file': None,
        'language': None
    }

def main():
    inputs_dir = "Inputs"
    traitement_dir = "Outputs"
    
    # Create traitement directory
    if not os.path.exists(traitement_dir):
        os.makedirs(traitement_dir)
    
    # List all project directories
    projects = os.listdir(inputs_dir)
    
    all_project_analyses = []
    
    for project in projects:
        project_path = os.path.join(inputs_dir, project)
        
        # Skip if not a directory
        if not os.path.isdir(project_path):
            continue
            
        # Copy project to traitement
        dest_path = os.path.join(traitement_dir, project)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        shutil.copytree(project_path, dest_path)
        
        # Analyze project files
        file_analysis = analyze_project_files(dest_path)
        
        # Determine project type and generate LLM context
        project_info = determine_project_type(project, file_analysis)
        
        # Check if project is interactive
        interactive_info = determine_project_is_interactive(dest_path)
        project_info['is_interactive'] = interactive_info['is_interactive']
        project_info['interactive_reason'] = interactive_info['reason']
        
        # Determine executable name for Makefile projects
        if project_info.get('build_system') == 'Makefile':
            makefile_target = parse_makefile_target(dest_path)
            if makefile_target:
                project_info['executable_name'] = makefile_target
            else:
                # Fallback: use first source file without extension
                first_file = project_info['files'].split(', ')[0] if project_info['files'] else ''
                project_info['executable_name'] = os.path.splitext(first_file)[0] if first_file else 'a.out'
        else:
            # For non-Makefile projects, determine executable based on language
            files_list = [f.strip() for f in project_info['files'].split(', ')] if project_info['files'] else []
            
            if project_info['type'] == 'typescript':
                # Filter out .d.ts files (type definitions), prefer main TypeScript files
                ts_files = [f for f in files_list if f.endswith('.ts') and not f.endswith('.d.ts')]
                if ts_files:
                    # Look for index.ts, main.ts, or app.ts first
                    for priority_file in ['index.ts', 'main.ts', 'app.ts']:
                        if priority_file in ts_files:
                            project_info['executable_name'] = priority_file
                            break
                    else:
                        # Use first non-.d.ts TypeScript file
                        project_info['executable_name'] = ts_files[0]
                else:
                    project_info['executable_name'] = files_list[0] if files_list else 'index.ts'
            
            elif project_info['type'] == 'java':
                # For Java, use class name WITH extension
                if files_list:
                    # Look for Main, App, or similar
                    for file in files_list:
                        if 'main' in file.lower() or 'app' in file.lower():
                            project_info['executable_name'] = file  # keep .java
                            break
                    else:
                        # Use first Java file WITH extension
                        project_info['executable_name'] = files_list[0]
                else:
                    project_info['executable_name'] = 'Main.java'

            
            elif project_info['type'] == 'go':
                # Go executable is typically the directory name or 'main'
                project_info['executable_name'] = 'main'
            
            elif project_info['type'] == 'python':
                # Python runs the .py file directly
                project_info['executable_name'] = files_list[0] if files_list else 'main.py'
            
            elif project_info['type'] in ['javascript', 'typescript']:
                # Node.js runs the .js/.ts file directly
                project_info['executable_name'] = files_list[0] if files_list else 'index.js'
            
            else:
                # Default fallback
                project_info['executable_name'] = files_list[0] if files_list else 'main'
        
        # Print for immediate feedback
        interactive_status = ".The project is interactive)" if project_info['is_interactive'] else ".The project is not interactive"
        executable_info = f" .The file to be executed during the CMD is: {project_info['executable_name']}"
        print(project_info['description'] + ', The name of the file(s) is(are) ' + project_info['files'] + interactive_status + executable_info)
        
        # Store for LLM usage
        all_project_analyses.append(project_info)
    
    return all_project_analyses

if __name__ == "__main__":
    analyses = main() # pyright: ignore[reportShadowedImports]