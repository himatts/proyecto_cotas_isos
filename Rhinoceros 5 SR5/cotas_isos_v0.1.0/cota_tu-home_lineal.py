# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import uuid

def add_perpendicular_line(point, vector):
    pt1 = rs.PointAdd(point, rs.VectorScale(vector, 20))
    pt2 = rs.PointAdd(point, rs.VectorScale(vector, -20))
    return rs.AddLine(pt1, pt2)

def set_layer_properties(layer_name, color, print_width):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, color=color)
    rs.LayerPrintWidth(layer_name, print_width)

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

def add_linear_dimension_in_cm_and_inches():
    objects_to_delete = []
    sub_layer_name = None
    initial_layer = rs.CurrentLayer()
    initial_dim_style = rs.CurrentDimStyle()
    
    try:
        rs.UnselectAllObjects()

        rs.CurrentDimStyle("Base")

        base_layer_name = "Cotas TU-HOME"
        layer_color = (0, 0, 0)
        print_width = 2.00
        set_layer_properties(base_layer_name, layer_color, print_width)

        uuid_str = "cota-" + str(uuid.uuid4())[:8]
        if not rs.IsLayer(base_layer_name + "::" + uuid_str):
            rs.AddLayer(uuid_str, color=layer_color, parent=base_layer_name)
            rs.LayerPrintWidth(base_layer_name + "::" + uuid_str, print_width)

        rs.CurrentLayer(base_layer_name + "::" + uuid_str)

        rs.Command("_Dim")  

        dims = rs.LastCreatedObjects()
        if not dims or not isinstance(dims, list):
            raise Exception("No se crearon dimensiones")

        dim = None
        for obj in dims:
            if rs.IsDimension(obj):
                dim = obj
                break

        if not dim:
            raise Exception("No se encontró ningún objeto de dimensión")

        dim_value_mm = rs.DimensionValue(dim)
        dim_value_cm = float(dim_value_mm) / 10.0
        dim_value_in = dim_value_mm / 25.4

        dim_text_cm = "{:.1f} cm".format(dim_value_cm).replace('.', ',')
        dim_text_in = '{:.1f}"'.format(dim_value_in).replace('.', ',')

        dim_text = "{}\n{}".format(dim_text_cm, dim_text_in)

        rs.DimensionUserText(dim, dim_text)

        rs.SelectObject(dim)
        rs.Command("_Explode")

        exploded_objs = rs.LastCreatedObjects()
        objects_to_delete.extend(exploded_objs)
        dim_line = None
        text_obj = None
        for obj in exploded_objs:
            if rs.IsCurve(obj) and rs.IsCurveClosed(obj):
                rs.DeleteObject(obj)
            elif rs.IsCurve(obj) and not rs.IsCurveClosed(obj):
                dim_line = obj
            elif rs.IsText(obj):
                text_obj = obj

        if dim_line:
            start_pt = rs.CurveStartPoint(dim_line)
            end_pt = rs.CurveEndPoint(dim_line)
            vector = rs.VectorUnitize(rs.VectorSubtract(end_pt, start_pt))
            perp_vector = rs.VectorRotate(vector, 90, [0, 0, 1])
            start_line = add_perpendicular_line(start_pt, perp_vector)
            end_line = add_perpendicular_line(end_pt, perp_vector)

            rs.SelectObjects([dim_line, start_line, end_line])
            rs.Command("_Group")

            line_length_x = abs(end_pt[0] - start_pt[0])
            line_length_y = abs(end_pt[1] - start_pt[1])
            if line_length_y > line_length_x and text_obj:
                text_center = rs.CurveMidPoint(dim_line)
                rs.RotateObject(text_obj, text_center, -90)

                text_bbox = rs.BoundingBox(text_obj)
                if text_bbox:
                    text_center_current = rs.PointAdd(text_bbox[0], rs.VectorScale(rs.VectorCreate(text_bbox[6], text_bbox[0]), 0.5))
                    move_vector = rs.VectorSubtract(text_center, text_center_current)
                    rs.MoveObject(text_obj, move_vector)

        for obj in exploded_objs:
            if rs.IsText(obj):
                rs.TextObjectFont(obj, "Myriad Pro")
                rs.TextObjectHeight(obj, 30)
                rs.ObjectColor(obj, layer_color)
            if rs.IsCurve(obj):
                rs.ObjectPrintWidth(obj, print_width)

        rs.CurrentLayer(initial_layer)
        rs.CurrentDimStyle(initial_dim_style)
        
        rs.UnselectAllObjects()

    except Exception as e:
        delete_objects_and_layer(objects_to_delete, base_layer_name + "::" + uuid_str)
        rs.CurrentLayer(initial_layer)
        rs.CurrentDimStyle(initial_dim_style)
        rs.UnselectAllObjects()
    finally:
        purge_empty_layers(base_layer_name)

add_linear_dimension_in_cm_and_inches()
