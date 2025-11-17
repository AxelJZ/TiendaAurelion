import os
import sys
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, normaltest

# Intentar importar display de IPython, pero usar print como fallback
try:
    from IPython.display import display
except ImportError:
    # Si estamos en un entorno que no tiene IPython, usar print
    def display(obj):
        print(obj)

def cargar_datos():
    try:
        ventas = pd.read_csv("ventas.csv")
        clientes = pd.read_csv("clientes.csv")
        productos = pd.read_csv("productos.csv")
        detalle_ventas = pd.read_csv("detalle_ventas.csv")
        print("✅ Archivos cargados correctamente.")
        return ventas, clientes, productos, detalle_ventas
    except Exception as e:
        print(f"❌ Error al cargar archivos: {e}")
        return None, None, None, None


def crear_df_maestro(ventas, clientes, productos, detalle_ventas):
    try:
        df_maestro = (
            detalle_ventas
            .merge(productos, on="id_producto", how="left")
            .merge(ventas, on="id_venta", how="left")
            .merge(clientes, on="id_cliente", how="left")
        )
        print("✅ DataFrame maestro creado correctamente.")
        return df_maestro
    except Exception as e:
        print(f"❌ Error al crear DataFrame maestro: {e}")
        return None


def cargar_tabla_unificada_csv():
    try:
        base_dir = os.path.dirname(__file__)
        ruta = os.path.join(base_dir, "..", "database", "tabla_unificada.csv")
        ruta = os.path.normpath(ruta)
        print(f"📥 Cargando tabla unificada desde: {ruta}")
        df = pd.read_csv(ruta)
        print("✅ Tabla unificada cargada correctamente.")
        return df
    except Exception as e:
        print(f"❌ Error al cargar tabla_unificada.csv: {e}")
        return None


def ejecutar_documentacion_notebook():
    try:
        base_dir = os.path.dirname(__file__)
        notebook_path = os.path.join(base_dir, "SPRINT2.ipynb")
        notebook_path = os.path.normpath(notebook_path)
        print(f"🧪 Ejecutando notebook y mostrando resultados: {notebook_path}\n")
        # Intento 1: jupyter en PATH
        cmd = [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--stdout",
            notebook_path,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except Exception:
            # Intento 2: python -m jupyter
            cmd = [
                "python",
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--stdout",
                notebook_path,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Mostrar salida en terminal (puede ser extensa)
        print(res.stdout)
        if res.stderr:
            print("\n[stderr]\n" + res.stderr)
        print("\n✅ Ejecución de SPRINT2.ipynb finalizada.")
    except subprocess.CalledProcessError as e:
        print("❌ Error al ejecutar el notebook con nbconvert.")
        print(e.stdout or "")
        print(e.stderr or "")
    except Exception as e:
        print(f"❌ Error inesperado al ejecutar el notebook: {e}")


def analisis_estadistico(df):
    print("\n📊 ANÁLISIS ESTADÍSTICO GENERAL:")
    print(df[["cantidad", "precio_unitario", "importe"]].describe().round(2))


def medios_pago(df):
    print("\n💳 ANÁLISIS DE MEDIOS DE PAGO:")
    conteo = df["medio_pago"].value_counts().reset_index()
    conteo.columns = ["Medio de Pago", "Cantidad de Ventas"]
    print(conteo)
    plt.figure(figsize=(7,5))
    sns.barplot(data=conteo, x="Medio de Pago", y="Cantidad de Ventas", palette="crest")
    plt.title("Frecuencia de Medios de Pago", fontsize=13, weight="bold")
    plt.show()


def conclusiones(df):
    top_pago = df["medio_pago"].value_counts().idxmax()
    print(f"✅ Conclusión: El medio de pago más utilizado por los clientes es **{top_pago}**.")


def info_general(df):
    print("\nℹ️ INFORMACIÓN GENERAL DEL DATAFRAME:")
    print(df.info())
    print("\nDescripción estadística de variables numéricas:")
    print(df.describe().T)


def medios_pago_conteo_porcentaje(df):
    print("\n📌 CONTEO Y PORCENTAJE POR MEDIO DE PAGO:")
    print(df["medio_pago"].value_counts())
    print("\nPorcentaje de participación por medio de pago:")
    print((df["medio_pago"].value_counts(normalize=True) * 100).round(2))


def encoding_medios_pago(df):
    print("\n🔤 ONE-HOT ENCODING DE MEDIOS DE PAGO:")
    df_encoded = pd.get_dummies(df.copy(), columns=["medio_pago"], prefix="medio")
    nuevas_cols = [c for c in df_encoded.columns if c.startswith("medio_")]
    print("Columnas generadas:")
    print(nuevas_cols)


def correlaciones_numericas(df):
    print("\n🧩 MATRIZ DE CORRELACIÓN (variables numéricas):")
    df_encoded = pd.get_dummies(df.copy(), columns=["medio_pago"], prefix="medio")
    corr = df_encoded.corr(numeric_only=True)
    print(corr.round(2))


def deteccion_outliers(df):
    print("\n🚩 DETECCIÓN DE OUTLIERS (IQR):")
    columnas_numericas = [col for col in ["cantidad", "precio_unitario", "importe"] if col in df.columns]
    for col in columnas_numericas:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lim_inf = Q1 - 1.5 * IQR
        lim_sup = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lim_inf) | (df[col] > lim_sup)]
        print(f"\n📍 Variable: {col}")
        print(f" - IQR: {IQR:.2f}")
        print(f" - Límite inferior: {lim_inf:.2f}")
        print(f" - Límite superior: {lim_sup:.2f}")
        print(f" - Outliers detectados: {outliers.shape[0]} registros")


