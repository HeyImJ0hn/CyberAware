import os
import json

class FileDAO:
    @staticmethod
    def create(path):
        file = os.path.basename(path)
        dir = os.path.dirname(path)

        if not os.path.exists(dir):
            print('Creating directory: ' + dir)
            os.makedirs(dir)

        if not os.path.exists(path):
            with open(file, 'w') as f:
                f.write('')

    @staticmethod
    def save(json_game, path):
        FileDAO.create(path)

        with open(path, 'w') as f:
            json.dump(json_game, f, indent=4)

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            game_json = json.load(f)
        return game_json
    
    @staticmethod
    def create_absolute_path(path, file):
        full_path = os.path.join(path, file)
        return full_path
    
    @staticmethod
    def get_app_folder():
        if os.name == 'nt':  # windows
            print("Detected OS: Windows")
            return os.path.join(os.environ['USERPROFILE'], 'CyberAware')
        else:  # mac / linux
            print("Detected OS: Unix-like")
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
            with open(settings_path, 'w') as f:
                f.write('') 

        return settings_path
    
    @staticmethod
    def save_settings(settings):
        with open(FileDAO.create_settings_file(), 'w') as f:
            json.dump(settings, f, indent=4)

    @staticmethod
    def load_settings():
        settings_file = FileDAO.create_settings_file()
        if os.path.getsize(settings_file) == 0:
            return None 

        with open(settings_file, 'r') as f:
            settings = json.load(f)
        return settings