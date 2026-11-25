"""ETL do Rodopar + cálculo do índice. Uso: python -m scripts.rodar_pipeline"""
from app.analise.executar import calcular_indices
from app.etl.sincronizar import sincronizar

if __name__ == "__main__":
    print("Snapshots gravados:", sincronizar())
    print("Clientes avaliados:", calcular_indices())
