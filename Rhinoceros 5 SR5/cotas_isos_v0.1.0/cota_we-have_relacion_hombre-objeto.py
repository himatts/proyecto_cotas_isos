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
    new_main_layer = "Figura-Humana WE-HAVE"
    temp_layer = "TempLayer"
    
    # Importa el archivo de Rhino en el documento
    rs.Command('_-Import "{}" _Enter'.format(file_path))
    print("Archivo importado:", file_path)
    
    # Encuentra el grupo insertado
    groups = rs.GroupNames()
    if not groups:
        print("No se encontraron grupos después de la importación.")
        return
    
    # Supongamos que el grupo importado es el último grupo en la lista
    group_name = groups[-1]
    group_objects = rs.ObjectsByGroup(group_name)
    print("Grupo encontrado:", group_name)
    
    # Verifica que los objetos del grupo coincidan con la estructura esperada
    expected_layers = ["Figura-Humana", "Figura-Humana_linea", "Figura-Humana_cota"]
    
    for obj in group_objects:
        obj_name = rs.ObjectName(obj)
        obj_layer = rs.ObjectLayer(obj)
        print("Objeto:", obj_name, "Capa:", obj_layer)
        
        if obj_layer not in expected_layers:
            print("Estructura de capa no coincide para el objeto:", obj_name)
            return
    
    print("Estructura de capas coincide con la esperada.")
    
    # Verifica si la nueva capa ya existe y mueve los objetos a una capa temporal
    if rs.IsLayer(new_main_layer):
        if not rs.IsLayer(temp_layer):
            rs.AddLayer(temp_layer)
            print("Capa temporal creada:", temp_layer)
        
        # Mueve los objetos de la capa y subcapas a una capa temporal
        sub_layers = rs.LayerChildren(new_main_layer)
        if sub_layers:
            for sub_layer in sub_layers:
                objects_in_sub_layer = rs.ObjectsByLayer(sub_layer)
                if objects_in_sub_layer:
                    rs.ObjectLayer(objects_in_sub_layer, temp_layer)
                    print("Objetos en subcapa movidos a la capa temporal:", sub_layer)
        objects_in_layer = rs.ObjectsByLayer(new_main_layer)
        if objects_in_layer:
            rs.ObjectLayer(objects_in_layer, temp_layer)
            print("Objetos en la capa movidos a la capa temporal:", new_main_layer)
        
        rs.PurgeLayer(new_main_layer)
        # Verificar si la capa se ha eliminado correctamente
        if rs.IsLayer(new_main_layer):
            print("No se pudo eliminar la capa existente:", new_main_layer)
            return
    
    # Renombra la capa principal
    if not rs.RenameLayer(main_layer, new_main_layer):
        print("No se pudo renombrar la capa:", main_layer)
        return
    
    print("Capa renombrada a:", new_main_layer)
    
    # Cambia el color de la capa Figura-Humana_linea a rojo
    if rs.IsLayer(new_main_layer + "::Figura-Humana_linea"):
        rs.LayerColor(new_main_layer + "::Figura-Humana_linea", (231, 91, 103))
        print("Color de la capa Figura-Humana_linea cambiado a rojo.")
    
    # Cambia la tipografía y el color del objeto cota en Figura-Humana_cota
    text_objs = rs.ObjectsByLayer(new_main_layer + "::Figura-Humana_cota")
    if text_objs:
        for text_obj in text_objs:
            if rs.IsText(text_obj):
                rs.TextObjectFont(text_obj, "MADETommySoft-Light")
                print("Tipografía del objeto de texto cambiada a MADETommySoft-Light:", text_obj)
        rs.LayerColor(new_main_layer + "::Figura-Humana_cota", (231, 91, 103))
        print("Color de la capa Figura-Humana_cota cambiado a rojo.")
    
    # Opcional: eliminar la capa temporal si ya no es necesaria
    if rs.IsLayer(temp_layer):
        rs.PurgeLayer(temp_layer)
        print("Capa temporal eliminada:", temp_layer)

if __name__ == "__main__":
    main()
