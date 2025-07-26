# src/main.py
import sys
import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                               QFileDialog, QLabel, QTextEdit, QProgressBar,
                               QFrame, QStyle, QComboBox, QDialog,
                               QCheckBox, QDialogButtonBox, QMessageBox)

# Importamos las funciones lógicas de parser_core
from parser_core import (EXTRACTORES, extraer_texto, limpiar_y_estructurar_texto)

# --- Generación dinámica de formatos ---
formatos_soportados_str = ", ".join(sorted(EXTRACTORES.keys()))
formatos_filtro_str = " *".join(sorted(EXTRACTORES.keys()))

# --- Paleta de colores y Estilos ---
class StyleConfig:
    COLOR_BACKGROUND = "#2E3440"
    COLOR_BACKGROUND_LIGHT = "#3B4252"
    COLOR_BACKGROUND_INPUT = "#434C5E"
    COLOR_FOREGROUND = "#D8DEE9"
    COLOR_FOREGROUND_SUBTLE = "#8FBCBB"
    COLOR_ACCENT = "#88C0D0"
    COLOR_ACCENT_HOVER = "#8FBCBB"
    COLOR_SUCCESS = "#A3BE8C"
    COLOR_ERROR = "#BF616A"
    FONT_BASE_SIZE = 14
    FONT_LARGE_SIZE = 18
    FONT_SMALL_SIZE = 12

APP_STYLESHEET = f"""
    QWidget {{
        background-color: {StyleConfig.COLOR_BACKGROUND};
        color: {StyleConfig.COLOR_FOREGROUND};
        font-family: Segoe UI, Arial, sans-serif;
        font-size: {StyleConfig.FONT_BASE_SIZE}px;
    }}
    QPushButton {{
        background-color: {StyleConfig.COLOR_BACKGROUND_INPUT};
        border: 1px solid #4C566A; padding: 8px; border-radius: 4px;
        min-width: 120px;
    }}
    QPushButton:hover {{ background-color: {StyleConfig.COLOR_ACCENT_HOVER}; }}
    QPushButton:disabled {{ background-color: #3B4252; color: #4C566A; }}
    QTextEdit, QComboBox {{
        background-color: {StyleConfig.COLOR_BACKGROUND_INPUT};
        border: 1px solid #4C566A; border-radius: 4px;
        padding: 5px;
    }}
    QProgressBar {{
        border: 1px solid #4C566A; border-radius: 4px; text-align: center;
        background-color: {StyleConfig.COLOR_BACKGROUND_INPUT};
    }}
    QProgressBar::chunk {{ background-color: {StyleConfig.COLOR_ACCENT}; border-radius: 2px; }}
    QDialog {{ background-color: {StyleConfig.COLOR_BACKGROUND_LIGHT}; }}
"""

# --- Traducciones Simplificadas ---
TRANSLATIONS = {
    'es': {
        "window_title": "Dissentis.AI Parser", "drop_zone_label": "Arrastra un archivo aquí",
        "select_file_button": " Seleccionar Archivo...", "save_result_button": " Guardar Resultado",
        "status_waiting": "Esperando archivo...", "status_processing": "Procesando: {filename}",
        "status_success": "Éxito: Archivo procesado correctamente.", "status_error": "Error: {error_msg}",
        "status_saved": "Archivo guardado en: {path}", "word_count_label": "Palabras: {count}",
        "char_count_label": "Caracteres: {count}", "welcome_title": "¡Bienvenido a Dissentis.AI Parser!",
        "welcome_text": (
            "Esta aplicación extrae y limpia texto de múltiples formatos para su uso con LLMs.\n\n"
            f"<b>Formatos Soportados:</b> {formatos_soportados_str}"
        ),
        "welcome_checkbox": "No volver a mostrar este mensaje", "welcome_ok_button": "Entendido",
        "dialog_select_file": "Seleccionar archivo", "dialog_save_file": "Guardar archivo",
        "supported_files": "Documentos Soportados", "all_files": "Todos los Archivos",
        "error_dialog_title": "Error"
    },
    'en': {
        "window_title": "Dissentis.AI Parser", "drop_zone_label": "Drag a file here",
        "select_file_button": " Select File...", "save_result_button": " Save Result",
        "status_waiting": "Waiting for file...", "status_processing": "Processing: {filename}",
        "status_success": "Success: File processed correctly.", "status_error": "Error: {error_msg}",
        "status_saved": "File saved to: {path}", "word_count_label": "Words: {count}",
        "char_count_label": "Characters: {count}", "welcome_title": "Welcome to Dissentis.AI Parser!",
        "welcome_text": (
            "This app extracts and cleans text from multiple formats for use with LLMs.\n\n"
            f"<b>Supported Formats:</b> {formatos_soportados_str}"
        ),
        "welcome_checkbox": "Don't show this message again", "welcome_ok_button": "Got it",
        "dialog_select_file": "Select file", "dialog_save_file": "Save file",
        "supported_files": "Supported Documents", "all_files": "All Files",
        "error_dialog_title": "Error"
    }
}

