import player as p
import random
import pickle
import statistics
import scipy.stats
import time
import json

class Game:
    def __init__(self):

        self.players = []

        self.round = 0

        #0 - responding, 1 - voting, 2 - results, 3 - interphase
        self.phase = 0
        self.can_signup = True

        self.screen_size = 10
        self.master_vote_list = []
        self.all_responses = []
        self.voter_registry = {}
        self.item_registry = []
        self.update_item_registry()

    def new_round(self):
        self.round += 1
        self.phase = 0
        for p in self.players:
            p.new_round()

        self.dump_game()

    def movement(self, score):
        return score//0.1

    def export_results(self):
        x = self.tabulate_results()
        x = sorted(x,key = lambda y: (-y["mean"],y["skew"],y["stdev"]))
        with open("results/results.json","w+") as f:
            json.dump(x,f)
        with open("results/results_{}.json".format(time.time()),"w") as f:
            json.dump(x,f)

        return x

    def get_response_index_by_id(self,id):
        for n,i in enumerate(self.all_responses):
            if i["id"] == id:
                return n

    def tabulate_results(self):
        responses = self.all_responses
        votes = self.voter_registry
        true_screensize = min(self.screen_size, len(responses))
        percentiles = [(true_screensize - 1 - i)/(true_screensize - 1) for i in range(true_screensize)]
        for r in responses:
            r["metas"] = []

        for voter in votes:
            vote_list = votes[voter]["votes"]

            metascores = [[] for i in range(len(responses))]

            for vote in vote_list:
                for rank,response in enumerate(vote):
                    metascores[response].append(percentiles[rank])

            for n,ms in enumerate(metascores):
                if ms != []:
                    responses[self.get_response_index_by_id(n)]["metas"].append(statistics.mean(ms))


        for r in responses:
            print(r)
            player = self.get_player_from_id(r['player'])

            r['mean'] = statistics.mean(r['metas'])
            try:
                r['stdev'] = statistics.stdev(r['metas'])
            except:
                r['stdev'] = 0
            r['skew'] = scipy.stats.skew(r['metas'])

            r['score'] = r['mean'] + sum(i[0] for i in player.score_boosts)
            r['movement'] = self.movement(r['score'])
        print(responses)
        return responses

    def add_player(self, aid):
        self.players.append(p.Player(self, aid))

    def start_voting(self):
        self.master_vote_list = []
        self.votes = []
        self.all_responses = []
        self.voter_registry = {}

        for p in self.players:
            self.all_responses.extend([i for i in p.current_responses[:p.maximum_responses] if i is not None])

        for n,i in enumerate(self.all_responses):
            i["id"] = n

    def start_results(self):
        self.all_responses = self.export_results()



    def generate_screens(self):
        num_reps = len(self.all_responses)
        size = min(self.screen_size,num_reps)
        screen_count = -(num_reps // -size)
        overflow = (screen_count * size) - num_reps
        overhang = size - overflow
        a = [i for i in range(num_reps)]
        b = [j for j in range(num_reps)]
        random.shuffle(a)
        random.shuffle(b)
        while any(i in a[-overhang:] for i in b[:overflow]):
            random.shuffle(b)

        screens = a + b[:overflow]

        def chunks(l, n):
            n = max(1, n)
            return [l[i:i + n] for i in range(0, len(l), n)]

        return chunks(screens,size)


    def print_screen(self,s):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        message = "```\n"
        for n,s in enumerate(s):
            message += "{}: {}\n".format(alphabet[n],self.all_responses[s]["response"])
        message += "```"
        return message

    def get_player_from_id(self, aid):
        for i in self.players:
            if i.id == aid:
                return i

        return None

    def update_item_registry(self):
        with open("items.json","r") as f:
            self.item_registry = json.load(f)

    def get_item_data(self, id):
        for i in self.item_registry:
            if i["id"] == id:
                return i

        return None

    def new_player_item(self, id):
        idata = self.get_item_data(id)
        return {
            "id" : id,
            "uuid" : random.randint(0,2**31-1),
            "fields" : [{"id" : i["id"], "name" : i["name"], "value" : i["default"]} for i in idata["fields"]]
        }


    def format_fields(self,item,forbidden_knowledge=False):
        if len(item["fields"]) == 0:
            s = ""
        else:
            s = "\n".join("{}: **{}**".format(i["name"], i["value"]) for i in item["fields"]) + "\n"
        if forbidden_knowledge:
            s += "*UUID: {}*\n".format(item["uuid"])
        return s

    def item_string(self,item,forbidden_knowledge=False):
        idata = self.get_item_data(item["id"])

        return "**{}**\nWeight: **{}** | Register: **{}**\nUse During **{}**, Activated in **{}**\nType(s): {}"\
        "\n{}\n-------\n{}-------".format(
            idata["name"],
            idata["weight"], idata["register"],
            ",".join(t.upper() for t in idata["use_phases"]), ",".join(t.upper() for t in idata["activation_phases"]),
            ", ".join(t.title() for t in idata["types"]),
            idata["description"],
            self.format_fields(item,forbidden_knowledge)
        )


    def dump_game(self):
        with open("game.pkl","wb") as f:
            pickle.dump(self, f)