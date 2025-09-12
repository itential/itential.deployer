#!/usr/bin/env python3
import json
import time
from collections import Counter, defaultdict
from prometheus_client import start_http_server, Counter as PromCounter, Histogram, Gauge
import argparse
from pathlib import Path
from urllib.parse import urlparse

# Prometheus metrics
request_count = PromCounter('web_requests_total', 'Total web requests', ['method', 'status', 'user', 'endpoint'])
request_size = Histogram('web_request_size_bytes', 'Size of web requests', ['method'])
response_size = Histogram('web_response_size_bytes', 'Size of web responses', ['status'])
response_time = Histogram('web_response_time_seconds', 'Response time', ['method', 'status'])
status_codes = PromCounter('web_status_codes_total', 'HTTP status codes', ['status'])
endpoints = PromCounter('web_endpoints_total', 'Requests by endpoint', ['endpoint', 'method'])
users = PromCounter('web_users_total', 'Requests by user', ['user', 'method'])
error_rate = Gauge('web_error_rate', 'Current error rate (5xx responses)')

class JSONLogParser:
    def __init__(self, log_file):
        self.log_file = Path(log_file)
        # Track file position for incremental parsing
        self.position_file = Path(f"{log_file}.position")
        self.position = self._load_position()
        self.stats = defaultdict(int)
        self.recent_requests = []  # For calculating error rates
        
    def _load_position(self):
        """Load the last file position from disk"""
        try:
            if self.position_file.exists():
                with open(self.position_file, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return 0
    
    def _save_position(self):
        """Save the current file position to disk"""
        try:
            with open(self.position_file, 'w') as f:
                f.write(str(self.position))
        except IOError as e:
            print(f"Warning: Could not save position: {e}")
        
    def parse_line(self, line):
        """Parse a single JSON log line"""
        try:
            data = json.loads(line.strip())
            
            # Validate required fields
            required_fields = ['remote_addr', 'method', 'url', 'status', 'result_length']
            if not all(field in data for field in required_fields):
                return None
            
            # Convert numeric fields
            try:
                data['status'] = int(data['status'])
                data['result_length'] = int(data['result_length'])
            except (ValueError, KeyError):
                return None
                
            return data
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON line: {e}")
            return None
        
    def extract_endpoint(self, url):
        """Extract endpoint from URL for grouping"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Group common patterns
            if path.startswith('/status'):
                return '/status'
            elif path.startswith('/myTtl'):
                return '/myTtl'
            elif path.startswith('/api/'):
                # Group API endpoints by first two segments
                parts = path.split('/')
                if len(parts) >= 3:
                    return f"/{parts[1]}/{parts[2]}"
                return f"/{parts[1]}"
            else:
                # For other paths, use the first segment or full path if short
                if len(path) < 20:
                    return path
                else:
                    return path.split('/')[1] if '/' in path[1:] else path
                    
        except Exception:
            return url
    
    def normalize_remote_addr(self, addr):
        """Normalize IPv6-mapped IPv4 addresses"""
        if addr.startswith('::ffff:'):
            return addr[7:]  # Remove IPv6 prefix
        return addr
        
    def process_logs(self):
        """Process new log entries since last run"""
        if not self.log_file.exists():
            print(f"Log file {self.log_file} not found")
            return
        
        # Check if log file was rotated (size decreased)
        try:
            current_size = self.log_file.stat().st_size
            if current_size < self.position:
                print("Log rotation detected, resetting position")
                self.position = 0
        except OSError:
            return
            
        try:
            with open(self.log_file, 'r') as f:
                # Seek to last position
                f.seek(self.position)
                
                lines_processed = 0
                for line in f:
                    if line.strip():  # Skip empty lines
                        parsed = self.parse_line(line)
                        if parsed:
                            self.update_metrics(parsed)
                            lines_processed += 1
                
                # Update and save position
                self.position = f.tell()
                self._save_position()
                
                if lines_processed > 0:
                    print(f"Processed {lines_processed} new log entries")
                
        except Exception as e:
            print(f"Error processing logs: {e}")
    
    def update_metrics(self, data):
        """Update Prometheus metrics with parsed data"""
        method = data.get('method', 'UNKNOWN')
        status = data.get('status', 0)
        status_str = str(status)
        user = data.get('remote_user', 'anonymous')
        url = data.get('url', '/')
        result_length = data.get('result_length', 0)
        remote_addr = self.normalize_remote_addr(data.get('remote_addr', 'unknown'))
        
        # Extract endpoint for grouping
        endpoint = self.extract_endpoint(url)
        
        # Update main counters
        request_count.labels(
            method=method, 
            status=status_str, 
            user=user, 
            endpoint=endpoint
        ).inc()
        
        # Update specific metric counters
        status_codes.labels(status=status_str).inc()
        endpoints.labels(endpoint=endpoint, method=method).inc()
        users.labels(user=user, method=method).inc()
        
        # Update histograms
        response_size.labels(status=status_str).observe(result_length)
        
        # Track recent requests for error rate calculation
        self.recent_requests.append(status >= 500)
        
        # Keep only last 100 requests for error rate
        if len(self.recent_requests) > 100:
            self.recent_requests = self.recent_requests[-100:]
            
        # Update error rate gauge
        if self.recent_requests:
            error_rate.set(sum(self.recent_requests) / len(self.recent_requests))
        
        # Track some basic stats for logging
        self.stats['total_requests'] += 1
        self.stats[f'status_{status_str}'] += 1
        self.stats['total_bytes'] += result_length
        
        # Log interesting events
        if status >= 500:
            print(f"Server error: {method} {url} -> {status} (user: {user})")
        elif status == 401 or status == 403:
            print(f"Auth issue: {method} {url} -> {status} (user: {user}, ip: {remote_addr})")

    def print_summary(self):
        """Print current statistics summary"""
        if self.stats['total_requests'] > 0:
            print(f"\n=== Statistics Summary ===")
            print(f"Total requests processed: {self.stats['total_requests']}")
            print(f"Total bytes served: {self.stats['total_bytes']:,}")
            
            # Print status code breakdown
            status_codes = {k: v for k, v in self.stats.items() if k.startswith('status_')}
            if status_codes:
                print("Status codes:")
                for status, count in sorted(status_codes.items()):
                    percentage = (count / self.stats['total_requests']) * 100
                    print(f"  {status.replace('status_', '')}: {count} ({percentage:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='JSON Web Log Prometheus Exporter')
    parser.add_argument('--log-file', required=True, help='Path to JSON web server log file')
    parser.add_argument('--port', type=int, default=8000, help='Metrics port (default: 8000)')
    parser.add_argument('--interval', type=int, default=30, help='Parse interval in seconds (default: 30)')
    parser.add_argument('--summary-interval', type=int, default=300, help='Summary print interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    # Initialize log parser
    log_parser = JSONLogParser(args.log_file)
    
    # Start Prometheus metrics server
    start_http_server(args.port)
    print(f"Metrics server started on port {args.port}")
    print(f"Monitoring JSON log file: {args.log_file}")
    print(f"Metrics available at: http://localhost:{args.port}/metrics")
    
    last_summary = time.time()
    
    # Main processing loop
    try:
        while True:
            log_parser.process_logs()
            
            # Print summary periodically
            if time.time() - last_summary >= args.summary_interval:
                log_parser.print_summary()
                last_summary = time.time()
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        log_parser.print_summary()

if __name__ == '__main__':
    main()