# --- Lógica de persistencia de configuración ---
CONFIG_FILE = Path.home() / ".parser_pro_settings.json"
def load_settings():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, IOError): return {}
    return {}
def save_settings(settings):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(settings, f, indent=4)

# --- Worker para procesamiento en segundo plano ---
class ParserWorker(QObject):
    trabajo_terminado = Signal(str) # Devuelve un único string
    error_ocurrido = Signal(str)
    progreso_actualizado = Signal(int)

    def __init__(self, ruta_archivo: str):
        super().__init__()
        self.ruta_archivo = ruta_archivo

    def ejecutar_trabajo(self):
        try:
            texto_bruto = extraer_texto(self.ruta_archivo, lambda p: self.progreso_actualizado.emit(p))
            if texto_bruto.startswith("Error:"): raise ValueError(texto_bruto)
            texto_limpio = limpiar_y_estructurar_texto(texto_bruto)
            self.trabajo_terminado.emit(texto_limpio)
        except Exception as e:
            self.error_ocurrido.emit(str(e))

# --- Widgets Personalizados ---
class DropZone(QFrame):
    archivo_soltado = Signal(str)
    def __init__(self):
        super().__init__(); self.setAcceptDrops(True)
        self.setStyleSheet(f"background-color: {StyleConfig.COLOR_BACKGROUND_LIGHT}; border-radius: 5px;")
        layout = QVBoxLayout(self); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel(); self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(); font.setPointSize(StyleConfig.FONT_LARGE_SIZE); self.label.setFont(font)
        layout.addWidget(self.label)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction(); self.setStyleSheet(f"background-color: {StyleConfig.COLOR_BACKGROUND_INPUT}; border-radius: 5px;")
    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"background-color: {StyleConfig.COLOR_BACKGROUND_LIGHT}; border-radius: 5px;")
    def dropEvent(self, event):
        self.setStyleSheet(f"background-color: {StyleConfig.COLOR_BACKGROUND_LIGHT}; border-radius: 5px;")
        if event.mimeData().hasUrls():
            ruta = event.mimeData().urls()[0].toLocalFile()
            if Path(ruta).is_file(): self.archivo_soltado.emit(ruta)

class WelcomeDialog(QDialog):
    def __init__(self, lang, parent=None):
        super().__init__(parent); tr = TRANSLATIONS[lang]
        self.setWindowTitle(tr["welcome_title"]); layout = QVBoxLayout(self)
        message_label = QLabel(tr["welcome_text"]); message_label.setWordWrap(True)
        self.checkbox = QCheckBox(tr.get("welcome_checkbox", "Don't show this again"))
        button_box = QDialogButtonBox(); ok_button = button_box.addButton(tr.get("welcome_ok_button", "Got It"), QDialogButtonBox.ButtonRole.AcceptRole)
        layout.addWidget(message_label); layout.addWidget(self.checkbox); layout.addWidget(button_box)
        ok_button.clicked.connect(self.accept)

