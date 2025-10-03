# -*- coding: utf-8 -*-
"""
DB → JSON 자동 저장 플러그인 GUI 버전
ArtistSul CMS 데이터베이스 연동 GUI 애플리케이션
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import time
from datetime import datetime
import os
import json
import sys
import socket

from config import *
from db_client import DBClient
from data_handler import DataHandler
from logger import get_logger

class SingleInstance:
    """프로그램 중복 실행 방지 클래스"""
    
    def __init__(self, port=12345):
        self.port = port
        self.socket = None
        
    def is_running(self):
        """다른 인스턴스가 실행 중인지 확인"""
        try:
            # 소켓을 사용해서 포트를 바인딩 시도
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('localhost', self.port))
            self.socket.listen(1)
            return False  # 바인딩 성공 = 다른 인스턴스 없음
        except socket.error:
            return True  # 바인딩 실패 = 다른 인스턴스 실행 중
    
    def cleanup(self):
        """소켓 정리"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

class DBToJSONGUI:
    """DB → JSON 플러그인 GUI 클래스"""
    
    def __init__(self):
        # 중복 실행 방지
        self.single_instance = SingleInstance()
        if self.single_instance.is_running():
            messagebox.showerror("오류", "프로그램이 이미 실행 중입니다!\n\n다른 창을 확인해주세요.")
            sys.exit(1)
        
        self.root = tk.Tk()
        self.root.title("LoadDB(directorkim@scenes.kr)")
        self.root.geometry("400x600")
        self.root.resizable(True, True)
        
        # 상태 변수
        self.is_running = False
        self.db_client = None
        self.data_handler = None
        self.stats = {
            "start_time": None,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_messages_saved": 0
        }
        
        # GUI 구성 요소 생성
        self.create_widgets()
        self.load_config()
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 자동 시작 체크 (GUI 로드 후 약간의 지연을 두고 실행)
        self.root.after(1000, self.check_auto_start)
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        
        # 설정 프레임
        self.create_config_frame(main_frame)
        
        # 제어 버튼 프레임
        self.create_control_frame(main_frame)
        
        # 상태 프레임
        self.create_status_frame(main_frame)
        
        # 로그 프레임
        self.create_log_frame(main_frame)
    
    def create_config_frame(self, parent):
        """설정 프레임 생성"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ 설정", padding="10")
        config_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # API URL (하드코딩, GUI에서 숨김)
        self.api_url_var = tk.StringVar(value=BASE_URL)
        
        # JWT 토큰 (하드코딩, GUI에서 숨김)
        self.jwt_token_var = tk.StringVar(value=JWT_TOKEN)
        
        # 실행 간격 (숨김 처리)
        ttk.Label(config_frame, text="실행 간격(초):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.interval_var = tk.StringVar(value=str(max(INTERVAL_SECONDS, 5)))  # 최소 5초 보장
        self.interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=10, state='readonly', show="*")
        self.interval_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 조회 개수 (숨김 처리)
        ttk.Label(config_frame, text="최신 메시지 개수:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.fetch_limit_var = tk.StringVar(value=str(FETCH_LIMIT))
        self.fetch_entry = ttk.Entry(config_frame, textvariable=self.fetch_limit_var, width=10, state='readonly', show="*")
        self.fetch_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 설명 라벨 추가
        desc_label = ttk.Label(config_frame, text="(등록시간 기준 최신순으로 정렬)", font=("TkDefaultFont", 8))
        desc_label.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # 설정값 숨김 안내 (작은 글씨)
        hidden_label = ttk.Label(config_frame, text="(설정값은 보안상 숨김 처리됨)", font=("TkDefaultFont", 7), foreground="gray")
        hidden_label.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=(2, 0))
        
        # 출력 폴더 (읽기 전용)
        ttk.Label(config_frame, text="출력 폴더:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_dir_var = tk.StringVar(value=OUTPUT_DIR)
        output_frame = ttk.Frame(config_frame)
        output_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, state='readonly', show="*")
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 설정 변경 버튼 (암호 보호)
        ttk.Button(output_frame, text="⚙️ 설정", command=self.open_settings_dialog).grid(row=0, column=1)
    
    def create_control_frame(self, parent):
        """제어 버튼 프레임 생성"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 버튼들
        self.start_button = ttk.Button(control_frame, text="🚀 시작", command=self.start_plugin)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ 중지", command=self.stop_plugin, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        
        # 자동 시작 토글 버튼
        self.auto_start_var = tk.BooleanVar(value=True)  # 기본값: True
        self.auto_start_check = ttk.Checkbutton(
            control_frame, 
            text="🔄 자동 시작", 
            variable=self.auto_start_var,
            command=self.toggle_auto_start
        )
        self.auto_start_check.pack(side=tk.LEFT)
    
    def create_status_frame(self, parent):
        """상태 프레임 생성"""
        status_frame = ttk.LabelFrame(parent, text="📊 상태", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(3, weight=1)
        
        # 상태 표시
        ttk.Label(status_frame, text="상태:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.status_var = tk.StringVar(value="대기 중")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(status_frame, text="마지막 실행:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.last_run_var = tk.StringVar(value="없음")
        ttk.Label(status_frame, textvariable=self.last_run_var).grid(row=0, column=3, sticky=tk.W)
        
        # 통계
        ttk.Label(status_frame, text="총 실행:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.total_runs_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.total_runs_var).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(5, 0))
        
        ttk.Label(status_frame, text="성공:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.success_runs_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.success_runs_var).grid(row=1, column=3, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(status_frame, text="저장된 메시지:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.messages_saved_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.messages_saved_var).grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=(5, 0))
    
    def create_log_frame(self, parent):
        """로그 프레임 생성"""
        log_frame = ttk.LabelFrame(parent, text="📝 로그", padding="10")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 로그 텍스트 위젯
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=40)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 제어 버튼
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(log_control_frame, text="🗑️ 로그 지우기", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_control_frame, text="💾 로그 저장", command=self.save_log).pack(side=tk.LEFT)
    
    def log_message(self, message, level="INFO"):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level} {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 로그 레벨에 따른 색상 설정
        if level == "ERROR":
            self.log_text.tag_add("error", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("error", foreground="red")
        elif level == "SUCCESS":
            self.log_text.tag_add("success", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("success", foreground="green")
        elif level == "WARNING":
            self.log_text.tag_add("warning", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("warning", foreground="orange")
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """로그 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message("로그가 저장되었습니다.", "SUCCESS")
            except Exception as e:
                self.log_message(f"로그 저장 실패: {e}", "ERROR")
    
    def open_hidden_settings(self, event=None):
        """숨겨진 설정 접근 (키보드 단축키)"""
        # 암호 입력 다이얼로그
        password = tk.simpledialog.askstring(
            "보안 설정", 
            "설정을 변경하려면 암호를 입력하세요:",
            show='*'
        )
        
        if password == "04300430":
            self.log_message("🔐 암호 인증 성공. 설정 변경 모드를 활성화합니다.", "SUCCESS")
            self.show_settings_dialog()
        elif password is None:
            self.log_message("⚙️ 설정 변경이 취소되었습니다.", "INFO")
        else:
            self.log_message("❌ 잘못된 암호입니다. 설정 변경이 거부되었습니다.", "ERROR")
            messagebox.showerror("인증 실패", "잘못된 암호입니다!\n\n설정을 변경할 수 없습니다.")
    
    def open_settings_dialog(self):
        """설정 변경 다이얼로그 열기 (암호 보호)"""
        # 암호 입력 다이얼로그
        password = tk.simpledialog.askstring(
            "보안 설정", 
            "설정을 변경하려면 암호를 입력하세요:",
            show='*'
        )
        
        if password == "04300430":
            self.log_message("🔐 암호 인증 성공. 설정 변경 모드를 활성화합니다.", "SUCCESS")
            self.show_settings_dialog()
        elif password is None:
            self.log_message("⚙️ 설정 변경이 취소되었습니다.", "INFO")
        else:
            self.log_message("❌ 잘못된 암호입니다. 설정 변경이 거부되었습니다.", "ERROR")
            messagebox.showerror("인증 실패", "잘못된 암호입니다!\n\n설정을 변경할 수 없습니다.")
    
    def show_settings_dialog(self):
        """설정 변경 다이얼로그 표시"""
        dialog = tk.Toplevel(self.root)
        dialog.title("설정 변경 - LoadDB(directorkim@scenes.kr)")
        dialog.geometry("450x500")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 다이얼로그 중앙 배치
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"450x500+{x}+{y}")
        
        # 메인 프레임
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 설정 변경 폼
        ttk.Label(main_frame, text="⚙️ 설정 변경", font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 30))
        
        # 설명 라벨
        desc_label = ttk.Label(main_frame, text="설정을 변경하면 자동으로 저장됩니다.", 
                              font=("TkDefaultFont", 9), foreground="gray")
        desc_label.pack(pady=(0, 20))
        
        # 실행 간격
        ttk.Label(main_frame, text="실행 간격(초):", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        interval_var = tk.StringVar(value=self.interval_var.get())
        interval_entry = ttk.Entry(main_frame, textvariable=interval_var, width=25, font=("TkDefaultFont", 10))
        interval_entry.pack(fill=tk.X, pady=(0, 20))
        
        # 조회 개수
        ttk.Label(main_frame, text="최신 메시지 개수:", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        fetch_limit_var = tk.StringVar(value=self.fetch_limit_var.get())
        fetch_entry = ttk.Entry(main_frame, textvariable=fetch_limit_var, width=25, font=("TkDefaultFont", 10))
        fetch_entry.pack(fill=tk.X, pady=(0, 20))
        
        # 출력 폴더
        ttk.Label(main_frame, text="출력 폴더:", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 30))
        
        output_dir_var = tk.StringVar(value=self.output_dir_var.get())
        output_entry = ttk.Entry(output_frame, textvariable=output_dir_var, font=("TkDefaultFont", 10))
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_dir():
            directory = filedialog.askdirectory()
            if directory:
                output_dir_var.set(directory)
                # 자동 저장
                auto_save_settings()
        
        ttk.Button(output_frame, text="📁 찾아보기", command=browse_dir).pack(side=tk.RIGHT)
        
        # 자동 저장 함수
        def auto_save_settings():
            try:
                # 입력 검증
                interval = int(interval_var.get())
                if interval < 5:
                    self.log_message("⚠️ 실행 간격은 최소 5초입니다. 5초로 설정됩니다.", "WARNING")
                    interval_var.set("5")
                    interval = 5
                
                fetch_limit = int(fetch_limit_var.get())
                if fetch_limit < 1:
                    self.log_message("⚠️ 메시지 개수는 1개 이상이어야 합니다. 1개로 설정됩니다.", "WARNING")
                    fetch_limit_var.set("1")
                    fetch_limit = 1
                
                # 설정 업데이트
                self.interval_var.set(str(interval))
                self.fetch_limit_var.set(str(fetch_limit))
                self.output_dir_var.set(output_dir_var.get())
                
                # 설정 저장
                self.save_config()
                
                self.log_message("💾 설정이 자동으로 저장되었습니다.", "SUCCESS")
                
            except ValueError:
                self.log_message("⚠️ 숫자만 입력해주세요.", "WARNING")
        
        # 입력 변경 시 자동 저장 바인딩
        interval_var.trace('w', lambda *args: auto_save_settings())
        fetch_limit_var.trace('w', lambda *args: auto_save_settings())
        
        # 상태 표시 라벨
        status_label = ttk.Label(main_frame, text="✅ 설정이 자동으로 저장됩니다", 
                                font=("TkDefaultFont", 9), foreground="green")
        status_label.pack(pady=(20, 10))
        
        # 버튼 프레임 (더 크게)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # 닫기 버튼 (중앙 배치)
        close_button = ttk.Button(button_frame, text="❌ 창 닫기", command=dialog.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # 새로고침 버튼
        def refresh_settings():
            interval_var.set(self.interval_var.get())
            fetch_limit_var.set(self.fetch_limit_var.get())
            output_dir_var.set(self.output_dir_var.get())
            self.log_message("🔄 설정이 새로고침되었습니다.", "INFO")
        
        refresh_button = ttk.Button(button_frame, text="🔄 새로고침", command=refresh_settings)
        refresh_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def browse_output_dir(self):
        """출력 폴더 선택 (더 이상 사용되지 않음)"""
        pass
    
    def validate_interval(self, event=None):
        """실행 간격 검증 (최소 5초 강제)"""
        try:
            interval = int(self.interval_var.get())
            if interval < 5:
                self.log_message(f"⚠️ 실행 간격은 최소 5초입니다. {interval}초 → 5초로 변경됩니다.", "WARNING")
                self.interval_var.set("5")
                messagebox.showwarning("입력 오류", "실행 간격은 최소 5초입니다!\n\n5초로 설정되었습니다.")
        except ValueError:
            self.log_message("⚠️ 실행 간격은 숫자여야 합니다. 5초로 설정됩니다.", "WARNING")
            self.interval_var.set("5")
            messagebox.showwarning("입력 오류", "실행 간격은 숫자여야 합니다!\n\n5초로 설정되었습니다.")
    
    def toggle_auto_start(self):
        """자동 시작 토글"""
        auto_start = self.auto_start_var.get()
        if auto_start:
            self.log_message("🔄 자동 시작이 활성화되었습니다.", "INFO")
        else:
            self.log_message("⏸️ 자동 시작이 비활성화되었습니다.", "INFO")
    
    def check_auto_start(self):
        """자동 시작 체크"""
        try:
            from config import AUTO_START
            
            # config.py의 AUTO_START 설정과 GUI 체크박스 동기화
            self.auto_start_var.set(AUTO_START)
            
            if AUTO_START and not self.is_running:
                self.log_message("🔄 자동 시작이 활성화되어 있습니다. 데이터 수집을 시작합니다...", "INFO")
                self.start_plugin()
            else:
                self.log_message("⏸️ 자동 시작이 비활성화되어 있습니다.", "INFO")
                
        except ImportError:
            self.log_message("⚠️ config.py에서 AUTO_START 설정을 찾을 수 없습니다.", "WARNING")
        except Exception as e:
            self.log_message(f"❌ 자동 시작 체크 오류: {e}", "ERROR")
    
    def load_config(self):
        """설정 로드"""
        try:
            from config import INTERVAL_SECONDS, FETCH_LIMIT, OUTPUT_DIR, AUTO_START
            
            # GUI 변수에 config.py 값 설정 (최소 5초 보장)
            self.interval_var.set(max(INTERVAL_SECONDS, 5))
            self.fetch_limit_var.set(FETCH_LIMIT)
            self.output_dir_var.set(OUTPUT_DIR)
            self.auto_start_var.set(AUTO_START)
            
            self.log_message("설정을 로드했습니다.", "SUCCESS")
        except Exception as e:
            self.log_message(f"설정 로드 실패: {e}", "ERROR")
    
    def save_config(self):
        """설정 자동 저장 (프로그램 종료 시 호출)"""
        try:
            # config.py 파일 업데이트
            config_content = f'''# -*- coding: utf-8 -*-
"""
DB → JSON 자동 저장 플러그인 설정 파일
ArtistSul CMS 데이터베이스 연동 설정
"""

# API 설정 (하드코딩)
BASE_URL = "https://artistsul-cms-worker.directorkim.workers.dev"
JWT_TOKEN = "None"

# 출력 설정
OUTPUT_DIR = "{self.output_dir_var.get()}"
JSON_FILENAME_PREFIX = "messages"
JSON_FILENAME = "messages.json"  # 고정 파일명 (갱신 방식)
USE_FIXED_FILENAME = True  # True: 고정 파일명, False: 타임스탬프 포함

# 실행 설정
INTERVAL_SECONDS = {max(int(self.interval_var.get()), 5)}  # 최소 5초 강제
FETCH_LIMIT = {self.fetch_limit_var.get()}
AUTO_START = {self.auto_start_var.get()}  # 프로그램 실행 시 자동으로 데이터 수집 시작

# 로그 설정
LOG_TO_CONSOLE = True
LOG_TO_FILE = True
LOG_FILE_PATH = "./logs/app.log"

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 5

# 데이터베이스 쿼리 설정
DEFAULT_START_DATE = "2025-01-01"
DEFAULT_END_DATE = None

# API 엔드포인트
API_ENDPOINTS = {{
    "messages": "/api/messages",
    "login": "/api/admin/login",
    "export": "/api/messages/export"
}}

# 요청 헤더
DEFAULT_HEADERS = {{
    "Content-Type": "application/json",
    "User-Agent": "DBToJSON-Plugin/1.0"
}}
'''
            
            with open("config.py", 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.log_message("설정이 저장되었습니다.", "SUCCESS")
            messagebox.showinfo("성공", "설정이 저장되었습니다!")
            
        except Exception as e:
            self.log_message(f"설정 저장 실패: {e}", "ERROR")
            messagebox.showerror("오류", f"설정 저장 실패: {e}")
    
    def start_plugin(self):
        """플러그인 시작"""
        if self.is_running:
            return
        
        try:
            # 상태 업데이트
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("실행 중...")
            
            # 통계 초기화
            self.stats["start_time"] = datetime.now()
            self.stats["total_runs"] = 0
            self.stats["successful_runs"] = 0
            self.stats["failed_runs"] = 0
            self.stats["total_messages_saved"] = 0
            
            self.log_message("플러그인이 시작되었습니다.", "SUCCESS")
            
            # 메인 실행 루프 시작
            self.run_main_loop()
            
        except Exception as e:
            self.log_message(f"시작 오류: {e}", "ERROR")
            self.stop_plugin()
    
    def stop_plugin(self):
        """플러그인 중지"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("중지됨")
        self.log_message("플러그인이 중지되었습니다.", "WARNING")
    
    def run_main_loop(self):
        """메인 실행 루프"""
        def main_loop_thread():
            try:
                # DB 클라이언트 및 데이터 핸들러 초기화
                self.db_client = DBClient()
                self.db_client.base_url = self.api_url_var.get()
                self.db_client.jwt_token = self.jwt_token_var.get()
                
                self.data_handler = DataHandler()
                self.data_handler.output_dir = self.output_dir_var.get()
                
                while self.is_running:
                    try:
                        # 실행 사이클
                        self.run_single_cycle()
                        
                        # 다음 실행까지 대기 (최소 5초 보장)
                        interval = max(int(self.interval_var.get()), 5)
                        for _ in range(interval):
                            if not self.is_running:
                                break
                            time.sleep(1)
                            
                    except Exception as e:
                        self.log_message(f"실행 루프 오류: {e}", "ERROR")
                        self.stats["failed_runs"] += 1
                        time.sleep(5)
                        
            except Exception as e:
                self.log_message(f"메인 루프 오류: {e}", "ERROR")
            finally:
                if self.is_running:
                    self.stop_plugin()
        
        # 별도 스레드에서 실행
        threading.Thread(target=main_loop_thread, daemon=True).start()
    
    def run_single_cycle(self):
        """단일 실행 사이클"""
        self.stats["total_runs"] += 1
        self.stats["last_run_time"] = datetime.now()
        
        self.log_message(f"실행 사이클 #{self.stats['total_runs']} 시작", "INFO")
        
        try:
            # 최근 메시지 조회
            fetch_limit = int(self.fetch_limit_var.get())
            messages = self.db_client.get_recent_messages(fetch_limit)
            
            if messages is None:
                self.log_message("메시지 조회 실패", "ERROR")
                self.stats["failed_runs"] += 1
                return
            
            # 메시지가 없어도 빈 데이터로 저장
            if not messages:
                self.log_message("조회된 메시지가 없습니다. 빈 데이터로 JSON 파일을 갱신합니다", "INFO")
                messages = []  # 빈 리스트로 설정
            
            # JSON 파일로 저장
            filepath = self.data_handler.save_messages_to_json(messages)
            
            if filepath:
                self.log_message(f"{len(messages)}개 메시지 저장 완료", "SUCCESS")
                self.stats["successful_runs"] += 1
                self.stats["total_messages_saved"] += len(messages)
                
                # UI 업데이트
                self.root.after(0, self.update_stats)
            else:
                self.log_message("JSON 저장 실패", "ERROR")
                self.stats["failed_runs"] += 1
                
        except Exception as e:
            self.log_message(f"실행 사이클 오류: {e}", "ERROR")
            self.stats["failed_runs"] += 1
    
    def update_stats(self):
        """통계 업데이트"""
        self.total_runs_var.set(str(self.stats["total_runs"]))
        self.success_runs_var.set(str(self.stats["successful_runs"]))
        self.messages_saved_var.set(str(self.stats["total_messages_saved"]))
        
        if self.stats.get("last_run_time"):
            last_run = self.stats["last_run_time"].strftime("%H:%M:%S")
            self.last_run_var.set(last_run)
    
    def on_closing(self):
        """창 닫기 이벤트 처리"""
        if self.is_running:
            if messagebox.askokcancel("종료", "플러그인이 실행 중입니다. 정말 종료하시겠습니까?"):
                self.stop_plugin()
                self.cleanup_and_exit()
        else:
            self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """정리 후 종료"""
        try:
            # 설정 자동 저장
            self.save_config()
            self.log_message("💾 설정이 자동으로 저장되었습니다.", "SUCCESS")
            
            # 소켓 정리
            if hasattr(self, 'single_instance'):
                self.single_instance.cleanup()
        except Exception as e:
            self.log_message(f"❌ 종료 중 오류: {e}", "ERROR")
        finally:
            self.root.destroy()
    
    def run(self):
        """GUI 실행"""
        self.log_message("GUI가 시작되었습니다.", "SUCCESS")
        self.root.mainloop()

def main():
    """메인 함수"""
    try:
        app = DBToJSONGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("오류", f"프로그램 시작 오류: {e}")

if __name__ == "__main__":
    main()
