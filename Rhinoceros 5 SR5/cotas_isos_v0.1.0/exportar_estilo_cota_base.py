# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os

# Obtener la ruta del script actual
script_path = os.path.dirname(__file__)

# Construir la ruta completa del archivo a importar
import_file_path = os.path.join(script_path, "dim_style.3dm")

# Importar el archivo dim_style.3dm
rs.Command('_-Import "{}" _Enter'.format(import_file_path), True)

# Obtener la lista de estilos de cota
dim_styles = rs.DimStyleNames()

# Establecer el estilo de cota "Base" como el predeterminado
if "Base" in dim_styles:
    rs.CurrentDimStyle("Base")
else:
    print("El estilo de cota 'Base' no se encontró en el archivo importado.")
