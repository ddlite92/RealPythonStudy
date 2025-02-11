#
# B-renderon is a render manager for Blender 3d.
# Copyright (C) 2024  Tomas Fenoglio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the h ope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from PyQt5.QtGui import QPalette, QFontDatabase


icons_botones_size = 24
icons_tablas_size = 20
atenuante_iconos_tablas = 0.85

font_size = 9

alto_filas = 24

sonido_render = ":/completed.wav"

render_timeout = 30

default_fps = 24

watchfolders_background = "998"
scheduler_background = "999"
shutdown_background = "1000"

backgrounds_state_functions = (watchfolders_background, scheduler_background, shutdown_background)

rutas_custom_viewers = {"imagenes": None, "secuencias": None, "videos": None}

sets_iconos = {"#FFFFFF": "White", "#000000": "Black"}

opciones = {"idioma": ["English", "Castellano", "中文"],
                         "cargar_escenas": ["escenas_activa", "escenas_elegir", "escenas_todas"],
                         "anteriores_terminados": ["omitir", "reiniciar", "preguntar"],
                         "anteriores_interrumpidos": ["preguntar", "continuar", "omitir", "reiniciar"],
                         "viewer_imagenes": ["B-renderon", "blender_player", "system_default", "custom_viewer"],
                         "viewer_secuencias": ["B-renderon", "blender_player", "system_default", "custom_viewer"],
                         "viewer_videos": ["blender_player", "system_default", "custom_viewer"]}

booleanas = {"auto_frame1": False,
                          "reproducir_sonido_render": False,
                          "tratar_fallidos": True,
                          "blender_factory": False,
                          "mantener_despierta": True,
                          "alternar_color_filas": True,
                          "botones_iconos": True,
                          "botones_texto": True,
                          "botones_autoraise": True,
                          }

valores_unicos = ("sonido_render",
                  "instancias_max",
                  "render_timeout",
                  "fps",
                  "alto_filas",
                  "factor_icons_size",
                  "factor_ui_font_size",
                  "factor_buttons_font_size",
                  "nombre_skin",
                  "app_font",
                  "rutas_custom_viewers")

pb_color1 = "Gradient 1"
pb_color2 = "Gradient 2"
pb_color3 = "Border"


validador_skins = {
    "Main": {
        "10": {"color": str, "nombre": str},  # QPalette.Window
        "0": {"color": str, "nombre": str},   # QPalette.WindowText
        "9": {"color": str, "nombre": str},   # QPalette.Base
        "16": {"color": str, "nombre": str},  # QPalette.AlternateBase
        "6": {"color": str, "nombre": str},   # QPalette.Text
        "1": {"color": str, "nombre": str},   # QPalette.Button
        "8": {"color": str, "nombre": str},   # QPalette.ButtonText
        "12": {"color": str, "nombre": str},  # QPalette.Highlight
        "13": {"color": str, "nombre": str},  # QPalette.HighlightedText
        watchfolders_background: {"color": str, "nombre": str},
        scheduler_background: {"color": str, "nombre": str},
        shutdown_background: {"color": str, "nombre": str},
    },
    "Disabled": {
        "2": {"color": str, "nombre": str},  # QPalette.Light
        "6": {"color": str, "nombre": str},   # QPalette.Text
        "8": {"color": str, "nombre": str},   # QPalette.ButtonText
        "0": {"color": str, "nombre": str},   # QPalette.WindowText
    },
    "Progress bar": {
        "terminado": {
            pb_color1: str,
            pb_color2: str,
            pb_color3: str
        },
        "renderizando": {
            pb_color1: str,
            pb_color2: str,
            pb_color3: str
        },
        "interrumpido": {
            pb_color1: str,
            pb_color2: str,
            pb_color3: str
        },
        "desactivado": {
            pb_color1: str,
            pb_color2: str,
            pb_color3: str
        }
    },
    "iconos": {"enabled": str, "disabled": str}
}

def actualizar_formato_skins(skins):
    for skin in skins.values():
        if "color_set" in skin["iconos"]:
            actualizar_formato_skin_iconos(skin)
        if watchfolders_background not in skin["Main"]:
            skin["Main"].update(state_functions_backgrounds_default)

def actualizar_formato_skin_iconos(skin):
    if not ("iconos" in skin and "color_set" in skin["iconos"]):
        return
    enabled_color = skin["iconos"]["colorizacion"]["enabled"]["color"]
    disabled_color = skin["iconos"]["colorizacion"]["disabled"]["color"]
    skin["iconos"] = {"enabled": enabled_color, "disabled": disabled_color}