def analisis_clientes(df):
    print("\n🧑‍🤝‍🧑 CLIENTES: gasto total, compras y ticket promedio")
    if not all(c in df.columns for c in ["id_cliente", "importe"]):
        print("No se encuentran las columnas necesarias para el análisis de clientes.")
        return
    agrupado = (
        df.groupby(["id_cliente"], as_index=False)
          .agg(
              nombre_cliente=("nombre_cliente", "first") if "nombre_cliente" in df.columns else ("id_cliente", "first"),
              ciudad=("ciudad", "first") if "ciudad" in df.columns else ("id_cliente", "first"),
              compras=("id_venta", "nunique") if "id_venta" in df.columns else ("id_cliente", "size"),
              total_gastado=("importe", "sum"),
              ticket_promedio_cliente=("importe", "mean"),
              fecha_ultima_compra=("fecha", "max") if "fecha" in df.columns else ("id_cliente", "first"),
          )
    )
    print("Clientes con mayor gasto total (top 10):")
    try:
        print(agrupado.sort_values("total_gastado", ascending=False).head(10).round(2))
    except Exception:
        print(agrupado.sort_values("total_gastado", ascending=False).head(10))
    print("\nEstadísticas generales de clientes:\n")
    try:
        print(agrupado[["compras", "total_gastado", "ticket_promedio_cliente"]].describe().round(2))
    except Exception:
        print(agrupado[["compras", "total_gastado", "ticket_promedio_cliente"]].describe())


def ver_tabla_unificada(df):
    print("\n📄 TABLA UNIFICADA:")
    try:
        print("Forma:", df.shape)
        print("\nColumnas:")
        print(df.columns.tolist())
        print("\nVista previa:")
        try:
            print(df.head(10))
        except Exception:
            print(df.head())
        print("\nNulos por columna:")
        print(df.isnull().sum())
    except Exception as e:
        print(f"Error al visualizar la tabla unificada: {e}")


def heatmap_correlaciones(df):
    print("\n🧩 MATRIZ DE CORRELACIÓN (heatmap):")
    df_encoded = pd.get_dummies(df.copy(), columns=["medio_pago"], prefix="medio")
    corr = df_encoded.corr(numeric_only=True)
    try:
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, cmap="crest", annot=False)
        plt.title("Matriz de correlación (variables numéricas)")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("No se pudo mostrar el heatmap, imprimiendo la matriz redondeada en su lugar:")
        print(corr.round(2))


def grafico_distribucion_importe(df):
    print("\n📈 Distribución de 'importe' (histograma + KDE):")
    if "importe" not in df.columns:
        print("No se encuentra la columna 'importe'.")
        return
    plt.figure(figsize=(7,5))
    try:
        sns.histplot(df["importe"].dropna(), kde=True, bins=30, color="#4c78a8")
    except Exception:
        plt.hist(df["importe"].dropna(), bins=30, color="#4c78a8")
    plt.xlabel("Importe")
    plt.ylabel("Frecuencia")
    plt.title("Distribución de Importe")
    plt.tight_layout()
    plt.show()


