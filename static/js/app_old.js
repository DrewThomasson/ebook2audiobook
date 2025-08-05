/**
 * JavaScript for ebook2audiobook Flask interface
 * Complete functionality to match original Gradio interface
 */

class Ebook2AudiobookApp {
    constructor() {
        this.socket = null;
        this.currentConversionId = null;
        this.uploadedFiles = {
            ebook: null,
            voice: null,
            customModel: null
        };
        
        this.init();
    }
    
    init() {
        this.initSocketIO();
        this.setupEventListeners();
        
        // Load initial data
        Promise.allSettled([
            this.loadAvailableVoices(),
            this.loadAvailableModels(),
            this.loadTTSEngines(),
            this.loadFineTunedModels(),
            this.loadAudiobooks()
        ]).finally(() => {
            setTimeout(() => {
                this.hideGlassMask();
            }, 500);
        });
        
        // Fallback: hide glass mask after 3 seconds no matter what
        setTimeout(() => {
            this.hideGlassMask();
        }, 3000);
    }
    
    initSocketIO() {
        try {
            if (typeof io === 'undefined') {
                console.warn('Socket.IO not available, continuing without real-time updates');
                return;
            }
            
            this.socket = io({
                timeout: 10000,
                transports: ['websocket', 'polling']
            });
            
            this.socket.on('connect', () => {
                console.log('Connected to server');
            });
            
            this.socket.on('connect_error', (error) => {
                console.warn('Socket connection error:', error);
            });
            
            this.socket.on('conversion_start', (data) => {
                this.handleConversionStart(data);
            });
            
            this.socket.on('conversion_progress', (data) => {
                this.handleConversionProgress(data);
            });
            
            this.socket.on('conversion_complete', (data) => {
                this.handleConversionComplete(data);
            });
            
            this.socket.on('conversion_error', (data) => {
                this.handleConversionError(data);
            });
        } catch (error) {
            console.error('Failed to initialize SocketIO:', error);
        }
    }
    
