import sys, gradio as gr

class ProgressHandler:
    def __init__(self, session):
        self.session = session

    def on_start(self):
        print('Export started')
        try:
            if session['is_gui_process']:
                self.progress_bar = gr.Progress(track_tqdm=False)
                self.progress_bar(0, desc='Starting export…')
        except Exception as e:
            error = f'ProgressHandler on_start error: {e}'
            print(error)
            self.progress_bar = None
            pass

    def on_progress(self, percent):
        sys.stdout.write(f'\rFinal Encoding: {percent:.1f}%')
        sys.stdout.flush()
        try:
            self.progress_bar(percent / 100, desc='Final Encoding')
        except Exception as e:
            error = f'ProgressHandler on_progress error: {e}'
            print(error)
            pass

    def on_complete(self, *_):
        print('\nExport completed successfully')
        try:
            if session['is_gui_process']:
                self.progress_bar(1.0, desc='Export completed')
        except Exception as e:
            error = f'ProgressHandler on_complete error: {e}'
            print(error)
            pass

    def on_error(self, err):
        print(f'\nExport failed: {err}')
        try:
            if session['is_gui_process']:
                self.progress_bar(0.0, desc='Export failed')
        except Exception as e:
            error = f'ProgressHandler on_error error: {e}'
            print(error)
            pass

    def on_cancel(self):
        print('\nExport cancelled')
        try:
            if session['is_gui_process']:
                self.progress_bar(0.0, desc='Cancelled')
        except Exception:
            error = f'ProgressHandler on_cancel error: {e}'
            print(error)
            pass
