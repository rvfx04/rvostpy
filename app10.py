import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime
from sqlalchemy import create_engine

# Parámetros de conexión
server = 'SQL5059.site4now.net'
database = 'db_a6b824_aql'
username = 'db_a6b824_aql_admin'
password = 'Drake2004'

try:
    # Cadena de conexión
    connection_string = f'mssql+pymssql://{username}:{password}@{server}/{database}'

    # Crear motor de SQLAlchemy
    engine = create_engine(connection_string)

    # Solicitar al usuario el código del pedido
    pedido_codigo = input("Ingrese el código del pedido que desea visualizar: ")

    # Consulta SQL para obtener los datos del pedido y proceso asociados
    sql_query = f"""
    SELECT p.Id_Pedido, p.Fecha_Emision, p.Fecha_Entrega, p.Nompedido, pr.Id_Proceso, pr.Tiempo, pr.Fecha_Inicial_Programada, pr.Fecha_Inicial_Real, pr.Fecha_Final_Real, pr.Porcentaje_Avance
    FROM Pedido p
    INNER JOIN Proceso pr ON p.Id_Pedido = pr.Id_Pedido
    WHERE p.Id_Pedido = '{pedido_codigo}'
    """


    # Leer datos del pedido y proceso en un DataFrame de pandas
    df = pd.read_sql(sql_query, engine)

    if df.empty:
        print(f"No se encontró ningún pedido con el código '{pedido_codigo}'")
    else:
        # Convertir las fechas a tipo datetime
        df['Fecha_Emision'] = pd.to_datetime(df['Fecha_Emision'])
        df['Fecha_Entrega'] = pd.to_datetime(df['Fecha_Entrega'])
        df['Fecha_Inicial_Programada'] = pd.to_datetime(df['Fecha_Inicial_Programada'])
        df['Fecha_Inicial_Real'] = pd.to_datetime(df['Fecha_Inicial_Real'])
        df['Fecha_Final_Real'] = pd.to_datetime(df['Fecha_Final_Real'])

        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Obtener la fecha de inicio y de entrega del Gantt
        fecha_inicio = df['Fecha_Emision'].iloc[0]
        fecha_entrega = df['Fecha_Entrega'].iloc[0]

        # Crear el gráfico de Gantt con un tamaño de figura más grande
        fig, ax = plt.subplots(figsize=(14, 5))

        # Establecer color de fondo de la figura y los ejes
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        # Definir coordenadas únicas para cada proceso
        coordenadas_procesos = range(len(df))

        # Colores para las barras y las líneas
        color_barras = 'slategrey'
        color_lineas = 'white'

        # Iterar sobre los procesos del pedido
        for index, row in df.iterrows():
            id_proceso = row['Id_Proceso']
            tiempo = row['Tiempo']
            fecha_inicial_programada = row['Fecha_Inicial_Programada']
            fecha_inicial_real = row['Fecha_Inicial_Real'] if not pd.isnull(row['Fecha_Inicial_Real']) else None
            fecha_final_real = row['Fecha_Final_Real'] if not pd.isnull(row['Fecha_Final_Real']) else None
            porcentaje_avance = row['Porcentaje_Avance']

            # Calcular la fecha de inicio y finalización del proceso
            start_date = fecha_inicial_programada
            end_date = start_date + pd.Timedelta(days=tiempo)

            # Calcular el porcentaje de avance respecto a lo programado
            porcentaje_real = 0
            if fecha_inicial_programada:
                dias_transcurridos = (fecha_actual - fecha_inicial_programada).days
                if dias_transcurridos < 0:
                    dias_transcurridos = 0
                else:
                    porcentaje_real = min((dias_transcurridos / tiempo) * 100, 100)

            # Calcular el color de la barra de acuerdo al porcentaje de avance real
            color_barra = 'royalblue' if porcentaje_avance > 0 else 'grey'

            # Calcular la longitud de la parte coloreada de la barra
            porcentaje_coloreado = min(porcentaje_avance, porcentaje_real) / 100

            # Dibujar la barra del proceso en el gráfico de Gantt
            ax.barh(y=coordenadas_procesos[index], width=(end_date - start_date).days, left=start_date, height=0.9, align='center', color=color_barras, edgecolor=color_barras, linewidth=1)  # Barra blanca
            ax.barh(y=coordenadas_procesos[index], width=(end_date - start_date).days * porcentaje_coloreado, left=start_date, height=0.9, align='center', color=color_barra, edgecolor=color_lineas, linewidth=1)  # Parte coloreada

            # Agregar marca en el día de inicio real del proceso con el porcentaje de avance
            if porcentaje_avance > 0:
                if fecha_inicial_real:
                    ax.plot([fecha_inicial_real, fecha_inicial_real], [coordenadas_procesos[index] - 0.4, coordenadas_procesos[index] + 0.4], color='lime', linewidth=3)

            if fecha_inicial_real:
                # Colocar el porcentaje a la derecha de la marca
                ax.text(fecha_inicial_real + pd.Timedelta(days=1.5), coordenadas_procesos[index], f"{porcentaje_avance}%", color='white', va='center', ha='left', weight='bold')

            # Agregar marca al final del proceso si el porcentaje es 100%
            if porcentaje_avance == 100:
                if fecha_final_real:
                    ax.plot([fecha_final_real, fecha_final_real], [coordenadas_procesos[index] - 0.4, coordenadas_procesos[index] + 0.4], color='lime', linewidth=3)

            # Agregar el porcentaje real al final de la barra del proceso
            ax.text(end_date + pd.Timedelta(days=0.5), coordenadas_procesos[index], f"{int(porcentaje_real)}%", color='red', va='center', ha='left', weight='bold')

        # Agregar líneas verticales cada día
        date_range = pd.date_range(start=fecha_inicio, end=fecha_entrega, freq='D')
        for date in date_range:
            ax.axvline(x=date, color=color_lineas, linestyle=':', linewidth=0.5)

        # Agregar una línea vertical en la fecha de entrega
        ax.axvline(x=fecha_entrega, color='red', linestyle='--')

        # Agregar una línea vertical en la fecha actual
        ax.axvline(x=fecha_actual, color='yellow', linestyle='--')

        # Configuración del formato de fecha en el eje x y reducir tamaño de fuente
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d_%b'))
        plt.xticks(fontsize=6, color='white')

        # Obtener el Nombre del Pedido
        NombrePedido = df['Nompedido'].iloc[0]

        # Configuración del gráfico
        ax.set_xlabel('Fecha', color='white')
        ax.set_ylabel('Proceso', color='white')
        ax.set_title(f'Carta Gantt de Procesos - {NombrePedido}', color='white')

        # Cambiar el color del marco del gráfico
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')

        # Invertir el eje y para mostrar el primer proceso arriba
        ax.invert_yaxis()

        # Ajustar el espacio entre las barras de los procesos en el eje y
        ax.set_yticks(coordenadas_procesos)
        ax.set_yticklabels(df['Id_Proceso'], fontsize=9, color='white')

        # Establecer las fechas en el eje x
        ax.set_xticks(pd.date_range(start=fecha_inicio, end=fecha_entrega, freq='2D'))
        ax.set_xticklabels([date.strftime('%d') for date in pd.date_range(start=fecha_inicio, end=fecha_entrega, freq='2D')], fontsize=6, rotation=0, ha='right')

        month_starts = pd.date_range(start=fecha_inicio, end=fecha_entrega, freq='MS')
        for month_start in month_starts:
            if month_start.day == 1:
                ax.text(month_start, 7.75, month_start.strftime('%b'), ha='center', fontsize=8, weight='bold', color='white')

        # Mostrar el gráfico
        plt.tight_layout()
        plt.show()

except Exception as e:
    print("Error al conectar a la base de datos:", e)
