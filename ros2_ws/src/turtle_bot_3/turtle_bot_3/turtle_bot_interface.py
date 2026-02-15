import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button # Importamos botón de matplotlib
import threading
import time
import os 

class TurtleBotInterface(Node):
    def __init__(self):
        super().__init__('turtle_bot_interface')
        
        # Visualización
        self.x_data, self.y_data = [], []
        # Suscripción para GRAFICAR (Posición)
        self.sub_pos = self.create_subscription(Twist, 'turtlebot_position', self.pos_callback, 10)
        
        # Grabación
        # Suscripción para GUARDAR (Acciones)
        self.sub_cmd = self.create_subscription(Twist, 'turtlebot_cmdVel', self.cmd_callback, 10)
        self.log_file = None
        self.start_time = 0

        # Cliente servicio
        self.player_client = self.create_client(Trigger, 'play_recording')

        # Configuración Matplotlib
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2) # Dejar espacio abajo para el botón
        self.line, = self.ax.plot([], [], 'r-', label='Trayectoria')
        self.ax.set_xlim(-2.5, 2.5)
        self.ax.set_ylim(-2.5, 2.5)
        self.ax.set_title("Posición TurtleBot2")
        self.ax.legend()

        # Botón en la interfaz para reproducir (Requerimiento 4)
        self.ax_btn = plt.axes([0.7, 0.05, 0.2, 0.075])
        self.btn = Button(self.ax_btn, 'Reproducir')
        self.btn.on_clicked(self.call_player_service)

        # Pregunta inicial
        self.check_recording()

    def check_recording(self):
        # Usamos input en la consola antes de abrir la gráfica
        save = input("¿Desea guardar el recorrido? (s/n): ").lower() == 's'
        if save:
            fname = input("Nombre del archivo (sin .txt): ")
            self.log_file = open(f"{fname}.txt", "w")
            self.start_time = time.time()
            print(f"--- GRABANDO EN {fname}.txt ---")

    def pos_callback(self, msg):
        # Callback solo para graficar
        self.x_data.append(msg.linear.x)
        self.y_data.append(msg.linear.y)

    def cmd_callback(self, msg):
        # Callback solo para guardar el archivo (Acciones)
        if self.log_file:
            dt = time.time() - self.start_time
            # Guardamos: Tiempo, Vel_Lineal, Vel_Angular
            self.log_file.write(f"{dt:.4f},{msg.linear.x:.4f},{msg.angular.z:.4f}\n")

    def update_plot(self, frame):
        if self.x_data:
            self.line.set_data(self.x_data, self.y_data)
        return self.line,

    def call_player_service(self, event):
    
    	fname = input("\nIngrese nombre de archivo a reproducir (sin .txt): ")
        path_ptr = os.path.join(os.getcwd(), "last_file.ptr")
    
    	with open(os.path.expanduser("~/ros2_ws/last_file.ptr"), "w") as f:
             f.write(fname)
    
    
    	if self.player_client.wait_for_service(timeout_sec=1.0):
             req = Trigger.Request()
             self.player_client.call_async(req)
             print(f"Solicitando reproducción de: {fname}...")
       

    def close_log(self):
        if self.log_file:
            self.log_file.close()

def main(args=None):
    rclpy.init(args=args)
    node = TurtleBotInterface()

    ani = FuncAnimation(node.fig, node.update_plot, interval=100)
    
    # Hilo para ROS
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    plt.show()

    node.close_log()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