def boxplot_importe_por_medio(df):
    print("\n📦 Boxplot de 'importe' por 'medio_pago':")
    if not all(c in df.columns for c in ["importe", "medio_pago"]):
        print("No se encuentran las columnas necesarias ('importe', 'medio_pago').")
        return
    plt.figure(figsize=(8,5))
    sns.boxplot(data=df, x="medio_pago", y="importe", palette="crest")
    plt.title("Importe por Medio de Pago")
    plt.xlabel("Medio de Pago")
    plt.ylabel("Importe")
    plt.tight_layout()
    plt.show()

def abrir_readme():
    """
    Abre el archivo README.md con la aplicación predeterminada del sistema operativo.
    Utiliza os.startfile() en Windows, 'open' en macOS y 'xdg-open' en Linux.
    """
    ruta_readme = "../README.md"
    
    if not os.path.exists(ruta_readme):
        print("❌ Error: No se encontró el archivo README.md en la ruta especificada.")
        print(f"   Ruta buscada: {os.path.abspath(ruta_readme)}")
        return
    
    try:
        if sys.platform == "win32":
            # Windows
            os.startfile(os.path.abspath(ruta_readme))
        elif sys.platform == "darwin":
            # macOS
            subprocess.Popen(["open", os.path.abspath(ruta_readme)])
        else:
            # Linux y otros
            subprocess.Popen(["xdg-open", os.path.abspath(ruta_readme)])
        
        print("✅ README.md abierto correctamente.")
    except Exception as e:
        print(f"❌ Error al intentar abrir README.md: {e}")

def cargar_documentacion_tema():
    """Opción 2: Tema, problema y solución"""
    print("\n" + "="*60)
    print("📌 TEMA, PROBLEMA Y SOLUCIÓN")
    print("="*60)
    print("""
TEMA:
Este proyecto simula la gestión de una Tienda a partir de datos sintéticos.

PROBLEMA:
El objetivo es determinar cuál es el medio de pago más utilizado por los clientes 
en la Tienda y comprender los patrones de comportamiento asociados.

SOLUCIÓN:
Desarrollo de un sistema de análisis de datos que permite:
- Procesar información de ventas y clientes
- Identificar patrones de pagos
- Generar reportes sobre métodos de pago más frecuentes
    """)

def cargar_dataset_referencia():
    """Opción 3: Dataset de referencia"""
    print("\n" + "="*60)
    print("📊 DATASET DE REFERENCIA")
    print("="*60)
    print("""
FUENTE: Datos sintéticos educativos, generados por Guayerd e IBM.

TABLAS:
1. Productos (productos.xlsx) - 100 filas
   - id_producto, nombre_producto, categoria, precio_unitario

2. Clientes (clientes.xlsx) - 100 filas
   - id_cliente, nombre_cliente, ciudad, fecha_alta

3. Ventas (ventas.xlsx) - 120 filas
   - id_venta, fecha, id_cliente, medio_pago

4. Detalle Ventas (detalle_ventas.xlsx) - 300+ filas
   - id_venta, id_producto, cantidad, importe

PERÍODO: Enero - Junio 2024
CIUDADES: Carlos Paz, Río Cuarto, Mendiolaza, Villa María, Alta Gracia, Córdoba
    """)

def cargar_pasos_pseudocodigo():
    """Opción 4: Pasos, pseudocódigo y diagrama"""
    print("\n" + "="*60)
    print("🔧 PASOS, PSEUDOCÓDIGO Y DIAGRAMA")
    print("="*60)
    print("""
PASOS DEL PROGRAMA:
1. Mostrar un menú numérico con opciones disponibles
2. Imprimir texto asociado a la opción escogida
3. Mantener acceso al menú hasta seleccionar "Salir"

PSEUDOCÓDIGO OPTIMIZADO:
INICIO
    Mientras True:
        Mostrar opciones (1-15)
        Leer opción
        Si opción == 15:
            Romper bucle (Salir)
        Sino si opción >= 1 y opción <= 14:
            Ejecutar función asociada
        Sino:
            Imprimir 'Opción inválida'
FIN

DIAGRAMA: Consultar archivo Diagrama_Flujo.png en la carpeta del proyecto
    """)

def cargar_mejoras_copilot():
    """Opción 5: Sugerencias y mejoras con Copilot"""
    print("\n" + "="*60)
    print("💡 SUGERENCIAS Y MEJORAS APLICADAS CON COPILOT")
    print("="*60)
    print("""
MEJORAS IMPLEMENTADAS:

1. Optimización del pseudocódigo
   - Mejorada la lógica de control de opciones
   - Se evitaron condiciones redundantes
   
2. Validación de entrada
   - Manejo de opciones inválidas
   - Control de errores en conversión de tipos
   
3. Claridad en la estructura
   - Simplificación del flujo de control
   - Mejor comprensión del programa
   
4. Eficiencia
   - Reducción de líneas de código
   - Reutilización de funciones
   
5. Eliminación de funcionalidad redundante
   - Removido One-Hot Encoding (opción 9 anterior)
   - Información ya disponible en análisis de correlaciones
    """)

