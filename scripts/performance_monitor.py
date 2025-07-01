#!/usr/bin/env python3
"""
Performance Monitoring Script

This script monitors application performance by:
1. Database query performance
2. API response times
3. Cache hit rates
4. System resource usage
"""

import sys
import os
import time
import psutil
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, timedelta
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.api_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:8000"
        self.db_config = {
            'dbname': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'host': settings.POSTGRES_SERVER,
            'port': settings.POSTGRES_PORT
        }
        self.metrics = {
            'database': {},
            'api': {},
            'system': {},
            'cache': {}
        }

    def get_db_connection(self):
        """데이터베이스 연결"""
        return psycopg2.connect(**self.db_config)

    def monitor_database_performance(self):
        """데이터베이스 성능 모니터링"""
        # # logger.info("데이터베이스 성능 모니터링 시작")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 활성 연결 수 확인
            cursor.execute("SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';")
            active_connections = cursor.fetchone()['active_connections']
            
            # 느린 쿼리 확인
            cursor.execute("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    shared_blks_hit,
                    shared_blks_read
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 5;
            """)
            
            slow_queries = cursor.fetchall()
            
            # 테이블 크기 확인
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            table_sizes = cursor.fetchall()
            
            # 인덱스 사용률 확인
            cursor.execute("""
                SELECT 
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 10;
            """)
            
            index_usage = cursor.fetchall()
            
            self.metrics['database'] = {
                'active_connections': active_connections,
                'slow_queries': [dict(q) for q in slow_queries],
                'table_sizes': [dict(t) for t in table_sizes],
                'index_usage': [dict(i) for i in index_usage],
                'timestamp': datetime.now().isoformat()
            }
            
            cursor.close()
            conn.close()
            
            # # logger.info(f"데이터베이스 모니터링 완료 - 활성 연결: {active_connections}")
            
        except Exception as e:
            logger.error(f"데이터베이스 모니터링 실패: {e}")

    def monitor_api_performance(self):
        """API 성능 모니터링"""
        # # logger.info("API 성능 모니터링 시작")
        
        api_endpoints = [
            '/api/v1/recipes/',
            '/api/v1/ingredients/',
            '/api/v1/locations/',
            '/api/v1/recommendations/',
            '/health'
        ]
        
        api_metrics = {}
        
        for endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}{endpoint}", timeout=10)
                response_time = (time.time() - start_time) * 1000  # ms
                
                api_metrics[endpoint] = {
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'content_length': len(response.content),
                    'timestamp': datetime.now().isoformat()
                }
                
                # # logger.info(f"API {endpoint}: {response_time:.2f}ms")
                
            except Exception as e:
                logger.error(f"API 모니터링 실패 {endpoint}: {e}")
                api_metrics[endpoint] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        self.metrics['api'] = api_metrics

    def monitor_system_resources(self):
        """시스템 리소스 모니터링"""
        # # logger.info("시스템 리소스 모니터링 시작")
        
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            
            self.metrics['system'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now().isoformat()
            }
            
            # # logger.info(f"시스템 모니터링 완료 - CPU: {cpu_percent}%, 메모리: {memory.percent}%")
            
        except Exception as e:
            logger.error(f"시스템 모니터링 실패: {e}")

    def monitor_cache_performance(self):
        """캐시 성능 모니터링"""
        # # logger.info("캐시 성능 모니터링 시작")
        
        try:
            import redis
            
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                decode_responses=True
            )
            
            # Redis 정보 조회
            info = redis_client.info()
            
            # 캐시 히트율 계산
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            total_requests = keyspace_hits + keyspace_misses
            hit_rate = (keyspace_hits / total_requests * 100) if total_requests > 0 else 0
            
            self.metrics['cache'] = {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': keyspace_hits,
                'keyspace_misses': keyspace_misses,
                'hit_rate_percent': round(hit_rate, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # # logger.info(f"캐시 모니터링 완료 - 히트율: {hit_rate:.2f}%")
            
        except Exception as e:
            logger.error(f"캐시 모니터링 실패: {e}")
            self.metrics['cache'] = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def generate_performance_report(self):
        """성능 리포트 생성"""
        # # logger.info("성능 리포트 생성 중...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'database_connections': self.metrics['database'].get('active_connections', 0),
                'slowest_api_endpoint': self._get_slowest_api_endpoint(),
                'system_cpu_percent': self.metrics['system'].get('cpu_percent', 0),
                'cache_hit_rate': self.metrics['cache'].get('hit_rate_percent', 0)
            },
            'details': self.metrics,
            'recommendations': self._generate_recommendations()
        }
        
        # 리포트 저장
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # # logger.info(f"성능 리포트 저장 완료: {report_file}")
        
        # 콘솔에 요약 출력
        self._print_summary(report)
        
        return report

    def _get_slowest_api_endpoint(self):
        """가장 느린 API 엔드포인트 찾기"""
        slowest = None
        slowest_time = 0
        
        for endpoint, metrics in self.metrics['api'].items():
            if 'response_time_ms' in metrics and metrics['response_time_ms'] > slowest_time:
                slowest = endpoint
                slowest_time = metrics['response_time_ms']
        
        return {'endpoint': slowest, 'response_time_ms': slowest_time} if slowest else None

    def _generate_recommendations(self):
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        # 데이터베이스 권장사항
        db_metrics = self.metrics['database']
        if db_metrics.get('active_connections', 0) > 50:
            recommendations.append("데이터베이스 연결 풀 크기를 늘리거나 연결을 최적화하세요.")
        
        slow_queries = db_metrics.get('slow_queries', [])
        if slow_queries:
            recommendations.append(f"{len(slow_queries)}개의 느린 쿼리가 발견되었습니다. 인덱스 추가를 고려하세요.")
        
        # API 권장사항
        api_metrics = self.metrics['api']
        for endpoint, metrics in api_metrics.items():
            if 'response_time_ms' in metrics and metrics['response_time_ms'] > 1000:
                recommendations.append(f"API {endpoint}의 응답 시간이 1초를 초과합니다. 최적화가 필요합니다.")
        
        # 시스템 권장사항
        system_metrics = self.metrics['system']
        if system_metrics.get('cpu_percent', 0) > 80:
            recommendations.append("CPU 사용률이 높습니다. 서버 리소스를 늘리거나 부하를 분산하세요.")
        
        if system_metrics.get('memory_percent', 0) > 90:
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수를 확인하거나 메모리를 늘리세요.")
        
        # 캐시 권장사항
        cache_metrics = self.metrics['cache']
        if cache_metrics.get('hit_rate_percent', 0) < 50:
            recommendations.append("캐시 히트율이 낮습니다. 캐시 전략을 재검토하세요.")
        
        return recommendations

    def _print_summary(self, report):
        """성능 요약 출력"""
        print("\n" + "="*60)
        print("성능 모니터링 리포트 요약")
        print("="*60)
        
        summary = report['summary']
        # Print(f"📊 데이터베이스 연결: {summary['database_connections']}개")
        
        slowest_api = summary['slowest_api_endpoint']
        if slowest_api:
            # Print(f"🐌 가장 느린 API: {slowest_api['endpoint']} ({slowest_api['response_time_ms']:.2f}ms)")
        
        # Print(f"💻 CPU 사용률: {summary['system_cpu_percent']:.1f}%")
        # Print(f"🎯 캐시 히트율: {summary['cache_hit_rate']:.1f}%")
        
        recommendations = report['recommendations']
        if recommendations:
            # Print(f"\n💡 권장사항 ({len(recommendations)}개):")
            for i, rec in enumerate(recommendations, 1):
                # Print(f"  {i}. {rec}")
        
        print("="*60)

    def run_monitoring(self):
        """전체 모니터링 실행"""
        # # logger.info("성능 모니터링 시작")
        
        try:
            # 각 모니터링 실행
            self.monitor_database_performance()
            self.monitor_api_performance()
            self.monitor_system_resources()
            self.monitor_cache_performance()
            
            # 리포트 생성
            report = self.generate_performance_report()
            
            # # logger.info("성능 모니터링 완료")
            return report
            
        except Exception as e:
            logger.error(f"성능 모니터링 중 오류 발생: {e}")
            return None

def main():
    """메인 함수"""
    monitor = PerformanceMonitor()
    report = monitor.run_monitoring()
    
    if report:
        print("✅ 성능 모니터링이 성공적으로 완료되었습니다.")
    else:
        print("❌ 성능 모니터링 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 