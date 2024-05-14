from dao.FileDAO import FileDAO

class JSONConverter:
    def convert_to_json(self, game):
        pass

    def convert_from_json(self, game_manager, path):
        json = FileDAO.load(path)

        game_manager.game_name = json["name"]

        for e in json["entities"]:
            entity = game_manager.add_entity()
            entity.id = e["id"]
            entity.name = e["name"]
            entity.x = e["coords"][0]
            entity.y = e["coords"][1]
            entity.width = e["size"][0]
            entity.height = e["size"][1]
            entity.depth = e["depth"]
            entity.text = e["text"]
            entity.notes = e["notes"]
            entity.media = e["media"]

            for o in e["options"]:
                option = entity.add_option()
                option.text = o["text"]
                option.entity = game_manager.get_entity_by_id(o["entity_id"])

        