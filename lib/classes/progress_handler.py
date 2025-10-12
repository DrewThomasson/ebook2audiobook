import sys, gradio as gr

class ProgressHandler:
    def __init__(self, session):
        self.session = session
        self.progress_bar = gr.Progress(track_tqdm=False) if session.get("is_gui_process") else None

    def on_start(self):
        print("Export started")
        if self.progress_bar:
            try:
                self.progress_bar(0, desc="Starting export…")
            except Exception:
                pass

    def on_progress(self, percent):
        sys.stdout.write(f"\rExport progress: {percent:.1f}%")
        sys.stdout.flush()
        if self.progress_bar:
            try:
                self.progress_bar(percent / 100, desc=f"Encoding {percent:.1f}%")
            except Exception:
                pass

    def on_complete(self, *_):
        print("\nExport completed successfully")
        if self.progress_bar:
            try:
                self.progress_bar(1.0, desc="Export completed")
            except Exception:
                pass

    def on_error(self, err):
        print(f"\nExport failed: {err}")
        if self.progress_bar:
            try:
                self.progress_bar(0.0, desc="Export failed")
            except Exception:
                pass

    def on_cancel(self):
        print("\nExport cancelled")
        if self.progress_bar:
            try:
                self.progress_bar(0.0, desc="Cancelled")
            except Exception:
                pass
