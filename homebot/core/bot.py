from homebot import modules_path
from homebot.core.error_handler import error_handler
from homebot.core.modules_manager import Module
from homebot.core.logging import LOGE, LOGI
from pkgutil import iter_modules
from telegram.ext import Updater

# TODO: Find a better way to provide
# modules status to modules itself
bot = None

def get_bot_context():
	return bot

class Bot:
	"""
	Bu sinif bir bot nümunəsini təmsil edir.
	"""
	def __init__(self, token):
		"""
		Botu və onun modullarını işə salın.
		"""
		LOGI("Bot işə salınır")
		self.updater = Updater(token=token, use_context=True)
		self.dispatcher = self.updater.dispatcher
		self.dispatcher.add_error_handler(error_handler, True)
		self.modules = {}
		LOGI("Bot işə salındı")

		LOGI("Modulların təhlili")
		for module in [name for _, name, _ in iter_modules([modules_path])]:
			try:
				module = Module(module)
			except Exception as e:
				LOGE(f"Error loading module {module}, will be skipped\n"
					 f"Error: {e}")
			else:
				self.modules[module] = "Disabled"
		LOGI("Modullar təhlil edildi")

		LOGI("Modullar yuklənir")
		for module in self.modules:
			self.load_module(module)
		LOGI("Modullar yükləndi")

		# TODO: Find a better way to provide
		# modules status to modules itself
		global bot
		bot = self

	def load_module(self, module: Module):
		"""
		Load a provided module and add its command handler
		to the bot's dispatcher.
		"""
		LOGI(f"Loading module {module.name}")
		self.modules[module] = "Starting up"

		for command in module.commands:
			self.dispatcher.add_handler(command.handler)

		self.modules[module] = "Running"
		LOGI(f"Module {module.name} loaded")

	def unload_module(self, module: Module):
		"""
		Unload a provided module and remove its command handler
		from the bot's dispatcher.
		"""
		LOGI(f"Unloading module {module.name}")
		self.modules[module] = "Stopping"

		for command in module.commands:
			self.dispatcher.remove_handler(command.handler)

		LOGI(f"Module {module.name} unloaded")
		self.modules[module] = "Disabled"
