import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import language_tool_python
from sentence_transformers import SentenceTransformer
import numpy as np

class PhoebeBot:
    def __init__(self):
        # Загрузка модели и токенизатора
        self.model = GPT2LMHeadModel.from_pretrained("./model/gpt2-phoebe")
        self.tokenizer = GPT2Tokenizer.from_pretrained("./model/gpt2-phoebe")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Добавляем специальные токены, если их нет
        if "<START>" not in self.tokenizer.get_vocab():
            self.tokenizer.add_tokens(["<START>", "<END>"])
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Загрузка инструментов для постобработки
        self.tool = language_tool_python.LanguageTool('en-US')  # Для исправления грамматики
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')  # Для вычисления семантического сходства

    def generate_response(self, input_text, max_length=50, temperature=0.7, top_k=50):
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)
        
        # Генерация ответа с учетом параметров
        output = self.model.generate(
            input_ids,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            do_sample=True,  # Включаем сэмплирование
            pad_token_id=self.tokenizer.pad_token_id,  # Указываем pad_token_id
            attention_mask=(input_ids != self.tokenizer.pad_token_id).long(),  # Указываем attention_mask
            no_repeat_ngram_size=2,  # Запрещаем повторение n-грамм
            repetition_penalty=1.5,  # Штраф за повторения
        )
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def filter_response(self, response, keywords):
        return any(keyword in response.lower() for keyword in keywords)

    def postprocess_response(self, response):
        # Исправление грамматики
        corrected_response = self.tool.correct(response)
        # Удаление повторений
        words = corrected_response.split()
        unique_words = []
        for word in words:
            if word not in unique_words:
                unique_words.append(word)
        return " ".join(unique_words)

    def generate_multiple_responses(self, input_text, num_responses=3):
        responses = []
        for _ in range(num_responses):
            response = self.generate_response(input_text)
            responses.append(response)
        return responses

    def select_best_response(self, responses, keywords):
        for response in responses:
            if self.filter_response(response, keywords):
                return response
        return responses[0]  # Возвращаем первый ответ, если ни один не подошел

    def get_response(self, input_text, context=None):
        # Добавляем контекст, если он есть
        if context:
            input_text = context + "\nUser: " + input_text
        
        # Генерация нескольких ответов
        responses = self.generate_multiple_responses(input_text)
        
        # Выбор лучшего ответа
        best_response = self.select_best_response(responses, keywords=["sing", "song", "music"])
        
        # Постобработка ответа
        best_response = self.postprocess_response(best_response)
        
        return best_response