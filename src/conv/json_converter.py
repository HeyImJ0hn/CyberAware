from dao.file_dao import FileDAO
from config.settings import Settings

class JSONConverter:
    def game_to_json(self, game_manager):

        gm_entities = game_manager.get_entities()
        entities = []
        for e in gm_entities:
            entity = {
                "id": e.id,
                "name": e.name,
                "coords": [e.x, e.y],
                "size": [e.width, e.height],
                "depth": e.depth,
                "text": e.text,
                "notes": e.notes,
                "media": e.media,
                "hidden": e.hidden,
                "colour": e.colour,
                "final": e.final,
                "options": []
            }

            for o in e.options:
                option = {
                    "text": o.text,
                    "entity_id": o.entity.id
                }
                entity["options"].append(option)

            entities.append(entity)

        return {
            "name": game_manager.game_name,
            "app_version": str(game_manager.app_version),
            "icon_path": game_manager.icon_path,
            "entities": entities
        }

    def game_from_json(self, game_manager, path):
        json = FileDAO.load(path)

        name = json["name"]
        app_version = int(json["app_version"])
        icon_path = json["icon_path"]

        entities = []
        for e in json["entities"]:
            entity = game_manager.create_entity()
            entity.id = e["id"]
            entity.name = e["name"]
            entity.set_position(e["coords"][0], e["coords"][1])
            entity.width = e["size"][0]
            entity.height = e["size"][1]
            entity.depth = e["depth"]
            entity.text = e["text"]
            entity.notes = e["notes"]
            entity.media = e["media"]
            colour = e["colour"]
            entity.update_colour((colour[0], colour[1], colour[2]))
            entity.hidden = e["hidden"]
            entity.final = e["final"]

            for o in e["options"]:
                entity.options.append(game_manager.create_option(o["text"], o["entity_id"]))

            entities.append(entity)

        return (name, app_version, icon_path, entities)
    
    def name_from_json(self, path):
        json = FileDAO.load(path)
        return json["name"]
    
    def settings_to_json(self):
        FileDAO.save_settings({
            "VERSION": Settings.VERSION,
            "FIRST_RUN": Settings.FIRST_RUN,
            "RECENT_FILES": Settings.RECENT_FILES,
            "RECENT_MEDIA_PATH": Settings.RECENT_MEDIA_PATH
        })
    
    def settings_from_json(self):
        json = FileDAO.load_settings()
        
        if json:
            Settings.VERSION = json["VERSION"]
            Settings.FIRST_RUN = json["FIRST_RUN"]
            Settings.RECENT_FILES = json["RECENT_FILES"]
            Settings.RECENT_MEDIA_PATH = json["RECENT_MEDIA_PATH"]
        

        