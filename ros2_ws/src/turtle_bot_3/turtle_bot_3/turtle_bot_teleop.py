import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pynput import keyboard

class TeleopNode(Node):
    def __init__(self):
        super().__init__('turtle_bot_teleop') # Nombre del nodo 
        self.pub = self.create_publisher(Twist, 'turtlebot_cmdVel', 10) # Tópico requerido 
        
        # Pedir velocidades al iniciar 
        print("--- Configuración de Velocidades ---")
        self.v_lin = float(input("Velocidad Lineal: "))
        self.v_ang = float(input("Velocidad Angular: "))

        # Diccionario de movimientos
        self.movimientos = {'w': [self.v_lin, 0.0], 's': [-self.v_lin, 0.0], 
                            'a': [0.0, self.v_ang], 'd': [0.0, -self.v_ang]}
        
        self.teclas_pulsadas = set()
        
        # Escuchar teclado sin bloquear el programa 
        keyboard.Listener(on_press=self.presiona, on_release=self.suelta).start()
        print("\n¡Listo! Usa W, A, S, D para mover al robot.")

    def presiona(self, key):
        try:
            if key.char in self.movimientos:
                self.teclas_pulsadas.add(key.char)
                self.enviar_comando()
        except: 
            pass

    def suelta(self, key):
        try:
            if key.char in self.teclas_pulsadas:
                self.teclas_pulsadas.remove(key.char)
            self.enviar_comando() # Publica 0.0 si no quedan teclas 
        except: 
            pass

    def enviar_comando(self):
        msg = Twist()
        # Si hay teclas, tomamos la última presionada para decidir el movimiento 
        if self.teclas_pulsadas:
            ultima_tecla = list(self.teclas_pulsadas)[-1]
            msg.linear.x, msg.angular.z = self.movimientos[ultima_tecla]
        
        self.pub.publish(msg) # Publica el movimiento o el freno 

def main():
    rclpy.init()
    rclpy.spin(TeleopNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
