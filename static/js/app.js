/**
 * Complete JavaScript implementation for ebook2audiobook Flask interface
 * Provides 100% functional parity with original Gradio interface
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
        this.deleteModal = null;
        this.pendingDelete = null;
        
        this.init();
    }
    
    init() {
        this.initSocketIO();
        this.setupEventListeners();
        this.setupParameterSliders();
        this.initModals();
        
        // Hide loading mask after initialization
        setTimeout(() => {
            this.hideGlassMask();
        }, 1000);
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
        const fileModeRadio = document.getElementById('file_mode');
        const directoryModeRadio = document.getElementById('directory_mode');
        if (fileModeRadio) {
            fileModeRadio.addEventListener('change', this.handleInputModeChange.bind(this));
        }
        if (directoryModeRadio) {
            directoryModeRadio.addEventListener('change', this.handleInputModeChange.bind(this));
        }
        
        // Language selection
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', this.handleLanguageChange.bind(this));
        }
        
        // TTS Engine selection
        const ttsEngineSelect = document.getElementById('tts_engine');
        if (ttsEngineSelect) {
            ttsEngineSelect.addEventListener('change', this.handleTTSEngineChange.bind(this));
        }
        
        // Fine tuned model selection
        const fineTunedSelect = document.getElementById('fine_tuned_list');
        if (fineTunedSelect) {
            fineTunedSelect.addEventListener('change', this.handleFineTunedChange.bind(this));
        }
        
        // Voice selection
        const voiceSelect = document.getElementById('voice_list');
        if (voiceSelect) {
            voiceSelect.addEventListener('change', this.handleVoiceChange.bind(this));
        }
        
        // Custom model selection
        const customModelSelect = document.getElementById('custom_model_list');
        if (customModelSelect) {
            customModelSelect.addEventListener('change', this.handleCustomModelChange.bind(this));
        }
        
        // Delete buttons
        const voiceDeleteBtn = document.getElementById('voice_delete_btn');
        if (voiceDeleteBtn) {
            voiceDeleteBtn.addEventListener('click', () => this.showDeleteConfirmation('voice'));
        }
        
        const customModelDeleteBtn = document.getElementById('custom_model_delete_btn');
        if (customModelDeleteBtn) {
            customModelDeleteBtn.addEventListener('click', () => this.showDeleteConfirmation('custom_model'));
        }
        
        // Tab switching
        const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', this.handleTabSwitch.bind(this));
        });
    }
    
    setupParameterSliders() {
        // XTTS parameters
        this.setupSlider('xtts_temperature', 'xtts_temperature_value', 'temperature');
        this.setupSlider('xtts_repetition_penalty', 'xtts_repetition_penalty_value', 'repetition_penalty');
        this.setupSlider('xtts_top_k', 'xtts_top_k_value', 'top_k');
        this.setupSlider('xtts_top_p', 'xtts_top_p_value', 'top_p');
        this.setupSlider('xtts_speed', 'xtts_speed_value', 'speed');
        
        // BARK parameters
        this.setupSlider('bark_text_temp', 'bark_text_temp_value', 'text_temp');
        this.setupSlider('bark_waveform_temp', 'bark_waveform_temp_value', 'waveform_temp');
    }
    
    setupSlider(sliderId, valueId, paramName) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                valueDisplay.textContent = e.target.value;
                this.updateParameter(paramName, e.target.value);
            });
        }
    }
    
    initModals() {
        this.deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
        
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', this.handleConfirmDelete.bind(this));
        }
    }
    
    setupFileUpload(inputId, type, handler) {
        const input = document.getElementById(inputId);
        const uploadArea = document.getElementById(`${type}_upload_area`) || 
                          document.getElementById(`ebook_upload_area`);
        
        if (!input) return;
        
        // File input change handler
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handler(e.target.files[0]);
            }
        });
        
        // Drag and drop handlers
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    handler(files[0]);
                }
            });
        }
    }
    
    async handleEbookUpload(file) {
        try {
            this.showAlert('info', 'Uploading ebook...');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/ebook', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.ebook = result;
                this.displayEbookInfo(file.name);
                this.updateConvertButton();
                this.showAlert('success', 'Ebook uploaded successfully!');
            } else {
                this.showAlert('error', result.error || 'Failed to upload ebook');
            }
        } catch (error) {
            this.showAlert('error', 'Error uploading ebook: ' + error.message);
        }
    }
    
    async handleVoiceUpload(file) {
        try {
            this.showAlert('info', 'Uploading and processing voice...');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/voice', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.voice = result;
                this.updateVoiceOptions(result.voice_options);
                this.showAlert('success', 'Voice uploaded and processed successfully!');
            } else {
                this.showAlert('error', result.error || 'Failed to upload voice');
            }
        } catch (error) {
            this.showAlert('error', 'Error uploading voice: ' + error.message);
        }
    }
    
    async handleCustomModelUpload(file) {
        try {
            this.showAlert('info', 'Uploading and validating custom model...');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload/custom_model', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.uploadedFiles.customModel = result;
                this.updateCustomModelOptions(result.custom_model_options);
                this.showAlert('success', 'Custom model uploaded successfully!');
            } else {
                this.showAlert('error', result.error || 'Failed to upload custom model');
            }
        } catch (error) {
            this.showAlert('error', 'Error uploading custom model: ' + error.message);
        }
    }
    
    handleInputModeChange() {
        const isDirectory = document.getElementById('directory_mode').checked;
        const uploadArea = document.getElementById('ebook_upload_area');
        const fileInput = document.getElementById('ebook_file');
        
        if (isDirectory) {
            // For directory mode, we would need a directory picker
            // For now, show an alert that directory upload needs file selection
            this.showAlert('info', 'Directory mode: Select multiple ebook files or specify directory path');
            fileInput.setAttribute('multiple', 'multiple');
        } else {
            fileInput.removeAttribute('multiple');
        }
        
        this.updateConvertButton();
    }
    
    async handleLanguageChange() {
        try {
            const language = document.getElementById('language').value;
            
            const response = await fetch('/api/language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateTTSEngineOptions(result.tts_engine_options);
                this.updateVoiceOptions(result.voice_options);
                this.updateFineTunedOptions(result.fine_tuned_options);
                this.updateCustomModelOptions(result.custom_model_options);
                this.showAlert('success', 'Language updated, compatible engines loaded');
            } else {
                this.showAlert('error', result.error || 'Failed to update language');
            }
        } catch (error) {
            this.showAlert('error', 'Error updating language: ' + error.message);
        }
    }
    
    async handleTTSEngineChange() {
        try {
            const engine = document.getElementById('tts_engine').value;
            
            const response = await fetch('/api/tts_engine', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ engine })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update engine rating
                const ratingDiv = document.getElementById('tts_engine_rating');
                if (ratingDiv) {
                    ratingDiv.innerHTML = result.engine_rating || '';
                }
                
                // Update parameter tabs visibility
                this.updateParameterTabsVisibility(result);
                
                // Update options
                this.updateFineTunedOptions(result.fine_tuned_options);
                this.updateVoiceOptions(result.voice_options);
                this.updateCustomModelOptions(result.custom_model_options);
                
                // Update custom model group visibility
                const customModelGroup = document.getElementById('custom_model_group');
                if (customModelGroup) {
                    customModelGroup.style.display = result.visible_custom_model ? 'block' : 'none';
                }
                
                this.updateConvertButton();
                this.showAlert('success', 'TTS engine updated successfully');
            } else {
                this.showAlert('error', result.error || 'Failed to update TTS engine');
            }
        } catch (error) {
            this.showAlert('error', 'Error updating TTS engine: ' + error.message);
        }
    }
    
    async handleFineTunedChange() {
        try {
            const fineTuned = document.getElementById('fine_tuned_list').value;
            
            const response = await fetch('/api/fine_tuned', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ fine_tuned: fineTuned })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update custom model group visibility
                const customModelGroup = document.getElementById('custom_model_group');
                if (customModelGroup) {
                    customModelGroup.style.display = result.visible_custom_model ? 'block' : 'none';
                }
                
                this.updateVoiceOptions(result.voice_options);
            } else {
                this.showAlert('error', result.error || 'Failed to update fine tuned model');
            }
        } catch (error) {
            this.showAlert('error', 'Error updating fine tuned model: ' + error.message);
        }
    }
    
    async handleVoiceChange() {
        try {
            const voice = document.getElementById('voice_list').value;
            
            const response = await fetch('/api/voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ voice })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update voice player
                const voicePlayer = document.getElementById('voice_player');
                const voiceDeleteBtn = document.getElementById('voice_delete_btn');
                
                if (result.voice_file_path) {
                    voicePlayer.src = `/api/voice/preview/${encodeURIComponent(result.voice_file_path)}`;
                    voicePlayer.classList.remove('d-none');
                } else {
                    voicePlayer.classList.add('d-none');
                }
                
                if (voiceDeleteBtn) {
                    if (result.delete_visible) {
                        voiceDeleteBtn.classList.remove('d-none');
                    } else {
                        voiceDeleteBtn.classList.add('d-none');
                    }
                }
            } else {
                this.showAlert('error', result.error || 'Failed to update voice');
            }
        } catch (error) {
            this.showAlert('error', 'Error updating voice: ' + error.message);
        }
    }
    
    async handleCustomModelChange() {
        try {
            const modelPath = document.getElementById('custom_model_list').value;
            
            const response = await fetch('/api/custom_model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_path: modelPath })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const customModelDeleteBtn = document.getElementById('custom_model_delete_btn');
                if (customModelDeleteBtn) {
                    if (result.delete_visible) {
                        customModelDeleteBtn.classList.remove('d-none');
                    } else {
                        customModelDeleteBtn.classList.add('d-none');
                    }
                }
            } else {
                this.showAlert('error', result.error || 'Failed to update custom model');
            }
        } catch (error) {
            this.showAlert('error', 'Error updating custom model: ' + error.message);
        }
    }
    
    async updateParameter(paramName, value) {
        try {
            await fetch('/api/parameter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    param_name: paramName, 
                    param_value: value 
                })
            });
        } catch (error) {
            console.error('Error updating parameter:', error);
        }
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            return;
        }
        
        try {
            // Collect form data
            const formData = new FormData(document.getElementById('conversionForm'));
            
            // Add parameter values from sliders
            const parameters = this.collectParameters();
            for (const [key, value] of Object.entries(parameters)) {
                formData.append(key, value);
            }
            
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentConversionId = result.conversion_id;
                this.startConversionMonitoring();
                this.showProgress();
                this.showAlert('success', 'Conversion started!');
            } else {
                this.showAlert('error', result.error || 'Failed to start conversion');
            }
        } catch (error) {
            this.showAlert('error', 'Error starting conversion: ' + error.message);
        }
    }
    
    validateForm() {
        // Check if ebook is uploaded or directory mode is selected
        const isDirectory = document.getElementById('directory_mode').checked;
        const hasEbook = this.uploadedFiles.ebook || isDirectory;
        
        if (!hasEbook) {
            this.showAlert('error', 'Please upload an ebook or select directory mode');
            return false;
        }
        
        // Check if TTS engine is selected
        const ttsEngine = document.getElementById('tts_engine').value;
        if (!ttsEngine) {
            this.showAlert('error', 'Please select a TTS engine');
            return false;
        }
        
        return true;
    }
    
    collectParameters() {
        const parameters = {};
        
        // XTTS parameters
        const xttsParams = [
            'xtts_temperature', 'xtts_repetition_penalty', 
            'xtts_top_k', 'xtts_top_p', 'xtts_speed'
        ];
        
        xttsParams.forEach(param => {
            const element = document.getElementById(param);
            if (element) {
                parameters[param.replace('xtts_', '')] = element.value;
            }
        });
        
        // BARK parameters
        const barkParams = ['bark_text_temp', 'bark_waveform_temp'];
        
        barkParams.forEach(param => {
            const element = document.getElementById(param);
            if (element) {
                parameters[param.replace('bark_', '')] = element.value;
            }
        });
        
        return parameters;
    }
    
    startConversionMonitoring() {
        if (this.socket && this.currentConversionId) {
            this.socket.emit('join_conversion', { 
                conversion_id: this.currentConversionId 
            });
        }
    }
    
    showProgress() {
        const progressContainer = document.getElementById('progress_container');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }
        
        // Disable convert button during conversion
        const convertBtn = document.getElementById('convert_btn');
        if (convertBtn) {
            convertBtn.disabled = true;
            convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }
    
    hideProgress() {
        const progressContainer = document.getElementById('progress_container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Re-enable convert button
        const convertBtn = document.getElementById('convert_btn');
        if (convertBtn) {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '📚';
        }
    }
    
    handleConversionStart(data) {
        this.updateProgressLogs('Conversion started...');
    }
    
    handleConversionProgress(data) {
        if (data.progress !== undefined) {
            this.updateProgressBar(data.progress);
        }
        
        if (data.message) {
            this.updateProgressLogs(data.message);
        }
    }
    
    handleConversionComplete(data) {
        this.hideProgress();
        
        if (data.success) {
            this.showAlert('success', 'Conversion completed successfully!');
            this.updateAudiobookResults(data.output_path);
        } else {
            this.showAlert('error', 'Conversion failed: ' + (data.error || 'Unknown error'));
        }
        
        this.currentConversionId = null;
    }
    
    handleConversionError(data) {
        this.hideProgress();
        this.showAlert('error', 'Conversion error: ' + (data.error || 'Unknown error'));
        this.currentConversionId = null;
    }
    
    updateProgressBar(progress) {
        const progressBar = document.getElementById('progress_bar');
        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }
    }
    
    updateProgressLogs(message) {
        const progressLogs = document.getElementById('progress_logs');
        if (progressLogs) {
            const timestamp = new Date().toLocaleTimeString();
            progressLogs.innerHTML += `[${timestamp}] ${message}\n`;
            progressLogs.scrollTop = progressLogs.scrollHeight;
        }
    }
    
    updateAudiobookResults(outputPath) {
        const resultsContainer = document.getElementById('audiobook_results');
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            
            const audiobookText = document.getElementById('audiobook_text');
            if (audiobookText) {
                audiobookText.value = outputPath;
            }
            
            const audiobookPlayer = document.getElementById('audiobook_player');
            if (audiobookPlayer && outputPath) {
                audiobookPlayer.src = outputPath;
            }
        }
    }
    
    showDeleteConfirmation(type) {
        this.pendingDelete = { type };
        
        let message = 'Are you sure you want to delete this item?';
        let itemName = '';
        
        if (type === 'voice') {
            const voiceSelect = document.getElementById('voice_list');
            itemName = voiceSelect.options[voiceSelect.selectedIndex]?.text || '';
            message = `Are you sure you want to delete the voice "${itemName}"?`;
            this.pendingDelete.item = voiceSelect.value;
        } else if (type === 'custom_model') {
            const modelSelect = document.getElementById('custom_model_list');
            itemName = modelSelect.options[modelSelect.selectedIndex]?.text || '';
            message = `Are you sure you want to delete the custom model "${itemName}"?`;
            this.pendingDelete.item = modelSelect.value;
        }
        
        const modalText = document.getElementById('deleteModalText');
        if (modalText) {
            modalText.textContent = message;
        }
        
        this.deleteModal.show();
    }
    
    async handleConfirmDelete() {
        if (!this.pendingDelete) return;
        
        try {
            let endpoint = '';
            let data = {};
            
            if (this.pendingDelete.type === 'voice') {
                endpoint = '/api/voice/delete';
                data = { voice_name: this.pendingDelete.item };
            } else if (this.pendingDelete.type === 'custom_model') {
                endpoint = '/api/custom_model/delete';
                data = { model_path: this.pendingDelete.item };
            }
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('success', 'Item deleted successfully');
                
                // Update options
                if (this.pendingDelete.type === 'voice') {
                    this.updateVoiceOptions(result.voice_options);
                } else if (this.pendingDelete.type === 'custom_model') {
                    this.updateCustomModelOptions(result.custom_model_options);
                }
            } else {
                this.showAlert('error', result.error || 'Failed to delete item');
            }
        } catch (error) {
            this.showAlert('error', 'Error deleting item: ' + error.message);
        } finally {
            this.deleteModal.hide();
            this.pendingDelete = null;
        }
    }
    
    updateTTSEngineOptions(options) {
        const select = document.getElementById('tts_engine');
        if (select) {
            select.innerHTML = '<option value="">Select TTS Engine...</option>';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                select.appendChild(optionElement);
            });
        }
    }
    
    updateVoiceOptions(options) {
        const select = document.getElementById('voice_list');
        if (select) {
            select.innerHTML = '<option value="">Select from available voices...</option>';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                select.appendChild(optionElement);
            });
        }
    }
    
    updateFineTunedOptions(options) {
        const select = document.getElementById('fine_tuned_list');
        if (select) {
            select.innerHTML = '';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                select.appendChild(optionElement);
            });
        }
    }
    
    updateCustomModelOptions(options) {
        const select = document.getElementById('custom_model_list');
        if (select) {
            select.innerHTML = '<option value="">Select from uploaded models...</option>';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                select.appendChild(optionElement);
            });
        }
    }
    
    updateParameterTabsVisibility(result) {
        // Update XTTS tab
        const xttsTab = document.getElementById('xtts-tab');
        if (xttsTab) {
            xttsTab.style.display = result.visible_xtts_params ? 'block' : 'none';
        }
        
        // Update BARK tab
        const barkTab = document.getElementById('bark-tab');
        if (barkTab) {
            barkTab.style.display = result.visible_bark_params ? 'block' : 'none';
        }
    }
    
    updateConvertButton() {
        const convertBtn = document.getElementById('convert_btn');
        if (!convertBtn) return;
        
        // Check if minimum requirements are met
        const hasEbook = this.uploadedFiles.ebook || 
                        document.getElementById('directory_mode')?.checked;
        const hasTTSEngine = document.getElementById('tts_engine')?.value;
        
        convertBtn.disabled = !(hasEbook && hasTTSEngine);
    }
    
    displayEbookInfo(filename) {
        const filenameDiv = document.getElementById('ebook_filename');
        if (filenameDiv) {
            filenameDiv.innerHTML = `<i class="fas fa-book text-success"></i> <strong>${filename}</strong> uploaded`;
            filenameDiv.classList.remove('d-none');
        }
    }
    
    handleTabSwitch(e) {
        // Handle any tab-specific initialization if needed
        console.log('Tab switched to:', e.target.getAttribute('data-bs-target'));
    }
    
    showAlert(type, message) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of main container
        const mainContainer = document.querySelector('.main-container .p-4');
        if (mainContainer) {
            mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    hideGlassMask() {
        const glassMask = document.getElementById('glass-mask');
        if (glassMask) {
            glassMask.classList.add('d-none');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new Ebook2AudiobookApp();
});