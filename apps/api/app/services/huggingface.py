# Hugging Face integration for llm-eval-guardrails-platform

from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import torch
import os

class HuggingFaceService:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self, model_name: str, model_type: str = "auto"):
        """Load a model from Hugging Face"""
        if model_type == "causal":
            return AutoModelForCausalLM.from_pretrained(model_name)
        elif model_type == "sentence":
            return SentenceTransformer(model_name)
        else:
            return AutoModel.from_pretrained(model_name)

    def load_tokenizer(self, model_name: str):
        """Load a tokenizer"""
        return AutoTokenizer.from_pretrained(model_name)

    def text_generation(self, model_name: str, prompt: str, max_length: int = 100):
        """Generate text using a model"""
        generator = pipeline("text-generation", model=model_name, device=self.device)
        result = generator(prompt, max_length=max_length)
        return result

    def text_embedding(self, model_name: str, text: str):
        """Get text embeddings"""
        model = SentenceTransformer(model_name)
        embedding = model.encode(text)
        return embedding

    def text_classification(self, model_name: str, text: str):
        """Classify text"""
        classifier = pipeline("text-classification", model=model_name, device=self.device)
        result = classifier(text)
        return result

    def question_answering(self, model_name: str, question: str, context: str):
        """Answer a question based on context"""
        qa = pipeline("question-answering", model=model_name, device=self.device)
        result = qa(question=question, context=context)
        return result

    def summarization(self, model_name: str, text: str, max_length: int = 130):
        """Summarize text"""
        summarizer = pipeline("summarization", model=model_name, device=self.device)
        result = summarizer(text, max_length=max_length)
        return result

    def translation(self, model_name: str, text: str, src_lang: str, tgt_lang: str):
        """Translate text"""
        translator = pipeline("translation", model=model_name, device=self.device)
        result = translator(text, src_lang=src_lang, tgt_lang=tgt_lang)
        return result

    def zero_shot_classification(self, model_name: str, text: str, labels: list):
        """Zero-shot classification"""
        classifier = pipeline("zero-shot-classification", model=model_name, device=self.device)
        result = classifier(text, labels)
        return result

    def ner(self, model_name: str, text: str):
        """Named entity recognition"""
        ner = pipeline("ner", model=model_name, device=self.device, aggregation_strategy="simple")
        result = ner(text)
        return result
