#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path


def main():
    # アプリケーションタイトル
    st.title("🚀 最終統合プロジェクト情報集約ツール")
    
    # サイドバーに説明を追加
    with st.sidebar:
        st.header("使い方")
        st.info("""
        1. 集約したいローカルディレクトリパスまたはWeb URLを入力します。
        2. 出力ファイルパスを指定します（デフォルト: ./ai_summary.md）。
        3. [Start Aggregation] ボタンをクリックして処理を開始します。
        """)
        
        st.header("対応ファイル形式")
        st.success("""
        - テキストファイル (.txt, .md, .py, .js, .html, .css, .json, .xml, .yaml, .yml, .csv, .sql)
        - PDFファイル (.pdf)
        - Excelファイル (.xlsx)
        - Wordファイル (.docx)
        """)
        
        st.warning("""
        注意: .xls と .doc ファイルは未対応です。
        """)
    
    # メインコンテンツ
    st.header("設定")
    
    # 入力フィールド
    col1, col2 = st.columns([3, 1])
    
    with col1:
        input_source = st.text_input(
            "Input Source (Local Path or URL)",
            placeholder="例: /path/to/directory または https://example.com",
            help="集約するルートディレクトリのパスまたは開始URLを入力してください。"
        )
    
    with col2:
        output_file = st.text_input(
            "Output File Path",
            value="./ai_summary.md",
            help="集約された内容を出力するファイルパスを指定してください。"
        )
    
    # 実行ボタン
    st.header("実行")
    
    if st.button("Start Aggregation", type="primary"):
        # 入力検証
        if not input_source:
            st.error("Input Sourceを入力してください。")
            return
        
        if not output_file:
            st.error("Output File Pathを入力してください。")
            return
        
        # 出力ディレクトリの存在確認
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                st.success(f"出力ディレクトリを作成しました: {output_dir}")
            except Exception as e:
                st.error(f"出力ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        # 実行状態の表示
        st.subheader("実行ログ")
        
        # プログレスバーとステータス表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # ログ表示エリア
        log_container = st.container()
        
        try:
            # コマンド構築
            command = [sys.executable, "aggregate_files.py", input_source, output_file]
            
            # 実行開始
            status_text.text("実行中...")
            progress_bar.progress(10)
            
            # サブプロセス実行
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            progress_bar.progress(30)
            
            # リアルタイムログ表示
            log_output = ""
            with log_container:
                log_placeholder = st.empty()
                
                for line in process.stdout:
                    log_output += line
                    log_placeholder.code(log_output, language="text")
            
            # プロセス完了待機
            return_code = process.wait()
            progress_bar.progress(90)
            
            if return_code == 0:
                progress_bar.progress(100)
                status_text.text("完了!")
                st.success(f"集約処理が正常に完了しました。出力ファイル: {output_file}")
                
                # 出力ファイルへのリンク
                if os.path.exists(output_file):
                    st.info("出力ファイルをダウンロード:")
                    with open(output_file, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="Download Output File",
                            data=f.read(),
                            file_name=os.path.basename(output_file),
                            mime="text/markdown"
                        )
            else:
                st.error(f"エラーが発生しました。リターンコード: {return_code}")
                if log_output:
                    st.error("エラーログ:")
                    st.code(log_output, language="text")
        
        except FileNotFoundError:
            st.error("aggregate_files.pyが見つかりません。同じディレクトリに存在することを確認してください。")
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {str(e)}")
    
    # フッター
    st.markdown("---")
    st.markdown("© 2023 最終統合プロジェクト情報集約ツール")


if __name__ == "__main__":
    main()