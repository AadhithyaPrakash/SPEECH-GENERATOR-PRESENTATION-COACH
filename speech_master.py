import os
import nltk
nltk.download('punkt')
import re  # noqa: E402
import logging  # noqa: E402
import base64  # noqa: E402
from typing import Dict, Tuple  # noqa: E402
import pyttsx3  # noqa: E402
import tempfile  # noqa: E402
from groq import Groq  # noqa: E402
from nltk.tokenize import sent_tokenize  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeechGenerator:
    
    STYLE_TEMPLATES = {
        "formal": "Write a formal {duration}-minute speech about '{topic}' suitable for a professional audience.",
        "casual": "Write a casual, friendly {duration}-minute speech about '{topic}'.",
        "motivational": "Write an inspiring {duration}-minute motivational speech about '{topic}' that energizes the audience.",
        "persuasive": "Write a compelling {duration}-minute persuasive speech about '{topic}' to change minds.",
        "instructional": "Write a step-by-step {duration}-minute instructional speech on '{topic}'.",
        "debate": "Write a {duration}-minute debate speech about '{topic}' with strong arguments and counterpoints.",
        "humorous": "Write a funny {duration}-minute speech about '{topic}' with appropriate humor and wit.",
        "storytelling": "Write an engaging {duration}-minute speech about '{topic}' using storytelling techniques.",
    }
    
    AUDIENCE_GUIDANCE = {
        "general": "Make the speech accessible to a general audience with no specialized knowledge.",
        "experts": "Include technical depth suitable for experts in the field.",
        "children": "Use simple, engaging language and examples suitable for kids.",
        "students": "Be educational and engaging for a student audience.",
        "executives": "Focus on strategic implications and leadership perspectives.",
        "international": "Use globally accessible references and minimize culturally specific idioms.",
    }
    
    AVAILABLE_MODELS = {
        "llama3-8b-8192": {"description": "Balanced model for general use", "max_tokens": 8192},
        "llama3-70b-8192": {"description": "Advanced model with better quality", "max_tokens": 8192},
        "gemma-7b-it": {"description": "Efficient model for simpler tasks", "max_tokens": 4096},
        "mixtral-8x7b-32768": {"description": "High-capacity model for longer context", "max_tokens": 32768}
    }
    
    TTS_VOICES = {
        "male": {"rate": 170, "volume": 1.0, "description": "Clear, professional male voice"},
        "female": {"rate": 165, "volume": 1.0, "description": "Clear, professional female voice"}
    }
    
    def __init__(self, api_key=None):
  
        self.api_key = api_key
        self.client = None
        self.output_folder = "speech_outputs"
        self.audio_folder = os.path.join(self.output_folder, "audio")
        self.history = []
        self.engine = None
        
        for folder in [self.output_folder, self.audio_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        self._initialize_tts_engine()
        
        if api_key:
            self.set_api_key(api_key)
    
    def _initialize_tts_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170)
            self.engine.setProperty('volume', 1.0)
            
            voices = self.engine.getProperty('voices')
            self.available_voices = voices
            
            if len(voices) > 0:
                self.engine.setProperty('voice', voices[0].id)
                logger.info(f"TTS engine initialized with {len(voices)} voices")
            else:
                logger.warning("No voices found for TTS engine")
                
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            self.engine = None
    
    def set_voice(self, voice_type="male"):
        if not self.engine or not hasattr(self, 'available_voices'):
            return
            
        voices = self.available_voices
        
        if voice_type == "female":
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
            else:
                self.engine.setProperty('voice', voices[0].id)
        else:
            self.engine.setProperty('voice', voices[0].id)
        
        self.engine.setProperty('rate', self.TTS_VOICES[voice_type]["rate"])
        self.engine.setProperty('volume', self.TTS_VOICES[voice_type]["volume"])
    
    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        self.initialize_client()
        logger.info("API key set successfully.")
    
    def initialize_client(self) -> None:
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized.")
        else:
            logger.warning("No API key available. Set API key before generating speeches.")
    
    def build_prompt(self, topic: str, duration: int, emotion: str = "formal", 
                   audience: str = "general", additional_instructions: str = "") -> str:
        base_prompt = self.STYLE_TEMPLATES.get(emotion, self.STYLE_TEMPLATES["formal"]).format(
            topic=topic, duration=duration
        )
        audience_note = self.AUDIENCE_GUIDANCE.get(audience, self.AUDIENCE_GUIDANCE["general"])
        
        word_count = duration * 130
        
        final_prompt = (
            f"{base_prompt}\n\n"
            f"{audience_note}\n\n"
            f"Structure the speech with an introduction, body, and conclusion.\n"
            f"Use engaging transitions, rhetorical devices, and paragraph breaks.\n"
            f"Include natural pauses (marked with [pause]) and emphasis points (marked with *emphasis*) to guide the delivery.\n"
            f"Add occasional delivery notes in [brackets] for pacing, tone, or gestures.\n"
            f"Aim for approximately {word_count} words to fill {duration} minutes when delivered aloud.\n"
        )
        
        if additional_instructions:
            final_prompt += f"\nAdditional instructions: {additional_instructions}\n"
        
        return final_prompt
    
    def generate_speech(self, topic: str, duration: int, emotion: str, audience: str, 
                        model: str = "llama3-8b-8192", temperature: float = 0.7, 
                        additional_instructions: str = "") -> Tuple[str, Dict]:
        if not self.client:
            raise ValueError("API key not set. Use set_api_key() first.")
        
        prompt = self.build_prompt(topic, duration, emotion, audience, additional_instructions)
        
        metadata = {
            "topic": topic,
            "duration": duration,
            "emotion": emotion,
            "audience": audience,
            "model": model,
            "temperature": temperature,
            "timestamp": None,
            "word_count": 0,
        }
        
        try:
            max_tokens = self.AVAILABLE_MODELS.get(model, {}).get("max_tokens", 2048)
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=min(max_tokens, 4096),
                top_p=1,
                stream=False
            )
            
            speech = completion.choices[0].message.content
            
            import datetime
            metadata["timestamp"] = datetime.datetime.now().isoformat()
            metadata["word_count"] = len(speech.split())
            
            self.history.append(metadata)
            
            return speech, metadata
            
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            raise
    
    def prepare_text_for_tts(self, text: str) -> str:
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'\n\n', '.\n\n', text)
        
        return text
    
    def generate_speech_audio(self, text: str, voice: str = "male") -> str:
        if not self.engine:
            raise ValueError("TTS engine not available. Check logs for initialization errors.")
            
        clean_text = self.prepare_text_for_tts(text)
        self.set_voice(voice)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        output_path = temp_file.name
        
        try:
            self.engine.save_to_file(clean_text, output_path)
            self.engine.runAndWait()
            
            logger.info(f"Audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_]', '', text.replace(" ", "_"))[:30]


class PresentationCoach:
    
    def __init__(self):
       
        pass
        
    def analyze_sentiment(self, text):
       
        positive_words = ['good', 'great', 'excellent', 'positive', 'happy', 'joy', 'love', 
                          'wonderful', 'fantastic', 'amazing', 'best', 'better', 'success']
        negative_words = ['bad', 'poor', 'terrible', 'negative', 'sad', 'hate', 'worst', 
                          'fail', 'failure', 'awful', 'unfortunately', 'problem', 'issue', 'difficult']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            label = "NEUTRAL"
            confidence = 0.5
        elif pos_count > neg_count:
            label = "POSITIVE"
            confidence = pos_count / (total) if total > 0 else 0.6
        else:
            label = "NEGATIVE"
            confidence = neg_count / (total) if total > 0 else 0.6
            
        return label, confidence * 100
        
    def structure_score(self, text):
        sentences = sent_tokenize(text) 
        score = min(100, len(sentences) * 10)
        return round(score, 2), len(sentences)
        
    def analyze_complexity(self, text):
        words = text.split()
        if not words:
            return 0
        
       
        avg_word_length = sum(len(word) for word in words) / len(words)
        

        complexity_score = min(100, avg_word_length * 10)
        
        return round(complexity_score, 2)
        
    def suggest_improvements(self, label, confidence, sentence_count, complexity_score):
        suggestions = []
        
        if confidence < 60:
            suggestions.append("Try to sound more confident and assertive in your delivery.")
            
        if sentence_count < 5:
            suggestions.append("Add more structured points to provide better organization to your speech.")
            
        if label == "NEGATIVE":
            suggestions.append("Use more positive wording to create a better impression on your audience.")
            
        if complexity_score < 40:
            suggestions.append("Consider using more varied vocabulary to engage your audience.")
            
        if complexity_score > 70:
            suggestions.append("Your language might be too complex. Try simplifying for better comprehension.")
            
        if not suggestions:
            suggestions.append("You're doing great! Keep practicing to maintain your skills.")
            
        return suggestions


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="download-button">Download {file_label}</a>'
    return href