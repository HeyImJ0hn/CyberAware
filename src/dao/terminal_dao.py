import subprocess
import platform
from dao.file_dao import FileDAO
import os
import time

class TerminalDao:

    @staticmethod
    def start_key_generation(game_name):
        if platform.system() == "Windows":
            command = f'start keytool -genkeypair -v -keyalg RSA -keysize 2048 -validity 10000 -alias cyberaware -keystore {FileDAO.join_path(FileDAO.create_game_folder(game_name), "keystore.jks")}'
        else:
            command = f'gnome-terminal -- bash -c "keytool -genkeypair -v -keyalg RSA -keysize 2048 -validity 10000 -alias cyberaware -keystore {FileDAO.join_path(FileDAO.create_game_folder(game_name), "keystore.jks")}; exec bash"'
        subprocess.Popen(command, shell=True)