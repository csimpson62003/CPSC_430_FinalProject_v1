from panda3d.bullet import BulletWorld, BulletBoxShape, BulletRigidBodyNode, BulletCapsuleShape, ZUp, BulletPlaneShape, \
    BulletCharacterControllerNode, BulletDebugNode
from panda3d.core import Vec3, TransformState, VBase3, Point3
from pubsub import pub
from game_object import GameObject
from player import Player
from gun_object import Gun
from enemy import Enemy
from bullet_object import BulletObject
import random


class GameWorld:
    def __init__(self, debugNode):
        self.playerPhysicsObejct = None
        pub.subscribe(self.handle_bullet_event, 'bullet_fire')
        pub.subscribe(self.damage_logic, 'bullet_hit')
        pub.subscribe(self.deleteGameObject, 'enemy_defeated')
        self.properties = {}
        self.game_objects = {}

        self.next_id = 0
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -3))
        self.physics_world.setDebugNode(debugNode)
        self.del_game_objects = []
        self.kind_to_shape = {
            "crate": self.create_box,
            "floor": self.create_box,
            "red box": self.create_box,
            "phillip": self.create_box,
            "denver": self.create_box,
            "mario": self.create_box,
            "bullet": self.create_capsule,
        }
   
    def create_capsule(self, position, size, kind, mass):
        radius = size[0]
        height = size[1]
        shape = BulletCapsuleShape(height, height, ZUp)
        # node = BulletCharacterControllerNode(shape, radius, kind)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setRestitution(0.0)
        # Assign a unique id to identify the node later
        node.setPythonTag("object_id", self.next_id)

        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))

        # self.physics_world.attachCharacter(node)
        self.physics_world.attachRigidBody(node)

        return node

    def create_box(self, position, size, kind, mass):
        # The box shape needs half the size in each dimension
        shape = BulletBoxShape(Vec3(size[0] / 2, size[1] / 2, size[2] / 2))
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        # Assign a unique id to identify the node later
        node.setPythonTag("object_id", self.next_id)
        
        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))
        node.setRestitution(0.0)

        self.physics_world.attachRigidBody(node)

        return node

    def create_physics_object(self, position, kind, size, mass):
        if kind in self.kind_to_shape:
            return self.kind_to_shape[kind](position, size, kind, mass)

        return None

    def create_object(self, position, kind, size, mass, subclass):
        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, physics)

        self.next_id += 1
        if kind == "player":
            self.playerPhysicsObejct = physics
        
        self.game_objects[obj.id] = obj

        pub.sendMessage('create', game_object=obj)
        return obj

    def create_projectile(self, position, kind, size, mass, speed, direction, subclass):
        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, speed, direction, physics)

        self.next_id += 1
        self.game_objects[obj.id] = obj
        print("MADE PROJECTILE")
        pub.sendMessage('create', game_object=obj)
        return obj

    def tick(self, dt):
        self.delete_game_obects()
        for id in self.game_objects:
            self.game_objects[id].tick(dt)

        self.physics_world.doPhysics(dt)
        
        # Check for collisions after physics update
        self.process_collisions()

    def process_collisions(self):
        """Process all collisions that occurred during the physics update"""
        # Get all active pairs of objects from the physics world
        for id in self.game_objects:
            if self.game_objects[id].is_collision_source:
                contacts = self.get_all_contacts(self.game_objects[id])

                for contact in contacts:
                    if contact.getNode1() and contact.getNode1().getPythonTag("owner"):
                        # Notify both objects about the collision
                        contact.getNode1().getPythonTag("owner").collision(self.game_objects[id])
                        self.game_objects[id].collision(contact.getNode1().getPythonTag("owner"))
                        
                    if contact.getNode1() and contact.getNode1().hasPythonTag("object_id"):
                        # Get the object ID and check if it exists in our game objects
                        other_id = contact.getNode1().getPythonTag("object_id")
                        if other_id in self.game_objects:
                            other_obj = self.game_objects[other_id]
                            # Notify both objects about the collision
                            other_obj.collision(self.game_objects[id])


    def load_world(self):
        self.create_object([0, 0, -30], "floor", (1000, 1000, 30), 0, GameObject)
        self.create_object([0, -20, 30], "player", (1, 0.5, 0.25, 0.5), 10, Player)
       # self.create_object([-10, 0, 0], "crate", (1, 1, 0.5), 0, GameObject)
        self.create_object([4,3, 5], "denver", (1, 0.5, 0.25, 0.5), 10, Enemy)  
        self.create_object([5,7, 5], "phillip", (1, 0.5, 0.25, 0.5), 10, Enemy)

       # self.create_object([3, 0, 0], "crate", (5, 2, 1), 10, GameObject)
        self.create_object([-1, 2, 0.5], "gun", (0.5,0.5,0.5), 2, Gun)
        
    def handle_bullet_event(self, weaponDetails):
        if weaponDetails is None:
            return
        print("HANDLE BULLET EVENT")
        position, speed, direction = weaponDetails
        self.create_projectile(position, "bullet", (0.25, 0.25, 0.25), 20, speed, direction, BulletObject)
        
    def damage_logic(self, gameObject1, gameObject2):
        # Check if either object is a bullet and safely remove it
        if isinstance(gameObject1, BulletObject):
            # Check if bullet still exists in game_objects before removing
            if gameObject1.id in self.game_objects:
                self.del_game_objects.append(gameObject1)
        elif isinstance(gameObject2, BulletObject):
            # Check if bullet still exists in game_objects before removing
            if gameObject2.id in self.game_objects:
                self.del_game_objects.append(gameObject2)

    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]

        return None

    def set_property(self, key, value):
        self.properties[key] = value

        pub.sendMessage('property', key=key, value=value)

    def get_nearest(self, from_pt, to_pt):
        # This shows the technique of near object detection using the physics engine.
        fx, fy, fz = from_pt
        tx, ty, tz = to_pt
        result = self.physics_world.rayTestClosest(Point3(fx, fy, fz), Point3(tx, ty, tz))
        return result

    # TODO: use this to demonstrate a teleporting trap
    def get_all_contacts(self, game_object):
        if game_object.physics:
            return self.physics_world.contactTest(game_object.physics).getContacts()

        return []
    def delete_game_obects(self):
        for obj in self.del_game_objects:
            if obj.id in self.game_objects:
                self.physics_world.removeRigidBody(obj.physics)
                del self.game_objects[obj.id]
                pub.sendMessage('remove', game_object=obj)
        self.del_game_objects = []
    def deleteGameObject(self, game_object):
        # Check if the game object exists in the game_objects dictionary
        if game_object.id in self.game_objects:
           self.del_game_objects.append(game_object)