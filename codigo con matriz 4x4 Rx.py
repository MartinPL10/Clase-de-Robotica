# Import libraries and packages
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np

# =============================================================================
# 🎯 SECCIÓN 1: CONFIGURACIÓN INICIAL - NO MODIFICAR
# =============================================================================
fig, ax = plt.subplots()
ax = plt.axes(projection="3d")

def setaxis(x1, x2, y1, y2, z1, z2):
    """
    🔧 FUNCIÓN: Configura los límites de los ejes
    ⚠️  NO MODIFICAR - Define el área de visualización
    """
    ax.set_xlim3d(x1, x2)
    ax.set_ylim3d(y1, y2)
    ax.set_zlim3d(z1, z2)
    ax.view_init(elev=30, azim=40)

def fix_system(axis_length):
    """
    🔧 FUNCIÓN: Dibuja los ejes coordenados
    ⚠️  NO MODIFICAR - Sistema de referencia fijo
    """
    x = [0, axis_length]
    y = [0, axis_length] 
    z = [0, axis_length]
    zp = [0, 0]
    ax.plot3D(x, zp, zp, color='red', label='X-axis')
    ax.plot3D(zp, y, zp, color='blue', label='Y-axis')
    ax.plot3D(zp, zp, z, color='green', label='Z-axis')
    ax.legend()

def sind(t):
    """⚡ NO MODIFICAR - Seno en grados"""
    return np.sin(t * np.pi / 180)

def cosd(t):
    """⚡ NO MODIFICAR - Coseno en grados"""
    return np.cos(t * np.pi / 180)

def to_homogeneous(v):
    """
    🔄 CONVERSIÓN: 3D → 4D (homogéneas)
    ⚠️  NO MODIFICAR - Conversión esencial para matrices 4x4
    """
    return np.array([v[0], v[1], v[2], 1])

def from_homogeneous(v_h):
    """
    🔄 CONVERSIÓN: 4D → 3D (homogéneas a cartesianas)
    ⚠️  NO MODIFICAR - Conversión inversa
    """
    if v_h[3] != 0:
        return v_h[0:3] / v_h[3]
    else:
        return v_h[0:3]

# =============================================================================
# 🎯 SECCIÓN 2: MATRICES DE TRANSFORMACIÓN - SOLO ROTACIÓN X
# =============================================================================
def RotX(t):
    """
    🔄 MATRIZ: Rotación en X (4x4)
    ✅ Matriz correcta para rotación alrededor del eje X
    📝 t: Ángulo de rotación en grados
    """
    Rx = np.array([
        [1, 0,        0,       0],  # ✅ CORRECTA para eje X
        [0, cosd(t), -sind(t), 0],  # ✅ CORRECTA para eje X
        [0, sind(t),  cosd(t), 0],  # ✅ CORRECTA para eje X
        [0, 0,        0,       1]   # ✅ CORRECTA para eje X
    ])
    return Rx

def Trans(dx=0, dy=0, dz=0):
    """
    🔄 MATRIZ: Traslación (4x4)
    ✅ MODIFICABLE: Cambiar valores por defecto si se desea
    📝 dx: Traslación en X (positivo = derecha, negativo = izquierda)
    📝 dy: Traslación en Y (positivo = arriba, negativo = abajo)  
    📝 dz: Traslación en Z (positivo = adelante, negativo = atrás)
    """
    T = np.array([
        [1, 0, 0, dx],  # 💡 dx controla movimiento en X
        [0, 1, 0, dy],  # 💡 dy controla movimiento en Y
        [0, 0, 1, dz],  # 💡 dz controla movimiento en Z
        [0, 0, 0, 1]
    ])
    return T

def drawVector(v, color='orange', label=None):
    """
    🎨 FUNCIÓN: Dibuja vectores en 3D
    ⚠️  NO MODIFICAR - Visualización de resultados
    """
    if len(v) == 4:
        v_3d = from_homogeneous(v)
    else:
        v_3d = v
    
    deltaX = [0, v_3d[0]]
    deltaY = [0, v_3d[1]]
    deltaZ = [0, v_3d[2]]
    ax.plot3D(deltaX, deltaY, deltaZ, color=color, linewidth=2, label=label)
    ax.scatter(v_3d[0], v_3d[1], v_3d[2], color=color, s=50)

# =============================================================================
# 🎯 SECCIÓN 3: SECUENCIA DE TRANSFORMACIONES - SOLO ROTACIÓN X
# =============================================================================
def transform_sequence(angle, dx=0, dy=0, dz=0):
    """
    🔄 SECUENCIA: Aplica rotación en X y traslación
    ✅ MODIFICABLE: Parámetros de entrada
    📝 angle: Ángulo de rotación en grados (0-360)
    📝 dx: Traslación en X (recommendado: -3 a 3)
    📝 dy: Traslación en Y (recommendado: -3 a 3)
    📝 dz: Traslación en Z (recommendado: -3 a 3)
    """
    ax.cla()
    setaxis(-3, 3, -3, 3, -3, 3)
    fix_system(2)
    
    # Vector original (apuntando a lo largo del eje Y para mejor visualización con RotX)
    v_original = to_homogeneous(np.array([0, 2, 0]))
    drawVector(v_original, color='orange', label='Vector original')
    
    # 1. APLICAR ROTACIÓN EN X
    R = RotX(angle)
    v_rotated = R.dot(v_original)
    drawVector(v_rotated, color='blue', label=f'Rotado {angle}° en X')
    
    # 2. APLICAR TRASLACIÓN (parámetros definidos por usuario)
    T = Trans(dx, dy, dz)
    v_transformed = T.dot(v_rotated)
    
    drawVector(v_transformed, color='green', 
               label=f'Trasladado [{dx}, {dy}, {dz}]')
    
    ax.legend()
    ax.set_title(f'Rotación X: {angle}° | Traslación: [{dx}, {dy}, {dz}]')
    plt.draw()

# =============================================================================
# 🎯 SECCIÓN 4: ZONA DE CONFIGURACIÓN - ¡MODIFICAR AQUÍ LOS VALORES!
# =============================================================================
"""
💡 INSTRUCCIONES DE MODIFICACIÓN:
----------------------------------
1. Elige UNO de los ejemplos below (descomenta quitando el '#')
2. Modifica los valores entre paréntesis ()
3. Ejecuta el código para ver los resultados

📊 VALORES RECOMENDADOS:
- angle: 0 a 360 grados
- dx, dy, dz: -3.0 a 3.0 unidades
"""

# 🔹 Ejemplo 1: Rotación en X de 90° (sin traslación)
transform_sequence(angle=90)

# 🔹 Ejemplo 2: Rotación en X + Traslación en Y
# transform_sequence(angle=45, dy=1.5)

# 🔹 Ejemplo 3: Rotación en X + Traslación en Z
# transform_sequence(angle=60, dz=1.2)

# 🔹 Ejemplo 4: Rotación en X + Traslación completa
# transform_sequence(angle=75, dx=1.0, dy=0.5, dz=0.8)

# 🔹 Ejemplo 5: Rotación en X de 180°
# transform_sequence(angle=180)

# 🔹 Ejemplo 6: Rotación en X negativa
# transform_sequence(angle=-45, dx=1.0)

# 🔹 Ejemplo 7: Experimenta con tus propios valores
# transform_sequence(angle=120, dx=1.5, dy=-1.0, dz=0.5)

# =============================================================================
# 🎯 SECCIÓN 5: EJECUCIÓN FINAL - NO MODIFICAR
# =============================================================================
plt.show()