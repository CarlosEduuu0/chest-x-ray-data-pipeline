# CheXNet - Classificação de Patologias Torácicas com PyTorch

## 📌 Objetivo
indentificar e diferenciar as patologias achadas no dataset por meio de visao computacional
---

## 🧠 Arquitetura do Modelo

- **estrutura central:** `DenseNet121` pré-treinado com pesos `torchvision.models.DenseNet121_Weights.DEFAULT`.
- **Camada final substituída:**  
  - Linear (num_features → num_classes)
  - Sigmoid (para ativação multi-label)
- **Função de perda:** `BCELoss` (Binary Cross-Entropy)
- **Otimizador:** `Adam` com `lr=1e-4`
- **Dispositivo:** Treinável em **GPU** (usando `torch.device("cuda")` se disponível)

---

## 📂 Estrutura do Dataset

- **Imagens:** RGB, resolvidas para 224x224 pixels
- **patologias:** Obtidos da coluna `"patologia"` no arquivo Parquet, com patologias separadas por `"|"`.
- **Pré-processamento:**
  - Exclusão de `"No Finding"`
  - Binarização multi-label via `MultiLabelBinarizer`
  - Normalização com médias e desvios padrão de `ImageNet`

---

## 🔁 Pipeline de Treinamento

1. **Carregamento do Dataset:**
   - Parquet: `/datalake/gold/paciente_gold.parquet`
   - Imagens: `/data/chest_x-ray/images`
   - Subconjunto: 20.000 amostras aleatórias
2. **Transformações:**
   - Resize 224x224
   - Normalização para ImageNet
3. **Treinamento:**
   - `epochs=5`, `batch_size=32`
   - Relatório de perda por batch e média por época
4. **Avaliação:**
   - `classification_report` (Precision, Recall, F1 por classe)
   - Matriz de confusão (flattened micro)
   - Curvas ROC por classe
   - Visualização de previsões com imagem + labels verdadeiros e preditos

---

## 🔍 Interpretabilidade

- **Grad-CAM++ com `torchcam`:**
  - Camada alvo: `features[-1]` do DenseNet
  - Imagem com maior probabilidade é visualizada com sobreposição do mapa de ativação
  - Facilita a análise de onde o modelo foca para prever determinada patologia

---

## 💾 Salvamento do Modelo

```python
torch.save(model.state_dict(), "/scripts/models/chexnet_model.pth")