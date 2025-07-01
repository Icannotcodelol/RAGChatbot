from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Dict
from backend.config import config

class QwenLLM:
    def __init__(self):
        # Detect best available device
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("Using MPS (Apple Silicon GPU) for acceleration")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("Using CUDA GPU for acceleration")
        else:
            self.device = torch.device("cpu")
            print("Using CPU (no GPU acceleration available)")
        
        print(f"Loading Qwen model: {config.QWEN_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.QWEN_MODEL,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            config.QWEN_MODEL,
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def generate_answer(self, question: str, context_docs: List[Dict]) -> str:
        """Generate answer based on question and retrieved context"""
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1} (from {doc['filename']}):\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Truncate context if too long
        if len(context) > config.MAX_CONTEXT_LENGTH:
            context = context[:config.MAX_CONTEXT_LENGTH] + "..."
        
        # Build prompt with clear structure for Qwen
        prompt = f"""<|im_start|>system
You are a helpful assistant that answers questions based on the provided context. 

IMPORTANT RULES:
- Answer concisely and accurately based ONLY on the provided context
- ALWAYS respond in the EXACT same language as the user's question
- Do NOT mix languages in your response
- If the question is in German, answer in German
- If the question is in English, answer in English
- Do NOT add Chinese characters or other languages
<|im_end|>
<|im_start|>user
Context:
{context}

Question: {question}
<|im_end|>
<|im_start|>assistant
"""
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        # Decode only the generated part (new tokens)
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        answer = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        
        # Clean up the response
        if answer.startswith('<|im_end|>'):
            answer = answer[len('<|im_end|>'):].strip()
        
        # Remove any Chinese characters that might have slipped through
        answer = self._clean_language_mixing(answer)
        
        # Fallback if answer is empty
        if not answer:
            return "I couldn't generate a proper answer based on the provided context."
        
        return answer
    
    def _clean_language_mixing(self, text: str) -> str:
        """Remove unwanted Chinese characters and clean up mixed language responses"""
        import re
        
        # Remove Chinese characters (CJK unified ideographs)
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        
        # Remove extra whitespace that might be left after removing Chinese
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text 