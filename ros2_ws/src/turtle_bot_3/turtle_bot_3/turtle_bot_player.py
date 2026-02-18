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
        # Definir el servicio Trigger
        self.srv = self.create_service(Trigger, 'play_recording', self.play_callback)
        self.publisher = self.create_publisher(Twist, 'turtlebot_cmdVel', 10)
        self.get_logger().info('Nodo Player listo y esperando servicio Trigger...')

    def play_callback(self, request, response):
        try:
            # Detectar la carpeta actual
            
            current_dir = os.getcwd()
            ptr_path = os.path.join(current_dir, "last_file.ptr")
            
            # Verificar si el archivo de control existe
            if not os.path.exists(ptr_path):
                self.get_logger().error(f"No se encontro el archivo: {ptr_path}")
                response.success = False
                response.message = "Error: No se ha seleccionado archivo en la interfaz."
                return response

            # Leer el nombre del archivo guardado por la interfaz
            with open(ptr_path, "r") as f:
                target_name = f.read().strip()
        
            # Construir la ruta al archivo .txt
            filename = os.path.join(current_dir, f"{target_name}.txt")
        
            if not os.path.exists(filename):
                self.get_logger().error(f"No existe el archivo de datos: {filename}")
                response.success = False
                response.message = f"Archivo '{target_name}.txt' no encontrado."
                return response

            # Leer las lineas del archivo
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            self.get_logger().info(f"Iniciando reproduccion de {len(lines)} lineas...")
            
            # Lógica de reproducción con tiempo sincronizado
            start_replay = time.time()
            
            for line in lines:
                partes = line.strip().split(',')
                # Validar que la linea tenga los 3 datos: Tiempo, Lineal, Angular
                if len(partes) < 3:
                    continue
                    
                tiempo_grabado = float(partes[0])
                v_lineal = float(partes[1])
                v_angular = float(partes[2])
                    
                # Esperar hasta que llegue el momento de ejecutar este comando
                while (time.time() - start_replay) < tiempo_grabado:
                    time.sleep(0.001) 
            
                # Publicar el comando de velocidad al robot
                msg = Twist()
                msg.linear.x = v_lineal
                msg.angular.z = v_angular
                self.publisher.publish(msg) 
            
            # Detener el robot al terminar
            self.publisher.publish(Twist())
            
            response.success = True
            response.message = "Reproduccion finalizada con exito"
            self.get_logger().info("Reproduccion finalizada")
                
        except Exception as e:
            response.success = False
            response.message = f"Error interno: {str(e)}"
            self.get_logger().error(f"Error en play_callback: {e}")
            
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
