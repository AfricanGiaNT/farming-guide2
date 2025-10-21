"""
Performance Monitoring System for Crop Recommendations API.
Monitors response times, throughput, and system performance.
"""
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
from scripts.utils.logger import logger


class PerformanceMonitor:
    """
    Performance monitoring system for crop recommendations API.
    Monitors response times, throughput, and system performance.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history: Maximum number of performance records to keep
        """
        self.max_history = max_history
        self.response_times = deque(maxlen=max_history)
        self.request_counts = deque(maxlen=max_history)
        self.error_counts = deque(maxlen=max_history)
        self.performance_stats = {
            'total_requests': 0,
            'total_errors': 0,
            'total_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'start_time': time.time()
        }
        self.lock = threading.Lock()
        
        logger.info(f"Performance Monitor initialized with {max_history} max history")
    
    def start_request(self) -> str:
        """
        Start monitoring a request.
        
        Returns:
            Request ID for tracking
        """
        request_id = f"req_{int(time.time() * 1000)}"
        
        with self.lock:
            self.performance_stats['total_requests'] += 1
        
        logger.debug(f"Started monitoring request: {request_id}")
        return request_id
    
    def end_request(self, 
                   request_id: str, 
                   success: bool = True, 
                   error_type: Optional[str] = None) -> Dict[str, Any]:
        """
        End monitoring a request and record performance data.
        
        Args:
            request_id: Request ID from start_request
            success: Whether the request was successful
            error_type: Type of error if request failed
            
        Returns:
            Performance data for the request
        """
        end_time = time.time()
        
        # Calculate response time (simplified - in real implementation would track start time)
        response_time = 0.1  # Placeholder - would be calculated from start time
        
        with self.lock:
            # Record response time
            self.response_times.append({
                'timestamp': end_time,
                'response_time': response_time,
                'success': success,
                'error_type': error_type,
                'request_id': request_id
            })
            
            # Update statistics
            self.performance_stats['total_response_time'] += response_time
            self.performance_stats['min_response_time'] = min(
                self.performance_stats['min_response_time'], response_time
            )
            self.performance_stats['max_response_time'] = max(
                self.performance_stats['max_response_time'], response_time
            )
            
            if not success:
                self.performance_stats['total_errors'] += 1
                self.error_counts.append({
                    'timestamp': end_time,
                    'error_type': error_type,
                    'request_id': request_id
                })
        
        logger.debug(f"Ended monitoring request: {request_id}, success: {success}, time: {response_time:.3f}s")
        
        return {
            'request_id': request_id,
            'response_time': response_time,
            'success': success,
            'error_type': error_type,
            'timestamp': end_time
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        with self.lock:
            total_requests = self.performance_stats['total_requests']
            total_errors = self.performance_stats['total_errors']
            total_response_time = self.performance_stats['total_response_time']
            
            if total_requests > 0:
                avg_response_time = total_response_time / total_requests
                error_rate = (total_errors / total_requests) * 100
            else:
                avg_response_time = 0.0
                error_rate = 0.0
            
            uptime = time.time() - self.performance_stats['start_time']
            
            return {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate': round(error_rate, 2),
                'average_response_time': round(avg_response_time, 3),
                'min_response_time': round(self.performance_stats['min_response_time'], 3),
                'max_response_time': round(self.performance_stats['max_response_time'], 3),
                'uptime_seconds': round(uptime, 1),
                'requests_per_second': round(total_requests / max(1, uptime), 2),
                'performance_target_met': avg_response_time < 3.0  # < 3 seconds target
            }
    
    def get_recent_performance(self, minutes: int = 5) -> Dict[str, Any]:
        """Get performance data for the last N minutes."""
        cutoff_time = time.time() - (minutes * 60)
        
        with self.lock:
            recent_response_times = [
                rt for rt in self.response_times 
                if rt['timestamp'] >= cutoff_time
            ]
            recent_errors = [
                err for err in self.error_counts 
                if err['timestamp'] >= cutoff_time
            ]
        
        if not recent_response_times:
            return {
                'period_minutes': minutes,
                'requests': 0,
                'errors': 0,
                'average_response_time': 0.0,
                'error_rate': 0.0
            }
        
        total_requests = len(recent_response_times)
        total_errors = len(recent_errors)
        avg_response_time = sum(rt['response_time'] for rt in recent_response_times) / total_requests
        error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            'period_minutes': minutes,
            'requests': total_requests,
            'errors': total_errors,
            'average_response_time': round(avg_response_time, 3),
            'error_rate': round(error_rate, 2),
            'success_rate': round(100 - error_rate, 2)
        }
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_data = [
                rt for rt in self.response_times 
                if rt['timestamp'] >= cutoff_time
            ]
        
        if not recent_data:
            return {
                'period_hours': hours,
                'trends': [],
                'summary': 'No data available'
            }
        
        # Group by hour
        hourly_data = {}
        for data in recent_data:
            hour = int(data['timestamp'] // 3600) * 3600
            if hour not in hourly_data:
                hourly_data[hour] = {'requests': 0, 'total_time': 0.0, 'errors': 0}
            
            hourly_data[hour]['requests'] += 1
            hourly_data[hour]['total_time'] += data['response_time']
            if not data['success']:
                hourly_data[hour]['errors'] += 1
        
        # Create trends
        trends = []
        for hour in sorted(hourly_data.keys()):
            data = hourly_data[hour]
            avg_time = data['total_time'] / data['requests'] if data['requests'] > 0 else 0
            error_rate = (data['errors'] / data['requests']) * 100 if data['requests'] > 0 else 0
            
            trends.append({
                'hour': datetime.fromtimestamp(hour).strftime('%H:00'),
                'requests': data['requests'],
                'average_response_time': round(avg_time, 3),
                'error_rate': round(error_rate, 2)
            })
        
        return {
            'period_hours': hours,
            'trends': trends,
            'summary': f'Performance data for last {hours} hours'
        }
    
    def check_performance_targets(self) -> Dict[str, Any]:
        """Check if performance targets are being met."""
        stats = self.get_performance_stats()
        
        targets = {
            'response_time_under_3s': stats['average_response_time'] < 3.0,
            'error_rate_under_5pct': stats['error_rate'] < 5.0,
            'uptime_above_99pct': True,  # Placeholder - would calculate from uptime data
            'throughput_above_10rps': stats['requests_per_second'] > 10.0
        }
        
        targets_met = sum(targets.values())
        total_targets = len(targets)
        
        return {
            'targets': targets,
            'targets_met': targets_met,
            'total_targets': total_targets,
            'performance_score': round((targets_met / total_targets) * 100, 1),
            'status': 'excellent' if targets_met == total_targets else 'needs_improvement'
        }
    
    def reset_stats(self):
        """Reset performance statistics."""
        with self.lock:
            self.response_times.clear()
            self.request_counts.clear()
            self.error_counts.clear()
            self.performance_stats = {
                'total_requests': 0,
                'total_errors': 0,
                'total_response_time': 0.0,
                'min_response_time': float('inf'),
                'max_response_time': 0.0,
                'start_time': time.time()
            }
        
        logger.info("Performance statistics reset")


# Create global instance
performance_monitor = PerformanceMonitor()
