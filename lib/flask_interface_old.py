"""
Flask-based web interface for ebook2audiobook
Replaces the Gradio interface while maintaining all functionality
"""

import os
import json
import uuid
import tempfile
import threading
import time
import shutil
import glob
import re
from pathlib import Path
from queue import Queue

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename

from lib import *
from lib.functions import (
    SessionContext, convert_ebook, convert_ebook_batch,
    show_alert, get_all_ip_addresses, get_compatible_tts_engines,
    get_sanitized
)
from lib.classes.voice_extractor import VoiceExtractor


class FlaskInterface:
    def __init__(self, args, ctx):
        self.app = Flask(__name__, 
                        template_folder='../templates',
                        static_folder='../static')
        self.app.secret_key = 'ebook2audiobook_' + str(uuid.uuid4())
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.args = args
        self.ctx = ctx
        self.script_mode = args['script_mode']
        self.is_gui_process = args['is_gui_process']
        self.is_gui_shared = args['share']
        
        # Thread management
        self.conversion_threads = {}
        self.log_buffers = {}
        
        # Initialize interface data
        self.language_options = self.get_language_options()
        self.device_options = self.get_device_options()
        self.output_format_options = self.get_output_format_options()
        
        # Setup routes
        self.setup_routes()
        self.setup_socket_handlers()
        
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main interface page"""
            try:
                # Initialize session if not exists
                if 'session_id' not in session:
                    session['session_id'] = str(uuid.uuid4())
                    
                session_id = session['session_id']
                
                # Create context session if not exists
                if not hasattr(self.ctx, 'sessions') or session_id not in self.ctx.sessions:
                    self.ctx.get_session(session_id)
                
                return render_template('index.html', 
                                     version=prog_version,
                                     session_id=session_id,
                                     language_options=self.language_options,
                                     tts_engine_options=self.get_tts_engine_options(),
                                     device_options=self.device_options,
                                     output_format_options=self.output_format_options,
                                     voice_options=self.get_voice_options(session_id),
                                     custom_model_options=self.get_custom_model_options(session_id),
                                     fine_tuned_options=self.get_fine_tuned_options(session_id),
                                     audiobook_options=self.get_audiobook_options(session_id),
                                     xtts_params=self.get_xtts_params(),
                                     bark_params=self.get_bark_params())
            except Exception as e:
                return f"Error loading interface: {e}", 500
        
        @self.app.route('/upload/ebook', methods=['POST'])
        def upload_ebook():
            """Handle ebook file upload"""
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not self.allowed_ebook_file(file.filename):
                return jsonify({'error': 'Invalid file format'}), 400
            
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(tmp_dir, 'uploads', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                session['ebook_path'] = filepath
                session['ebook_filename'] = filename
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'path': filepath
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/upload/voice', methods=['POST'])
        def upload_voice():
            """Handle voice file upload"""
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': 'No session found'}), 400
                
            ctx_session = self.ctx.get_session(session_id)
            
            # Check voice limit
            voice_options = self.get_voice_options(session_id)
            if len([v for v in voice_options if not v.get('builtin', False)]) >= max_custom_voices:
                return jsonify({'error': f'Maximum {max_custom_voices} custom voices allowed'}), 400
            
            if not self.allowed_voice_file(file.filename):
                return jsonify({'error': 'Invalid voice file format'}), 400
            
            try:
                filename = secure_filename(file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                file.save(temp_path)
                
                # Extract voice using VoiceExtractor
                voice_name = os.path.splitext(filename)[0].replace('&', 'And')
                voice_name = get_sanitized(voice_name)
                
                extractor = VoiceExtractor(ctx_session, temp_path, voice_name)
                status, msg = extractor.extract_voice()
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if status:
                    final_voice_file = os.path.join(ctx_session['voice_dir'], f'{voice_name}_24000.wav')
                    ctx_session['voice'] = final_voice_file
                    
                    return jsonify({
                        'success': True,
                        'message': f'Voice {voice_name} added successfully',
                        'voice_path': final_voice_file,
                        'voice_name': voice_name,
                        'voice_options': self.get_voice_options(session_id)
                    })
                else:
                    return jsonify({'error': f'Voice extraction failed: {msg}'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/upload/custom_model', methods=['POST'])
        def upload_custom_model():
            """Handle custom model file upload"""
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': 'No session found'}), 400
                
            ctx_session = self.ctx.get_session(session_id)
            
            if not file.filename.lower().endswith('.zip'):
                return jsonify({'error': 'Only .zip files are allowed for custom models'}), 400
            
            try:
                filename = secure_filename(file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                file.save(temp_path)
                
                # Extract and validate custom model
                model_name = os.path.splitext(filename)[0]
                model_dir = os.path.join(ctx_session['custom_model_dir'], model_name)
                
                # Extract the zip file
                import zipfile
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(model_dir)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Validate model files
                required_files = ['config.json', 'model.pth', 'vocab.json']
                missing_files = []
                for req_file in required_files:
                    if not any(os.path.exists(os.path.join(root, req_file)) 
                             for root, dirs, files in os.walk(model_dir)):
                        missing_files.append(req_file)
                
                if missing_files:
                    # Clean up invalid model
                    shutil.rmtree(model_dir, ignore_errors=True)
                    return jsonify({'error': f'Invalid model: missing files {missing_files}'}), 400
                
                ctx_session['custom_model'] = model_dir
                
                return jsonify({
                    'success': True,
                    'message': f'Custom model {model_name} uploaded successfully',
                    'model_path': model_dir,
                    'model_name': model_name,
                    'custom_model_options': self.get_custom_model_options(session_id)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
        @self.app.route('/upload/directory', methods=['POST'])
        def upload_directory():
            """Handle directory upload for batch processing"""
            if 'files' not in request.files:
                return jsonify({'error': 'No files provided'}), 400
            
            files = request.files.getlist('files')
            if not files:
                return jsonify({'error': 'No files selected'}), 400
                
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': 'No session found'}), 400
                
            ctx_session = self.ctx.get_session(session_id)
            
            try:
                ebook_files = []
                upload_dir = os.path.join(tmp_dir, 'batch_uploads', session_id)
                os.makedirs(upload_dir, exist_ok=True)
                
                for file in files:
                    if file.filename and self.allowed_ebook_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(upload_dir, filename)
                        file.save(filepath)
                        ebook_files.append(filepath)
                
                if not ebook_files:
                    return jsonify({'error': 'No valid ebook files found'}), 400
                
                ctx_session['ebook_list'] = ebook_files
                ctx_session['ebook_mode'] = 'directory'
                
                return jsonify({
                    'success': True,
                    'message': f'Uploaded {len(ebook_files)} ebook files',
                    'file_count': len(ebook_files),
                    'files': [os.path.basename(f) for f in ebook_files]
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/upload/custom_model', methods=['POST'])
        def upload_custom_model():
            """Handle custom model upload"""
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith('.zip'):
                return jsonify({'error': 'Only ZIP files are allowed'}), 400
            
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(tmp_dir, 'models', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                # Extract and validate the model
                model_info = extract_custom_model(filepath, self.ctx)
                
                session['custom_model_path'] = filepath
                session['custom_model_filename'] = filename
                session['custom_model_info'] = model_info
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'path': filepath,
                    'model_info': model_info
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/convert', methods=['POST'])
        def start_conversion():
            """Start the ebook conversion process"""
            try:
                # Get conversion parameters from form
                params = self.get_conversion_params()
                
                # Create a unique session ID for this conversion
                conversion_id = str(uuid.uuid4())
                
                # Start conversion in a separate thread
                thread = threading.Thread(
                    target=self.run_conversion,
                    args=(conversion_id, params)
                )
                thread.daemon = True
                thread.start()
                
                self.conversion_threads[conversion_id] = thread
                
                return jsonify({
                    'success': True,
                    'conversion_id': conversion_id
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/download/<conversion_id>')
        def download_audiobook(conversion_id):
            """Download the generated audiobook"""
            try:
                # Get the output file path from session or database
                output_path = session.get(f'output_path_{conversion_id}')
                if not output_path or not os.path.exists(output_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(output_path, as_attachment=True)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/preview/voice')
        def preview_voice():
            """Preview uploaded voice file"""
            voice_path = session.get('voice_path')
            if not voice_path or not os.path.exists(voice_path):
                return jsonify({'error': 'Voice file not found'}), 404
            
            return send_file(voice_path)
        
        @self.app.route('/voices/list')
        def list_voices():
            """List available voices"""
            voices = []
            voices_directory = os.path.join(os.getcwd(), 'voices')
            if os.path.exists(voices_directory):
                for file in os.listdir(voices_directory):
                    if any(file.lower().endswith(ext) for ext in voice_formats):
                        voices.append({
                            'name': file,
                            'path': os.path.join(voices_directory, file)
                        })
            return jsonify({'voices': voices})
        
        @self.app.route('/models/list')
        def list_models():
            """List available custom models"""
            models = []
            models_directory = os.path.join(os.getcwd(), 'models')
            if os.path.exists(models_directory):
                for file in os.listdir(models_directory):
                    if file.endswith('.zip'):
                        models.append({
                            'name': file,
                            'path': os.path.join(models_directory, file)
                        })
            return jsonify({'models': models})
    
    def setup_socket_handlers(self):
        """Setup SocketIO event handlers for real-time communication"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            emit('connected', {'status': 'Connected to ebook2audiobook'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print('Client disconnected')
        
        @self.socketio.on('join_conversion')
        def handle_join_conversion(data):
            """Join a conversion room for real-time updates"""
            conversion_id = data.get('conversion_id')
            if conversion_id:
                join_room(conversion_id)
    
    def get_conversion_params(self):
        """Extract conversion parameters from request"""
        data = request.get_json() or request.form
        
        params = {
            'ebook': session.get('ebook_path'),
            'language': data.get('language', default_language_code),
            'voice': session.get('voice_path'),
            'device': data.get('device', default_device),
            'tts_engine': data.get('tts_engine'),
            'custom_model': session.get('custom_model_path'),
            'fine_tuned': data.get('fine_tuned'),
            'output_format': data.get('output_format', default_output_format),
            'temperature': data.get('temperature'),
            'repetition_penalty': data.get('repetition_penalty'),
            'top_k': data.get('top_k'),
            'top_p': data.get('top_p'),
            'speed': data.get('speed'),
            'enable_text_splitting': data.get('enable_text_splitting', False),
            'text_temp': data.get('text_temp'),
            'waveform_temp': data.get('waveform_temp'),
        }
        
        return params
    
    def run_conversion(self, conversion_id, params):
        """Run the conversion process in a background thread"""
        try:
            # Set up logging for this conversion
            log_buffer = Queue()
            self.log_buffers[conversion_id] = log_buffer
            
            # Emit start message
            self.socketio.emit('conversion_started', {
                'conversion_id': conversion_id,
                'message': 'Starting conversion...'
            }, room=conversion_id)
            
            # Call the actual conversion function
            # This would need to be adapted to use the actual conversion logic
            success, output_path = self.convert_ebook_with_progress(params, conversion_id)
            
            if success:
                session[f'output_path_{conversion_id}'] = output_path
                self.socketio.emit('conversion_complete', {
                    'conversion_id': conversion_id,
                    'success': True,
                    'output_path': output_path,
                    'download_url': f'/download/{conversion_id}'
                }, room=conversion_id)
            else:
                self.socketio.emit('conversion_error', {
                    'conversion_id': conversion_id,
                    'error': 'Conversion failed'
                }, room=conversion_id)
                
        except Exception as e:
            self.socketio.emit('conversion_error', {
                'conversion_id': conversion_id,
                'error': str(e)
            }, room=conversion_id)
        finally:
            # Clean up
            if conversion_id in self.conversion_threads:
                del self.conversion_threads[conversion_id]
            if conversion_id in self.log_buffers:
                del self.log_buffers[conversion_id]
    
    def convert_ebook_with_progress(self, params, conversion_id):
        """Convert ebook with progress updates"""
        try:
            # This is a placeholder - would need to integrate with actual conversion
            for i in range(0, 101, 10):
                self.socketio.emit('conversion_progress', {
                    'conversion_id': conversion_id,
                    'progress': i,
                    'message': f'Converting... {i}%'
                }, room=conversion_id)
                time.sleep(1)  # Simulate work
            
            return True, '/path/to/output/file.mp3'
        except Exception as e:
            return False, None
    
    def get_language_options(self):
        """Get list of available languages"""
        return [
            {
                'code': lang,
                'name': f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name']
            }
            for lang, details in language_mapping.items()
        ]
    
    def get_device_options(self):
        """Get list of available devices"""
        return [
            {'value': 'cpu', 'label': 'CPU'},
            {'value': 'cuda', 'label': 'GPU'},
            {'value': 'mps', 'label': 'MPS'}
        ]
    
    def get_output_format_options(self):
        """Get list of available output formats"""
        return [
            {'value': fmt, 'label': fmt.upper()}
            for fmt in output_formats
        ]
    
    def get_tts_engine_options(self, language=None):
        """Get list of available TTS engines"""
        if language:
            compatible_engines = get_compatible_tts_engines(language)
        else:
            compatible_engines = list(TTS_ENGINES.values())
        
        engines_with_ratings = []
        for engine in compatible_engines:
            rating = default_engine_settings.get(engine, {}).get('rating', {})
            engines_with_ratings.append({
                'value': engine,
                'label': engine,
                'rating': self.format_engine_rating(rating)
            })
        
        return engines_with_ratings
    
    def format_engine_rating(self, rating):
        """Format engine rating display"""
        if not rating:
            return ""
        
        def yellow_stars(n):
            return "★" * n
        
        def color_box(value, label):
            if value <= 4:
                color = "#4CAF50"  # Green = low
            elif value <= 8:
                color = "#FF9800"  # Orange = medium
            else:
                color = "#F44336"  # Red = high
            return f'<span style="background:{color};color:white;padding:1px 5px;border-radius:3px;font-size:11px">{value} GB</span>'
        
        return f"""
        <div style="font-size:12px; display:inline; gap:10px;">
            <span><b>GPU VRAM:</b> {color_box(rating.get("GPU VRAM", 0), "GPU VRAM")}</span>
            <span><b>CPU:</b> {yellow_stars(rating.get("CPU", 0))}</span>
            <span><b>RAM:</b> {color_box(rating.get("RAM", 0), "RAM")}</span>
            <span><b>Realism:</b> {yellow_stars(rating.get("Realism", 0))}</span>
        </div>
        """
    
    def get_voice_options(self, session_id):
        """Get list of available voices for session"""
        ctx_session = self.ctx.get_session(session_id)
        voices = []
        
        # Add builtin voices for each engine
        for engine, settings in default_engine_settings.items():
            if 'voices' in settings:
                for voice_name, voice_path in settings['voices'].items():
                    voices.append({
                        'value': voice_path,
                        'label': voice_name,
                        'builtin': True,
                        'engine': engine
                    })
        
        # Add custom voices from session directory
        voice_dir = ctx_session.get('voice_dir')
        if voice_dir and os.path.exists(voice_dir):
            for file in os.listdir(voice_dir):
                if file.endswith('_24000.wav'):
                    voice_name = file.replace('_24000.wav', '')
                    voice_path = os.path.join(voice_dir, file)
                    voices.append({
                        'value': voice_path,
                        'label': voice_name,
                        'builtin': False,
                        'engine': 'custom'
                    })
        
        return voices
    
    def get_custom_model_options(self, session_id):
        """Get list of available custom models for session"""
        ctx_session = self.ctx.get_session(session_id)
        models = []
        
        model_dir = ctx_session.get('custom_model_dir')
        if model_dir and os.path.exists(model_dir):
            for item in os.listdir(model_dir):
                item_path = os.path.join(model_dir, item)
                if os.path.isdir(item_path):
                    # Check if it's a valid model directory
                    config_path = os.path.join(item_path, 'config.json')
                    if os.path.exists(config_path):
                        models.append({
                            'value': item_path,
                            'label': item,
                            'path': item_path
                        })
        
        return models
    
    def get_fine_tuned_options(self, session_id, tts_engine=None):
        """Get list of fine-tuned models for TTS engine"""
        if not tts_engine:
            ctx_session = self.ctx.get_session(session_id)
            tts_engine = ctx_session.get('tts_engine', TTS_ENGINES['XTTSv2'])
        
        presets = []
        
        # Get presets for the selected engine
        engine_settings = default_engine_settings.get(tts_engine, {})
        if 'presets' in engine_settings:
            for preset_name, preset_path in engine_settings['presets'].items():
                presets.append({
                    'value': preset_path,
                    'label': preset_name,
                    'engine': tts_engine
                })
        
        return presets
    
    def get_audiobook_options(self, session_id):
        """Get list of generated audiobooks for session"""
        ctx_session = self.ctx.get_session(session_id)
        audiobooks = []
        
        audiobook_dir = ctx_session.get('audiobook_dir', audiobooks_dir)
        if audiobook_dir and os.path.exists(audiobook_dir):
            for item in os.listdir(audiobook_dir):
                item_path = os.path.join(audiobook_dir, item)
                if os.path.isfile(item_path) and any(item.lower().endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac']):
                    audiobooks.append({
                        'value': item_path,
                        'label': item,
                        'path': item_path,
                        'size': os.path.getsize(item_path)
                    })
                elif os.path.isdir(item_path):
                    # Directory of audio files
                    audiobooks.append({
                        'value': item_path,
                        'label': item,
                        'path': item_path,
                        'type': 'directory'
                    })
        
        return audiobooks
    
    def get_xtts_params(self):
        """Get XTTS parameter defaults"""
        xtts_settings = default_engine_settings.get(TTS_ENGINES['XTTSv2'], {})
        return {
            'temperature': {
                'min': 0.1, 'max': 10.0, 'step': 0.1,
                'value': float(xtts_settings.get('temperature', 0.7)),
                'info': 'Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone.'
            },
            'repetition_penalty': {
                'min': 1.0, 'max': 10.0, 'step': 0.1,
                'value': float(xtts_settings.get('repetition_penalty', 5.0)),
                'info': 'Penalizes repeated phrases. Higher values reduce repetition.'
            },
            'top_k': {
                'min': 10, 'max': 100, 'step': 1,
                'value': int(xtts_settings.get('top_k', 50)),
                'info': 'Lower values restrict outputs to more likely words and increase speed.'
            },
            'top_p': {
                'min': 0.1, 'max': 1.0, 'step': 0.01,
                'value': float(xtts_settings.get('top_p', 0.8)),
                'info': 'Controls cumulative probability for word selection. Lower values make output more predictable.'
            },
            'speed': {
                'min': 0.5, 'max': 3.0, 'step': 0.1,
                'value': float(xtts_settings.get('speed', 1.0)),
                'info': 'Adjusts how fast the narrator will speak.'
            }
        }
    
    def get_bark_params(self):
        """Get BARK parameter defaults"""
        bark_settings = default_engine_settings.get(TTS_ENGINES['BARK'], {})
        return {
            'text_temp': {
                'min': 0.0, 'max': 1.0, 'step': 0.01,
                'value': float(bark_settings.get('text_temp', 0.7)),
                'info': 'Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
            },
            'waveform_temp': {
                'min': 0.0, 'max': 1.0, 'step': 0.01,
                'value': float(bark_settings.get('waveform_temp', 0.7)),
                'info': 'Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
            }
        }
            'device': data.get('device', default_device),
            'tts_engine': data.get('tts_engine'),
            'custom_model': session.get('custom_model_path'),
            'fine_tuned': data.get('fine_tuned'),
            'output_format': data.get('output_format', default_output_format),
            'temperature': data.get('temperature'),
            'length_penalty': data.get('length_penalty'),
            'num_beams': data.get('num_beams'),
            'repetition_penalty': data.get('repetition_penalty'),
            'top_k': data.get('top_k'),
            'top_p': data.get('top_p'),
            'speed': data.get('speed'),
            'enable_text_splitting': data.get('enable_text_splitting', False),
            'text_temp': data.get('text_temp'),
            'waveform_temp': data.get('waveform_temp'),
            'output_dir': data.get('output_dir') or audiobooks_gradio_dir,
            'session': data.get('session_id') or self.ctx.get_session_id(),
            'is_gui_process': True,
            'audiobooks_dir': audiobooks_gradio_dir
        }
        
        # Clean up None values
        return {k: v for k, v in params.items() if v is not None}
    
    def run_conversion(self, conversion_id, params):
        """Run the conversion process in a separate thread"""
        try:
            # Emit conversion start
            self.socketio.emit('conversion_start', 
                             {'conversion_id': conversion_id}, 
                             room=conversion_id)
            
            # Setup progress callback
            def progress_callback(message, percentage=None):
                self.socketio.emit('conversion_progress', {
                    'conversion_id': conversion_id,
                    'message': message,
                    'percentage': percentage
                }, room=conversion_id)
            
            # Run conversion
            progress_status, passed = convert_ebook(params, self.ctx)
            
            if passed:
                # Store output path for download
                session[f'output_path_{conversion_id}'] = progress_status
                
                self.socketio.emit('conversion_complete', {
                    'conversion_id': conversion_id,
                    'success': True,
                    'output_path': progress_status
                }, room=conversion_id)
            else:
                self.socketio.emit('conversion_complete', {
                    'conversion_id': conversion_id,
                    'success': False,
                    'error': progress_status
                }, room=conversion_id)
                
        except Exception as e:
            self.socketio.emit('conversion_error', {
                'conversion_id': conversion_id,
                'error': str(e)
            }, room=conversion_id)
        finally:
            # Clean up thread reference
            if conversion_id in self.conversion_threads:
                del self.conversion_threads[conversion_id]
    
    def allowed_ebook_file(self, filename):
        """Check if uploaded file is an allowed ebook format"""
        return any(filename.lower().endswith(ext) for ext in ebook_formats)
    
    def allowed_voice_file(self, filename):
        """Check if uploaded file is an allowed voice format"""
        return any(filename.lower().endswith(ext) for ext in voice_formats)
    
    def get_language_options(self):
        """Get available language options"""
        return [
            {
                'code': lang,
                'name': f"{details['name']} - {details['native_name']}" 
                       if details['name'] != details['native_name'] 
                       else details['name']
            }
            for lang, details in language_mapping.items()
        ]
    
    def get_tts_engine_options(self):
        """Get available TTS engine options"""
        return [
            {'value': key, 'label': key} 
            for key in TTS_ENGINES.keys()
        ]
    
    def get_device_options(self):
        """Get available device options"""
        return [
            {'value': 'cpu', 'label': 'CPU'},
            {'value': 'cuda', 'label': 'GPU'},
            {'value': 'mps', 'label': 'MPS'}
        ]
    
    def get_output_format_options(self):
        """Get available output format options"""
        return [
            {'value': fmt, 'label': fmt.upper()} 
            for fmt in output_formats
        ]
    
    def run(self, host='0.0.0.0', port=7860, debug=False):
        """Run the Flask application"""
        try:
            all_ips = get_all_ip_addresses()
            print(f'IPs available for connection:\n{all_ips}')
            print(f'Note: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect.')
            
            # Handle public sharing
            if self.is_gui_shared:
                self.setup_public_sharing(host, port)
            
            # Disable reloader when running from main app to prevent port conflicts
            use_reloader = debug and not self.is_gui_process
            
            self.socketio.run(self.app, 
                            host=host, 
                            port=port, 
                            debug=debug,
                            use_reloader=use_reloader,
                            allow_unsafe_werkzeug=True)
        except Exception as e:
            print(f'Error starting Flask server: {e}')
            raise
    
    def setup_public_sharing(self, host, port):
        """Setup public sharing using ngrok or similar"""
        try:
            # Try to import and use pyngrok for public sharing
            from pyngrok import ngrok
            
            # Start ngrok tunnel
            public_url = ngrok.connect(port)
            print(f'Public URL: {public_url}')
            print(f'Share this URL to access the interface publicly')
            
        except ImportError:
            print('Warning: pyngrok not installed. Public sharing not available.')
            print('To enable public sharing, install pyngrok: pip install pyngrok')
        except Exception as e:
            print(f'Warning: Could not setup public sharing: {e}')


def web_interface_flask(args, ctx):
    """Flask-based web interface replacement for Gradio"""
    interface = FlaskInterface(args, ctx)
    interface.run(
        host=interface_host,
        port=interface_port,
        debug=debug_mode
    )