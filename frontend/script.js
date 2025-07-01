const API_BASE_URL = 'http://localhost:8000/api';

class ChatInterface {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.questionInput = document.getElementById('question-input');
        this.sendButton = document.getElementById('send-button');
        this.loadingIndicator = document.getElementById('loading');
        this.fileInput = document.getElementById('file-input');
        this.uploadButton = document.getElementById('upload-button');
        this.uploadStatus = document.getElementById('upload-status');
        
        this.init();
    }
    
    init() {
        this.sendButton.addEventListener('click', () => this.sendQuestion());
        this.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendQuestion();
            }
        });
        
        // Upload functionality
        this.uploadButton.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        
        // Focus input on load
        this.questionInput.focus();
    }
    
    async sendQuestion() {
        const question = this.questionInput.value.trim();
        if (!question) return;
        
        // Add user message
        this.addMessage(question, 'user');
        
        // Clear input and disable
        this.questionInput.value = '';
        this.setLoading(true);
        
        try {
            const response = await fetch(`${API_BASE_URL}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await response.json();
            this.addMessage(data.answer, 'assistant', data.sources);
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            this.setLoading(false);
            this.questionInput.focus();
        }
    }
    
    addMessage(content, type, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        messageDiv.appendChild(contentDiv);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
            
            sources.forEach(source => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.textContent = `📄 ${source.filename} (relevance: ${(source.score * 100).toFixed(1)}%)`;
                sourcesDiv.appendChild(sourceItem);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    setLoading(isLoading) {
        this.sendButton.disabled = isLoading;
        this.questionInput.disabled = isLoading;
        this.loadingIndicator.classList.toggle('hidden', !isLoading);
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            this.showUploadStatus('Please select a PDF, DOCX, or TXT file.', 'error');
            return;
        }
        
        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showUploadStatus('File size must be less than 10MB.', 'error');
            return;
        }
        
        this.setUploadLoading(true);
        this.showUploadStatus('Processing document...', 'processing');
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed');
            }
            
            this.showUploadStatus(
                `✅ ${data.filename} uploaded successfully! Processed ${data.chunks_processed} chunks.`, 
                'success'
            );
            
            // Clear the file input
            this.fileInput.value = '';
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showUploadStatus(`❌ Upload failed: ${error.message}`, 'error');
        } finally {
            this.setUploadLoading(false);
        }
    }
    
    showUploadStatus(message, type) {
        this.uploadStatus.textContent = message;
        this.uploadStatus.className = `upload-status ${type}`;
        
        // Clear success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.uploadStatus.textContent = '';
                this.uploadStatus.className = 'upload-status';
            }, 5000);
        }
    }
    
    setUploadLoading(isLoading) {
        this.uploadButton.disabled = isLoading;
        this.fileInput.disabled = isLoading;
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
}); 