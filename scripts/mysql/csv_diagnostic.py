# csv_diagnostic.py
import os
import pandas as pd
from pathlib import Path

def diagnose_csv_loading():
    """
    Diagnóstico paso a paso del proceso de carga de CSV
    """
    print("\n🔍 Iniciando diagnóstico de carga de CSV...")

    # 1. Verificar directorio data
    data_dir = 'data'
    print(f"\n1. Verificando directorio 'data':")
    if os.path.exists(data_dir):
        print(f"✅ Directorio '{data_dir}' encontrado")
        print(f"   Ruta absoluta: {os.path.abspath(data_dir)}")
    else:
        print(f"❌ Directorio '{data_dir}' no encontrado")
        return

    # 2. Buscar archivos CSV
    print("\n2. Buscando archivos CSV:")
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if csv_files:
        print(f"✅ Se encontraron {len(csv_files)} archivos CSV:")
        for file in csv_files:
            file_path = os.path.join(data_dir, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size/1024:.2f} KB)")
    else:
        print("❌ No se encontraron archivos CSV")
        return

    # 3. Intentar leer cada archivo
    print("\n3. Intentando leer cada archivo:")
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        print(f"\nArchivo: {file}")
        
        success = False
        # Intentar con diferentes combinaciones de encoding y separador
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        separators = [';', ',', '|', '\t']
        
        for encoding in encodings:
            if success:
                break
                
            for sep in separators:
                try:
                    # Primero leemos solo unas pocas líneas para detectar problemas
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=5)
                    
                    # Si llegamos aquí, la lectura fue exitosa
                    success = True
                    print(f"✅ Lectura exitosa con:")
                    print(f"   - Encoding: {encoding}")
                    print(f"   - Separador: '{sep}'")
                    print(f"   - Columnas encontradas: {len(df.columns)}")
                    print("\n   Nombres de columnas:")
                    for col in df.columns:
                        print(f"      - {col}")
                    
                    # Verificar consistencia en el número de campos
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = [line.strip() for line in f.readlines()[:10]]
                        fields_per_line = [len(line.split(sep)) for line in lines if line]
                        
                    if len(set(fields_per_line)) > 1:
                        print("\n⚠️ Advertencia: Número inconsistente de campos entre líneas:")
                        for i, count in enumerate(fields_per_line):
                            print(f"      Línea {i+1}: {count} campos")
                    
                    print(f"\n   Muestra de datos:")
                    print(df.head().to_string())
                    break
                    
                except UnicodeDecodeError:
                    continue
                except pd.errors.EmptyDataError:
                    print(f"❌ Error: Archivo vacío")
                    break
                except Exception as e:
                    continue
        
        if not success:
            print("❌ No se pudo leer el archivo con ninguna combinación de encoding y separador")
            print("   Intentando leer las primeras líneas directamente:")
            try:
                with open(file_path, 'r', encoding='cp1252') as f:
                    print("\n   Primeras 5 líneas del archivo:")
                    for i, line in enumerate(f):
                        if i < 5:
                            print(f"      {line.strip()}")
            except Exception as e:
                print(f"❌ Error al leer el archivo directamente: {str(e)}")

    print("\n📋 Resumen del diagnóstico:")
    print(f"- Directorio data existe: ✅")
    print(f"- Archivos CSV encontrados: {len(csv_files)}")
    print("\nPróximos pasos recomendados:")
    print("1. Verifica que los archivos CSV tengan el formato esperado")
    print("2. Asegúrate de que los nombres de las columnas sean válidos")
    print("3. Revisa que el separador y encoding sean consistentes")

if __name__ == "__main__":
    diagnose_csv_loading()