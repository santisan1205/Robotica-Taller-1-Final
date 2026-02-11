#1/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from geometry_msgs.msg import Twist
import os
import time

class TurtleBotPlayer(Node):
    def __init__(self):
        super().__init__('turtle_bot_player')
        # Definimos el servicio Trigger (sin campos de texto para evitar errores)
        self.srv = self.create_service(Trigger, 'play_recording', self.play_callback)
        self.publisher = self.create_publisher(Twist, 'turtlebot_cmdVel', 10)
        self.get_logger().info('Nodo Player listo y esperando servicio Trigger...')

    def play_callback(self, request, response):
    # 1. Leer el nombre del archivo del puntero temporal
        ptr_path = os.path.expanduser("~/ros2_ws/last_file.ptr")
        with open(ptr_path, "r") as f:
            target_name = f.read().strip()
    
        filename = os.path.expanduser(f"~/ros2_ws/{target_name}.txt")
    
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
        
            self.get_logger().info(f"Iniciando reproduccion de {len(lines)} lineas...")
        
        # IMPORTANTE: Reiniciamos el tiempo justo antes de empezar a publicar
            start_replay = time.time()
        
            for line in lines:
                partes = line.strip().split(',')
                tiempo_grabado = float(partes[0])
                v_lineal = float(partes[1])
                v_angular = float(partes[2])
                
                # Esperar hasta que llegue el momento de ejecutar este comando
                while (time.time() - start_replay) < tiempo_grabado:
                    time.sleep(0.001) # Micro-espera para no saturar el CPU
            
                # Publicar el comando
                msg = Twist()
                msg.linear.x = v_lineal
                msg.angular.z = v_angular
                self.publisher.publish(msg)
            
        # Detener el robot al final
            self.publisher.publish(Twist())
        
            response.success = True
            response.message = "Reproduccion finalizada con exito"
            self.get_logger().info("Reproduccion finalizada")
            
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().error(f"Error: {e}")
        
        return response

def main(args=None):
    rclpy.init(args=args)
    node = TurtleBotPlayer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
