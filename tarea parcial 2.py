import matplotlib.pyplot as plt
import numpy as np

def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))

def norm_ang(a):
    return (a + np.pi) % (2*np.pi) - np.pi

def cinematica_directa(theta1, theta2, l1, l2):
    x1 = l1 * np.cos(theta1)
    y1 = l1 * np.sin(theta1)
    x2 = x1 + l2 * np.cos(theta1 + theta2)
    y2 = y1 + l2 * np.sin(theta1 + theta2)
    return (0,0), (x1,y1), (x2,y2)

def cinematica_inversa(Xf, Yf, l1, l2, codo):
    r2 = Xf**2 + Yf**2
    r = np.sqrt(r2)
    if r > l1 + l2 or r < abs(l1 - l2):
        return None

    cos_alpha2 = clamp((r2 - l1**2 - l2**2) / (2*l1*l2))
    alpha2 = np.arccos(cos_alpha2)
    cos_alpha1 = clamp((r2 + l1**2 - l2**2) / (2*l1*r))
    alpha1 = np.arccos(cos_alpha1)
    phi = np.arctan2(Yf, Xf)

    theta2_pos = alpha2
    theta2_neg = -alpha2
    
    theta1_pos = phi - np.arctan2(l2*np.sin(theta2_pos), l1 + l2*np.cos(theta2_pos))
    theta1_neg = phi - np.arctan2(l2*np.sin(theta2_neg), l1 + l2*np.cos(theta2_neg))
    
    soluciones = [(theta2_pos, theta1_pos), (theta2_neg, theta1_neg)]

    candidatos = []
    for theta2, theta1 in soluciones:
        _, (x_codo, y_codo), (x_ef, y_ef) = cinematica_directa(theta1, theta2, l1, l2)
        candidatos.append((theta1, theta2, y_codo))

    if codo == "arriba":
        theta1_final, theta2_final, _ = max(candidatos, key=lambda x: x[2])
    else:
        theta1_final, theta2_final, _ = min(candidatos, key=lambda x: x[2])

    return theta1_final, theta2_final

def dibujar_ejes(ax, longitud=5):
    # Eje X horizontal - azul oscuro con transparencia
    ax.plot([-longitud, longitud], [0, 0], color="#00008B", linewidth=2, alpha=0.7, label="X")
    # Eje Y vertical - verde oscuro con transparencia
    ax.plot([0, 0], [-longitud, longitud], color="#006400", linewidth=2, alpha=0.7, label="Y")
    
    # Añadir leyenda de los ejes
    ax.legend(loc="upper right")

def dibujar_brazo(ax, theta1, theta2, l1, l2, efector_final=None):
    base, codo, ef = cinematica_directa(theta1, theta2, l1, l2)
    if efector_final is not None:
        ef = efector_final
    xs = [base[0], codo[0], ef[0]]
    ys = [base[1], codo[1], ef[1]]
    # Brazo robótico color naranja
    ax.plot(xs, ys, color="orange", linewidth=4, alpha=0.8)
    ax.scatter(xs, ys, color="darkorange", s=40, alpha=0.9)

def interp_angulo(a0, a1, t):
    diff = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
    return a0 + diff*t

def main():
    print("Animación planar de codo arriba o abajo")

    codo = input("Elige que tipo de configuración quieres, codo 'arriba' o 'abajo': ").strip().lower()
    if codo not in ["arriba","abajo"]:
        print("ERROR: La configuración debe ser 'arriba' o 'abajo'.")
        return

    l1 = float(input("Longitud l1: "))
    l2 = float(input("Longitud l2: "))
    Xf = float(input("Posición Xf: "))
    Yf = float(input("Posición Yf: "))

    sol = cinematica_inversa(Xf, Yf, l1, l2, codo)
    if sol is None:
        print("Objetivo no alcanzable.")
        return

    theta1_final, theta2_final = sol
    print(f"theta1 = {np.degrees(theta1_final):.2f}°, theta2 = {np.degrees(theta2_final):.2f}°")

    theta1_init, theta2_init = 0.0, 0.0
    pasos = 100
    fig, ax = plt.subplots(figsize=(6,6))
    lim = l1 + l2 + 1

    for n in range(pasos+1):
        t = n/pasos
        th1 = interp_angulo(theta1_init, theta1_final, t)
        th2 = interp_angulo(theta2_init, theta2_final, t)

        ax.cla()
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.set_title(f"Animación planar - codo {codo}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        dibujar_ejes(ax, l1+l2)
        # Punto objetivo en color rojo oscuro
        ax.scatter([Xf],[Yf], color="darkred", s=80, alpha=0.8, marker="X")

        ef_final = (Xf, Yf) if n == pasos else None
        dibujar_brazo(ax, th1, th2, l1, l2, efector_final=ef_final)

        plt.pause(0.03)

    plt.show()

if __name__ == "__main__":
    main()