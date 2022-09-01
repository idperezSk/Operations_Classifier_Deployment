import time
from matplotlib.pyplot import axis
import pandas as pd # Libreria para el manejo de Dataframes (Datos estructurados).
import numpy as np  # libreria para el manejo de series o Vectores.
import pyodbc  # Libreria para conexion con Azure SQL.
import keras
from requests import head
from sklearn.preprocessing import StandardScaler

# Credenciales para la conexion a BD.
server = 'siindependenceserver.database.windows.net'
database = 'OxyDB'
username = 'indsii'
password = '1nd3p3nd3nc32019*'
driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server +
                      ';PORT=1433;DATABASE='+database+';UID='+username+';PWD=' + password)

# Cargo el modelo
model = keras.models.load_model('operations_model_60In_23_125.h5')

def query(regs):

    query_sql = f'''SELECT TOP {regs} fecha_hora, posicion_bloque, profundidad, velocidad_bloque, carga_gancho, contador_tuberia
            FROM Oxy.Oxy_Operational_data
            WHERE deviceId = 'IndependenceRig23'
            ORDER BY fecha_hora DESC
          '''

    data = pd.read_sql(query_sql, cnxn)
    data = data.sort_values('fecha_hora').reset_index(drop=True)
    return data

def get_data(regs):

    data = query(regs)
    columns = ['posicion_bloque', 'profundidad', 'velocidad_bloque', 'carga_gancho', 'contador_tuberia']

    scaler = StandardScaler()
    scaler.fit(data[columns].values)

    data_Scale = scaler.transform(data[columns].values)

    data_expand = np.expand_dims(data_Scale, axis=0)

    labels = ['A', 'B', 'C', 'D', 'OTHER']    

    prediction = model.predict(data_expand)

    value_label = labels[np.argmax(prediction)]
    if value_label == 'A' or value_label == 'C':
        value_label = 'POOH'
    elif value_label == 'B' or value_label == 'D':
        value_label = 'RIH'
        
    print(value_label)

    tag = [value_label]*data_expand.shape[1]

    data['Ops'] = tag

    return data

def update_data(data_record):

    data_temp = get_data(60) # Obtengo los n registros mas recientes

    # Obtengo los datos nuevos que no están en data_record
    df_all = data_temp.merge(data_record.drop_duplicates('fecha_hora'), how='left', indicator=True)
    new_records = df_all['_merge'].value_counts()['left_only']
    print(f'Hay {new_records} nuevos registros')
    df_all = df_all.drop(df_all.head(len(df_all)-new_records).index)
    df_all = df_all.drop('_merge', axis=1)

    data_record = pd.concat([data_record, df_all])

    return data_record
    