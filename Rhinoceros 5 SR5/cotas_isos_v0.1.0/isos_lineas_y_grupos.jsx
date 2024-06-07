// Crear un documento de Illustrator activo
var doc = app.activeDocument;

// Función para modificar el trazo de un elemento
function modificarTrazo(item) {
    if (item.stroked) {
        item.strokeCap = StrokeCap.BUTTENDCAP; // Extremo plano
        item.strokeJoin = StrokeJoin.MITERENDJOIN; // Unión de ángulo
    }
}

// Función para modificar el interlineado de un texto
function modificarTexto(texto) {
    if (texto.kind == TextType.POINTTEXT || texto.kind == TextType.AREATEXT) {
        var textRange = texto.textRange;
        var charAttributes = textRange.characterAttributes;
        var originalSize = charAttributes.size; // Mantener el tamaño original de la fuente
        charAttributes.autoLeading = false; // Desactiva el interlineado automático
        charAttributes.leading = originalSize; // Establece el interlineado al tamaño de la fuente
    }
}

// Recorrer todos los elementos del documento y modificar el trazo y el texto si es necesario
function recorrerElementos(elementos) {
    for (var i = 0; i < elementos.length; i++) {
        var item = elementos[i];
        if (item.typename == "PathItem" || item.typename == "CompoundPathItem") {
            modificarTrazo(item);
        } else if (item.typename == "TextFrame") {
            modificarTexto(item);
        } else if (item.typename == "GroupItem") {
            recorrerElementos(item.pageItems);
        }
    }
}

// Agrupar todos los trazados en una capa específica
function agruparTrazadosEnCapa(capa) {
    var trazados = [];
    var restantes = [];
    
    // Separar trazados de los otros elementos
    for (var i = 0; i < capa.pageItems.length; i++) {
        var item = capa.pageItems[i];
        if (item.typename == "PathItem" || item.typename == "CompoundPathItem") {
            trazados.push(item);
        } else {
            restantes.push(item);
        }
    }

    // Agrupar trazados si hay más de uno
    if (trazados.length > 1) {
        for (var i = 0; i < trazados.length; i++) {
            trazados[i].selected = true;
        }
        app.executeMenuCommand('group');
        for (var i = 0; i < trazados.length; i++) {
            trazados[i].selected = false;
        }
    }

    // Agrupar todos los elementos en la capa (trazados agrupados + restantes)
    var todosElementos = capa.pageItems;
    if (todosElementos.length > 1) {
        for (var i = 0; i < todosElementos.length; i++) {
            todosElementos[i].selected = true;
        }
        app.executeMenuCommand('group');
        for (var i = 0; i < todosElementos.length; i++) {
            todosElementos[i].selected = false;
        }
    }
}

// Recorrer todas las capas y agrupar los trazados y luego todos los elementos si el nombre de la capa contiene "cota"
function agruparElementosPorCapa(capas) {
    for (var i = 0; i < capas.length; i++) {
        if (capas[i].name.toLowerCase().indexOf("cota") !== -1) {
            agruparTrazadosEnCapa(capas[i]);
        }
    }
}

// Ejecutar las funciones en el documento activo
recorrerElementos(doc.pageItems);
agruparElementosPorCapa(doc.layers);

alert("Script ejecutado exitosamente");
