#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Set, Optional

import requests
from bs4 import BeautifulSoup
import pdfplumber
import openpyxl
import docx


class FileAggregator:
    def __init__(self, input_source: str, output_file: str):
        self.input_source = input_source
        self.output_file = output_file
        self.visited_urls: Set[str] = set()
        self.base_domain = None
        self.base_path = None
        
        # スキップするファイル/ディレクトリのリスト
        self.skip_patterns = [
            r'bin$', r'obj$', r'\.git$', r'\.vs$', r'__pycache__$', 
            r'node_modules$', r'\.exe$', r'\.dll$', r'\.pdb$', 
            r'\.zip$', r'\.tar\.gz$', r'\.log$', r'\.jpg$', 
            r'\.jpeg$', r'\.png$', r'\.ico$', r'\.css$', r'\.js$'
        ]
        
        # 未対応のファイル形式
        self.unsupported_formats = {'.xls', '.doc'}
    
    def is_web_url(self, source: str) -> bool:
        """入力ソースがWeb URLかどうかを判定"""
        return source.startswith(('http://', 'https://'))
    
    def should_skip_file(self, file_path: str) -> bool:
        """ファイルをスキップすべきか判定"""
        for pattern in self.skip_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False
    
    def is_unsupported_format(self, file_path: str) -> bool:
        """未対応のファイル形式か判定"""
        ext = Path(file_path).suffix.lower()
        return ext in self.unsupported_formats
    
    def extract_pdf_text(self, file_path: str) -> str:
        """PDFファイルからテキストを抽出"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            return f"[ERROR: Failed to extract PDF content: {str(e)}]"
    
    def extract_xlsx_text(self, file_path: str) -> str:
        """Excelファイルからテキストを抽出"""
        try:
            workbook = openpyxl.load_workbook(file_path)
            text = ""
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                text += f"Sheet: {sheet_name}\n"
                for row in sheet.iter_rows(values_only=True):
                    row_text = "\t".join([str(cell) if cell is not None else "" for cell in row])
                    if row_text.strip():
                        text += row_text + "\n"
                text += "\n"
            return text
        except Exception as e:
            return f"[ERROR: Failed to extract Excel content: {str(e)}]"
    
    def extract_docx_text(self, file_path: str) -> str:
        """Wordファイルからテキストを抽出"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"[ERROR: Failed to extract Word content: {str(e)}]"
    
    def process_local_file(self, file_path: str, relative_path: str) -> str:
        """ローカルファイルを処理"""
        if self.should_skip_file(relative_path):
            return ""
        
        if self.is_unsupported_format(relative_path):
            return f"# File: {relative_path}\n```text\n[WARNING: The file format ({Path(relative_path).suffix}) is not supported. Content was skipped.]\n```\n\n"
        
        ext = Path(relative_path).suffix.lower()
        
        try:
            if ext == '.pdf':
                content = self.extract_pdf_text(file_path)
                return f"# File: {relative_path}\n```text\n{content}\n```\n\n"
            elif ext == '.xlsx':
                content = self.extract_xlsx_text(file_path)
                return f"# File: {relative_path}\n```text\n{content}\n```\n\n"
            elif ext == '.docx':
                content = self.extract_docx_text(file_path)
                return f"# File: {relative_path}\n```text\n{content}\n```\n\n"
            elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.csv', '.sql']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"# File: {relative_path}\n```{ext[1:] if ext else 'text'}\n{content}\n```\n\n"
            else:
                # テキストファイルとして読み込みを試みる
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"# File: {relative_path}\n```text\n{content}\n```\n\n"
        except Exception as e:
            return f"# File: {relative_path}\n```text\n[ERROR: Failed to read file: {str(e)}]\n```\n\n"
    
    def process_local_directory(self, root_path: str) -> str:
        """ローカルディレクトリを再帰的に処理"""
        result = ""
        root_path = Path(root_path).resolve()
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(root_path)
                result += self.process_local_file(str(file_path), str(relative_path))
        
        return result
    
    def is_same_domain(self, url: str) -> bool:
        """URLが同じドメインか判定"""
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain
    
    def is_under_base_path(self, url: str) -> bool:
        """URLがベースパス配下か判定"""
        parsed = urlparse(url)
        return parsed.path.startswith(self.base_path)
    
    def download_binary_file(self, url: str, session: requests.Session) -> Optional[str]:
        """バイナリファイルをダウンロードしてテキストを抽出"""
        try:
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            # 一時ファイルに保存
            temp_file = f"temp_{os.path.basename(url)}"
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # ファイル拡張子に基づいてテキスト抽出
            ext = Path(url).suffix.lower()
            if ext == '.pdf':
                content = self.extract_pdf_text(temp_file)
            elif ext == '.xlsx':
                content = self.extract_xlsx_text(temp_file)
            elif ext == '.docx':
                content = self.extract_docx_text(temp_file)
            else:
                content = f"[WARNING: Binary file format ({ext}) is not supported for content extraction.]"
            
            # 一時ファイルを削除
            os.remove(temp_file)
            
            return content
        except Exception as e:
            return f"[ERROR: Failed to download or process {url}: {str(e)}]"
    
    def crawl_web_page(self, url: str, session: requests.Session) -> str:
        """Webページをクロールしてコンテンツを抽出"""
        if url in self.visited_urls:
            return ""
        
        self.visited_urls.add(url)
        
        try:
            response = session.get(url)
            response.raise_for_status()
            
            # コンテンツタイプを確認
            content_type = response.headers.get('content-type', '').lower()
            
            # バイナリファイルの場合
            if any(ext in url.lower() for ext in ['.pdf', '.xlsx', '.docx']):
                content = self.download_binary_file(url, session)
                return f"# URL: {url}\n```text\n{content}\n```\n\n"
            
            # HTMLページの場合
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # スクリプトとスタイルを除去
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # テキストコンテンツを抽出
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                result = f"# URL: {url}\n```text\n{text}\n```\n\n"
                
                # 同じドメイン内のリンクを探索
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    
                    if self.is_same_domain(absolute_url) and self.is_under_base_path(absolute_url):
                        if absolute_url not in self.visited_urls:
                            time.sleep(1)  # サーバー負荷軽減のための遅延
                            result += self.crawl_web_page(absolute_url, session)
                
                return result
            else:
                # その他のコンテンツタイプ
                return f"# URL: {url}\n```text\n[WARNING: Content type '{content_type}' is not supported for text extraction.]\n```\n\n"
                
        except Exception as e:
            return f"# URL: {url}\n```text\n[ERROR: Failed to crawl {url}: {str(e)}]\n```\n\n"
    
    def process_web_source(self, start_url: str) -> str:
        """Webソースを処理"""
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc
        self.base_path = '/'.join(parsed.path.split('/')[:-1]) if '/' in parsed.path else '/'
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return self.crawl_web_page(start_url, session)
    
    def aggregate(self):
        """メインの集約処理"""
        print(f"開始: {self.input_source}")
        
        if self.is_web_url(self.input_source):
            content = self.process_web_source(self.input_source)
        else:
            content = self.process_local_directory(self.input_source)
        
        # 出力ファイルに書き込み
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"完了: {self.output_file}")


def main():
    parser = argparse.ArgumentParser(description='ファイル情報集約ツール')
    parser.add_argument('input_source', help='集約するルートディレクトリまたは開始URL')
    parser.add_argument('output_file', help='出力ファイルのパス')
    
    args = parser.parse_args()
    
    aggregator = FileAggregator(args.input_source, args.output_file)
    aggregator.aggregate()


if __name__ == "__main__":
    main()