import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np

# Configuración inicial
fig, ax = plt.subplots()
ax = plt.axes(projection="3d")

def setaxis(x1, x2, y1, y2, z1, z2):
    ax.set_xlim3d(x1, x2)
    ax.set_ylim3d(y1, y2)
    ax.set_zlim3d(z1, z2)
    ax.view_init(elev=30, azim=40)

def fix_system(axis_length):
    x = [0, axis_length]
    y = [0, axis_length] 
    z = [0, axis_length]
    zp = [0, 0]
    ax.plot3D(x, zp, zp, color='red', label='X-axis')
    ax.plot3D(zp, y, zp, color='blue', label='Y-axis')
    ax.plot3D(zp, zp, z, color='green', label='Z-axis')
    ax.legend()

def sind(t):
    return np.sin(t * np.pi / 180)

def cosd(t):
    return np.cos(t * np.pi / 180)

def to_homogeneous(v):
    return np.array([v[0], v[1], v[2], 1])

def from_homogeneous(v_h):
    if v_h[3] != 0:
        return v_h[0:3] / v_h[3]
    else:
        return v_h[0:3]

# Matriz de rotación en Y
def RotY(t):
    Ry = np.array([
        [cosd(t),  0,       sind(t),  0],
        [0,        1,       0,        0],
        [-sind(t), 0,       cosd(t),  0],
        [0,        0,       0,        1]
    ])
    return Ry

# Matriz de traslación en X
def Trans(dx=0):
    T = np.array([
        [1, 0, 0, dx],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    return T

def drawVector(v, color='orange', label=None):
    if len(v) == 4:
        v_3d = from_homogeneous(v)
    else:
        v_3d = v
    
    deltaX = [0, v_3d[0]]
    deltaY = [0, v_3d[1]]
    deltaZ = [0, v_3d[2]]
    ax.plot3D(deltaX, deltaY, deltaZ, color=color, linewidth=2, label=label)
    ax.scatter(v_3d[0], v_3d[1], v_3d[2], color=color, s=50)

# Animación: Rotación Y + Traslación X (simultánea)
def animate_rotation_y():
    for frame in range(0, 91, 2):  # 0° a 90°
        ax.cla()
        setaxis(-3, 3, -3, 3, -3, 3)
        fix_system(2)
        
        # Vector original en X
        v_original = to_homogeneous(np.array([2, 0, 0]))
        drawVector(v_original, color='orange', label='Vector original')
        
        # Matriz combinada: Rotación Y + Traslación X (simultánea)
        R = RotY(frame)  # Rotación progresiva
        T = Trans(1.5 * (frame / 90.0))  # Traslación progresiva
        
        # Aplicar ambas transformaciones: Primero rotar, luego trasladar
        v_transformed = T.dot(R.dot(v_original))
        
        # Dibujar vector transformado
        drawVector(v_transformed, color='green', 
                  label=f'Rotado {frame}° en Y + Trasladado {1.5*(frame/90.0):.1f} en X')
        
        ax.legend()
        ax.set_title(f'Rotación Y + Traslación X Simultánea')
        plt.draw()
        plt.pause(0.05)
    
    plt.show()

# Ejecutar animación
animate_rotation_y()