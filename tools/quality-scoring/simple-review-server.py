#!/usr/bin/env python3
"""
Simple review server that serves a single HTML file.
No complex routing - just serves the file.
"""
import sys
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class SimpleReviewHandler(SimpleHTTPRequestHandler):
    html_file = None
    
    def do_GET(self):
        # Always serve the same HTML file regardless of path
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(content.encode('utf-8'))
            print(f"✓ Served: {self.path}")
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
            print(f"✗ Error: {e}")
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python simple-review-server.py <path-to-review.html>")
        sys.exit(1)
    
    html_path = Path(sys.argv[1]).resolve()
    
    if not html_path.exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)
    
    SimpleReviewHandler.html_file = str(html_path)
    
    print("=" * 80)
    print("SIMPLE REVIEW SERVER")
    print("=" * 80)
    print(f"\nServing: {html_path}")
    print(f"File size: {html_path.stat().st_size / 1024:.1f} KB")
    print("\nServer started at: http://localhost:8000")
    print("Press Ctrl+C to stop\n")
    
    server = HTTPServer(('localhost', 8000), SimpleReviewHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
