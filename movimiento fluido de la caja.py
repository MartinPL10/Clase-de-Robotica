# Import libraries and packages
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np

# create the fig and ax objects to handle figure and axes of the fixed frame
fig, ax = plt.subplots()

# Use 3d view 
ax = plt.axes(projection="3d")

def setaxis(x1, x2, y1, y2, z1, z2):
    ax.set_xlim3d(x1, x2)
    ax.set_ylim3d(y1, y2)
    ax.set_zlim3d(z1, z2)
    ax.view_init(elev=30, azim=40)

def fix_system(axis_length, linewidth=5):
    x = [-axis_length, axis_length]
    y = [-axis_length, axis_length] 
    z = [-axis_length, axis_length]
    zp = [0, 0]
    ax.plot3D(x, zp, zp, color='red', linewidth=linewidth)
    ax.plot3D(zp, y, zp, color='blue', linewidth=linewidth)
    ax.plot3D(zp, zp, z, color='green', linewidth=linewidth)

def sind(t):
    res = np.sin(t * np.pi / 180)
    return res

def cosd(t):
    res = np.cos(t * np.pi / 180)
    return res

# Matrices de rotación para los tres ejes
def RotX(t):
    Rx = np.array([
        [1, 0, 0],
        [0, cosd(t), -sind(t)],
        [0, sind(t), cosd(t)]
    ])
    return Rx

def RotY(t):
    Ry = np.array([
        [cosd(t), 0, sind(t)],
        [0, 1, 0],
        [-sind(t), 0, cosd(t)]
    ])
    return Ry

def RotZ(t):
    Rz = np.array([
        [cosd(t), -sind(t), 0],
        [sind(t), cosd(t), 0],
        [0, 0, 1]
    ])
    return Rz

def drawVector(p_fin, p_init=[0, 0, 0], color='black', linewidth=1):
    deltaX = [p_init[0], p_fin[0]]
    deltaY = [p_init[1], p_fin[1]]
    deltaZ = [p_init[2], p_fin[2]]
    ax.plot3D(deltaX, deltaY, deltaZ, color=color, linewidth=linewidth)

def drawBox(p1, p2, p3, p4, p5, p6, p7, p8, color='black', alpha=1.0):
    drawScatter(p1, color=color)
    drawScatter(p2, color=color)
    drawScatter(p3, color=color)
    drawScatter(p4, color=color)
    drawScatter(p5, color=color)
    drawScatter(p6, color=color)
    drawScatter(p7, color=color)
    drawScatter(p8, color=color)

    drawVector(p1, p2, color=color)
    drawVector(p2, p3, color=color)
    drawVector(p3, p4, color=color)
    drawVector(p4, p1, color=color)
    drawVector(p5, p6, color=color)
    drawVector(p6, p7, color=color)
    drawVector(p7, p8, color=color)
    drawVector(p8, p5, color=color)
    drawVector(p4, p8, color=color)
    drawVector(p1, p5, color=color)
    drawVector(p3, p7, color=color)
    drawVector(p2, p6, color=color)

def drawScatter(point, color='black', marker='o'):
    ax.scatter(point[0], point[1], point[2], marker=marker, color=color)

def rotate_box_simultaneous(points, angle_z=0, angle_y=0, angle_x=0):
    """Aplica rotaciones simultáneas en los tres ejes"""
    # Matriz de rotación compuesta: Rz * Ry * Rx
    R_total = RotZ(angle_z) @ RotY(angle_y) @ RotX(angle_x)
    
    rotated_points = []
    for point in points:
        rotated_points.append(R_total.dot(point))
    
    return rotated_points

def animate_simultaneous_rotation(total_angle_z=45, total_angle_y=30, total_angle_x=15, steps=60, delay=0.02):
    """Anima rotaciones simultáneas en los tres ejes"""
    angle_step_z = total_angle_z / steps
    angle_step_y = total_angle_y / steps
    angle_step_x = total_angle_x / steps
    
    for step in range(steps + 1):
        ax.cla()
        
        # Configurar ejes y vista
        setaxis(-15, 15, -15, 15, -15, 15)
        fix_system(10, 1)
        
        # Calcular ángulos actuales
        current_angle_z = step * angle_step_z
        current_angle_y = step * angle_step_y
        current_angle_x = step * angle_step_x
        
        # Dibujar la caja original (en gris)
        drawBox(*original_points, color='gray', alpha=0.5)
        
        # Aplicar rotaciones simultáneas y dibujar la caja rotada
        rotated_points = rotate_box_simultaneous(
            original_points,
            angle_z=current_angle_z,
            angle_y=current_angle_y,
            angle_x=current_angle_x
        )
        drawBox(*rotated_points, color='red')
        
        # Actualizar título con los ángulos actuales
        ax.set_title(f'Rotación Simultánea:\nZ: {current_angle_z:.1f}° / {total_angle_z}°\n'
                    f'Y: {current_angle_y:.1f}° / {total_angle_y}°\n'
                    f'X: {current_angle_x:.1f}° / {total_angle_x}°')
        
        plt.draw()
        plt.pause(delay)
    
    return rotated_points

# Puntos iniciales de la caja
p1_init = [0, 0, 0]
p2_init = [7, 0, 0]
p3_init = [7, 0, 3]
p4_init = [0, 0, 3]
p5_init = [0, 2, 0]
p6_init = [7, 2, 0]
p7_init = [7, 2, 3]
p8_init = [0, 2, 3]

original_points = [p1_init, p2_init, p3_init, p4_init, p5_init, p6_init, p7_init, p8_init]

# Animación de rotaciones simultáneas
print("Animación de rotaciones simultáneas: 45° Z + 30° Y + 15° X")
final_points = animate_simultaneous_rotation(
    total_angle_z=45,
    total_angle_y=30, 
    total_angle_x=15,
    steps=90,      # Más pasos para mayor fluidez
    delay=0.015    # Menor delay para mayor fluidez
)

# Mostrar el resultado final con posición inicial y final
ax.cla()
setaxis(-15, 15, -15, 15, -15, 15)
fix_system(10, 1)

# Dibujar la caja inicial (gris) y final (rojo)
drawBox(*original_points, color='gray', alpha=0.5)
drawBox(*final_points, color='red')

ax.set_title('Resultado Final: Rotación Simultánea\n45° Z + 30° Y + 15° X')
plt.draw()

# Mostrar la ventana al final
plt.show()

# Imprimir coordenadas finales
print("\nCoordenadas finales después de rotación simultánea:")
print("45° Z + 30° Y + 15° X")
for i, point in enumerate(final_points, 1):
    print(f"P{i}: [{point[0]:.2f}, {point[1]:.2f}, {point[2]:.2f}]")

# También mostrar la matriz de rotación compuesta final
print("\nMatriz de rotación compuesta final (Rz * Ry * Rx):")
R_final = RotZ(45) @ RotY(30) @ RotX(15)
print(R_final)