# -*- coding: utf-8 -*-
"""
DB → JSON 자동 저장 플러그인 메인 실행 파일
ArtistSul CMS 데이터베이스에서 메시지 데이터를 주기적으로 가져와 JSON으로 저장
"""

import time
import signal
import sys
import socket
from datetime import datetime, timedelta
from typing import Optional

from config import INTERVAL_SECONDS, FETCH_LIMIT
from db_client import DBClient
from data_handler import DataHandler
from logger import get_logger

class SingleInstance:
    """프로그램 중복 실행 방지 클래스"""
    
    def __init__(self, port=12346):  # GUI와 다른 포트 사용
        self.port = port
        self.socket = None
        
    def is_running(self):
        """다른 인스턴스가 실행 중인지 확인"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('localhost', self.port))
            self.socket.listen(1)
            return False
        except socket.error:
            return True
    
    def cleanup(self):
        """소켓 정리"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

class DBToJSONPlugin:
    """DB → JSON 자동 저장 플러그인 메인 클래스"""
    
    def __init__(self):
        # 중복 실행 방지
        self.single_instance = SingleInstance()
        if self.single_instance.is_running():
            print("❌ 프로그램이 이미 실행 중입니다!")
            print("   다른 창을 확인해주세요.")
            sys.exit(1)
        
        self.logger = get_logger("DBToJSONPlugin")
        self.db_client = DBClient()
        self.data_handler = DataHandler()
        self.running = False
        self.stats = {
            "start_time": None,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_messages_saved": 0,
            "last_run_time": None
        }
        
        # 시그널 핸들러 설정 (Ctrl+C 처리)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (프로그램 종료 처리)"""
        self.logger.info(f"🛑 종료 신호 수신 (신호: {signum})")
        self.stop()
    
    def start(self):
        """플러그인 시작"""
        self.logger.info("🚀 DB → JSON 자동 저장 플러그인 시작!")
        self.logger.info(f"⚙️ 설정: {INTERVAL_SECONDS}초 간격, {FETCH_LIMIT}개 메시지")
        
        # API 연결 테스트
        if not self._test_connection():
            self.logger.error_emoji("API 연결 실패! 프로그램을 종료합니다.")
            return False
        
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.logger.info("👋 사용자에 의해 중단됨")
        except Exception as e:
            self.logger.error_emoji(f"예상치 못한 오류: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """플러그인 중지"""
        if not self.running:
            return
        
        self.running = False
        self._print_final_stats()
        self.logger.info("🛑 플러그인이 중지되었습니다.")
        
        # 소켓 정리
        try:
            if hasattr(self, 'single_instance'):
                self.single_instance.cleanup()
        except:
            pass
    
    def _test_connection(self) -> bool:
        """API 연결 테스트"""
        self.logger.info("🔍 API 연결 테스트 중...")
        return self.db_client.test_connection()
    
    def _main_loop(self):
        """메인 실행 루프"""
        self.logger.info("🔄 메인 루프 시작")
        
        while self.running:
            try:
                self._run_single_cycle()
                self._wait_for_next_cycle()
                
            except Exception as e:
                self.logger.error_emoji(f"실행 루프 오류: {e}")
                self.stats["failed_runs"] += 1
                time.sleep(5)  # 오류 시 5초 대기 후 재시도
    
    def _run_single_cycle(self):
        """단일 실행 사이클"""
        self.stats["total_runs"] += 1
        self.stats["last_run_time"] = datetime.now()
        
        self.logger.info(f"🔄 실행 사이클 #{self.stats['total_runs']} 시작")
        
        try:
            # 최근 메시지 조회
            messages = self.db_client.get_recent_messages(FETCH_LIMIT)
            
            if messages is None:
                self.logger.error_emoji("메시지 조회 실패")
                self.stats["failed_runs"] += 1
                return
            
            # 메시지가 없어도 빈 데이터로 저장
            if not messages:
                self.logger.info("📝 조회된 메시지가 없습니다. 빈 데이터로 JSON 파일을 갱신합니다")
                messages = []  # 빈 리스트로 설정
            
            # JSON 파일로 저장
            filepath = self.data_handler.save_messages_to_json(messages)
            
            if filepath:
                self.logger.success(f"{len(messages)}개 메시지 저장 완료 → {filepath}")
                self.stats["successful_runs"] += 1
                self.stats["total_messages_saved"] += len(messages)
            else:
                self.logger.error_emoji("JSON 저장 실패")
                self.stats["failed_runs"] += 1
                
        except Exception as e:
            self.logger.error_emoji(f"실행 사이클 오류: {e}")
            self.stats["failed_runs"] += 1
    
    def _wait_for_next_cycle(self):
        """다음 사이클까지 대기"""
        if not self.running:
            return
        
        # 최소 5초 보장 (API 서버 보호)
        safe_interval = max(INTERVAL_SECONDS, 5)
        self.logger.info(f"⏰ 다음 실행까지 {safe_interval}초 대기...")
        
        # 1초씩 대기하면서 중단 신호 확인
        for _ in range(safe_interval):
            if not self.running:
                break
            time.sleep(1)
    
    def _print_final_stats(self):
        """최종 통계 출력"""
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            self.logger.info("📊 === 실행 통계 ===")
            self.logger.info(f"⏱️ 총 실행 시간: {runtime}")
            self.logger.info(f"🔄 총 실행 횟수: {self.stats['total_runs']}")
            self.logger.info(f"✅ 성공한 실행: {self.stats['successful_runs']}")
            self.logger.info(f"❌ 실패한 실행: {self.stats['failed_runs']}")
            self.logger.info(f"💾 총 저장된 메시지: {self.stats['total_messages_saved']}개")
            
            if self.stats['total_runs'] > 0:
                success_rate = (self.stats['successful_runs'] / self.stats['total_runs']) * 100
                self.logger.info(f"📈 성공률: {success_rate:.1f}%")
    
    def run_once(self) -> bool:
        """한 번만 실행 (테스트용)"""
        self.logger.info("🧪 단일 실행 모드")
        
        if not self._test_connection():
            return False
        
        self._run_single_cycle()
        return True

def main():
    """메인 함수"""
    print("=" * 60)
    print("LoadDB(directorkim@scenes.kr)")
    print("ArtistSul CMS 데이터베이스 연동")
    print("=" * 60)
    
    try:
        # 플러그인 인스턴스 생성
        plugin = DBToJSONPlugin()
        
        # 명령행 인수 확인
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # 테스트 모드 (한 번만 실행)
            print("테스트 모드로 실행합니다...")
            success = plugin.run_once()
            sys.exit(0 if success else 1)
        else:
            # 일반 모드 (주기적 실행)
            print("주기적 실행 모드로 시작합니다...")
            print("중지하려면 Ctrl+C를 누르세요")
            print()
            
            success = plugin.start()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