skin_bdark = {"Main":
    {
        str(QPalette.Window): {"color": "#232323", "nombre": "Window"},
        str(QPalette.WindowText): {"color": "#D9D9D9", "nombre": "Window Text"},
        str(QPalette.Base): {"color": "#424242", "nombre": "Base"},
        str(QPalette.AlternateBase): {"color": "#353535", "nombre": "Alternate Base"},
        str(QPalette.Text): {"color": "#FCFCFC", "nombre": "Text"},
        str(QPalette.Button): {"color": "#2C2C2C", "nombre": "Button"},
        str(QPalette.ButtonText): {"color": "#FFFFFF", "nombre": "Button Text"},
        str(QPalette.Highlight): {"color": "#5680C2", "nombre": "Highlight"},
        str(QPalette.HighlightedText): {"color": "#000000", "nombre": "Highlighted Text"},
        # state functions backgrounds se agregan justo despues

        # str(QPalette.BrightText): {"color": "#FF0000", "nombre": "Bright Text"},
        # str(QPalette.Light): {"color": "#FF0000", "nombre": "Light"},
        # str(QPalette.Midlight): {"color": "#FF0000", "nombre": "Midlight"},
    },
    "Disabled": {
        str(QPalette.Light): {"color": "#3f3f3f", "nombre": "Disabled Light"},
        str(QPalette.Text): {"color": "#A9A9A9", "nombre": "Disabled Text"},
        str(QPalette.ButtonText): {"color": "#A9A9A9", "nombre": "Disabled Button Text"},
        str(QPalette.WindowText): {"color": "#A9A9A9", "nombre": "Disabled Window Text"},
    },
    "Progress bar": {
        "terminado": {
            pb_color1: "#056C04",
            pb_color2: "#46D708",
            pb_color3: "#92D050"
        },
        "renderizando": {
            pb_color1: "#355396",
            pb_color2: "#7DC1F2",
            pb_color3: "#82C5F4"
        },
        "interrumpido": {
            pb_color1: "#C86000",
            pb_color2: "#FF912D",
            pb_color3: "#E3A746"
        },
        "desactivado": {
            pb_color1: "#AAAAAA",
            pb_color2: "#AAAAAA",
            pb_color3: "#AAAAAA"
        }
    },
    "iconos": {"enabled": "#FFFFFF", "disabled": "#A9A9A9"}
}

state_functions_backgrounds_default = {
    watchfolders_background: {"color": "#3DE57A", "nombre": "Checked watchfolders background"},
    scheduler_background: {"color": "#A9FFFF", "nombre": "Checked scheduler background"},
    shutdown_background: {"color": "#FF0000", "nombre": "Checked shutdown background"},
}

skin_bdark["Main"].update(state_functions_backgrounds_default)

sin_skin = {
    "Main":
        {
            watchfolders_background: {"color": "#3DE57A", "nombre": "Checked watchfolders background"},
            scheduler_background: {"color": "#A9FFFF", "nombre": "Checked scheduler background"},
            shutdown_background: {"color": "#FF0000", "nombre": "Checked shutdown background"},
        },
    "Disabled": {
        str(QPalette.Light): {"color": "#CCCCCC", "nombre": "Disabled Light"},
        str(QPalette.Text): {"color": "#A9A9A9", "nombre": "Disabled Text"},
        str(QPalette.ButtonText): {"color": "#A9A9A9", "nombre": "Disabled Button Text"},
        str(QPalette.WindowText): {"color": "#A9A9A9", "nombre": "Disabled Window Text"},
        },
    "Progress bar": {
        "terminado": {
            pb_color1: "#14ba25",
            pb_color2: "#85ff4d",
            pb_color3: "#71f23a"
        },
        "renderizando": {
            pb_color1: "#4579f8",
            pb_color2: "#b4e0ff",
            pb_color3: "#82C5F4"
        },
        "interrumpido": {
            pb_color1: "#C86000",
            pb_color2: "#ffc92e",
            pb_color3: "#E3A746"
        }
    },
    "iconos": {"enabled": "#000000", "disabled": "#5D5D5D"}
}

skins_builtin = {"sin_skin": sin_skin, "bdark": skin_bdark}

# "desactivado": (
#     {"color": "#3B3834", "nombre": pb_color1},
#     {"color": "#645C4F", "nombre": pb_color2},
#     {"color": "#645C4F", "nombre": pb_color3}
# ),
# "fallo": (
#     {"color": "#B41218", "nombre": pb_color1},
#     {"color": "#DA464C", "nombre": pb_color2},
#     {"color": "#DA464C", "nombre": pb_color3}
# ),
# "no_comenzado": (
#     {"color": "#BBBBBB", "nombre": pb_color1},
#     {"color": "#BBBBBB", "nombre": pb_color2},
#     {"color": "#BBBBBB", "nombre": pb_color3}
# )

base_qss_pb = """
             QProgressBar {{
                 border: 1px solid black;
                 border-radius: 5px;
                 text-align: center;
             }}
             """
base_qss_fallidos_pb = """
             QProgressBar {{
                 border: 1px solid red;
                 border-radius: 5px;
                 text-align: center;
                 background-color: rgba(255, 0, 0, 40);
             }}
             """

chunk_qss_pb = """
     QProgressBar::chunk {{
         background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {0}, stop:1 {1});
         border: 1px solid {2};
         border-radius: 4px;
     }}
 """


def default_font():
    disponibles = QFontDatabase().families()
    for font in ["Barlow", "Bahnschrift", "Segoe UI", "Noto Sans Cond"]:
        if font in disponibles:
            return font
    return "Arial"
