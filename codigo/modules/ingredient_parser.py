from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch


class IngredientParser:
    def __init__(self, model_name="dslim/bert-base-NER"):
        # Puedes cambiar a otro modelo si lo deseas, este es bueno para reconocer entidades como comidas
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.nlp_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer, grouped_entities=True)

    def extract_ingredients(self, text):
        entities = self.nlp_pipeline(text)
        ingredients = [ent['word'] for ent in entities if ent['entity_group'] in ["MISC", "ORG", "PER", "FOOD", "LOC"]]
        # Post-procesamiento para limpiar sub-palabras
        cleaned = [word.replace("##", "") for word in ingredients if word.isalpha()]
        return list(set(cleaned))  # Sin duplicados

    def adapt_model(self, new_data):
        """
        Punto de entrada para implementar aprendizaje personalizado a futuro (fine-tuning).
        De momento, puedes guardar el texto para entrenar posteriormente.
        """
        with open("data/user_sentences.txt", "a", encoding="utf-8") as f:
            f.write(new_data.strip() + "\n")
