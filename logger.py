# -*- coding: utf-8 -*-
"""
로깅 모듈
콘솔 및 파일 로그 출력을 담당
"""

import logging
import os
from datetime import datetime
from typing import Optional

from config import LOG_TO_CONSOLE, LOG_TO_FILE, LOG_FILE_PATH

class ColoredFormatter(logging.Formatter):
    """컬러가 포함된 로그 포맷터"""
    
    # ANSI 컬러 코드
    COLORS = {
        'DEBUG': '\033[36m',    # 청록색
        'INFO': '\033[32m',     # 초록색
        'WARNING': '\033[33m',  # 노란색
        'ERROR': '\033[31m',    # 빨간색
        'CRITICAL': '\033[35m', # 자주색
        'RESET': '\033[0m'      # 리셋
    }
    
    def format(self, record):
        # 컬러 적용
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class Logger:
    """로깅 시스템 관리 클래스"""
    
    def __init__(self, name: str = "DBToJSON"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        self._setup_console_handler()
        if LOG_TO_FILE:
            self._setup_file_handler()
    
    def _setup_console_handler(self):
        """콘솔 핸들러 설정"""
        if not LOG_TO_CONSOLE:
            return
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 컬러 포맷터 사용
        console_formatter = ColoredFormatter(
            '[%(asctime)s] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """파일 핸들러 설정"""
        try:
            # 로그 디렉토리 생성
            log_dir = os.path.dirname(LOG_FILE_PATH)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 파일 포맷터 (컬러 없음)
            file_formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"❌ 로그 파일 설정 실패: {e}")
    
    def debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """에러 로그"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """치명적 오류 로그"""
        self.logger.critical(message)
    
    def success(self, message: str):
        """성공 로그 (INFO 레벨)"""
        self.logger.info(f"✅ {message}")
    
    def progress(self, message: str):
        """진행 상황 로그 (INFO 레벨)"""
        self.logger.info(f"🔄 {message}")
    
    def error_emoji(self, message: str):
        """에러 로그 (이모지 포함)"""
        self.logger.error(f"❌ {message}")
    
    def warning_emoji(self, message: str):
        """경고 로그 (이모지 포함)"""
        self.logger.warning(f"⚠️ {message}")

def get_logger(name: str = "DBToJSON") -> Logger:
    """로거 인스턴스 반환"""
    return Logger(name)

# 전역 로거 인스턴스
logger = get_logger()

