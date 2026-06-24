# 🚀 VisiGuard AI — Document Verification ML Module
# 📌 Overview
The Document Verification ML Module is responsible for analyzing uploaded documents and determining their authenticity through forensic analysis and structural matching.
The system combines:
- 🔍 Error Level Analysis (ELA)
- 🧠 ResNet50 Feature Extraction
- 🤝 Siamese Network-Based Structural Matching
- 📏 Similarity Scoring
- 🎯 Multi-Modal Trust Score Generation
---
# 🏗️ Architecture
```
                DOCUMENT IMAGE
                       │
                       ▼
         ┌─────────────────────────┐
         │  Error Level Analysis   │
         │        (ELA)            │
         └─────────────────────────┘
                       │
                       ▼
                Forensic Score

                       +

         ┌─────────────────────────┐
         │     ResNet50 CNN        │
         │ Feature Extraction      │
         └─────────────────────────┘
                       │
                       ▼
              2048-D Embeddings

                       ▼

         ┌─────────────────────────┐
         │    Siamese Network      │
         │ Structural Matching     │
         └─────────────────────────┘
                       │
                       ▼
              128-D Embeddings

                       ▼

         ┌─────────────────────────┐
         │  Similarity Engine      │
         └─────────────────────────┘
                       │
                       ▼
              Structural Score

                       +

             Behavioral Score
          (External Team Module)

                       ▼

         ┌─────────────────────────┐
         │ MultiModal Risk Engine  │
         └─────────────────────────┘
                       │
                       ▼

              MASTER TRUST SCORE
```
# 📂 Project Structure for ML PART
```
VisiGuard-AI/
│
├── models/
│   │
│   ├── feature_extractor.py
│   │
│   ├── siamese.py
│   │
│   ├── Similarity.py
│   │
│   ├── contrastive_loss.py
│   │
│   ├── multimodel_risk_engine.py
│   │
│   └── ela.py
│
├── training/
│   │
│   └── inference.py
│
├── outputs/
│
└── README.md
```

# 🔬 Implemented Components

## 1️⃣ Error Level Analysis (ELA)
**File:** `models/ela.py`
### Purpose
Detects pixel-level tampering and image manipulation.
### Detects
- Forged signatures
- Edited balances
- Altered text fields
- Fake stamps/seals
- Copy-pasted regions
### Workflow
```
Original Image
      │
      ▼
JPEG Recompression
      │
      ▼
Difference Map
      │
      ▼
ELA Heatmap
      │
      ▼
Forensic Score
```

## 2️⃣ ResNet50 Feature Extractor
**File:** `models/feature_extractor.py`
### Purpose
Extracts structural and visual features from document images.
### Learns
- Layout structure
- Headers
- Tables
- Margins
- Logos
- Official seals
### Workflow
```
Document Image
      │
      ▼
ResNet50
      │
      ▼
2048-D Feature Vector
```


## 3️⃣ Siamese Network
**File:** `models/siamese.py`
### Purpose
Performs structural comparison between a trusted template and an uploaded document.
### Architecture
```
Template Image
      │
      ▼
ResNet50 Backbone
      │
      ▼
Embedding Head
      │
      ▼
128-D Vector


Uploaded Image
      │
      ▼
ResNet50 Backbone
      │
      ▼
Embedding Head
      │
      ▼
128-D Vector
```
### Embedding Head
```
2048
 ↓
512
 ↓
128
```
### Output
Produces two embeddings used for similarity comparison.

## 4️⃣ Similarity Engine
**File:** `models/Similarity.py`
### Purpose
Measures similarity between document embeddings.
### Metrics Implemented
#### Cosine Similarity
```
1.0 → Perfect Match
0.0 → Completely Different
```
#### Euclidean Distance
```
Low Distance  → Similar Documents
High Distance → Different Documents
```

## 5️⃣ Contrastive Loss (WILL NOT BE USED FOR DEMO PURPOSE BECAUSE WE DONT HAVE ANY DATA)
**File:** `models/contrastive_loss.py`
### Purpose
Provides a training-ready loss function for future Siamese Network fine-tuning.
### Current Status
No labeled forgery dataset is currently available.
The prototype therefore uses:
```
Pretrained ResNet50
+
Distance-Based Similarity Matching
```
### Future Use
```
Genuine Document Pairs
      +
Forged Document Pairs
      ▼
Siamese Training
```
## 6️⃣ Inference Pipeline
**File:** `training/inference.py`
### Purpose
Runs the complete document verification process.
### Workflow
```
Input Document
      │
      ▼
Feature Extraction
      │
      ▼
Siamese Embedding Generation
      │
      ▼
Similarity Computation
      │
      ▼
Verification Result
```

## 7️⃣ MultiModal Risk Engine
**File:** `models/multimodel_risk_engine.py`
### Purpose
Aggregates trust signals from multiple verification layers.
### Inputs
```
Forensic Score
+
Structural Score
+
Behavioral Score
```
### Weight Distribution
```
Forensic Analysis   → 35%
Structural Matching → 45%
Behavior Analysis   → 20%
```

# 🔄 End-to-End Verification Flow

```
Document Upload
      │
      ▼
Error Level Analysis
      │
      ▼
Forensic Score
      │
      ▼
ResNet50 Feature Extraction
      │
      ▼
Siamese Structural Matching
      │
      ▼
Similarity Calculation
      │
      ▼
Structural Score
      │
      ▼
Behavioral Score
      │
      ▼
MultiModal Risk Engine
      │
      ▼
Master Trust Score
      │
      ▼
Final Decision
```

---


## ✅ This Module (My Responsibility)

- Error Level Analysis (ELA)
- ResNet50 Feature Extraction
- Siamese Network
- Similarity Engine
- Contrastive Loss
- Inference Pipeline
- Structural Scoring
- MultiModal Risk Engine

