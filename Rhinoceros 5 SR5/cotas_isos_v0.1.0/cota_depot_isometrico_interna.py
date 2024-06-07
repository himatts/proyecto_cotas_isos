# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import uuid

def set_layer_properties(layer_name, layer_color, print_width):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, layer_color)
    rs.LayerPrintWidth(layer_name, print_width)

def add_arrow(point, vector, color):
    arrow_length = 10
    arrow_width = 10
    pt1 = point
    pt2 = rs.PointAdd(pt1, rs.VectorScale(rs.VectorRotate(vector, 150, [0,0,1]), arrow_width))
    pt3 = rs.PointAdd(pt1, rs.VectorScale(rs.VectorRotate(vector, -150, [0,0,1]), arrow_width))
    arrow_curve = rs.AddPolyline([pt1, pt2, pt3, pt1])
    if arrow_curve:
        rs.ObjectColor(arrow_curve, color)
        hatch = rs.AddHatch(arrow_curve, "Solid")
        if hatch:
            rs.ObjectColor(hatch, color)
        return arrow_curve, hatch
    return None, None

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

    try:
        layer_name = "Cotas DEPOT"
        layer_color = (0, 0, 0)
        print_width = 1.10
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

        vector = rs.VectorUnitize(rs.VectorCreate(punto2_desplazado, punto1_desplazado))
        arrow1, hatch1 = add_arrow(punto1_desplazado, rs.VectorReverse(vector), layer_color)
        arrow2, hatch2 = add_arrow(punto2_desplazado, vector, layer_color)
        objects_to_delete.extend([arrow1, hatch1, arrow2, hatch2])

        cota_id = rs.GetObject("Seleccione una cota para copiar la dimensión", rs.filter.annotation)
        if not cota_id: raise Exception("No se seleccionó ninguna cota.")

        dimension_text = rs.DimensionText(cota_id)
        midpoint = rs.CurveMidPoint(linea)
        texto = rs.AddText(dimension_text, midpoint, height=35)
        objects_to_delete.append(texto)

        if rs.IsText(texto):
            rs.TextObjectFont(texto, "Kanit-Regular")
            rs.ObjectColor(texto, layer_color)

        rs.SelectObjects(objects_to_delete)
        rs.Command("_Group")

    except:
        delete_objects_and_layer(objects_to_delete, layer_name + "::" + uuid_str)
        rs.Command("_Ortho _Off")
        print("Script cancelado. Se eliminaron los objetos creados.")
    finally:
        rs.CurrentLayer(layer_name)
        purge_empty_layers(layer_name)

crear_cota_simulada()
