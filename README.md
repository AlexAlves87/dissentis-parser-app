

# Dissentis.AI Parser

**Extractor y Limpiador Inteligente de Texto**

---

**Autor:** Alex Alves
**Versión:** 1.0.0
**Fecha:** 26 de julio de 2025
**Licencia:** [MIT](LICENSE)

---

## 📌 Resumen del Proyecto

**Dissentis.AI Parser** es una aplicación de escritorio multiplataforma diseñada para la extracción, limpieza y estructuración de contenido textual a partir de diversos formatos de archivo.

Su principal objetivo es preprocesar documentos para facilitar tareas posteriores de **Procesamiento del Lenguaje Natural (PLN)** y servir como corpus para **Modelos de Lenguaje Grandes (LLMs)**.

Cuenta con una interfaz gráfica intuitiva (GUI) para una experiencia fluida, tanto para usuarios técnicos como no técnicos.

---

## 🚀 Características Principales

* ✅ **Soporte Multi-Formato**: Procesa una amplia variedad de archivos:

  * **Documentos de texto**: `.pdf`, `.docx`, `.odt`, `.rtf`, `.txt`, `.md`
  * **Presentaciones y Hojas de cálculo**: `.pptx`, `.xlsx`
  * **Libros electrónicos**: `.epub`
  * **Formatos web y datos estructurados**: `.html`, `.xml`, `.json`, `.csv`

* ✅ **Limpieza Inteligente de Texto**:

  * Eliminación de ruido textual mediante heurísticas y expresiones regulares.
  * Formateo automático de títulos, listas y elementos estructurales.

* ✅ **Interfaz Gráfica Intuitiva**:

  * Funcionalidad **Drag and Drop** para archivos.
  * Barra de progreso y notificaciones en tiempo real.
  * Contadores automáticos de palabras y caracteres.

* ✅ **Procesamiento Asíncrono**:

  * Análisis de archivos ejecutado en segundo plano para mantener la interfaz siempre fluida y receptiva.

---

## 🖥️ Captura de Pantalla

![Interfaz de Dissentis.AI Parser mostrando un documento procesado](screenshot.png)

*(Nota: Reemplazar con imagen real del proyecto.)*

---

## 🛠️ Pila Tecnológica

| Componente               | Detalles                                                  |
| ------------------------ | --------------------------------------------------------- |
| Lenguaje de Programación | Python 3.12+                                              |
| Interfaz Gráfica (GUI)   | PySide6 (Qt for Python)                                   |
| Gestión de Dependencias  | Poetry                                                    |
| Bibliotecas principales  | `pdfplumber`, `python-docx`, `BeautifulSoup4`, `openpyxl` |

---

## 🔧 Instalación y Puesta en Marcha

### 📌 Prerrequisitos

* Python **3.12 o superior**
* Poetry (gestor de paquetes)

### ⚙️ Pasos de Instalación (opcional si usas el ejecutable)

```bash
git clone https://github.com/AlexAlves87/dissentis-parser-app.git
cd dissentis-parser-app
poetry install
```

---

## 🚦 Ejecución de la Aplicación

* **✅ Usando el ejecutable incluido:**
  Descarga el archivo correspondiente a tu sistema operativo desde la carpeta `dist/` y ejecútalo directamente.
  *(No requiere instalación adicional ni dependencias).*

* **📌 Desde el código fuente (opcional):**

```bash
poetry run python src/main.py
```

---

## 📁 Estructura del Proyecto

```plaintext
dissentis-parser-app/
├── dist/                 # Ejecutables listos para usar
├── src/
│   ├── main.py           # Lógica de la interfaz gráfica (GUI)
│   └── parser_core.py    # Módulo con la lógica de extracción y limpieza
├── .gitignore
├── poetry.lock
├── pyproject.toml
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).

---

**© 2025 Alex Alves. Todos los derechos reservados.**