    setupEventListeners() {
        // File upload handlers
        this.setupFileUpload('ebook_file', 'ebook', this.handleEbookUpload.bind(this));
        this.setupFileUpload('voice_file', 'voice', this.handleVoiceUpload.bind(this));
        this.setupFileUpload('custom_model_file', 'customModel', this.handleCustomModelUpload.bind(this));
        
        // Form submission
        const form = document.getElementById('conversionForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }
        
        // Convert button
        const convertBtn = document.getElementById('convert_btn');
        if (convertBtn) {
            convertBtn.addEventListener('click', this.handleFormSubmit.bind(this));
        }
        
        // Input mode switching
        const inputModeRadios = document.getElementsByName('input_mode');
        if (inputModeRadios) {
            inputModeRadios.forEach(radio => {
                radio.addEventListener('change', this.handleInputModeChange.bind(this));
            });
        }
        
        // Voice list selection
        const voiceList = document.getElementById('voice_list');
        if (voiceList) {
            voiceList.addEventListener('change', this.handleVoiceSelection.bind(this));
        }
        
        // Custom model list selection
        const modelList = document.getElementById('custom_model_list');
        if (modelList) {
            modelList.addEventListener('change', this.handleCustomModelSelection.bind(this));
        }
        
        // TTS engine change
        const ttsEngine = document.getElementById('tts_engine');
        if (ttsEngine) {
            ttsEngine.addEventListener('change', this.handleTTSEngineChange.bind(this));
        }
        
        // Language change
        const language = document.getElementById('language');
        if (language) {
            language.addEventListener('change', this.handleLanguageChange.bind(this));
        }
        
        // Audiobook list selection
        const audiobookList = document.getElementById('audiobook_list');
        if (audiobookList) {
            audiobookList.addEventListener('change', this.handleAudiobookSelection.bind(this));
        }
        
        // Parameter sliders
        this.setupParameterSliders();
        
        // Delete buttons
        this.setupDeleteButtons();
    }
    
    setupFileUpload(inputId, fileType, callback) {
        const input = document.getElementById(inputId);
        const uploadArea = document.getElementById(`${fileType === 'ebook' ? 'ebook' : 
                                                   fileType === 'voice' ? 'voice' : 'model'}_upload_area`);
        
        if (!input || !uploadArea) {
            console.warn(`Missing elements for file upload: ${inputId}`);
            return;
        }
        
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                callback(e.target.files[0]);
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                callback(e.dataTransfer.files[0]);
            }
        });
    }
    
    async handleEbookUpload(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/ebook', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.ebook = result;
                this.showFilePreview('ebook', result.filename, file.size);
                this.showSuccess(`Ebook uploaded: ${result.filename}`);
                this.enableConvertButton();
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to upload ebook: ' + error.message);
        }
    }
    
    async handleVoiceUpload(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/voice', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.voice = result;
                this.showFilePreview('voice', result.filename, file.size);
                this.showSuccess(`Voice file uploaded: ${result.voice_name}`);
                this.loadAvailableVoices(); // Refresh voice list
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to upload voice file: ' + error.message);
        }
    }
    
    async handleCustomModelUpload(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/custom_model', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.customModel = result;
                this.showFilePreview('model', result.filename, file.size);
                this.showSuccess(`Custom model uploaded: ${result.model_name}`);
                this.loadAvailableModels(); // Refresh model list
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to upload custom model: ' + error.message);
        }
    }
    
    showFilePreview(type, filename, size) {
        const container = document.getElementById(`${type}_filename`);
        container.innerHTML = `
            <div class="file-preview">
                <div class="file-info">
                    <i class="fas fa-file file-icon"></i>
                    <span class="file-name">${filename}</span>
                    <span class="file-size">(${this.formatFileSize(size)})</span>
                </div>
                <button type="button" class="remove-file" onclick="app.removeFile('${type}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        container.classList.remove('d-none');
        
        const uploadArea = document.getElementById(`${type === 'model' ? 'model' : 
                                                   type === 'voice' ? 'voice' : 'ebook'}_upload_area`);
        uploadArea.classList.add('has-file');
    }
    
    removeFile(type) {
        this.uploadedFiles[type] = null;
        const container = document.getElementById(`${type}_filename`);
        container.classList.add('d-none');
        container.innerHTML = '';
        
        const uploadArea = document.getElementById(`${type === 'model' ? 'model' : 
                                                   type === 'voice' ? 'voice' : 'ebook'}_upload_area`);
        uploadArea.classList.remove('has-file');
        
        const input = document.getElementById(`${type === 'voice' ? 'voice' : 
                                              type === 'model' ? 'custom_model' : 'ebook'}_file`);
        input.value = '';
        
        if (type === 'voice') {
            document.getElementById('voice_preview').classList.add('d-none');
        }
    }
    
    async loadAvailableVoices() {
        try {
            const response = await fetch('/api/voices');
            const result = await response.json();
            
            const select = document.getElementById('voice_list');
            if (select && result.voices) {
                select.innerHTML = '<option value="">Select from available voices...</option>';
                result.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.value;
                    option.textContent = voice.label + (voice.builtin ? ' (built-in)' : ' (custom)');
                    option.dataset.builtin = voice.builtin;
                    option.dataset.engine = voice.engine;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.warn('Failed to load voices:', error);
        }
    }
    
    async loadAvailableModels() {
        try {
            const response = await fetch('/api/custom_models');
            const result = await response.json();
            
            const select = document.getElementById('custom_model_list');
            if (select && result.custom_models) {
                select.innerHTML = '<option value="">Select from uploaded models...</option>';
                result.custom_models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.value;
                    option.textContent = model.label;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.warn('Failed to load custom models:', error);
        }
    }
    
    async loadTTSEngines() {
        try {
            const response = await fetch('/api/tts_engines');
            const result = await response.json();
            
            const select = document.getElementById('tts_engine');
            if (select && result.engines) {
                select.innerHTML = '';
                result.engines.forEach(engine => {
                    const option = document.createElement('option');
                    option.value = engine.value;
                    option.textContent = engine.label;
                    option.dataset.rating = JSON.stringify(engine.rating);
                    select.appendChild(option);
                });
                
                // Update rating display for first engine
                if (result.engines.length > 0) {
                    this.updateTTSRating(result.engines[0].rating);
                    this.handleTTSEngineChange({target: {value: result.engines[0].value}});
                }
            }
        } catch (error) {
            console.warn('Failed to load TTS engines:', error);
        }
    }
    
    async loadFineTunedModels() {
        try {
            const response = await fetch('/api/fine_tuned_models');
            const result = await response.json();
            
            const select = document.getElementById('fine_tuned');
            if (select && result.fine_tuned_models) {
                select.innerHTML = '<option value="">Select preset...</option>';
                result.fine_tuned_models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.value;
                    option.textContent = model.label;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.warn('Failed to load fine-tuned models:', error);
        }
    }
    
    async loadAudiobooks() {
        try {
            const response = await fetch('/api/audiobooks');
            const result = await response.json();
            
            const select = document.getElementById('audiobook_list');
            if (select && result.audiobooks) {
                select.innerHTML = '<option value="">Select audiobook...</option>';
                result.audiobooks.forEach(audiobook => {
                    const option = document.createElement('option');
                    option.value = audiobook.value;
                    option.textContent = audiobook.label;
                    select.appendChild(option);
                });
                
                // Show audiobook section if there are audiobooks
                const audiobookSection = document.getElementById('audiobook_section');
                if (audiobookSection) {
                    audiobookSection.classList.toggle('d-none', result.audiobooks.length === 0);
                }
            }
        } catch (error) {
            console.warn('Failed to load audiobooks:', error);
        }
    }
    
    handleInputModeChange(e) {
        const isDirectory = e.target.value === 'directory';
        // Update UI for directory vs file mode
        // This would be implemented based on the specific requirements
    }
    
    handleVoiceSelection(event) {
        const selectedPath = event.target.value;
        const selectedOption = event.target.options[event.target.selectedIndex];
        
        if (selectedPath) {
            // Show voice preview
            this.showVoicePreview(selectedPath);
            
            // Show delete button for custom voices
            const deleteBtn = document.getElementById('voice_delete_btn');
            if (deleteBtn) {
                const isBuiltin = selectedOption.dataset.builtin === 'true';
                deleteBtn.classList.toggle('d-none', isBuiltin);
            }
        } else {
            // Hide preview and delete button
            const preview = document.getElementById('voice_preview');
            if (preview) preview.classList.add('d-none');
            const deleteBtn = document.getElementById('voice_delete_btn');
            if (deleteBtn) deleteBtn.classList.add('d-none');
        }
    }
    
    handleCustomModelSelection(event) {
        const selectedPath = event.target.value;
        
        const deleteBtn = document.getElementById('model_delete_btn');
        if (deleteBtn) {
            deleteBtn.classList.toggle('d-none', !selectedPath);
        }
    }
    
    handleLanguageChange(event) {
        // Reload TTS engines for new language
        this.loadTTSEngines();
    }
    
    handleTTSEngineChange(event) {
        const selectedEngine = event.target.value;
        const selectedOption = event.target.options[event.target.selectedIndex];
        
        // Update rating display
        if (selectedOption && selectedOption.dataset.rating) {
            const rating = JSON.parse(selectedOption.dataset.rating);
            this.updateTTSRating(rating);
        }
        
        // Reload fine-tuned models for this engine
        this.loadFineTunedModels();
        
        // Show/hide parameter tabs based on engine
        this.updateParameterTabs(selectedEngine);
    }
    
    handleAudiobookSelection(event) {
        const selectedPath = event.target.value;
        
        if (selectedPath) {
            // Show audiobook player
            this.showAudiobookPlayer(selectedPath);
            
            // Show delete button
            const deleteBtn = document.getElementById('audiobook_delete_btn');
            if (deleteBtn) {
                deleteBtn.classList.remove('d-none');
            }
        } else {
            // Hide player and delete button
            const player = document.getElementById('audiobook_player');
            if (player) player.classList.add('d-none');
            const deleteBtn = document.getElementById('audiobook_delete_btn');
            if (deleteBtn) deleteBtn.classList.add('d-none');
        }
    }
    
    updateTTSRating(rating) {
        const ratingDiv = document.getElementById('tts_rating');
        if (ratingDiv && rating) {
            const gpuVramColor = rating['GPU VRAM'] <= 4 ? '#4CAF50' : rating['GPU VRAM'] <= 8 ? '#FF9800' : '#F44336';
            const ramColor = rating['RAM'] <= 4 ? '#4CAF50' : rating['RAM'] <= 8 ? '#FF9800' : '#F44336';
            const stars = (n) => '★'.repeat(n || 0);
            
            ratingDiv.innerHTML = `
                <div style="font-size:12px; display:flex; gap:10px; flex-wrap:wrap;">
                    <span><b>GPU VRAM:</b> <span style="background:${gpuVramColor};color:white;padding:1px 5px;border-radius:3px;">${rating['GPU VRAM'] || 0} GB</span></span>
                    <span><b>CPU:</b> <span style="color:#FFD700;">${stars(rating['CPU'])}</span></span>
                    <span><b>RAM:</b> <span style="background:${ramColor};color:white;padding:1px 5px;border-radius:3px;">${rating['RAM'] || 0} GB</span></span>
                    <span><b>Realism:</b> <span style="color:#FFD700;">${stars(rating['Realism'])}</span></span>
                </div>
            `;
        }
    }
    
    updateParameterTabs(engine) {
        const xttsTab = document.getElementById('xtts-tab');
        const barkTab = document.getElementById('bark-tab');
        
        if (xttsTab && barkTab) {
            const isXTTS = engine && engine.includes('XTTSv2');
            const isBark = engine && engine.includes('BARK');
            
            xttsTab.style.display = isXTTS ? 'block' : 'none';
            barkTab.style.display = isBark ? 'block' : 'none';
        }
    }
    
    showVoicePreview(path) {
        const preview = document.getElementById('voice_preview');
        const source = document.getElementById('voice_audio_source');
        if (preview && source) {
            source.src = `/api/voices/${encodeURIComponent(path)}/preview`;
            preview.classList.remove('d-none');
        }
    }
    
    showAudiobookPlayer(path) {
        const player = document.getElementById('audiobook_player');
        const source = document.getElementById('audiobook_audio_source');
        if (player && source) {
            source.src = `/api/audiobooks/${encodeURIComponent(path)}/preview`;
            player.classList.remove('d-none');
            player.load();
        }
    }
    
    setupDeleteButtons() {
        // Voice delete button
        const voiceDeleteBtn = document.getElementById('voice_delete_btn');
        if (voiceDeleteBtn) {
            voiceDeleteBtn.addEventListener('click', () => {
                const voiceList = document.getElementById('voice_list');
                if (voiceList && voiceList.value) {
                    this.deleteVoice(voiceList.value);
                }
            });
        }
        
        // Model delete button
        const modelDeleteBtn = document.getElementById('model_delete_btn');
        if (modelDeleteBtn) {
            modelDeleteBtn.addEventListener('click', () => {
                const modelList = document.getElementById('custom_model_list');
                if (modelList && modelList.value) {
                    this.deleteCustomModel(modelList.value);
                }
            });
        }
        
        // Audiobook delete button
        const audiobookDeleteBtn = document.getElementById('audiobook_delete_btn');
        if (audiobookDeleteBtn) {
            audiobookDeleteBtn.addEventListener('click', () => {
                const audiobookList = document.getElementById('audiobook_list');
                if (audiobookList && audiobookList.value) {
                    this.deleteAudiobook(audiobookList.value);
                }
            });
        }
    }
    
    async deleteVoice(voicePath) {
        if (!confirm('Are you sure you want to delete this voice?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/voices/${encodeURIComponent(voicePath)}/delete`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.loadAvailableVoices(); // Refresh voice list
                
                // Clear selection
                document.getElementById('voice_list').value = '';
                document.getElementById('voice_preview').classList.add('d-none');
                document.getElementById('voice_delete_btn').classList.add('d-none');
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to delete voice: ' + error.message);
        }
    }
    
    async deleteCustomModel(modelPath) {
        if (!confirm('Are you sure you want to delete this custom model?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/custom_models/${encodeURIComponent(modelPath)}/delete`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.loadAvailableModels(); // Refresh model list
                
                // Clear selection
                document.getElementById('custom_model_list').value = '';
                document.getElementById('model_delete_btn').classList.add('d-none');
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to delete custom model: ' + error.message);
        }
    }
    
    async deleteAudiobook(audiobookPath) {
        if (!confirm('Are you sure you want to delete this audiobook?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/audiobooks/${encodeURIComponent(audiobookPath)}/delete`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.loadAudiobooks(); // Refresh audiobook list
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Failed to delete audiobook: ' + error.message);
        }
    }
    
    setupParameterSliders() {
        // XTTS Parameter sliders
        this.setupSlider('temperature', 0.1, 10.0, 0.1, 0.7);
        this.setupSlider('repetition_penalty', 1.0, 10.0, 0.1, 5.0);
        this.setupSlider('top_k', 10, 100, 1, 50);
        this.setupSlider('top_p', 0.1, 1.0, 0.01, 0.8);
        this.setupSlider('speed', 0.5, 3.0, 0.1, 1.0);
        
        // BARK Parameter sliders
        this.setupSlider('text_temp', 0.0, 1.0, 0.01, 0.7);
        this.setupSlider('waveform_temp', 0.0, 1.0, 0.01, 0.7);
    }
    
    setupSlider(name, min, max, step, defaultValue) {
        const slider = document.getElementById(name);
        const valueDisplay = document.getElementById(`${name}_value`);
        
        if (slider) {
            slider.min = min;
            slider.max = max;
            slider.step = step;
            slider.value = defaultValue;
            
            if (valueDisplay) {
                valueDisplay.textContent = defaultValue;
            }
            
            slider.addEventListener('input', (e) => {
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value;
                }
            });
        }
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate required fields
        if (!this.uploadedFiles.ebook) {
            this.showError('Please upload an ebook file');
            return;
        }
        
        // Prepare form data
        const formData = this.getFormData();
        
        try {
            this.showProgress();
            this.disableForm();
            
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentConversionId = result.conversion_id;
                if (this.socket) {
                    this.socket.emit('join_conversion', { conversion_id: this.currentConversionId });
                }
                this.showSuccess('Conversion started successfully');
            } else {
                this.showError(result.error);
                this.enableForm();
                this.hideProgress();
            }
        } catch (error) {
            this.showError('Failed to start conversion: ' + error.message);
            this.enableForm();
            this.hideProgress();
        }
    }
    
    getFormData() {
        const form = document.getElementById('conversionForm');
        const formData = new FormData(form);
        const data = {};
        
        // Get all form values
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Add selected values from dropdowns
        const voiceList = document.getElementById('voice_list');
        if (voiceList && voiceList.value) {
            data.voice = voiceList.value;
        }
        
        const modelList = document.getElementById('custom_model_list');
        if (modelList && modelList.value) {
            data.custom_model = modelList.value;
        }
        
        return data;
    }
    
    showProgress() {
        const progressTextarea = document.getElementById('conversion_progress');
        if (progressTextarea) {
            progressTextarea.value = 'Starting conversion...\n';
            progressTextarea.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    hideProgress() {
        const progressTextarea = document.getElementById('conversion_progress');
        if (progressTextarea) {
            progressTextarea.value = '';
        }
    }
    
    disableForm() {
        const form = document.getElementById('conversionForm');
        if (form) {
            const inputs = form.querySelectorAll('input, select, button');
            inputs.forEach(input => input.disabled = true);
        }
    }
    
    enableForm() {
        const form = document.getElementById('conversionForm');
        if (form) {
            const inputs = form.querySelectorAll('input, select, button');
            inputs.forEach(input => input.disabled = false);
        }
    }
    
    enableConvertButton() {
        const convertBtn = document.getElementById('convert_btn');
        if (convertBtn) {
            convertBtn.disabled = false;
        }
    }
    
    handleConversionStart(data) {
        this.updateProgress('Conversion started');
    }
    
    handleConversionProgress(data) {
        const message = data.message || 'Processing...';
        this.updateProgress(message);
    }
    
    handleConversionComplete(data) {
        if (data.success) {
            this.updateProgress('Conversion completed successfully!');
            this.showSuccess('Conversion completed successfully');
            this.loadAudiobooks(); // Refresh audiobook list
        } else {
            this.showError(`Conversion failed: ${data.error}`);
            this.updateProgress(`Error: ${data.error}`);
        }
        
        this.enableForm();
    }
    
    handleConversionError(data) {
        this.showError(`Conversion error: ${data.error}`);
        this.updateProgress(`Error: ${data.error}`);
        this.enableForm();
    }
    
    updateProgress(message) {
        const progressTextarea = document.getElementById('conversion_progress');
        if (progressTextarea) {
            const timestamp = new Date().toLocaleTimeString();
            const logLine = `[${timestamp}] ${message}\n`;
            progressTextarea.value += logLine;
            progressTextarea.scrollTop = progressTextarea.scrollHeight;
        }
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showAlert(message, type) {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showGlassMask(message = 'Please wait...') {
        const mask = document.getElementById('glass-mask');
        if (mask) {
            mask.querySelector('div').textContent = message;
            mask.classList.remove('d-none');
        }
    }
    
    hideGlassMask() {
        const mask = document.getElementById('glass-mask');
        if (mask) {
            mask.classList.add('d-none');
        }
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new Ebook2AudiobookApp();
});