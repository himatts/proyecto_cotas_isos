# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import uuid

def set_layer_properties(layer_name, color, print_width):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, color=color)
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
    # Configuración inicial
    base_layer = "Cotas FM"
    sublayer_prefix = "cota-"
    line_color = (237, 118, 32)
    print_width = 2.0
    text_height = 40.0

    objects_to_delete = []
    sublayer_name = None
    initial_layer = rs.CurrentLayer()

    try:
        # Crear capa principal y subcapa
        set_layer_properties(base_layer, line_color, print_width)
        sublayer_name = "{}{}".format(sublayer_prefix, str(uuid.uuid4())[:8])
        if not rs.IsLayer(base_layer + "::" + sublayer_name):
            rs.AddLayer(sublayer_name, color=line_color, parent=base_layer)
            rs.LayerPrintWidth(base_layer + "::" + sublayer_name, print_width)
        rs.CurrentLayer(base_layer + "::" + sublayer_name)

        # Insertar la polilínea
        rs.MessageBox("Por favor, dibuje una polilínea con 2 o 3 líneas que representan la altura, profundidad (opcional) y anchura.")
        rs.Command("_Polyline")
        polyline = rs.LastCreatedObjects()
        if not polyline or len(polyline) != 1:
            rs.MessageBox("No se creó una polilínea válida. Terminando el script.", 0)
            return

        polyline = polyline[0]

        # Obtener el número de segmentos en la polilínea
        vertices = rs.PolylineVertices(polyline)
        line_count = len(vertices) - 1

        if line_count < 2 or line_count > 3:
            rs.MessageBox("Debe crear una polilínea con 2 o 3 líneas. Terminando el script.", 0)
            rs.DeleteObject(polyline)
            return

        # Definir la distancia de offset visualmente
        base_point = rs.GetPoint("Seleccione el punto base para el offset")
        offset_point = rs.GetPoint("Seleccione el punto de destino para el offset", base_point)
        if not base_point or not offset_point:
            rs.MessageBox("Debe seleccionar dos puntos para definir la distancia de offset.", 0)
            return

        offset_distance = rs.Distance(base_point, offset_point)
        offset_polyline = create_offset_polyline(polyline, offset_distance)

        # Obtener los vértices de la polilínea offseteada
        vertices = rs.PolylineVertices(offset_polyline)

        # Obtener los puntos medios específicos
        midpoints = get_specific_midpoints(vertices, line_count)

        # Asignar propiedades a la polilínea offseteada
        rs.ObjectColor(offset_polyline, line_color)
        rs.ObjectPrintWidth(offset_polyline, print_width)

        created_objects = [offset_polyline]

        # Solicitar textos de referencia y asignar el texto centrado en los puntos medios
        labels = ["Altura", "Anchura"] if line_count == 2 else ["Altura", "Profundidad", "Anchura"]
        for i, label in enumerate(labels):
            rs.MessageBox("Seleccione el texto para la {}.".format(label))
            text_ref = rs.GetObject("Seleccione el texto para la {}: ".format(label), rs.filter.annotation)
            if text_ref:
                text_content = rs.TextObjectText(text_ref)
                text = rs.AddText(text_content, midpoints[i], height=text_height)
                if text:
                    rs.ObjectColor(text, line_color)
                    rs.TextObjectFont(text, "Bahnschrift")
                    created_objects.append(text)

        # Eliminar la polilínea original
        rs.DeleteObject(polyline)

        # Agrupar los objetos creados
        group_name = rs.AddGroup()
        rs.AddObjectsToGroup(created_objects, group_name)

    except Exception as e:
        # Manejo de errores: eliminar objetos creados y purgar capas
        for obj in objects_to_delete:
            if rs.IsObject(obj):
                rs.DeleteObject(obj)
        if sublayer_name and rs.IsLayer(sublayer_name):
            rs.PurgeLayer(sublayer_name)
        rs.CurrentLayer(initial_layer)
        rs.MessageBox("Ocurrió un error: " + str(e), 0)

    finally:
        # Volver a activar la capa madre y purgar capas vacías
        rs.CurrentLayer(base_layer)
        purge_empty_layers(base_layer)

main()
