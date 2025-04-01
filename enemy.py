from panda3d.core import Quat, lookAt, Vec3, TransformState
from game_object import GameObject
from pubsub import pub

class Enemy(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)
        self.health = 100
        # Rotate the model to make it upright
        
        # self.physics.setLinearFactor(Vec3(0, 0, 1))  # Disable Z-axis movement
        # self.physics.setAngularFactor(Vec3(0, 0, 0))  # Disable all rotation
        
        
        
        
        

    def collision(self, other):
        # Print message about the collision
        
        # If hit by a bullet, handle it specially
        if other.kind == "bullet":
            print(f"Enemy {self.kind} was hit by a bullet!")
            # Remove the bullet from the game world
    def dealDamage(self, damage):
        self.health -= damage
        print(f"Enemy {self.kind} took {damage} damage! Health left: {self.health}")
        if self.health <= 0:
            print(f"Enemy {self.kind} has been defeated!")
            pub.sendMessage('enemy_defeated', game_object=self)