def cargar_ejecutar_documentacion(df_maestro):
    """Opción 6: Cargar tabla_unificada.csv y ejecutar documentación"""
    print("\n" + "="*60)
    print("📁 CARGAR TABLA UNIFICADA Y EJECUTAR DOCUMENTACIÓN")
    print("="*60)
    
    try:
        # Obtener la ruta base del script actual
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construir la ruta a la carpeta database
        database_dir = os.path.join(script_dir, "..", "database")
        database_dir = os.path.normpath(database_dir)
        
        csv_path = os.path.join(database_dir, "tabla_unificada.csv")
        csv_path = os.path.normpath(csv_path)
        
        print(f"🔍 Buscando tabla unificada en: {csv_path}")
        
        # Intentar cargar la tabla unificada
        if os.path.exists(csv_path):
            df_maestro = pd.read_csv(csv_path)
            print("✅ Tabla unificada cargada exitosamente desde tabla_unificada.csv")
            print(f"   Dimensiones: {df_maestro.shape}")
            print(f"   Columnas: {df_maestro.columns.tolist()}")
            return df_maestro
        else:
            print(f"⚠️ Archivo tabla_unificada.csv no encontrado en: {csv_path}")
            print("   Intentando cargar desde fuentes individuales (Excel)...\n")
            
            # Rutas a los archivos Excel
            clientes_path = os.path.join(database_dir, "clientes.xlsx")
            productos_path = os.path.join(database_dir, "productos.xlsx")
            ventas_path = os.path.join(database_dir, "ventas.xlsx")
            detalle_path = os.path.join(database_dir, "detalle_ventas.xlsx")
            
            # Verificar que todos los archivos existan
            archivos_requeridos = {
                "clientes.xlsx": clientes_path,
                "productos.xlsx": productos_path,
                "ventas.xlsx": ventas_path,
                "detalle_ventas.xlsx": detalle_path
            }
            
            archivos_faltantes = [nombre for nombre, ruta in archivos_requeridos.items() if not os.path.exists(ruta)]
            
            if archivos_faltantes:
                print(f"❌ Error: Faltan los siguientes archivos en {database_dir}:")
                for archivo in archivos_faltantes:
                    print(f"   - {archivo}")
                return None
            
            print("📥 Cargando archivos Excel...")
            clientes = pd.read_excel(clientes_path)
            productos = pd.read_excel(productos_path)
            ventas = pd.read_excel(ventas_path)
            detalle = pd.read_excel(detalle_path)
            
            print("✅ Archivos Excel cargados correctamente")
            
            # Corrección de categorías
            keywords_alimentos = [
                "gallet", "harina", "fideo", "aceite", "azúcar", "yerba",
                "arroz", "leche", "pan", "helado", "coca", "pepsi", "sprite",
                "fanta", "agua", "medialuna", "aceituna", "café", "vino",
                "fernet", "cerveza", "hamburguesa", "queso", "jamón"
            ]
            
            def corregir_categoria(nombre):
                nombre_lower = nombre.lower()
                for palabra in keywords_alimentos:
                    if palabra in nombre_lower:
                        return "Alimentos"
                return "Limpieza"
            
            print("🔧 Corrigiendo categorías de productos...")
            productos["categoria_corregida"] = productos["nombre_producto"].apply(corregir_categoria)
            
            # Imputación de importes faltantes
            print("🔧 Imputando importes faltantes...")
            detalle["importe"] = detalle.apply(
                lambda row: row["cantidad"] * row["precio_unitario"] 
                if pd.isna(row["importe"]) else row["importe"],
                axis=1
            )
            
            # Merges en cascada
            print("🔗 Uniendo tablas en cascada...")
            detalle_productos = detalle.merge(
                productos[["id_producto", "categoria_corregida", "precio_unitario"]],
                on="id_producto", how="left"
            )
            
            detalle_ventas = detalle_productos.merge(
                ventas[["id_venta", "fecha", "id_cliente", "medio_pago"]],
                on="id_venta", how="left"
            )
            
            df_maestro = detalle_ventas.merge(
                clientes[["id_cliente", "nombre_cliente", "email", "ciudad", "fecha_alta"]],
                on="id_cliente", how="left"
            )
            
            # Guardar tabla unificada
            print(f"💾 Guardando tabla unificada en: {csv_path}")
            df_maestro.to_csv(csv_path, index=False)
            print("✅ Tabla unificada creada y guardada en tabla_unificada.csv")
            print(f"   Dimensiones: {df_maestro.shape}")
            
            return df_maestro
    
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al cargar datos: {e}")
        import traceback
        traceback.print_exc()
        return None

