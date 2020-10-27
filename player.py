import collections


class Player:
    def __init__(self,game, id):
        self.game = game
        self.alive = True
        self.id = id

        self.current_responses = [None]
        self.response_archive = []

        self.inventory = []

        self.maximum_responses = 1

        self.score_boosts = []

        self.specials = {}


    def get_item(self,uuid):
        for item in self.inventory:
            if item["uuid"] == uuid:
                return item
        return None

    def remove_item_with_uuid(self, uuid):
        target_item = self.get_item(uuid)

        if target_item is not None:
            self.inventory.remove(target_item)

        return target_item

    def update_max_responses(self,new_max):
        self.maximum_responses = new_max
        while len(self.current_responses) < new_max:
            self.current_responses.append(None)
        self.game.dump_game()

    def new_round(self):
        self.response_archive.append(self.current_responses)
        self.current_responses = [None for i in range(self.maximum_responses)]
        for b in self.score_boosts:
            b[1] -= 1
        self.score_boosts = [i for i in self.score_boosts if i[1] != 0]

    def add_response(self, response, index):
        r = {
            "player" : self.id,
            "response" : response,
            "index" : index,

            "id" : None,
            "mean" : None,
            "stdev" : None,
            "skew" : None,
            "score" : None,
            "movement" : None,
            "metas" : []

        }

        self.current_responses[index-1] = r
        self.game.dump_game()
