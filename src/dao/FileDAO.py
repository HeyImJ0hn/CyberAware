import os
import json

class FileDAO:

    @staticmethod
    def create(path, file, game_name):
        if not os.path.exists(path):
            print('Creating path: ' + path)
            os.makedirs(path)

        save_template_path = "save_template.json"
        with open(save_template_path, 'r') as f:
            save_template = json.load(f)

        save_template["name"] = game_name

        full_path = os.path.join(path, file)
        with open(full_path, 'w') as f:
            json.dump(save_template, f, indent=4)

    @staticmethod
    def save(file):
        pass

    @staticmethod
    def load(path):
        # Returns file
        pass