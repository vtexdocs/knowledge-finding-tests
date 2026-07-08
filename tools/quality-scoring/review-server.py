#!/usr/bin/env python3
"""
Local HTTP server for the quality review tool.
Serves review.html and automatically saves human scores to sampled_for_review.json
"""

import json
import sys
import io
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class ReviewHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the review tool."""
    
    # Will be set by the server
    sampled_file = None
    html_file = None
    output_dir = None
    
    def do_GET(self):
        """Handle GET requests - serve the HTML file and data files."""
        if self.path == '/' or self.path == '/review.html':
            try:
                # Use Path to handle the file robustly
                html_path = Path(self.html_file)
                if not html_path.exists():
                    raise FileNotFoundError(f"HTML file not found at {html_path}")
                
                # Read and serve the HTML file
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                # CACHE-BUSTING: Prevent all caching to ensure fresh data
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError as e:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'HTML file not found: {e}'.encode('utf-8'))
        
        elif self.path == '/sampled_for_review.json':
            try:
                with open(self.sampled_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "File not found"}')
        
        elif self.path == '/api/scores':
            try:
                with open(self.sampled_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Scores file not found"}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        
        elif self.path == '/responses_to_score.json':
            try:
                # Try to find responses_to_score.json in the same directory
                output_path = Path(self.output_dir)
                responses_file = output_path / 'responses_to_score.json'
                
                if not responses_file.exists():
                    # Try parent directory
                    responses_file = output_path.parent / 'responses_to_score.json'
                
                if responses_file.exists():
                    with open(responses_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"error": "Responses file not found"}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def do_POST(self):
        """Handle POST requests - save human scores."""
        if self.path == '/save-progress' or self.path == '/save-scores':
            try:
                # Read the request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Decode to string
                body_str = body.decode('utf-8')
                
                # Parse JSON
                scores_data = json.loads(body_str)
                
                # Write to sampled_for_review.json with explicit path resolution
                sampled_path = Path(self.sampled_file).resolve()
                
                with open(sampled_path, 'w', encoding='utf-8') as f:
                    json.dump(scores_data, f, indent=2, ensure_ascii=False)
                
                # Send success response FIRST (before logging)
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'success': True,
                    'message': 'Scores saved successfully',
                    'count': len(scores_data),
                    'file': str(sampled_path)
                }
                response_json = json.dumps(response_data)
                self.wfile.write(response_json.encode('utf-8'))
                self.wfile.flush()
                
                # Now log the success
                sys.stdout.flush()
                sys.stderr.flush()
                print(f"✓ SUCCESS: Saved {len(scores_data)} scores to {sampled_path}")
                sys.stdout.flush()
                sys.stderr.flush()
                
            except json.JSONDecodeError as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': f'Invalid JSON: {str(e)}'})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Invalid JSON received: {e}")
                
            except IOError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': f'File write error: {str(e)}'})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Failed to write file: {e}")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': str(e)})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Unexpected error: {e}")
        
        elif self.path == '/export-data':
            try:
                # Read the request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Decode to string
                body_str = body.decode('utf-8')
                
                # Parse JSON
                scores_data = json.loads(body_str)
                
                # Write to sampled_for_review.json with explicit path resolution
                sampled_path = Path(self.sampled_file).resolve()
                
                with open(sampled_path, 'w', encoding='utf-8') as f:
                    json.dump(scores_data, f, indent=2, ensure_ascii=False)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'success': True,
                    'message': 'Data exported successfully',
                    'count': len(scores_data),
                    'file': str(sampled_path)
                }
                response_json = json.dumps(response_data)
                self.wfile.write(response_json.encode('utf-8'))
                self.wfile.flush()
                
                # Log the export
                sys.stdout.flush()
                sys.stderr.flush()
                print(f"✓ EXPORTED: {len(scores_data)} items exported to {sampled_path}")
                sys.stdout.flush()
                sys.stderr.flush()
                
            except json.JSONDecodeError as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': f'Invalid JSON: {str(e)}'})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Invalid JSON received: {e}")
                
            except IOError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': f'File write error: {str(e)}'})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Failed to write file: {e}")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': str(e)})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ ERROR: Unexpected error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging to reduce noise."""
        pass


def main():
    """Run the review server."""
    parser = argparse.ArgumentParser(
        description="Local HTTP server for the quality review tool."
    )
    parser.add_argument(
        "sampled_file",
        help="Path to the sampled_for_review.json (or batch data file) to save scores to",
    )
    parser.add_argument(
        "html_file",
        help="Path to the review HTML file to serve",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000). Use distinct ports for parallel batches.",
    )
    args = parser.parse_args()

    sampled_file = Path(args.sampled_file).resolve()
    html_file = Path(args.html_file).resolve()
    port = args.port
    
    print(f"DEBUG: sampled_file = {sampled_file}")
    print(f"DEBUG: html_file = {html_file}")
    print(f"DEBUG: sampled_file.exists() = {sampled_file.exists()}")
    print(f"DEBUG: html_file.exists() = {html_file.exists()}")
    
    if not sampled_file.exists():
        print(f"Error: Sampled file not found: {sampled_file}")
        return 1
    
    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}")
        return 1
    
    # Set class variables - use str() for consistency
    ReviewHandler.sampled_file = str(sampled_file)
    ReviewHandler.html_file = str(html_file)
    ReviewHandler.output_dir = str(sampled_file.parent)
    
    # Create and start server
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, ReviewHandler)
    
    print("=" * 80)
    print("QUALITY SCORE REVIEW SERVER")
    print("=" * 80)
    print()
    print(f"Sampled file: {sampled_file.resolve()}")
    print(f"HTML file: {html_file.resolve()}")
    print()
    print(f"Server started at: http://localhost:{port}")
    print()
    print("How to use:")
    print(f"  1. Open http://localhost:{port} in your browser")
    print("  2. Review responses and assign scores (1-4)")
    print("  3. Optionally add notes for each item")
    print("  4. Click 'Export Data' button to save to the sampled JSON file")
    print("  5. Or click 'Download Progress' to backup scores locally")
    print()
    print("To stop the server: Press Ctrl+C")
    print()
    sys.stdout.flush()
    
    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("Server stopped.")
        print("=" * 80)
        return 0


if __name__ == '__main__':
    sys.exit(main())
