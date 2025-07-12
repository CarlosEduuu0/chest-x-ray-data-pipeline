 CREATE TABLE IF NOT EXISTS {table_name} AS 
                    SELECT * FROM read_parquet('{file_path}/**/*.parquet')

                    CREATE TABLE IF NOT EXISTS {table_name} AS
                    SELECT * FROM read_parquet('{file_path}')