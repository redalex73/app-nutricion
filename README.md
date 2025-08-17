# Fitness App - Asistente de Fitness Definitivo

Aplicación de escritorio para seguimiento de nutrición, ejercicio y progreso físico. Permite registrar comidas y ejercicios, calcular calorías netas, proteínas y visualizar gráficas de seguimiento histórico.

---

## 🏋️ Características

- Registro de **comidas** con análisis nutricional mediante la API de [Edamam Nutrition](https://developer.edamam.com/edamam-nutrition-api).  
- Registro de **ejercicio** con calorías quemadas.  
- **Dashboard** diario con:
  - Calorías netas.
  - Proteínas consumidas.
  - Barra de progreso de calorías contra objetivo diario.  
- **Seguimiento gráfico** de los últimos 7 días:
  - Calorías netas.
  - Proteínas totales.
- Almacenamiento local en **SQLite**, con historial de registros.  
- Interfaz moderna con **CustomTkinter** y soporte para modo oscuro.

---

## 💾 Requisitos

- Python 3.10+  
- Librerías:
  ```bash
  pip install customtkinter requests pillow matplotlib

