from Meh import Config, Option, ExceptionInConfigError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import telegram

from os.path import isdir, abspath, relpath, basename, splitext
from os import mkdir, system, stat
from urllib.parse import quote
from time import sleep

def wait_for_write_finish(path):
		last_size, size = -1, 0
		while size != last_size:
				sleep(1)
				last_size, size = size, stat(path).st_size

def convert_video(path):
	print("Converting video: %s" % path)
	destination = config.converted_path + splitext(basename(path))[0] + ".mp4"
	system("avconv -i %s -c:v libx264 -y %s" % (path, destination))
	return destination

def send_video(path):
	url = "%s%s" % (config.converted_base_url, quote(basename(path)))
	print("Sending message '%s'" % url)
	bot.send_message(text=url, chat_id=config.group_id)

class FSHandler(FileSystemEventHandler):
	def on_created(self, event):
		wait_for_write_finish(event.src_path)
		send_video(convert_video(event.src_path))


config = Config()
config += Option("telegram_secret", "")
config += Option("group_id", "")
config += Option("originals_path", ".", validator=isdir)
config += Option("converted_path", ".", validator=isdir)
config += Option("converted_base_url", "")

CONFIG_PATH = "config.cfg"

try:
    config = config.load(CONFIG_PATH)
except (IOError, ExceptionInConfigError):
    config.dump(CONFIG_PATH)
    config = config.load(CONFIG_PATH)

config.originals_path = config.originals_path + "/" if not config.originals_path[-1] == "/" else config.originals_path
config.converted_path = config.converted_path + "/" if not config.converted_path[-1] == "/" else config.converted_path
config.converted_base_url = config.converted_base_url + "/" if not config.converted_base_url[-1] == "/" else config.converted_base_url

bot = telegram.Bot(config.telegram_secret)

observer = Observer()
observer.schedule(FSHandler(), path=config.originals_path)
observer.start()

while True:
	sleep(10)