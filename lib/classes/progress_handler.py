import sys, gradio as gr

class ProgressHandler:
    def __init__(self, session):
        self.session = session
        self.progress_bar = gr.Progress(track_tqdm=False) if session.get("is_gui_process") else None

    def on_start(self):
        try:
            print("Final export started")
            if session.get("is_gui_process"):
                self.progress_bar(0, desc="Starting Final export…")
        except Exception:
            pass

    def on_progress(self, percent):
        try:
            sys.stdout.write(f"\Final export progress: {percent:.1f}%")
            sys.stdout.flush()
            if session.get("is_gui_process"):
                self.progress_bar(percent / 100, desc=f"Final export")
        except Exception:
            pass

    def on_complete(self, *_):
        try:
            print("\Final export  completed successfully")
            if session.get("is_gui_process"):
                self.progress_bar(1.0, desc="Export completed")
        except Exception:
            pass

    def on_error(self, err):
        try:
            print(f"\Final export failed: {err}")
            if session.get("is_gui_process"):
                self.progress_bar(0.0, desc="Export failed")
        except Exception:
            pass

    def on_cancel(self):
        try:
            print("\Final export cancelled")
            if session.get("is_gui_process"):
                self.progress_bar(0.0, desc="Cancelled")
        except Exception:
            pass
