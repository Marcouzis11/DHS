import os

# Carpeta donde está ESTE archivo
base_dir = os.path.dirname(os.path.abspath(__file__))

# Carpeta output dentro de python
output_dir = os.path.join(base_dir, "output")

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

# Ruta completa del archivo
ruta = os.path.join(output_dir, "codigoIntermedio.txt")

print("Escribiendo en:", ruta)

with open(ruta, "w") as f:
    f.write("Hola desde prueba\n")
    f.write("Si ves esto, funciona\n")

print("Archivo escrito correctamente.")