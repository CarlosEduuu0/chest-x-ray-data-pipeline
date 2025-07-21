# 🫁 Projeto: Pipeline de Dados para Diagnóstico por Raio-X de Tórax

Este projeto implementa uma pipeline completa para processamento e análise de imagens de raio-X do tórax, com foco em detecção automática de patologias como **pneumonia**. Ele inclui:

✅ Um **Data Lake** organizado em camadas  
✅ Três **Modelos de Machine Learning**  
✅ Dois **Modelos de Deep Learning (CNN)**  
✅ Um **site com dashboards interativos (Dash)**

---

## 🤖 Modelos Treinados

### Machine Learning
- 🔹 Regressão Logística com ponderação
- 🔹 Support Vector Machine (SVM)
- 🔹 Random Forest Classifier

### Deep Learning
- 🔸 VGG16 com extração de features
- 🔸 CheXNet (DenseNet121 pré-treinada)

---

## 📊 Dashboards

Você pode visualizar os resultados do pipeline, métricas dos modelos e estatísticas do dataset em um site interativo criado com **Plotly Dash**.

---

## 🚀 Instruções para Execução

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/projeto_lapes.git
   cd projeto_lapes
   Baixe o dataset NIH Chest X-Ray a partir deste link:

👉 https://www.kaggle.com/datasets/nih-chest-xrays

Extraia apenas as imagens e coloque-as na pasta:

D:/projeto_lapes/data/chest_x-ray/images/

Instale as dependências:

e por fim voce pode executar tanto o datalake quanto o dashboard ou os noteboks dos modelos