# --- Ventana Principal de la Aplicación ---
class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        settings = load_settings()
        self.current_lang = settings.get('language', 'es')
        self.ruta_archivo_original = None

        self._init_ui()
        self._connect_signals()
        self.actualizar_ui_textos()
        if (index := self.selector_idioma.findData(self.current_lang)) != -1:
            self.selector_idioma.setCurrentIndex(index)

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # --- Zona Superior (DropZone y Botones) ---
        self.drop_zone = DropZone()
        self.boton_examinar = QPushButton()
        self.boton_examinar.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.boton_guardar = QPushButton()
        self.boton_guardar.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.boton_guardar.setEnabled(False)
        
        layout_botones = QHBoxLayout()
        layout_botones.addWidget(self.boton_examinar)
        layout_botones.addStretch()
        layout_botones.addWidget(self.boton_guardar)

        # --- Barra de Progreso y Estado ---
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setVisible(False)
        self.status_label = QLabel()
        
        layout_estado = QHBoxLayout()
        layout_estado.addWidget(self.status_label, 1)
        layout_estado.addWidget(self.barra_progreso)

        # --- Área de Texto Principal ---
        self.texto_resultado = QTextEdit()
        self.texto_resultado.setReadOnly(True)

        # --- Zona Inferior (Contadores, Idioma y Branding) ---
        self.contador_palabras = QLabel()
        self.contador_caracteres = QLabel()
        self.selector_idioma = QComboBox()
        self.selector_idioma.addItem("Español", "es")
        self.selector_idioma.addItem("English", "en")
        
        layout_inferior = QHBoxLayout()
        layout_inferior.addWidget(self.selector_idioma)
        layout_inferior.addStretch()
        layout_inferior.addWidget(self.contador_palabras)
        layout_inferior.addWidget(self.contador_caracteres)

        # --- Añadir widgets al layout principal ---
        layout_principal.addWidget(self.drop_zone, 1)
        layout_principal.addLayout(layout_botones)
        layout_principal.addLayout(layout_estado)
        layout_principal.addWidget(self.texto_resultado, 3)
        layout_principal.addLayout(layout_inferior)

    def _connect_signals(self):
        self.drop_zone.archivo_soltado.connect(self.iniciar_procesamiento)
        self.boton_examinar.clicked.connect(self.abrir_dialogo_archivo)
        self.boton_guardar.clicked.connect(self.guardar_resultado)
        self.selector_idioma.currentIndexChanged.connect(self.cambiar_idioma)
        self.texto_resultado.textChanged.connect(self.actualizar_contadores)

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, '_welcome_shown'):
            self._welcome_shown = True
            settings = load_settings()
            if settings.get("show_welcome", True):
                dialog = WelcomeDialog(self.current_lang, self)
                if dialog.exec() and dialog.checkbox.isChecked():
                    settings["show_welcome"] = False; save_settings(settings)

    def actualizar_ui_textos(self):
        tr = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(tr["window_title"])
        self.drop_zone.label.setText(tr["drop_zone_label"])
        self.boton_examinar.setText(tr["select_file_button"])
        self.boton_guardar.setText(tr["save_result_button"])
        self.set_status(tr["status_waiting"])
        self.actualizar_contadores()

    def cambiar_idioma(self):
        self.current_lang = self.selector_idioma.currentData()
        self.actualizar_ui_textos()
        settings = load_settings(); settings['language'] = self.current_lang; save_settings(settings)
    
    def actualizar_contadores(self):
        tr = TRANSLATIONS[self.current_lang]
        texto = self.texto_resultado.toPlainText()
        num_palabras = len(texto.split()) if texto else 0
        num_caracteres = len(texto)
        self.contador_palabras.setText(tr["word_count_label"].format(count=num_palabras))
        self.contador_caracteres.setText(tr["char_count_label"].format(count=num_caracteres))

    def abrir_dialogo_archivo(self):
        tr = TRANSLATIONS[self.current_lang]
        filtro_documentos = f"{tr.get('supported_files', 'Supported Documents')} (*{formatos_filtro_str})"
        filtro_todos = f"{tr.get('all_files', 'All Files')} (*)"
        ruta, _ = QFileDialog.getOpenFileName(self, tr.get('dialog_select_file', 'Select file'), "", f"{filtro_documentos};;{filtro_todos}")
        if ruta: self.iniciar_procesamiento(ruta)

    def iniciar_procesamiento(self, ruta_archivo):
        self.ruta_archivo_original = Path(ruta_archivo)
        self.boton_examinar.setEnabled(False); self.boton_guardar.setEnabled(False)
        self.set_status(TRANSLATIONS[self.current_lang]["status_processing"].format(filename=self.ruta_archivo_original.name))
        self.texto_resultado.clear()
        self.barra_progreso.setValue(0); self.barra_progreso.setVisible(True)

        self.thread = QThread()
        self.worker = ParserWorker(ruta_archivo)
        self.worker.moveToThread(self.thread)
        self.worker.progreso_actualizado.connect(self.barra_progreso.setValue)
        self.thread.started.connect(self.worker.ejecutar_trabajo)
        self.worker.trabajo_terminado.connect(self.manejar_resultado_exitoso)
        self.worker.error_ocurrido.connect(self.manejar_error)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.trabajo_terminado.connect(self.thread.quit)
        self.worker.error_ocurrido.connect(self.thread.quit)
        self.thread.start()

    def manejar_resultado_exitoso(self, texto_limpio):
        self.barra_progreso.setVisible(False)
        self.texto_resultado.setText(texto_limpio)
        self.set_status(TRANSLATIONS[self.current_lang]["status_success"], "success")
        self.boton_examinar.setEnabled(True); self.boton_guardar.setEnabled(True)

    def manejar_error(self, mensaje_error):
        tr = TRANSLATIONS[self.current_lang]
        self.barra_progreso.setVisible(False)
        QMessageBox.critical(self, tr["error_dialog_title"], str(mensaje_error))
        self.set_status(tr["status_waiting"], "error")
        self.boton_examinar.setEnabled(True)
        self.boton_guardar.setEnabled(False)

    def set_status(self, texto, tipo="subtle"):
        self.status_label.setText(texto)
        color = StyleConfig.COLOR_FOREGROUND_SUBTLE
        if tipo == "success": color = StyleConfig.COLOR_SUCCESS
        elif tipo == "error": color = StyleConfig.COLOR_ERROR
        self.status_label.setStyleSheet(f"color: {color};")

    def guardar_resultado(self):
        texto_a_guardar = self.texto_resultado.toPlainText()
        if not texto_a_guardar: return
        
        nombre_sugerido = f"{self.ruta_archivo_original.stem}_procesado.txt"
        ruta_guardar, _ = QFileDialog.getSaveFileName(self, "Guardar Resultado", nombre_sugerido, "Archivos de Texto (*.txt)")
        
        if ruta_guardar:
            try:
                Path(ruta_guardar).write_text(texto_a_guardar, encoding='utf-8')
                self.set_status(TRANSLATIONS[self.current_lang]["status_saved"].format(path=ruta_guardar), "success")
            except Exception as e:
                self.manejar_error(f"No se pudo guardar el archivo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    ventana = VentanaPrincipal()
    ventana.resize(800, 600)
    ventana.show()
    sys.exit(app.exec())
