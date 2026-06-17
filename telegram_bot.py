import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Configuração de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class SalonTelegramBot:
    def __init__(self, token, gemini_key, salao_info):
        self.token = token
        self.salao_info = salao_info
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_keyboard = [['Agendar Horário', 'Ver Serviços'], ['Localização', 'Falar com Atendente']]
        await update.message.reply_text(
            f"Olá! Bem-vindo ao {self.salao_info['nome']}. Eu sou a {self.salao_info['ia_nome']}, sua assistente virtual.\n\nComo posso ajudar você hoje?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        
        if self.model:
            prompt = f"""
            Você é a assistente virtual {self.salao_info['ia_nome']} do salão {self.salao_info['nome']}.
            Endereço: {self.salao_info['endereco']}
            Telefone: {self.salao_info['telefone']}
            
            O cliente disse: "{user_text}"
            
            Responda de forma gentil, profissional e curta. Se o cliente quiser agendar, peça o nome e o serviço.
            """
            response = self.model.generate_content(prompt)
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Desculpe, meu cérebro (IA) não está configurado no momento, mas logo estarei pronta!")

    def run(self):
        application = ApplicationBuilder().token(self.token).build()
        
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        print("Bot do Telegram iniciado...")
        application.run_polling()

if __name__ == '__main__':
    # Exemplo de uso isolado
    from dotenv import load_dotenv
    load_dotenv()
    
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GEMINI = os.getenv("GEMINI_API_KEY")
    INFO = {
        'nome': os.getenv("SALAO_NOME", "Salão Bella"),
        'ia_nome': os.getenv("IA_NOME", "Sofia"),
        'endereco': os.getenv("SALAO_ENDERECO", "Rua das Flores, 123"),
        'telefone': os.getenv("SALAO_TELEFONE", "(81) 99999-9999")
    }
    
    if TOKEN:
        bot = SalonTelegramBot(TOKEN, GEMINI, INFO)
        bot.run()
    else:
        print("TELEGRAM_BOT_TOKEN não encontrado no .env")
