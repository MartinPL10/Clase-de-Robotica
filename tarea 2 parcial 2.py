import matplotlib.pyplot as plt
import numpy as np

def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))

# Normalización del ángulo, para que quede entre -180º y 180º
def norm_ang(a):
    return (a + np.pi) % (2*np.pi) - np.pi

def setaxis(x1, x2, y1, y2, z1, z2):
    # this function is used to fix the view to the values of input arguments
    # -----------------------------------------------------------------------
    # ARGUMENTS
    # x1, x2 -> numeric value
    # y1, y2 -> numeric value
    # y1, z2 -> numeric value
    # -----------------------------------------------------------------------
    ax.set_xlim3d(x1,x2)
    ax.set_ylim3d(y1,y2)
    ax.set_zlim3d(z1,z2)
    ax.view_init(elev=30, azim=40)

def fix_system(axis_length, linewidth=3):
    # Fix system function 
    # Plots a 3D centered at [x,y,z] = [0,0,0]
    # -------------------------------------------------------------------
    # Arguments 
    # axis_length -> used to specify the length of the axis, in this case
    #                all axes are of the same length
    # -------------------------------------------------------------------
    x = [-axis_length, axis_length]
    y = [-axis_length, axis_length] 
    z = [-axis_length, axis_length]
    zp = [0, 0]
    # Ejes con colores oscuros y transparencia
    ax.plot3D(x, zp, zp, color='#00008B', linewidth=linewidth, alpha=0.7, label="X")
    ax.plot3D(zp, y, zp, color='#006400', linewidth=linewidth, alpha=0.7, label="Y")
    ax.plot3D(zp, zp, z, color='#8B0000', linewidth=linewidth, alpha=0.7, label="Z")
    ax.legend(loc="upper right")

# Cinemática directa: Calcula dónde está el codo y el efector final
def cinematica_directa(theta_base, theta1, theta2, l1, l2):
    x_codo = l1 * np.cos(theta1)
    z_codo = l1 * np.sin(theta1)

    x_ef = x_codo + l2 * np.cos(theta1 + theta2)
    z_ef = z_codo + l2 * np.sin(theta1 + theta2)

    # Matriz de rotación
    rot = np.array([
        [np.cos(theta_base), -np.sin(theta_base), 0],
        [np.sin(theta_base),  np.cos(theta_base), 0],
        [0,                  0,                   1]
    ])

    # Multiplica la matriz de rotación por el vector de la articulación
    base = np.array([0, 0, 0])
    codo = rot @ np.array([x_codo, 0, z_codo])
    ef   = rot @ np.array([x_ef,   0, z_ef])

    return base, codo, ef

# Cinemática inversa: Con el efector final calcula los ángulos
def cinematica_inversa(px, py, pz, l1, l2, codo="arriba"):
    theta_base = np.arctan2(py, px)
    r = np.hypot(px, py)

    X, Z = r, pz
    dist = np.hypot(X, Z)

    if dist > l1 + l2 or dist < abs(l1 - l2):
        return None

    # Aplicar la ley del coseno
    cos_theta2 = clamp((X**2 + Z**2 - l1**2 - l2**2) / (2*l1*l2))  # Corregido: ** en lugar de *
    theta2 = np.arccos(cos_theta2)

    if codo == "arriba":
        theta2 = -theta2

    k1 = l1 + l2*np.cos(theta2)
    k2 = l2*np.sin(theta2)
    theta1 = np.arctan2(Z, X) - np.arctan2(k2, k1)

    return theta_base, theta1, theta2

# Obtener las posiciones del brazo con cinemática directa y dibujarlo
def dibujar_brazo(tb, t1, t2, l1, l2):
    base, codo, ef = cinematica_directa(tb, t1, t2, l1, l2)
    xs = [base[0], codo[0], ef[0]]
    ys = [base[1], codo[1], ef[1]]
    zs = [base[2], codo[2], ef[2]]
    # Brazo robótico color naranja
    ax.plot(xs, ys, zs, color="orange", linewidth=4, alpha=0.8)
    ax.scatter(xs, ys, zs, color="darkorange", s=50, alpha=0.9)

# Interpolar los ángulos para una mejor animación
def interp_angulo(a0, a1, t):
    diff = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
    return a0 + diff*t

def main():
    print("Animación rotatoria de codo arriba o abajo")

    # Preguntar si quieres que sea codo arriba o abajo
    codo = input("Elige que tipo de configuración quieres, codo 'arriba' o 'abajo': ").strip().lower()
    if codo not in ["arriba","abajo"]:
        print("ERROR: La configuración debe ser 'arriba' o 'abajo'.")
        return

    # Preguntar cuales son los datos que se van a querer utilizar
    l1 = float(input("Longitud l1: "))
    l2 = float(input("Longitud l2: "))
    Xf = float(input("Posición Xf: "))
    Yf = float(input("Posición Yf: "))
    Zf = float(input("Posición Zf: "))

    # Calcular los ángulos finales y si el resultado no es alcanzable mandar un mensaje diciéndolo
    sol = cinematica_inversa(Xf, Yf, Zf, l1, l2, codo)
    if sol is None:
        print("Objetivo no alcanzable.")
        return

    # Mostrar los ángulos finales en grados
    tb_f, t1_f, t2_f = sol
    print(f"θ_base = {np.degrees(tb_f):.2f}°, θ1 = {np.degrees(t1_f):.2f}°, θ2 = {np.degrees(t2_f):.2f}°")

    # Animación
    pasos = 100
    tb0, t10, t20 = 0.0, 0.0, 0.0
    fig = plt.figure(figsize=(8,8))
    global ax
    ax = fig.add_subplot(111, projection="3d")
    lim = l1 + l2 + 2

    # Interpolación de los ángulos
    for n in range(pasos+1):
        t = n/pasos
        tb = interp_angulo(tb0, tb_f, t)
        t1 = interp_angulo(t10, t1_f, t)
        t2 = interp_angulo(t20, t2_f, t)

        # Dibujar todo
        ax.cla()
        setaxis(-lim, lim, -lim, lim, -lim, lim)
        fix_system(lim, 2)
        ax.set_title(f"Brazo 3D - codo {codo}")
        ax.scatter([0], [0], [0], color="black", s=100)  # base
        ax.scatter([Xf], [Yf], [Zf], color="darkred", s=80, alpha=0.8, marker="X") # destino
        dibujar_brazo(tb, t1, t2, l1, l2)

        plt.pause(0.03)

    plt.show()

# Ejecutar el programa - CORRECCIÓN: Esta línea estaba mal escrita
if __name__ == "__main__":
    main()
    