def visualizar_tabla_unificada(df_maestro):
    """Opción 7: Visualizar tabla unificada"""
    print("\n" + "="*60)
    print("📊 VISUALIZAR TABLA UNIFICADA")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    print(f"\n✅ Dimensiones (filas, columnas): {df_maestro.shape}")
    print(f"\n✅ Columnas disponibles:")
    print(df_maestro.columns.tolist())
    print(f"\n✅ Muestra de datos (primeras 5 filas):")
    print(df_maestro.head())
    print(f"\n✅ Valores nulos por columna:")
    print(df_maestro.isnull().sum())

def resultados_estadisticos_generales(df_maestro):
    """Opción 8: Resultados estadísticos generales"""
    print("\n" + "="*60)
    print("📈 RESULTADOS ESTADÍSTICOS GENERALES")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    print("\n✅ Estadísticas descriptivas (variables numéricas):")
    print(df_maestro.describe().round(2))
    
    print("\n✅ Información sobre tipos de datos:")
    print(df_maestro.info())

def medios_pago_conteo_porcentaje(df_maestro):
    """Opción 9: Medios de pago - conteo y porcentaje"""
    print("\n" + "="*60)
    print("💳 MEDIOS DE PAGO: CONTEO Y PORCENTAJE")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    print("\n✅ Conteo de medios de pago:")
    conteo = df_maestro["medio_pago"].value_counts()
    print(conteo)
    
    print("\n✅ Porcentaje de participación:")
    porcentaje = (df_maestro["medio_pago"].value_counts(normalize=True) * 100).round(2)
    print(porcentaje)
    
    # Tabla combinada
    resumen_medios = pd.DataFrame({
        "Frecuencia": conteo,
        "Porcentaje (%)": porcentaje
    })
    print("\n✅ Resumen combinado:")
    print(resumen_medios)

def matriz_correlaciones(df_maestro):
    """Opción 10: Matriz de correlaciones"""
    print("\n" + "="*60)
    print("📊 MATRIZ DE CORRELACIONES")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    # Seleccionar solo columnas numéricas
    cols_numericas = ["cantidad", "precio_unitario", "importe"]
    
    # Verificar que las columnas existan
    cols_disponibles = [col for col in cols_numericas if col in df_maestro.columns]
    
    if not cols_disponibles:
        print("❌ Error: No se encontraron columnas numéricas esperadas.")
        return
    
    print("\n✅ Matriz de Correlación (Pearson):")
    corr_matrix = df_maestro[cols_disponibles].corr(method="pearson")
    print(corr_matrix.round(2))
    
    # Visualizar con heatmap
    print("\n✅ Generando heatmap de correlaciones...")
    plt.figure(figsize=(6, 4))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Mapa de Calor – Correlación entre Variables Numéricas", fontsize=13, weight="bold")
    plt.tight_layout()
    plt.show()

def deteccion_outliers(df_maestro):
    """Opción 11: Detección de outliers (IQR)"""
    print("\n" + "="*60)
    print("🎯 DETECCIÓN DE OUTLIERS (MÉTODO IQR)")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    variables_numericas = ["cantidad", "precio_unitario", "importe"]
    
    print("\n✅ Análisis de outliers por variable:\n")
    
    for var in variables_numericas:
        Q1 = df_maestro[var].quantile(0.25)
        Q3 = df_maestro[var].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        outliers = df_maestro[(df_maestro[var] < limite_inferior) | (df_maestro[var] > limite_superior)]
        cantidad_outliers = outliers.shape[0]
        
        print(f"📍 Variable: {var}")
        print(f"   - Rango Intercuartílico (IQR): {IQR:.2f}")
        print(f"   - Límite inferior: {limite_inferior:.2f}")
        print(f"   - Límite superior: {limite_superior:.2f}")
        print(f"   - Outliers detectados: {cantidad_outliers} registros ({(cantidad_outliers/len(df_maestro)*100):.2f}%)")
        print()

