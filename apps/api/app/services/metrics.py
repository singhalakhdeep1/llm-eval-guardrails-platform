from typing import Dict

class MetricsService:
    def __init__(self):
        try:
            from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
            from rouge import Rouge
            self.rouge = Rouge()
            self.smoothie = SmoothingFunction().method4
        except Exception:
            self.rouge = None
            self.smoothie = None
    
    def calculate_bleu(self, reference: str, hypothesis: str) -> Dict:
        """Calculate BLEU score for text generation"""
        try:
            from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
            
            reference_tokens = reference.split()
            hypothesis_tokens = hypothesis.split()
            
            smoothie = SmoothingFunction().method4
            bleu_score = sentence_bleu(
                [reference_tokens],
                hypothesis_tokens,
                smoothing_function=smoothie
            )
            
            return {
                "bleu_score": bleu_score,
                "interpretation": "excellent" if bleu_score > 0.8 else "good" if bleu_score > 0.6 else "fair" if bleu_score > 0.4 else "poor"
            }
        except Exception:
            return self._fallback_bleu(reference, hypothesis)
    
    def _fallback_bleu(self, reference: str, hypothesis: str) -> Dict:
        """Fallback BLEU calculation using simple overlap"""
        ref_words = set(reference.lower().split())
        hyp_words = set(hypothesis.lower().split())
        
        if len(hyp_words) == 0:
            return {"bleu_score": 0, "interpretation": "poor"}
        
        overlap = len(ref_words & hyp_words)
        precision = overlap / len(hyp_words)
        
        return {
            "bleu_score": precision,
            "interpretation": "good" if precision > 0.7 else "fair" if precision > 0.4 else "poor"
        }
    
    def calculate_rouge(self, reference: str, hypothesis: str) -> Dict:
        """Calculate ROUGE score for summarization"""
        if not self.rouge:
            return self._fallback_rouge(reference, hypothesis)
        
        try:
            scores = self.rouge.get_scores(hypothesis, reference)[0]
            
            return {
                "rouge_1": scores['rouge-1']['f'],
                "rouge_2": scores['rouge-2']['f'],
                "rouge_l": scores['rouge-l']['f'],
                "interpretation": "good" if scores['rouge-l']['f'] > 0.5 else "needs_improvement"
            }
        except Exception:
            return self._fallback_rouge(reference, hypothesis)
    
    def _fallback_rouge(self, reference: str, hypothesis: str) -> Dict:
        """Fallback ROUGE calculation using n-gram overlap"""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        # ROUGE-1: unigram overlap
        ref_unigrams = set(ref_words)
        hyp_unigrams = set(hyp_words)
        rouge_1 = len(ref_unigrams & hyp_unigrams) / max(len(ref_unigrams), 1)
        
        # ROUGE-2: bigram overlap
        ref_bigrams = set(zip(ref_words[:-1], ref_words[1:]))
        hyp_bigrams = set(zip(hyp_words[:-1], hyp_words[1:]))
        rouge_2 = len(ref_bigrams & hyp_bigrams) / max(len(ref_bigrams), 1)
        
        # ROUGE-L: longest common subsequence (simplified)
        rouge_l = rouge_1  # Simplified
        
        return {
            "rouge_1": rouge_1,
            "rouge_2": rouge_2,
            "rouge_l": rouge_l,
            "interpretation": "good" if rouge_l > 0.5 else "needs_improvement"
        }
    
    def calculate_perplexity(self, text: str) -> Dict:
        """Calculate perplexity score"""
        try:
            import torch
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            model = GPT2LMHeadModel.from_pretrained('gpt2')
            model.eval()
            
            encodings = tokenizer(text, return_tensors='pt')
            
            with torch.no_grad():
                outputs = model(encodings.input_ids, labels=encodings.input_ids)
                loss = outputs.loss.item()
                perplexity = torch.exp(torch.tensor(loss)).item()
            
            return {
                "perplexity": perplexity,
                "loss": loss,
                "interpretation": "good" if perplexity < 100 else "fair" if perplexity < 500 else "poor"
            }
        except Exception:
            return self._fallback_perplexity(text)
    
    def _fallback_perplexity(self, text: str) -> Dict:
        """Fallback perplexity using word frequency"""
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate entropy approximation
        total_words = len(words)
        if total_words == 0:
            return {"perplexity": float('inf'), "loss": 0, "interpretation": "poor"}
        
        entropy = 0
        for freq in word_freq.values():
            prob = freq / total_words
            entropy -= prob * (prob and (prob.bit_length() - 1) or 0)
        
        perplexity = 2 ** entropy if entropy > 0 else 1
        
        return {
            "perplexity": perplexity,
            "loss": entropy,
            "interpretation": "good" if perplexity < 100 else "fair" if perplexity < 500 else "poor"
        }


class HallucinationDetectionService:
    def __init__(self):
        pass
    
    def detect_hallucination(self, response: str, context: str) -> Dict:
        """Detect hallucinations in LLM responses"""
        context_entities = self._extract_entities(context)
        response_entities = self._extract_entities(response)
        
        hallucinated = []
        for entity in response_entities:
            if entity not in context_entities:
                hallucinated.append(entity)
        
        # Check for unsupported claims
        unsupported_claims = self._detect_unsupported_claims(response, context)
        
        hallucination_score = len(hallucinated) / max(len(response_entities), 1)
        
        return {
            "has_hallucination": len(hallucinated) > 0 or len(unsupported_claims) > 0,
            "hallucinated_entities": hallucinated,
            "unsupported_claims": unsupported_claims,
            "hallucination_score": hallucination_score,
            "interpretation": "high_risk" if hallucination_score > 0.3 else "medium_risk" if hallucination_score > 0.1 else "low_risk"
        }
    
    def _extract_entities(self, text: str) -> list:
        """Extract entities from text (simplified)"""
        # In production, use spaCy or similar
        words = text.split()
        entities = []
        
        for word in words:
            # Simple heuristic: capitalized words might be entities
            if word[0].isupper() and len(word) > 3:
                entities.append(word)
        
        return entities
    
    def _detect_unsupported_claims(self, response: str, context: str) -> list:
        """Detect unsupported claims"""
        # Look for definitive statements not supported in context
        unsupported = []
        
        response_sentences = response.split('.')
        context_lower = context.lower()
        
        for sentence in response_sentences:
            if any(word in sentence.lower() for word in ["definitely", "certainly", "absolutely"]):
                # Check if the claim is supported in context
                if sentence.strip().lower() not in context_lower:
                    unsupported.append(sentence.strip())
        
        return unsupported
