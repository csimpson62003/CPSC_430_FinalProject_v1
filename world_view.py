from pubsub import pub
from view_object import ViewObject
from player_view import PlayerView

class WorldView:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.view_objects = {}

        pub.subscribe(self.new_game_object, 'create')
        pub.subscribe(self.remove_game_object, 'remove')

    def new_game_object(self, game_object):
        view_object = None
        if game_object.kind == 'player':
            view_object = PlayerView(game_object)
        else:
            view_object = ViewObject(game_object)
        self.view_objects[game_object.id] = view_object

    def remove_game_object(self, game_object):
        print("Made it to remove game object")
        if game_object.id in self.view_objects:
           self.view_objects[game_object.id].deleted()
           del self.view_objects[game_object.id]
    def tick(self):
        for key in self.view_objects:
            self.view_objects[key].tick()
