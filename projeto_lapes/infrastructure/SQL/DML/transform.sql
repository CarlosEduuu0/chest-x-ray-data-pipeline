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
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Finding Labels" TO patologia;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Patient Age" TO idades;""")
            con.execute(f"""ALTER TABLE gold_pacientes RENAME COLUMN "Image Index" TO index_da_imagem;""")
        except duckdb.CatalogException:

                 ""
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