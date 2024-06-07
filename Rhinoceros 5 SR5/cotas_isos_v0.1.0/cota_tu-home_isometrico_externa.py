# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import uuid

def set_layer_properties(layer_name, layer_color, print_width):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, layer_color)
    rs.LayerPrintWidth(layer_name, print_width)

def add_perpendicular_line(point, vector, length=20):
    if vector is None or rs.VectorLength(vector) == 0:
        vector = (1, 0, 0)
    unit_vector = rs.VectorUnitize(vector)
    perpendicular_vector = rs.VectorRotate(unit_vector, 90, [0, 0, 1])
    pt1 = rs.PointAdd(point, rs.VectorScale(perpendicular_vector, length))
    pt2 = rs.PointAdd(point, rs.VectorScale(perpendicular_vector, -length))
    return rs.AddLine(pt1, pt2)

def delete_objects_and_layer(objects_to_delete, sub_layer_name):
    for obj in objects_to_delete:
        if rs.IsObject(obj):
            rs.DeleteObject(obj)
    if sub_layer_name and rs.IsLayer(sub_layer_name):
        rs.PurgeLayer(sub_layer_name)

def purge_empty_layers(base_layer_name):
    sub_layers = rs.LayerChildren(base_layer_name)
    if sub_layers:
        for layer in sub_layers:
            if rs.IsLayerEmpty(layer):
                rs.DeleteLayer(layer)

def crear_cota_simulada():
    objects_to_delete = []
    sub_layer_name = None
    initial_layer = rs.CurrentLayer()

    try:
        layer_name = "Cotas TU-HOME"
        layer_color = (0, 0, 0)
        print_width = 2.00
        set_layer_properties(layer_name, layer_color, print_width)

        uuid_str = "cota-" + str(uuid.uuid4())[:8]
        if not rs.IsLayer(layer_name + "::" + uuid_str):
            rs.AddLayer(uuid_str, color=layer_color, parent=layer_name)
            rs.LayerPrintWidth(layer_name + "::" + uuid_str, print_width)
        rs.CurrentLayer(layer_name + "::" + uuid_str)

        punto1 = rs.GetPoint("Seleccione el primer punto de referencia")
        if not punto1: return

        punto2 = rs.GetPoint("Seleccione el segundo punto de referencia", punto1)
        if not punto2: return

        linea = rs.AddLine(punto1, punto2)
        objects_to_delete.append(linea)

        desplazamiento = rs.GetPoint("Seleccione el punto de desplazamiento", punto2)
        if not desplazamiento: return

        deltaX = desplazamiento[0] - punto2[0]
        deltaY = desplazamiento[1] - punto2[1]

        punto3 = (punto2[0] + deltaX, punto2[1] + deltaY, punto2[2])
        punto4 = (punto1[0] + deltaX, punto1[1] + deltaY, punto1[2])

        rs.MoveObject(linea, (punto4[0] - punto1[0], punto4[1] - punto1[1], 0))

        punto1_desplazado = rs.CurveStartPoint(linea)
        punto2_desplazado = rs.CurveEndPoint(linea)

        vector_perpendicular = (deltaY, -deltaX, 0)
        linea_perpendicular1 = add_perpendicular_line(punto1_desplazado, vector_perpendicular)
        linea_perpendicular2 = add_perpendicular_line(punto2_desplazado, vector_perpendicular)
        objects_to_delete.extend([linea_perpendicular1, linea_perpendicular2])

        cota_id = rs.GetObject("Seleccione una cota para copiar la dimensión", rs.filter.annotation)
        if not cota_id: raise Exception("No se seleccionó ninguna cota.")

        dimension_text = rs.DimensionText(cota_id)
        midpoint = rs.CurveMidPoint(linea)
        texto = rs.AddText(dimension_text, midpoint, height=30)
        objects_to_delete.append(texto)

        if rs.IsText(texto):
            rs.TextObjectFont(texto, "Myriad Pro")

        rs.SelectObjects(objects_to_delete)
        rs.Command("_Group")

    except:
        delete_objects_and_layer(objects_to_delete, layer_name + "::" + uuid_str)
        rs.CurrentLayer(initial_layer)
        rs.Command("_Ortho _Off")
        print("Script cancelado. Se eliminaron los objetos creados.")
    finally:
        rs.CurrentLayer(layer_name)
        purge_empty_layers(layer_name)

crear_cota_simulada()
