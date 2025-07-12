import pandas as pd
import os
import duckdb
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataLake:
    def __init__(self, base_path="datalake"):
        self.base_path = base_path
        self.conn = duckdb.connect(database=':memory:')
        logger.info(f"Data Lake inicializado em {base_path}")

    def ensure_directory_exists(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            logger.info(f"diretorio {self.base_path} criado")

    def extract(self, data, path, table_name, partition_by=None):

        os.makedirs(path, exist_ok=True)

        if partition_by:
            data.to_parquet(path, partition_cols=[partition_by], index=False)
            logger.info(f" dados ingeridos em {path} (particionado por {partition_by})")
            return path
        else:
            file_path = f"{path}/{table_name}.parquet"
            data.to_parquet(file_path, index=False)
            logger.info(f" Dados ingeridos em {file_path}")
            return file_path

    def register_parquet_file(self, file_path, table_name):
        try:
            if os.path.isdir(file_path):
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} AS 
                    SELECT * FROM read_parquet('{file_path}/**/*.parquet')
                """
                logger.info(f" diretorio particionado detectado: {file_path}")
            else:
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} AS 
                    SELECT * FROM read_parquet('{file_path}')
                """
                logger.info(f" Arquivo Parquet único detectado: {file_path}")

            self.conn.execute(query)
            logger.info(f" tabela '{table_name}' registrada com sucesso no duckDB.")

        except Exception as e:
            logger.error(f" erro ao registrar tabela '{table_name}': {str(e)}")
            raise

    def gerar_silver(self,input_path,output_path):
        con = duckdb.connect(database=':memory:')

        con.execute(f"""
            CREATE OR REPLACE TABLE silver_pacientes AS
            SELECT 
             *,
                CASE
                    WHEN upper("Patient Gender") IN ('M', 'MALE') THEN 'Male'
                    WHEN upper("Patient Gender") IN ('F', 'FEMALE') THEN 'Female'
                    ELSE NULL
                END AS genero
            FROM read_parquet('{input_path}')
            WHERE "Patient Age" BETWEEN 0 AND 100
              AND "Patient Gender" IS NOT NULL;
              
        """)

        try:
            con.execute(f"""ALTER TABLE silver_pacientes DROP COLUMN "Unnamed: 11";""")
            con.execute(f"""ALTER TABLE silver_pacientes DROP COLUMN "Patient ID";""")
            con.execute(f"""ALTER TABLE silver_pacientes DROP COLUMN "Patient Gender";""")
        except duckdb.CatalogException:
            print(" coluna  nao encontrada, ignorando...")

        con.execute(f"COPY silver_pacientes TO '{output_path}' (FORMAT 'parquet');")
        print("camada silver gerado com sucesso")

    def gerar_gold(self, input_path, output_path):
        con = duckdb.connect(database=':memory:')

        con.execute(f"""
            CREATE OR REPLACE TABLE gold_pacientes AS
            SELECT 
                "Image Index",
                "genero",
                "View Position",
                "Finding Labels",

                -- Colunas com valores normalizados sobrescrevendo os originais
                ("Patient Age" - MIN("Patient Age") OVER ()) / NULLIF((MAX("Patient Age") OVER () - MIN("Patient Age") OVER ()), 0) AS "Patient Age",
                ("OriginalImage[Width" - MIN("OriginalImage[Width") OVER ()) / NULLIF((MAX("OriginalImage[Width") OVER () - MIN("OriginalImage[Width") OVER ()), 0) AS "OriginalImage[Width",
                ("Height]" - MIN("Height]") OVER ()) / NULLIF((MAX("Height]") OVER () - MIN("Height]") OVER ()), 0) AS "Height]",
                ("OriginalImagePixelSpacing[x" - MIN("OriginalImagePixelSpacing[x") OVER ()) / NULLIF((MAX("OriginalImagePixelSpacing[x") OVER () - MIN("OriginalImagePixelSpacing[x") OVER ()), 0) AS "OriginalImagePixelSpacing[x",
                "y]"
            FROM read_parquet('{input_path}');
        """)


        try:
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "OriginalImage[Width" TO largura_original;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Height]" TO altura_original;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "OriginalImagePixelSpacing[x" TO espacamento_vertical;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "y]" TO espacamento_horizontal;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "View Position" TO angulo_de_vista;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Finding Labels" TO doencas;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Patient Age" TO idades;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Image Index" TO index_da_imagem;""")
        except duckdb.CatalogException:
            print(" algumas colunas ja estavam renomeadas ou nao foram encontradas.")

        con.execute(f"COPY gold_pacientes TO '{output_path}' (FORMAT 'parquet');")
        print(" camada gold recriada com colunas normalizadas!")

    def gerar_dimond(self,input_path,output_path):
        # para  camada dimond como sera utilizada apenas parea gerar dashboards so apgarei as colunas com injfos sobre as imagens
        con = duckdb.connect(database=':memory:')
        con.execute(f"""
                    CREATE TABLE diamond_pacientes AS
                    SELECT *
                    FROM read_parquet('{input_path}');
                    """)


        try:
            con.execute('ALTER TABLE diamond_pacientes DROP COLUMN largura_original;')
            con.execute('ALTER TABLE diamond_pacientes DROP COLUMN altura_original;')
            con.execute('ALTER TABLE diamond_pacientes DROP COLUMN espacamento_vertical;')
            con.execute('ALTER TABLE diamond_pacientes DROP COLUMN espacamento_horizontal;')
            con.execute('ALTER TABLE diamond_pacientes DROP COLUMN  angulo_de_vista;')
        except duckdb.CatalogException as e:
            print(f" algumas colunas nao foram encontradas: {e}")


        con.execute(f"""
               COPY diamond_pacientes TO'{output_path}' (FORMAT 'parquet');
           """)
        print(f" camada ciamond atualizada com colunas removidas.")

def main():

    df = pd.read_csv("D:/projeto_lapes/data/chest_x-ray/Data_Entry_2017.csv")

    dl = DataLake()

    file_path = dl.extract(df,'D:/projeto_lapes/datalake/bronze/pacientes',table_name='pacientes')

    dl.register_parquet_file(file_path, 'pacientes')
    dl.gerar_silver('D:/projeto_lapes/datalake/bronze/pacientes/pacientes.parquet','D:/projeto_lapes/datalake/silver/silver_pacientes.parquet')
    dl.gerar_gold('D:/projeto_lapes/datalake/silver/silver_pacientes.parquet', 'D:/projeto_lapes/datalake/gold/paciente_gold.parquet')
    dl.gerar_dimond('D:/projeto_lapes/datalake/gold/paciente_gold.parquet','D:/projeto_lapes/datalake/diamond/pacientes_dimond.parquet')

if __name__ == "__main__":
    main()
