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
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                json.dump(save_template, f, indent=4)

    @staticmethod
    def save(game_manager):
        file_path = game_manager.file_path
        file_name = game_manager.file_name

        full_path = os.path.join(file_path, file_name)
        FileDAO.create(file_path, file_name, game_manager.game_name)

        with open(full_path, 'r') as f:
            game_file = json.load(f)

        entity_template_path = "entity.json"
        with open(entity_template_path, 'r') as f:
            entity_template = json.load(f)

        option_template_path = "option.json"
        with open(option_template_path, 'r') as f:
            option_template = json.load(f)

        entities = game_manager.get_entities()
        for e in entities:
            entity = entity_template.copy()
            entity["id"] = e.id
            entity["name"] = e.name
            entity["coords"] = [e.x, e.y]
            entity["size"] = [e.width, e.height]
            entity["depth"] = e.depth
            entity["text"] = e.text
            entity["notes"] = e.notes
            entity["media"] = e.media
            entity["options"] = []

            for o in e.options:
                option = option_template.copy()
                option["text"] = o.text
                option["entity_id"] = o.entity.id
                entity["options"].append(option)

            game_file["entities"].append(entity)


        with open(full_path, 'w') as f:
            json.dump(game_file, f, indent=4)

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            game_json = json.load(f)
        
        return game_json