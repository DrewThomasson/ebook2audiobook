import os
import sys
import time
from datetime import datetime, timedelta


class RunLogger:
    """
    Captures stdout and stderr to a log file while preserving normal output.
    Does not change what the user sees in terminal/Gradio UI.
    Uses memory buffering to minimize disk I/O overhead.
    """
    
    # Buffer size for log file writes (128KB for optimal performance)
    BUFFER_SIZE = 128 * 1024
    
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
        self.buffer = []
        self.buffer_size = 0
        
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
            
            # Open log file with larger buffer for better performance
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=self.BUFFER_SIZE)
            
            # Write header
            self.log_file.write(f"=== Log started at {datetime.now().isoformat()} ===\n")
            self.log_file.write(f"Session ID: {self.session_id}\n")
            self.log_file.write("=" * 60 + "\n\n")
            # Flush header to ensure it's written immediately
            self.log_file.flush()
            
            # Save original streams
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            
            # Create tee streams that write to both original and log file
            # Pass the RunLogger instance for buffered writing
            self.tee_stdout = TeeStream(self.original_stdout, self)
            self.tee_stderr = TeeStream(self.original_stderr, self)
            
            # Replace sys streams
            sys.stdout = self.tee_stdout
            sys.stderr = self.tee_stderr
            
        except Exception as e:
            # If logging fails, just continue without logging
            print(f"Warning: Could not initialize log file: {e}", file=sys.stderr)
            self.enabled = False
    
    def write_to_log(self, message):
        """
        Write message to log file with buffering to minimize disk I/O.
        
        Args:
            message: String to write to log file
        """
        if not self.enabled or not self.log_file or self.log_file.closed:
            return
        
        try:
            # Write to file (Python's buffering handles the actual I/O optimization)
            self.log_file.write(message)
        except:
            pass
    
    def flush_log(self):
        """Flush the log file buffer to disk."""
        if self.enabled and self.log_file and not self.log_file.closed:
            try:
                self.log_file.flush()
            except:
                pass
            
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
            
            # Flush any remaining buffered data
            self.flush_log()
                
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
    Used to write to both terminal and log file with buffered writes.
    """
    
    def __init__(self, terminal_stream, logger):
        """
        Initialize TeeStream.
        
        Args:
            terminal_stream: Output stream for terminal (usually sys.__stdout__ or sys.__stderr__)
            logger: RunLogger instance for buffered log file writing
        """
        self.terminal_stream = terminal_stream
        self.logger = logger
        
    def write(self, message):
        """Write message to both terminal and log file."""
        # Always write to terminal immediately for real-time feedback
        try:
            self.terminal_stream.write(message)
            self.terminal_stream.flush()
        except:
            pass
            
        # Write to log file via buffered method (no immediate flush)
        try:
            self.logger.write_to_log(message)
        except:
            pass
            
    def flush(self):
        """Flush both terminal and log file."""
        try:
            self.terminal_stream.flush()
        except:
            pass
        try:
            self.logger.flush_log()
        except:
            pass
            
    def isatty(self):
        """Check if stream is a TTY (delegate to terminal_stream)."""
        try:
            return self.terminal_stream.isatty()
        except:
            return False
