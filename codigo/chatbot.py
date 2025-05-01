import random

class Chatbot:
    def __init__(self):
        self.greetings = ['Hola, ¿en qué te puedo ayudar hoy?', '¡Hola! ¿Qué tal va todo?', '¡Hola! ¿En qué puedo asistirte?']
        self.farewells = ['¡Hasta luego!', '¡Nos vemos!', '¡Que tengas un buen día!']
        self.unknown_responses = ['Lo siento, no entiendo eso. ¿Puedes preguntar de otra manera?', 'No estoy seguro de cómo responder a eso. ¿Puedes ser más claro?']

    def greet(self):
        """Devuelve un saludo aleatorio."""
        return random.choice(self.greetings)

    def farewell(self):
        """Devuelve una despedida aleatoria."""
        return random.choice(self.farewells)

    def unknown(self):
        """Devuelve una respuesta cuando el chatbot no entiende la pregunta."""
        return random.choice(self.unknown_responses)

    def process_message(self, message):
        """Procesa un mensaje de entrada del usuario."""
        message = message.lower()
        if "hola" in message:
            return self.greet()
        elif "adiós" in message or "bye" in message:
            return self.farewell()
        elif "comida" in message or "alimento" in message:
            return "¿Quieres saber sobre las calorías o nutrientes de algún alimento en particular?"
        else:
            return self.unknown()

    def get_response(self, user_message):
        """Recibe un mensaje del usuario y devuelve la respuesta correspondiente."""
        return self.process_message(user_message)
