import os
import json
import shutil
import platform
import subprocess
from pathlib import Path

class FileDAO:
    @staticmethod
    def create(path):
        file = os.path.basename(path)
        dir = os.path.dirname(path)

        if not os.path.exists(dir):
            print('Creating directory: ' + dir)
            os.makedirs(dir)

        if not os.path.exists(path):
            with open(file, 'w', encoding='utf-8') as f:
                f.write('')

    @staticmethod
    def save(json_game, path):
        FileDAO.create(path)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json_game, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load(path):
        with open(path, 'r', encoding='utf-8') as f:
            game_json = json.load(f)
        return game_json
    
    @staticmethod
    def create_absolute_path(path, file):
        full_path = os.path.join(path, file)
        return full_path
    
    @staticmethod
    def get_app_folder():
        if os.name == 'nt':  # windows
            return os.path.join(os.environ['USERPROFILE'], 'CyberAware')
        else:  # mac / linux
            return os.path.join(os.environ['HOME'], 'CyberAware')

    @staticmethod
    def create_settings_file():
        app_folder = FileDAO.get_app_folder()
        settings_path = os.path.join(app_folder, 'settings.dat')

        if not os.path.exists(app_folder):
            print('Creating directory: ' + app_folder)
            os.makedirs(app_folder)

        if not os.path.exists(settings_path):
            print('Creating file: ' + settings_path)
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write('') 

        return settings_path
    
    @staticmethod
    def save_settings(settings):
        with open(FileDAO.create_settings_file(), 'w') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_settings():
        settings_file = FileDAO.create_settings_file()
        if os.path.getsize(settings_file) == 0:
            return None 

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    
    @staticmethod
    def create_game_folder(game_name):
        app_folder = FileDAO.get_app_folder()
        game_folder = os.path.join(app_folder, game_name)

        if not os.path.exists(game_folder):
            print('Creating directory: ' + game_folder)
            os.makedirs(game_folder)

        return game_folder
    
    @staticmethod
    def copy_media(source, game_name):
        destination = FileDAO.create_game_folder(game_name)

        if not os.path.exists(source):
            print('Media does not exist: ' + source)
            return
        else:
            print('Copying media: ' + source + ' to ' + destination)
            shutil.copy2(source, destination)
            return os.path.join(destination, os.path.basename(source))

    @staticmethod
    def get_base_name(file):
        return os.path.basename(file)
    
    @staticmethod
    def get_file_name_without_extension(file):
        return os.path.splitext(os.path.basename(file))[0]
    
    @staticmethod
    def get_dir_name(file):
        return os.path.dirname(file)
    
    @staticmethod
    def update_game_name(old_name, new_name):
        app_folder = FileDAO.get_app_folder()
        old_game_folder = os.path.join(app_folder, old_name)
        new_game_folder = os.path.join(app_folder, new_name)

        if os.path.exists(old_game_folder):
            print('Renaming directory: ' + old_game_folder + ' to ' + new_game_folder)
            os.rename(old_game_folder, new_game_folder)
        else:
            print('Directory does not exist: ' + old_game_folder)

    @staticmethod
    def get_game_folder(game_name):
        app_folder = FileDAO.get_app_folder()
        return os.path.join(app_folder, game_name)
    
    @staticmethod
    def save_temp_image(image):
        temp_folder = os.path.join(FileDAO.get_app_folder(), 'temp')
        if not os.path.exists(temp_folder):
            print('Creating directory: ' + temp_folder)
            os.makedirs(temp_folder)

        temp_image = os.path.join(temp_folder + "temp_image.png")
        print('Saving temp image: ' + temp_image)
        image.save(temp_image)
        return temp_image
    
    @staticmethod
    def delete_temp_image():
        temp_folder = os.path.join(FileDAO.get_app_folder(), 'temp')
        temp_image = os.path.join(temp_folder + "temp_image.png")
        if os.path.exists(temp_image):
            print('Deleting temp image: ' + temp_image)
            os.remove(temp_image)
        else:
            print('Temp image does not exist: ' + temp_image)

    @staticmethod
    def is_video_file(path):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        return any(path.endswith(ext) for ext in video_extensions)
    
    @staticmethod
    def is_image_file(path):
        image_extensions = ['.png', '.jpg', '.jpeg']
        return any(path.endswith(ext) for ext in image_extensions)
    
    @staticmethod
    def does_path_exist(path):
        return os.path.exists(path)
    
    @staticmethod
    def join_path(path, file):
        return os.path.join(path, file)
    
    @staticmethod
    def move_build_folder(game_name):
        build_folder = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..', '..' ,'android', 'app', 'build', 'outputs'))
        game_folder = FileDAO.get_game_folder(game_name)
        if os.path.exists(build_folder):
            print('Moving build folder: ' + build_folder + ' to ' + game_folder)
            if os.path.exists(os.path.join(game_folder, 'outputs')):
                shutil.rmtree(os.path.join(game_folder, 'outputs'))
            shutil.move(build_folder, game_folder)
        else:
            print('Build folder does not exist: ' + build_folder)
            
        FileDAO.open_folder(game_folder)
    
    @staticmethod        
    def open_folder(path):
        if not os.path.isdir(path):
            print(f"{path} is not a valid directory.")
            return
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer {os.path.normpath(path)}')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux
            subprocess.Popen(['xdg-open', path])