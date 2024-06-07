# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import uuid

def set_layer_properties(layer_name, color, print_width):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, color)
    rs.LayerPrintWidth(layer_name, print_width)

def create_offset_polyline(polyline, offset_distance):
    offset_polyline = rs.OffsetCurve(polyline, [0, 0, 0], offset_distance)
    return offset_polyline

def get_specific_midpoints(vertices, line_count):
    midpoints = []
    if line_count == 2:
        midpoint_pairs = [(0, 1), (3, 4)]
    elif line_count == 3:
        midpoint_pairs = [(0, 1), (3, 4), (6, 7)]
    for pair in midpoint_pairs:
        mid = rs.PointAdd(vertices[pair[0]], rs.VectorScale(rs.VectorCreate(vertices[pair[1]], vertices[pair[0]]), 0.5))
        midpoints.append(mid)
    return midpoints

def purge_empty_layers(base_layer_name):
    sub_layers = rs.LayerChildren(base_layer_name)
    if sub_layers:
        for layer in sub_layers:
            if rs.IsLayerEmpty(layer):
                rs.DeleteLayer(layer)

def main():
    
    base_layer = "Cotas WE-HAVE"
    sublayer_prefix = "cota-"
    line_color = (231, 91, 103)
    print_width = 2.0
    text_height = 35

    objects_to_delete = []
    sublayer_name = None
    initial_layer = rs.CurrentLayer()

    try:
        
        set_layer_properties(base_layer, line_color, print_width)
        sublayer_name = "{}{}".format(sublayer_prefix, str(uuid.uuid4())[:8])
        sublayer_fullname = "{}::{}".format(base_layer, sublayer_name)
        set_layer_properties(sublayer_fullname, line_color, print_width)
        rs.CurrentLayer(sublayer_fullname)

        
        rs.MessageBox("Por favor, dibuje una polilínea con 2 o 3 líneas que representan la altura, profundidad (opcional) y anchura.")
        rs.Command("_Polyline")
        polyline = rs.LastCreatedObjects()
        if not polyline or len(polyline) != 1:
            rs.MessageBox("No se creó una polilínea válida. Terminando el script.", 0)
            return
        
        polyline = polyline[0]

        
        vertices = rs.PolylineVertices(polyline)
        line_count = len(vertices) - 1
        
        if line_count < 2 or line_count > 3:
            rs.MessageBox("Debe crear una polilínea con 2 o 3 líneas. Terminando el script.", 0)
            rs.DeleteObject(polyline)
            return

        
        base_point = rs.GetPoint("Seleccione el punto base para el offset")
        offset_point = rs.GetPoint("Seleccione el punto de destino para el offset", base_point)
        if not base_point or not offset_point:
            rs.MessageBox("Debe seleccionar dos puntos para definir la distancia de offset.", 0)
            return
        
        offset_distance = rs.Distance(base_point, offset_point)
        offset_polyline = create_offset_polyline(polyline, offset_distance)
        
        
        vertices = rs.PolylineVertices(offset_polyline)
        
        
        midpoints = get_specific_midpoints(vertices, line_count)

        
        rs.ObjectColor(offset_polyline, line_color)
        rs.ObjectPrintWidth(offset_polyline, print_width)

        created_objects = [offset_polyline]

        
        labels = ["Altura", "Anchura"] if line_count == 2 else ["Altura", "Profundidad", "Anchura"]
        for i, label in enumerate(labels):
            rs.MessageBox("Seleccione el texto para la {}.".format(label))
            text_ref = rs.GetObject("Seleccione el texto para la {}: ".format(label), rs.filter.annotation)
            if text_ref:
                text_content = rs.TextObjectText(text_ref)
                text = rs.AddText(text_content, midpoints[i], height=text_height)
                if text:
                    rs.ObjectColor(text, line_color)
                    rs.TextObjectFont(text, "MADETommySoft-Light")
                    created_objects.append(text)

        
        rs.DeleteObject(polyline)
        
        
        group_name = rs.AddGroup()
        rs.AddObjectsToGroup(created_objects, group_name)

    except Exception as e:
        
        for obj in objects_to_delete:
            if rs.IsObject(obj):
                rs.DeleteObject(obj)
        if sublayer_name and rs.IsLayer(sublayer_name):
            rs.PurgeLayer(sublayer_name)
        rs.CurrentLayer(initial_layer)
        rs.MessageBox("Ocurrió un error: " + str(e), 0)
    
    finally:
        
        rs.CurrentLayer(base_layer)
        purge_empty_layers(base_layer)

main()
