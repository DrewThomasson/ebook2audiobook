import os
import sys
import time
from datetime import datetime, timedelta


class RunLogger:
    """
    Captures stdout and stderr to a log file while preserving normal output.
    Does not change what the user sees in terminal/Gradio UI.
    """
    
    def __init__(self, log_dir, session_id=None, enabled=True):
        """
        Initialize the RunLogger.
        
        Args:
            log_dir: Directory to store log files
            session_id: Optional session ID to include in log filename
            enabled: Whether logging is enabled
        """
        self.enabled = enabled
        self.log_dir = log_dir
        self.session_id = session_id or "unknown"
        self.log_file = None
        self.log_file_path = None
        self.original_stdout = None
        self.original_stderr = None
        self.tee_stdout = None
        self.tee_stderr = None
        
    def start(self):
        """Start capturing stdout/stderr to log file."""
        if not self.enabled:
            return
            
        try:
            # Create log directory if it doesn't exist
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Generate log filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            log_filename = f"run_{timestamp}_{self.session_id}.log"
            self.log_file_path = os.path.join(self.log_dir, log_filename)
            
            # Open log file
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=1)
            
            # Write header
            self.log_file.write(f"=== Log started at {datetime.now().isoformat()} ===\n")
            self.log_file.write(f"Session ID: {self.session_id}\n")
            self.log_file.write("=" * 60 + "\n\n")
            self.log_file.flush()
            
            # Save original streams
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            
            # Create tee streams that write to both original and log file
            self.tee_stdout = TeeStream(self.original_stdout, self.log_file)
            self.tee_stderr = TeeStream(self.original_stderr, self.log_file)
            
            # Replace sys streams
            sys.stdout = self.tee_stdout
            sys.stderr = self.tee_stderr
            
        except Exception as e:
            # If logging fails, just continue without logging
            print(f"Warning: Could not initialize log file: {e}", file=sys.stderr)
            self.enabled = False
            
    def stop(self):
        """Stop capturing stdout/stderr and close log file."""
        if not self.enabled or not self.log_file:
            return
            
        try:
            # Restore original streams
            if self.original_stdout:
                sys.stdout = self.original_stdout
            if self.original_stderr:
                sys.stderr = self.original_stderr
                
            # Write footer and close log file
            if self.log_file and not self.log_file.closed:
                self.log_file.write(f"\n\n{'=' * 60}\n")
                self.log_file.write(f"=== Log ended at {datetime.now().isoformat()} ===\n")
                self.log_file.flush()
                self.log_file.close()
                
        except Exception as e:
            print(f"Warning: Error closing log file: {e}", file=sys.stderr)
            
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Log any exceptions
        if exc_type is not None and self.enabled and self.log_file:
            try:
                import traceback
                self.log_file.write("\n\n=== EXCEPTION OCCURRED ===\n")
                self.log_file.write(f"Exception type: {exc_type.__name__}\n")
                self.log_file.write(f"Exception value: {exc_val}\n")
                self.log_file.write("\nTraceback:\n")
                traceback.print_exception(exc_type, exc_val, exc_tb, file=self.log_file)
                self.log_file.flush()
            except:
                pass
                
        self.stop()
        return False  # Don't suppress exceptions
        
    @staticmethod
    def cleanup_old_logs(log_dir, retention_days):
        """
        Clean up log files older than retention_days.
        
        Args:
            log_dir: Directory containing log files
            retention_days: Number of days to keep log files
        """
        if not os.path.exists(log_dir):
            return
            
        try:
            cutoff_time = time.time() - (retention_days * 86400)  # 86400 seconds per day
            
            for filename in os.listdir(log_dir):
                if filename.startswith("run_") and filename.endswith(".log"):
                    filepath = os.path.join(log_dir, filename)
                    try:
                        if os.path.isfile(filepath):
                            file_mtime = os.path.getmtime(filepath)
                            if file_mtime < cutoff_time:
                                os.remove(filepath)
                                print(f"Deleted old log file: {filename}")
                    except Exception as e:
                        print(f"Warning: Could not delete log file {filename}: {e}")
                        
        except Exception as e:
            print(f"Warning: Error during log cleanup: {e}")


class TeeStream:
    """
    A stream that writes to two destinations simultaneously.
    Used to write to both terminal and log file.
    """
    
    def __init__(self, stream1, stream2):
        """
        Initialize TeeStream.
        
        Args:
            stream1: First output stream (usually terminal)
            stream2: Second output stream (usually log file)
        """
        self.stream1 = stream1
        self.stream2 = stream2
        
    def write(self, message):
        """Write message to both streams."""
        try:
            # Write to terminal
            self.stream1.write(message)
            self.stream1.flush()
        except:
            pass
            
        try:
            # Write to log file
            self.stream2.write(message)
            self.stream2.flush()
        except:
            pass
            
    def flush(self):
        """Flush both streams."""
        try:
            self.stream1.flush()
        except:
            pass
        try:
            self.stream2.flush()
        except:
            pass
            
    def isatty(self):
        """Check if stream is a TTY (delegate to stream1)."""
        try:
            return self.stream1.isatty()
        except:
            return False
