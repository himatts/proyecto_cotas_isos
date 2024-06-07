# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import os

def main():
    # Obtiene la ruta del directorio del script
    script_dir = os.path.dirname(__file__)
    
    # Ruta relativa del archivo a importar
    file_name = "referencia_dim_hombre-objeto.3dm"
    file_path = os.path.join(script_dir, file_name)
    
    # Nombre de la capa principal
    main_layer = "Figura-Humana"
    new_main_layer = "Figura-Humana TU-HOME"
    temp_layer = "TempLayer"
    
    # Importa el archivo de Rhino en el documento
    rs.Command('_-Import "{}" Enter'.format(file_path))
    
    # Encuentra el grupo insertado
    groups = rs.GroupNames()
    if not groups:
        return
    
    # Supongamos que el grupo importado es el último grupo en la lista
    group_name = groups[-1]
    group_objects = rs.ObjectsByGroup(group_name)
    
    # Verifica que los objetos del grupo coincidan con la estructura esperada
    layer_structure = {
        "Figura-Humana": "Figura-Humana",
        "Figura-Humana::Figura-Humana_linea": "Figura-Humana_linea",
        "Figura-Humana::Figura-Humana_cota": "Figura-Humana_cota"
    }
    
    for obj in group_objects:
        obj_name = rs.ObjectName(obj)
        obj_layer = rs.ObjectLayer(obj)
        
        if obj_name != layer_structure.get(obj_layer):
            return
    
    # Verifica si la nueva capa ya existe y mueve los objetos a una capa temporal
    if rs.IsLayer(new_main_layer):
        if not rs.IsLayer(temp_layer):
            rs.AddLayer(temp_layer)
        
        # Mueve los objetos de la capa y subcapas a la capa temporal
        sub_layers = rs.LayerChildren(new_main_layer)
        if sub_layers:
            for sub_layer in sub_layers:
                objects_in_sub_layer = rs.ObjectsByLayer(sub_layer)
                if objects_in_sub_layer:
                    rs.ObjectLayer(objects_in_sub_layer, temp_layer)
        objects_in_layer = rs.ObjectsByLayer(new_main_layer)
        if objects_in_layer:
            rs.ObjectLayer(objects_in_layer, temp_layer)
        
        rs.PurgeLayer(new_main_layer)
        # Verificar si la capa se ha eliminado correctamente
        if rs.IsLayer(new_main_layer):
            return
    
    # Renombra la capa principal
    if not rs.RenameLayer(main_layer, new_main_layer):
        return
    
    # Cambia el color de la capa Figura-Humana_linea a rojo
    rs.LayerColor(new_main_layer + "::Figura-Humana_linea", (0, 0, 0))
    
    # Cambia la tipografía y el color del objeto cota en Figura-Humana_cota
    text_obj = rs.ObjectsByLayer(new_main_layer + "::Figura-Humana_cota")[0]
    rs.TextObjectFont(text_obj, "Myriad Pro")
    rs.LayerColor(new_main_layer + "::Figura-Humana_cota", (0, 0, 0))
    
    # Opcional: eliminar la capa temporal si ya no es necesaria
    if rs.IsLayer(temp_layer):
        rs.PurgeLayer(temp_layer)

if __name__ == "__main__":
    main()