def grafico_frecuencia_medios_pago(df_maestro):
    """Opción 12: Gráfico - Frecuencia de medios de pago"""
    print("\n" + "="*60)
    print("📊 GRÁFICO: FRECUENCIA DE MEDIOS DE PAGO")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    conteo = df_maestro["medio_pago"].value_counts()
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x=conteo.index, y=conteo.values, palette="crest")
    plt.title("Distribución de Medios de Pago", fontsize=13, weight="bold")
    plt.xlabel("Medio de Pago")
    plt.ylabel("Cantidad de Operaciones")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

def grafico_distribucion_importe(df_maestro):
    """Opción 13: Gráfico - Distribución de importe"""
    print("\n" + "="*60)
    print("📊 GRÁFICO: DISTRIBUCIÓN DE IMPORTE")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    plt.figure(figsize=(10, 5))
    sns.histplot(df_maestro["importe"], kde=True, bins=30)
    plt.title("Distribución del Importe", fontsize=13, weight="bold")
    plt.xlabel("Importe ($)")
    plt.ylabel("Frecuencia")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

def grafico_boxplot_importe_medio_pago(df_maestro):
    """Opción 14: Gráfico - Boxplot de importe por medio de pago"""
    print("\n" + "="*60)
    print("📊 GRÁFICO: BOXPLOT DE IMPORTE POR MEDIO DE PAGO")
    print("="*60)
    
    if df_maestro is None or df_maestro.empty:
        print("❌ Error: No hay datos cargados. Ejecuta la opción 6 primero.")
        return
    
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df_maestro, x="medio_pago", y="importe", palette="Set2")
    plt.title("Distribución del Importe por Medio de Pago", fontsize=13, weight="bold")
    plt.xlabel("Medio de Pago")
    plt.ylabel("Importe ($)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

def main():
    """Función principal con menú interactivo"""
    df_maestro = None
    
    print("\n" + "="*60)
    print("🏪 BIENVENIDO AL PROGRAMA DE ANÁLISIS DE TIENDA")
    print("="*60)
    
    while True:
        print("\n" + "="*60)
        print("📋 MENÚ PRINCIPAL - SELECCIONA UNA OPCIÓN")
        print("="*60)
        print("""
1.  Abrir README.md
2.  Tema, problema y solución
3.  Dataset de referencia
4.  Pasos, pseudocódigo y diagrama
5.  Sugerencias y mejoras con Copilot
6.  Cargar tabla_unificada.csv y ejecutar documentación
7.  Visualizar tabla unificada (shape, columnas, muestra, nulos)
8.  Resultados estadísticos generales (describe)
9.  Medios de pago: conteo y porcentaje
10. Matriz de correlaciones (tabla + heatmap)
11. Detección de outliers (IQR)
12. Gráfico: Frecuencia de medios de pago
13. Gráfico: Distribución de importe
14. Gráfico: Boxplot de importe por medio de pago
15. Salir
        """)
        
        try:
            opcion = input("Ingresa el número de la opción: ").strip()
            
            if opcion == "1":
                abrir_readme()
            elif opcion == "2":
                cargar_documentacion_tema()
            elif opcion == "3":
                cargar_dataset_referencia()
            elif opcion == "4":
                cargar_pasos_pseudocodigo()
            elif opcion == "5":
                cargar_mejoras_copilot()
            elif opcion == "6":
                df_maestro = cargar_ejecutar_documentacion(df_maestro)
            elif opcion == "7":
                visualizar_tabla_unificada(df_maestro)
            elif opcion == "8":
                resultados_estadisticos_generales(df_maestro)
            elif opcion == "9":
                medios_pago_conteo_porcentaje(df_maestro)
            elif opcion == "10":
                matriz_correlaciones(df_maestro)
            elif opcion == "11":
                deteccion_outliers(df_maestro)
            elif opcion == "12":
                grafico_frecuencia_medios_pago(df_maestro)
            elif opcion == "13":
                grafico_distribucion_importe(df_maestro)
            elif opcion == "14":
                grafico_boxplot_importe_medio_pago(df_maestro)
            elif opcion == "15":
                print("\n👋 ¡Hasta luego! Gracias por usar el programa de análisis.")
                break
            else:
                print("❌ Opción no válida. Por favor, ingresa un número entre 1 y 15.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido por el usuario.")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            print("   Por favor, intenta de nuevo.")

if __name__ == "__main__":
    main()