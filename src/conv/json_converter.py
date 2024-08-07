from dao.file_dao import FileDAO
from config.Settings import Settings

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
            "entities": entities
        }

    def game_from_json(self, game_manager, path):
        json = FileDAO.load(path)

        name = json["name"]

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

        return (name, entities)
    
    def settings_to_json(self):
        FileDAO.save_settings({
            "VERSION": Settings.VERSION,
            "RESOLUTION": Settings.RESOLUTION,
            "FULLSCREEN": Settings.FULLSCREEN,
            "POSITION": Settings.POSITION,
            "FIRST_RUN": Settings.FIRST_RUN
        })
    
    def settings_from_json(self):
        json = FileDAO.load_settings()
        
        if json:
            Settings.VERSION = json["VERSION"]
            Settings.RESOLUTION = json["RESOLUTION"]
            Settings.FULLSCREEN = json["FULLSCREEN"]
            Settings.POSITION = json["POSITION"]
            Settings.FIRST_RUN = json["FIRST_RUN"]
        

        