import sys, gradio as gr

class ProgressHandler:
    def __init__(self, session):
        self.session = session
        self.is_gui = bool(session.get("is_gui_process"))
        self.progress_bar = None
        if self.is_gui:
            try:
                self.progress_bar = gr.Progress(track_tqdm=False)
                self.progress_bar(0, desc="Preparing export…")
            except Exception:
                self.progress_bar = None

    def on_start(self):
        print("Export started")
        try:
            if self.is_gui and self.progress_bar is not None:
                self.progress_bar(0, desc="Starting export…")
        except Exception:
            pass

    def on_progress(self, percent):
        sys.stdout.write(f"\rExport progress: {percent:.1f}%")
        sys.stdout.flush()
        try:
            if self.is_gui and self.progress_bar is not None:
                self.progress_bar(percent / 100, desc=f"Encoding {percent:.1f}%")
        except Exception:
            pass

    def on_complete(self, *_):
        print("\nExport completed successfully")
        try:
            if self.is_gui and self.progress_bar is not None:
                self.progress_bar(1.0, desc="Export completed")
        except Exception:
            pass

    def on_error(self, err):
        print(f"\nExport failed: {err}")
        try:
            if self.is_gui and self.progress_bar is not None:
                self.progress_bar(0.0, desc="Export failed")
        except Exception:
            pass

    def on_cancel(self):
        print("\nExport cancelled")
        try:
            if self.is_gui and self.progress_bar is not None:
                self.progress_bar(0.0, desc="Cancelled")
        except Exception:
            pass
