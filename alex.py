import streamlit as st
import numpy as np
import pandas as pd

# Título de la aplicación
st.title("Generador de Onda Senoidal")

st.write("Esta aplicación genera y grafica una onda senoidal interactiva. Ajusta la frecuencia y la amplitud para ver cómo cambia la onda.")

# Controles deslizantes para la frecuencia y la amplitud
frecuencia = st.slider("Frecuencia", min_value=1, max_value=10, value=1, step=1)
amplitud = st.slider("Amplitud", min_value=1, max_value=10, value=1, step=1)

# Generación de datos para la onda senoidal
x = np.linspace(0, 2 * np.pi, 400)
y = amplitud * np.sin(frecuencia * x)

# Preparar los datos en un DataFrame para la gráfica
data = pd.DataFrame({"x": x, "y": y})

# Mostrar la gráfica
st.line_chart(data.set_index("x"))
