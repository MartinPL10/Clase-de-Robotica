"""
SIMULACIÓN CINEMÁTICA DE ROBOT SCARA (RRPR - 4-DOF)
(Modificado: Movimiento añadido a Eslabón 1. Rango Z a la mitad.
 Línea de orientación añadida al gripper.)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

# ------------------ Módulo de Entrada de Datos ------------------
def solicitar_valor_numerico(mensaje, valor_por_defecto=None):
    """Solicita y valida entrada numérica del usuario"""
    while True:
        entrada = input(mensaje).strip().replace(',', '.')
        if not entrada and valor_por_defecto is not None:
            return float(valor_por_defecto)
        try:
            return float(entrada)
        except ValueError:
            print("Entrada no válida. Introduce un valor numérico.")

# ------------------ Módulo de Transformaciones DH ------------------
def matriz_transformacion_DH(angulo_grados, desplazamiento, longitud, angulo_torsion_grados=0.0):
    """Calcula matriz de transformación homogénea usando parámetros DH"""
    theta = np.radians(angulo_grados)
    alpha = np.radians(angulo_torsion_grados)

    cos_theta, sin_theta = np.cos(theta), np.sin(theta)
    cos_alpha, sin_alpha = np.cos(alpha), np.sin(alpha)

    return np.array([
        [cos_theta, -sin_theta*cos_alpha,  sin_theta*sin_alpha, longitud*cos_theta],
        [sin_theta,  cos_theta*cos_alpha, -cos_theta*sin_alpha, longitud*sin_theta],
        [0,           sin_alpha,            cos_alpha,            desplazamiento],
        [0,           0,                    0,                    1]
    ], dtype=np.float64)

# ------------------ Módulo de Visualización de Ejes ------------------
def dibujar_ejes(ax, matriz_T, longitud=150):
    """Dibuja los ejes X (rojo), Y (verde), Z (azul) para una matriz dada"""
    origen = matriz_T[:3, 3]
    eje_x_dir = matriz_T[:3, 0]
    eje_y_dir = matriz_T[:3, 1]
    eje_z_dir = matriz_T[:3, 2]

    ax.plot([origen[0], origen[0] + longitud * eje_x_dir[0]],
            [origen[1], origen[1] + longitud * eje_x_dir[1]],
            [origen[2], origen[2] + longitud * eje_x_dir[2]], color='red', linewidth=2.5)
    ax.plot([origen[0], origen[0] + longitud * eje_y_dir[0]],
            [origen[1], origen[1] + longitud * eje_y_dir[1]],
            [origen[2], origen[2] + longitud * eje_y_dir[2]], color='green', linewidth=2.5)
    ax.plot([origen[0], origen[0] + longitud * eje_z_dir[0]],
            [origen[1], origen[1] + longitud * eje_z_dir[1]],
            [origen[2], origen[2] + longitud * eje_z_dir[2]], color='blue', linewidth=2.5)

# ------------------ Módulo de Cálculo Cinemático ------------------
def calcular_cinematica_directa(angulo_articulacion1, angulo_articulacion2,
                                desplazamiento_articulacion3_z, angulo_articulacion4,
                                longitud_eslabon1, longitud_eslabon2,
                                altura_base, offset_vertical, radio_efector):
    """Calcula la posición y orientación (modelo RRPR)"""

    LONGITUD_HERRAMIENTA = 300.0 # Longitud fija del vástago
    variacion_altura = float(desplazamiento_articulacion3_z - altura_base)

    # Cadena cinemática (RRPR)
    T0_a_1 = matriz_transformacion_DH(angulo_articulacion1, 0.0, longitud_eslabon1, 0.0)
    T1_a_2 = matriz_transformacion_DH(angulo_articulacion2, offset_vertical, longitud_eslabon2, 0.0)
    T2_a_3 = matriz_transformacion_DH(0.0, variacion_altura, 0.0, 0.0)
    T3_a_4 = matriz_transformacion_DH(angulo_articulacion4, 0.0, 0.0, 0.0)

    # Cadena de transformación completa
    T0_a_2 = T0_a_1 @ T1_a_2
    T0_a_3 = T0_a_2 @ T2_a_3
    T0_a_4 = T0_a_3 @ T3_a_4

    # Puntos de referencia
    origen_sistema = np.array([0, 0, 0])
    punto_base = np.array([0, 0, altura_base])

    P_base_global = np.array([0, 0, altura_base, 1])

    posicion_articulacion1 = (T0_a_1 @ P_base_global)[:3]
    posicion_articulacion2 = (T0_a_2 @ P_base_global)[:3]

    # Punto de la muñeca (base del vástago)
    punto_muñeca = (T0_a_3 @ P_base_global)[:3]

    # Punta de la herramienta (Efector final)
    eje_z_efector = T0_a_4[:3, 2]
    extremo_efector = punto_muñeca + eje_z_efector * LONGITUD_HERRAMIENTA

    # Geometría del efector (círculo)
    angulo_actual = np.radians(angulo_articulacion4)
    angulos_circulo = np.linspace(0, 2*np.pi, 60)

    circulo_x = extremo_efector[0] + radio_efector * np.cos(angulos_circulo + angulo_actual)
    circulo_y = extremo_efector[1] + radio_efector * np.sin(angulos_circulo + angulo_actual)
    circulo_z = np.full_like(circulo_x, extremo_efector[2])

    punto_referencia_x = extremo_efector[0] + radio_efector * np.cos(angulo_actual)
    punto_referencia_y = extremo_efector[1] + radio_efector * np.sin(angulo_actual)
    punto_referencia_z = extremo_efector[2]

    return (origen_sistema, punto_base,
            posicion_articulacion1, posicion_articulacion2, punto_muñeca,
            extremo_efector, circulo_x, circulo_y, circulo_z,
            punto_referencia_x, punto_referencia_y, punto_referencia_z,
            T0_a_1, T0_a_2, T0_a_3, T0_a_4)

# ------------------ Módulo de Visualización (Gripper con Línea de Orientación) ------------------
def visualizar_configuracion_robot(eje_3d, origen, base,
                                   art1, art2, muñeca, efector,
                                   circ_x, circ_y, circ_z,
                                   punto_ref_x, punto_ref_y, punto_ref_z,
                                   limite,
                                   T0_a_1, T0_a_2, T0_a_3, T_efector): # T_efector IS T0_a_4
    """Dibuja el robot SCARA (RRPR) con línea de orientación en el gripper"""

    eje_3d.set_xlim(-limite, limite)
    eje_3d.set_ylim(-limite, limite)
    eje_3d.set_zlim(0, max(1600, limite))
    eje_3d.set_xlabel('Coordenada X (mm)')
    eje_3d.set_ylabel('Coordenada Y (mm)')
    eje_3d.set_zlabel('Coordenada Z (mm)')
    eje_3d.set_title("Robot SCARA - Configuración Cinemática")
    eje_3d.set_facecolor('white')
    eje_3d.view_init(elev=25, azim=45)

    # --- DIBUJAR EJES DE COORDENADAS ---
    T_Base = np.eye(4)
    T_Base[:3, 3] = base
    dibujar_ejes(eje_3d, T_Base, longitud=200) # Eje Base

    T_Frame1 = T0_a_1.copy()
    T_Frame1[:3, 3] = art1
    dibujar_ejes(eje_3d, T_Frame1, longitud=150) # Eje Articulación 1

    T_Frame2 = T0_a_2.copy()
    T_Frame2[:3, 3] = art2
    dibujar_ejes(eje_3d, T_Frame2, longitud=150) # Eje Articulación 2

    T_Frame_Efector = T_efector.copy() # T_efector es T0_a_4
    T_Frame_Efector[:3, 3] = efector   # Posición = punta
    dibujar_ejes(eje_3d, T_Frame_Efector, longitud=100) # Eje Articulación 4 (Rotación)
    # --- FIN DIBUJAR EJES ---

    # Eslabón 0 (Base)
    eje_3d.scatter(*origen, color='red', s=80)
    eje_3d.plot([origen[0], base[0]], [origen[1], base[1]],
                [origen[2], base[2]], color='red', linewidth=4)
    eje_3d.text(base[0] + 50, base[1] + 50, base[2] + 20, "Eslabón 0 (Base)", color='black', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))


    # Eslabón 1
    eje_3d.plot([base[0], art1[0]], [base[1], art1[1]],
                [base[2], art1[2]], color='#FF5733', linewidth=6)
    eje_3d.text((base[0] + art1[0]) / 2 + 30, (base[1] + art1[1]) / 2 + 30, (base[2] + art1[2]) / 2 + 20,
                "Eslabón 1", color='black', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))

    # Eslabón 2
    eje_3d.plot([art1[0], art2[0]], [art1[1], art2[1]],
                [art1[2], art2[2]], color='#33FF57', linewidth=6)
    eje_3d.text((art1[0] + art2[0]) / 2 + 30, (art1[1] + art2[1]) / 2 + 30,
                (art1[2] + art2[2]) / 2 + 20,
                "Eslabón 2", color='black', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))


    # 1. Guía/Collarín (Sleeve) en el Eslabón 2
    alto_guia = 60.0
    punto_arriba = [art2[0], art2[1], art2[2] + alto_guia / 2]
    punto_abajo = [art2[0], art2[1], art2[2] - alto_guia / 2]
    eje_3d.plot([punto_arriba[0], punto_abajo[0]], [punto_arriba[1], punto_abajo[1]],
                [punto_arriba[2], punto_abajo[2]], color='#303030', linewidth=12) # Gris oscuro
    eje_3d.text(art2[0] + 50, art2[1] + 50, art2[2], "Guía Z", color='black', fontsize=8,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))


    # 2. Articulación 3 (Pistón / Actuador Z) - OCULTO

    # 3. Eslabón 3 (Vástago Rígido)
    eje_3d.plot([muñeca[0], efector[0]], [muñeca[1], efector[1]],
                [muñeca[2], efector[2]], color='#C0C0C0', linewidth=6) # <-- Color Plateado
    eje_3d.text((muñeca[0] + efector[0]) / 2 + 30, (muñeca[1] + efector[1]) / 2 + 30,
                (muñeca[2] + efector[2]) / 2,
                "Eslabón 3 (Vástago)", color='black', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))


    # Efector final (Gripper)
    eje_3d.plot(circ_x, circ_y, circ_z, color='green', linewidth=4) # Círculo
    eje_3d.scatter(punto_ref_x, punto_ref_y, punto_ref_z, color='red', s=50) # Punto rojo

    # --- NUEVA LÍNEA DE ORIENTACIÓN ---
    # Dibuja una línea desde el centro del efector (efector) hasta el punto rojo
    eje_3d.plot([efector[0], punto_ref_x], [efector[1], punto_ref_y], [efector[2], punto_ref_z],
                color='purple', linewidth=3) # Línea morada gruesa
    # --- FIN NUEVA LÍNEA ---

    # Puntos de articulación
    eje_3d.scatter(art1[0], art1[1], art1[2], color='black', s=25)
    eje_3d.scatter(art2[0], art2[1], art2[2], color='black', s=40) #Punto de la guía
    eje_3d.scatter(muñeca[0], muñeca[1], muñeca[2], color='black', s=25)
    eje_3d.text(efector[0] + 50, efector[1] + 50, efector[2] + 20,
                "Efector Final", color='black', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.7, pad=0.5, edgecolor='none'))


# ------------------ Módulo de Animación ------------------
def ejecutar_simulacion_movimiento(long_eslabon1, long_eslabon2,
                                   longitud_minima_brazo, longitud_maxima_brazo, radio_efector,
                                   offset_vertical, num_frames=180,
                                   angulo_inicial_art1=0.0, angulo_final_art1=90.0,
                                   angulo_final_art2=120.0,
                                   rotacion_total_art4=270.0):
    """Ejecuta la simulación animada del movimiento del robot con todos los ejes móviles"""

    ALTURA_BASE = 800.0

    if longitud_maxima_brazo < longitud_minima_brazo:
        longitud_minima_brazo, longitud_maxima_brazo = longitud_maxima_brazo, longitud_minima_brazo

    # Secuencias de movimiento
    punto_medio_z = (longitud_maxima_brazo + longitud_minima_brazo) / 2.0
    valores_longitud = np.linspace(longitud_maxima_brazo, punto_medio_z, num_frames) # Movimiento Articulación 3 (Z)
    valores_angulo_art1 = np.linspace(angulo_inicial_art1, angulo_final_art1, num_frames) # Movimiento Articulación 1
    valores_angulo_art2 = np.linspace(0, angulo_final_art2, num_frames)                     # Movimiento Articulación 2
    valores_angulo_art4 = np.linspace(0, rotacion_total_art4, num_frames)                   # Movimiento Articulación 4 (Muñeca)

    figura = plt.figure(figsize=(10, 8))
    eje_3d = figura.add_subplot(111, projection='3d')
    limite_visualizacion = max(1600, long_eslabon1 + long_eslabon2 + 300)

    def actualizar_cuadro(indice):
        eje_3d.cla()
        (origen, base, art1, art2, muñeca, efector,
         cx, cy, cz, px, py, pz,
         T0_a_1, T0_a_2, T0_a_3, T_efector) = calcular_cinematica_directa(
            valores_angulo_art1[indice], # Usa el ángulo variable
            valores_angulo_art2[indice],
            valores_longitud[indice],
            valores_angulo_art4[indice],
            long_eslabon1, long_eslabon2, ALTURA_BASE,
            offset_vertical, radio_efector)

        visualizar_configuracion_robot(eje_3d, origen, base, art1, art2, muñeca, efector,
                                       cx, cy, cz, px, py, pz,
                                       limite_visualizacion,
                                       T0_a_1, T0_a_2, T0_a_3, T_efector)
        return []

    animacion = animation.FuncAnimation(figura, actualizar_cuadro, frames=num_frames,
                                        interval=40, blit=False, repeat=False)
    plt.show()

# ------------------ Programa Principal ------------------
if __name__ == "__main__":

    print("CONFIGURACIÓN DEL ROBOT SCARA (RRPR) - MODELO INDUSTRIAL")
    print("=" * 50)

    longitud_eslabon1 = solicitar_valor_numerico("Longitud del brazo proximal (Eslabón 1) [650]: ", 650.0)
    longitud_eslabon2 = solicitar_valor_numerico("Longitud del brazo distal (Eslabón 2) [720]: ", 720.0)
    longitud_min_brazo = solicitar_valor_numerico("Altura mínima de trabajo (Art. 3 - Z) [350]: ", 350.0)
    longitud_max_brazo = solicitar_valor_numerico("Altura máxima de trabajo (Art. 3 - Z) [820]: ", 820.0)
    radio_efector = solicitar_valor_numerico("Diámetro del gripper [85]: ", 85.0)
    offset_z = solicitar_valor_numerico("Compensación vertical (Eslabón 2) [-35]: ", -35.0)

    num_frames = int(solicitar_valor_numerico("Número de frames [180]: ", 180))

    angulo_inicial_art1 = solicitar_valor_numerico("Ángulo inicial articulación 1 [0]: ", 0.0)
    angulo_final_art1 = solicitar_valor_numerico("Ángulo final articulación 1 [90]: ", 90.0)

    angulo_final_art2 = solicitar_valor_numerico("Ángulo final articulación 2 [120]: ", 120.0)
    rotacion_total_art4 = solicitar_valor_numerico("Rotación total articulación 4 (Muñeca) [270]: ", 270.0)

    ejecutar_simulacion_movimiento(longitud_eslabon1, longitud_eslabon2,
                                   longitud_min_brazo, longitud_max_brazo, radio_efector, offset_z,
                                   num_frames=num_frames,
                                   angulo_inicial_art1=angulo_inicial_art1, angulo_final_art1=angulo_final_art1,
                                   angulo_final_art2=angulo_final_art2,
                                   rotacion_total_art4=rotacion_total_art4)