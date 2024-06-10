import os
import librosa
import sys
import csv

def guardar_resultados_en_archivo(archivos_bpm, ruta_archivo):
    with open(ruta_archivo, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Archivo', 'BPM'])
        for archivo_bpm in archivos_bpm:
            writer.writerow([archivo_bpm['Archivo'], archivo_bpm['BPM']])

def cargar_resultados_desde_archivo(ruta_archivo):
    archivos_bpm = []
    with open(ruta_archivo, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Saltar la primera fila (encabezados)
        for row in reader:
            archivos_bpm.append({'Archivo': row[0], 'BPM': float(row[1])})
    return archivos_bpm

def obtener_bpm_archivos_en_directorio(directorio):
    # Verificar si existe un archivo con resultados previos para el directorio especificado
    nombre_directorio = os.path.basename(os.path.normpath(directorio))
    ruta_archivo_resultados = os.path.join(os.getcwd(), f'resultados_bpm_{nombre_directorio}.csv')
    if os.path.exists(ruta_archivo_resultados):
        # Cargar los resultados desde el archivo
        archivos_bpm = cargar_resultados_desde_archivo(ruta_archivo_resultados)
        
        # Verificar si cada archivo en la lista de resultados aún existe en el directorio
        archivos_bpm_actualizados = []
        for archivo_bpm in archivos_bpm:
            ruta_archivo = os.path.join(directorio, archivo_bpm['Archivo'])
            if os.path.exists(ruta_archivo):
                archivos_bpm_actualizados.append(archivo_bpm)
        
        # Actualizar la lista de resultados
        archivos_bpm = archivos_bpm_actualizados
    else:
        # Inicializar la lista de resultados vacía
        archivos_bpm = []
    
    # Recorrer todos los archivos del directorio
    archivos = os.listdir(directorio)
    for i, archivo in enumerate(archivos):
        ruta_archivo = os.path.join(directorio, archivo)
        
        # Verificar si es un archivo de audio MP3 o WAV
        if archivo.endswith(".mp3") or archivo.endswith(".wav"):
            # Verificar si el archivo ya ha sido analizado
            archivo_analizado = False
            for archivo_bpm in archivos_bpm:
                if archivo_bpm['Archivo'] == archivo:
                    archivo_analizado = True
                    break
            
            if not archivo_analizado:
                try:
                    # Imprimir mensaje de espera con el porcentaje total y el número de archivo que se está analizando
                    porcentaje_carga = int((i + 1) / len(archivos) * 100)
                    sys.stdout.write(f"\r{porcentaje_carga}% Analizando audio {i + 1}/{len(archivos)}")
                    sys.stdout.flush()
                    
                    # Cargar el archivo de audio
                    audio_data, sr = librosa.load(ruta_archivo, sr=None)
                    
                    # Eliminar el silencio al principio y al final del audio
                    audio_data, _ = librosa.effects.trim(audio_data)
                    
                    # Calcular el tempo (BPM)
                    tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr, hop_length=512)
                    
                    # Multiplicar por dos el BPM si es menor a 100
                    if tempo < 100:
                        tempo *= 2
                    
                    # Agregar el nombre del archivo y el BPM a la lista
                    archivos_bpm.append({"Archivo": archivo, "BPM": tempo})
                    
                    # Formatear el BPM para que solo tenga un dígito después del punto decimal
                    bpm = round(tempo, 1)
                    
                    # Imprimir el número de orden, el BPM y el nombre completo del archivo
                    print(f"\r{i+1}.  {bpm} bpm | {archivo}")
                except Exception as e:
                    print(f"\nError al analizar el archivo {archivo}: {str(e)}")
    
    # Guardar los resultados en un archivo
    guardar_resultados_en_archivo(archivos_bpm, ruta_archivo_resultados)
    
    return archivos_bpm

while True:
    try:
        # Obtener la ruta del directorio desde el usuario
        directorio = input("\nPATH: ")
        
        # Verificar si el usuario desea salir del programa
        if directorio.lower() == 'exit':
            break
        
        # Obtener la lista de archivos y BPMs
        archivos_bpm = obtener_bpm_archivos_en_directorio(directorio)

        # Imprimir la línea horizontal superior
        print("____________________________________\n")

        # Ordenar la lista de resultados por el nombre del archivo
        archivos_bpm = sorted(archivos_bpm, key=lambda x: x['Archivo'])

        # Imprimir los resultados
        for i, archivo_bpm in enumerate(archivos_bpm):
            # Formatear el BPM para que solo tenga un dígito después del punto decimal
            bpm = round(archivo_bpm['BPM'], 1)
            
            # Imprimir el número de orden, el BPM y el nombre completo del archivo
            print(f"{i+1}.  {bpm} bpm | {archivo_bpm['Archivo']}")

        # Imprimir la línea horizontal inferior
        print("____________________________________")
    except KeyboardInterrupt:
        break
