#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import pdfplumber
from pathlib import Path

def should_skip_directory(dir_name):
    """Check if a directory should be skipped based on the exclusion list."""
    skip_dirs = {'bin', 'obj', '.git', '.vs', '__pycache__', 'node_modules'}
    return dir_name in skip_dirs

def should_skip_file(file_name):
    """Check if a file should be skipped based on the extension exclusion list."""
    skip_extensions = {'.exe', '.dll', '.pdb', '.zip', '.tar.gz', '.log', '.jpg', '.jpeg', '.png', '.ico', '.md'}
    file_ext = os.path.splitext(file_name)[1].lower()
    return file_ext in skip_extensions

def extract_pdf_text(file_path):
    """Extract text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            return '\n'.join(text_content)
    except Exception as e:
        print(f"Warning: Could not extract text from PDF file {file_path}: {str(e)}")
        return None

def get_file_content(file_path):
    """Get the content of a file, handling different file types."""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_pdf_text(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Warning: Could not read file {file_path}: {str(e)}")
                return None
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {str(e)}")
            return None

def get_language_from_extension(file_ext):
    """Get the language identifier for Markdown code blocks based on file extension."""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.cmd': 'batch',
        '.sql': 'sql',
        '.md': 'markdown',
        '.tex': 'latex',
        '.r': 'r',
        '.m': 'matlab',
        '.pl': 'perl',
        '.lua': 'lua',
        '.dart': 'dart',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.pdf': 'text',
    }
    return language_map.get(file_ext, '')

def process_directory(target_dir, output_file):
    """Process the target directory and generate the aggregated output file."""
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists():
        print(f"Error: Target directory '{target_dir}' does not exist.")
        return False
    
    if not target_path.is_dir():
        print(f"Error: '{target_dir}' is not a directory.")
        return False
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write("# Project File Aggregation\n\n")
        out_file.write(f"Source Directory: {target_path}\n\n")
        out_file.write("---\n\n")
        
        for root, dirs, files in os.walk(target_path):
            # Remove directories that should be skipped
            dirs[:] = [d for d in dirs if not should_skip_directory(d)]
            
            for file_name in files:
                if should_skip_file(file_name):
                    continue
                
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, target_path)
                
                # Skip the output file itself to avoid recursive inclusion
                if os.path.abspath(file_path) == os.path.abspath(output_file):
                    continue
                
                # Get file content
                content = get_file_content(file_path)
                if content is None:
                    continue
                
                # Write file header
                out_file.write(f"# File: {relative_path}\n")
                
                # Determine language for code block
                file_ext = os.path.splitext(file_name)[1].lower()
                language = get_language_from_extension(file_ext)
                
                # Write content in code block
                out_file.write(f"```{language}\n")
                out_file.write(content)
                out_file.write("\n```\n\n")
    
    print(f"Successfully aggregated files to '{output_file}'")
    return True

def main():
    """Main function to parse arguments and execute the aggregation."""
    parser = argparse.ArgumentParser(
        description='Aggregate source code, configuration files, and PDF documents into a single Markdown file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python aggregate_files.py ./my-project ./ai_summary.txt
  python aggregate_files.py /path/to/project /path/to/output.md
        '''
    )
    
    parser.add_argument('target_dir', 
                        help='Root directory to aggregate files from')
    parser.add_argument('output_file', 
                        help='Output text file path for the aggregated content')
    
    args = parser.parse_args()
    
    success = process_directory(args.target_dir, args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()