import pubsub.pub
from panda3d.core import CollisionBox, CollisionNode
from pubsub import pub

class ViewObject:
    def __init__(self, game_object):
        
        self.game_object = game_object

        if self.game_object.physics:
            self.node_path = base.render.attachNewNode(self.game_object.physics)
        else:
            self.node_path = base.render.attachNewNode(self.game_object.kind)

        # TODO: we don't always need a cube model.  Check the
        # game object's kind property to what type of model to use
        
        # TODO: we don't always need a texture.  We need a
        # mechanism to see if we need a texture or color,
        # and what texture/color to use.
        self.cube = None
        if(self.game_object.kind == 'gun'):
            print("GGGUUUNNN")
            self.cube = base.loader.loadModel("Models/shotgun.gltf")
            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/shotgun.png")
            self.cube.setTexture(self.cube_texture)
            pub.sendMessage('holding', node_path=self.node_path)

        elif (self.game_object.kind == 'denver'):
            self.cube = base.loader.loadModel("Models/Wrestling_Athlete_0328191122_texture.fbx")

            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/Wrestling_Athlete_0328191122_texture.png")

            self.cube.setTexture(self.cube_texture)
        elif (self.game_object.kind == 'phillip'):
            self.cube = base.loader.loadModel("Models/steve.gltf")
            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/steve.png")

            self.cube.setTexture(self.cube_texture)
        elif (self.game_object.kind == 'mario'):
            self.cube = base.loader.loadModel("Models/mario.gltf")

            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/mario.png")

            self.cube.setTexture(self.cube_texture)
        elif (self.game_object.kind == 'bullet'):
            print("MAKING BULLET")
            self.cube = base.loader.loadModel("Models/cube")
            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/crate.png")
            self.cube.setTexture(self.cube_texture)
            
            pub.sendMessage('new_bullet', bullet=self.node_path)
            
        else:
            self.cube = base.loader.loadModel("Models/cube")
            self.cube.reparentTo(self.node_path)
            self.cube_texture = base.loader.loadTexture("Textures/crate.png")
            self.cube.setTexture(self.cube_texture)
        self.node_path.setHpr(self.game_object.y_rotation, self.game_object.x_rotation, self.game_object.z_rotation)
        bounds = self.cube.getTightBounds()
        # bounds is two vectors
        bounds = bounds[1]-bounds[0]
        # bounds is now the widths with bounds[0] the x width, bounds[1] the y depth, bounds[2] the z height
        size = game_object.size

        x_scale = size[0] / bounds[0]
        y_scale = size[1] / bounds[1]
        z_scale = size[2] / bounds[2]

        self.cube.setScale(x_scale, y_scale, z_scale)

        self.is_selected = False
        self.texture_on = True
        self.toggle_texture_pressed = False
        pub.subscribe(self.toggle_texture, 'input')

    def deleted(self):
        # Prevent circular references from keeping both the view object and the cube alive
        self.cube.setPythonTag("owner", None)
        self.node_path.removeNode()
        self.cube.removeNode()
        self.node_path = None
        del self

    def toggle_texture(self, events=None):
        if 'toggleTexture' in events:
            self.toggle_texture_pressed = True

    def tick(self):
        # This will only be needed for game objects that
        # aren't also physics objects.  physics objects will
        # have their position and rotation updated by the
        # engine automatically
        if not self.game_object.physics:
            h = self.game_object.z_rotation
            p = self.game_object.x_rotation
            r = self.game_object.y_rotation
            self.cube.setHpr(h, p, r)
            self.cube.set_pos(*self.game_object.position)

        # If the right control was pressed, and the game object
        # is currently selected, toggle the texture.
        if self.toggle_texture_pressed and self.game_object.is_selected:
            if self.texture_on:
                self.texture_on = False
                self.cube.setTextureOff(1)
            else:
                self.texture_on = True
                self.cube.setTexture(self.cube_texture)

        self.toggle_texture_pressed = False
        self.game_object.is_selected = False
