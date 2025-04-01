import pubsub.pub
from panda3d.core import CollisionBox, CollisionNode
from pubsub import pub

class PlayerView:
    def __init__(self, game_object):
        pub.subscribe(self.holdItem, 'holding')
        self.game_object = game_object

        self.player_node = base.render.attachNewNode(self.game_object.kind)
        
    def holdItem(self, node_path):
        #if holding, set pos of node path
        node_path.reparentTo(self.player_node)
        pub.sendMessage('set_owner', owner=self.game_object)

    def tick(self):
        # This will only be needed for game objects that
        # aren't also physics objects.  physics objects will
        # have their position and rotation updated by the
        # engine automatically
        
        #if player, set pos of node path
        #
        
        if not self.game_object.physics:
            h = self.game_object.z_rotation
            p = self.game_object.x_rotation
            r = self.game_object.y_rotation
            self.player_node.setHpr(h, p, r)
            self.player_node.set_pos(*self.game_object.position)
            


