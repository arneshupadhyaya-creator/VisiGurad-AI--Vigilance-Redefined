"""
VisiGuard AI — Behavioral Scoring Layer
========================================
Captures passive user biometrics during document upload:
  - Keystroke dynamics  : [hold_time, flight_time]  (from typing.py)
  - Mouse dynamics      : [mouse_distance, mouse_velocity, click_count] (from behaviour.py)

Both signals are fed into a single unified BehaviorLSTM that outputs
a 0–100 behavioral score consumed by the MultiModalRiskEngine.

Why unified instead of two separate models:
  - Fewer parameters, one training loop, one inference call
  - Forces the model to learn cross-modal patterns
    (e.g. fast typing + jerky mouse = inconsistent persona)
  - Single score output matches what the risk engine expects

Feature vector per time-step (5 features):
  [hold_time, flight_time, mouse_distance, mouse_velocity, click_count]

Training:
  python behavioral_layer.py --train --epochs 20 --save model.pt

Inference (from pipeline):
  layer  = BehavioralScoringLayer.load("model.pt")   # trained model
  score  = layer.score(keystroke_seq, mouse_seq)      # returns float 0-100

  # or without a saved model (uses random weights — demo only):
  layer  = BehavioralScoringLayer()
  score  = layer.score(keystroke_seq, mouse_seq)
"""

import argparse
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

# Feature layout (must match what the frontend sends)
#   Index 0: hold_time       — duration key is held down (seconds)
#   Index 1: flight_time     — gap between key-up and next key-down (seconds)
#   Index 2: mouse_distance  — Euclidean px distance in this time-step
#   Index 3: mouse_velocity  — px/s
#   Index 4: click_count     — number of clicks in this time-step
FEATURE_DIM  = 5
SEQ_LENGTH   = 30    # time-steps per evaluation window
HIDDEN_DIM   = 128   # larger than before — now handles 5 features instead of 2 or 4
NUM_LAYERS   = 2
DROPOUT      = 0.2
BATCH_SIZE   = 32
LEARNING_RATE = 0.001


# ══════════════════════════════════════════════════════════════════════════════
# DATASET  (synthetic — replace X / y with real captured data in production)
# ══════════════════════════════════════════════════════════════════════════════

class BehaviorDataset(Dataset):
    """
    Synthetic dataset for training/testing the behavioral LSTM.

    In production replace self.X and self.y with real numpy arrays:
      self.X = np.load("keystroke_mouse_features.npy")   # (N, SEQ_LENGTH, FEATURE_DIM)
      self.y = np.load("behavioral_scores.npy")          # (N, 1)  values in [0, 100]

    Score semantics:
      100 = perfectly consistent with stored user persona
        0 = completely anomalous behaviour
    """

    def __init__(self, num_samples: int = 500,
                 seq_length: int = SEQ_LENGTH,
                 feature_dim: int = FEATURE_DIM):

        # Synthetic feature generation
        # Normal users: low hold/flight times, moderate mouse activity
        # Anomalous: high variance across all channels
        rng = np.random.default_rng(42)

        normal_mask  = rng.random(num_samples) > 0.3   # 70% normal
        X = np.zeros((num_samples, seq_length, feature_dim), dtype=np.float32)

        # Normal behaviour — tight distributions
        n_normal = normal_mask.sum()
        X[normal_mask] = rng.normal(
            loc=[0.08, 0.12, 50.0, 120.0, 0.5],
            scale=[0.02, 0.03, 15.0,  30.0, 0.3],
            size=(n_normal, seq_length, feature_dim)
        ).astype(np.float32)

        # Anomalous behaviour — high variance
        n_anom = (~normal_mask).sum()
        X[~normal_mask] = rng.normal(
            loc=[0.25, 0.40, 200.0, 400.0, 3.0],
            scale=[0.15, 0.20, 100.0, 150.0, 2.0],
            size=(n_anom, seq_length, feature_dim)
        ).astype(np.float32)

        # Clip to physically plausible ranges
        X = np.clip(X, 0, None)

        # Target scores: normal → high score (80-100), anomalous → low (0-40)
        y = np.zeros((num_samples, 1), dtype=np.float32)
        y[normal_mask]  = rng.uniform(75, 100, (n_normal, 1))
        y[~normal_mask] = rng.uniform(0,   40, (n_anom,  1))

        self.X = X
        self.y = y

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx):
        return torch.from_numpy(self.X[idx]), torch.from_numpy(self.y[idx])


# ══════════════════════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════════════════════

class BehaviorLSTM(nn.Module):
    """
    Many-to-one LSTM that maps a sequence of biometric time-steps
    to a single behavioral trust score in [0, 100].

    Architecture:
      Input  → LSTM (num_layers, hidden_dim) → last hidden state
             → FC(hidden_dim → hidden_dim//2) → ReLU → Dropout
             → FC(hidden_dim//2 → 1) → Sigmoid × 100
    """

    def __init__(self,
                 input_dim:  int = FEATURE_DIM,
                 hidden_dim: int = HIDDEN_DIM,
                 num_layers: int = NUM_LAYERS,
                 dropout:    float = DROPOUT):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size  = input_dim,
            hidden_size = hidden_dim,
            num_layers  = num_layers,
            batch_first = True,
            dropout     = dropout if num_layers > 1 else 0.0,
        )

        # MLP head
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),      # → (0, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, feature_dim)
        Returns:
            score: (batch, 1)  values in [0, 100]
        """
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim,
                         device=x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim,
                         device=x.device)
        out, _ = self.lstm(x, (h0, c0))
        last   = out[:, -1, :]          # (batch, hidden_dim)
        return self.fc(last) * 100.0    # → (0, 100)


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def train(
    model_save_path: str = "behavioral_model.pt",
    epochs:          int = 20,
    num_samples:     int = 500,
) -> BehaviorLSTM:
    """
    Train the BehaviorLSTM on synthetic data and save weights.
    Replace BehaviorDataset with real data before deploying.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[BehavioralLayer] Training on {device}")

    dataset    = BehaviorDataset(num_samples=num_samples)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model     = BehaviorLSTM().to(device)
    criterion = nn.MSELoss()   # regression on 0-100 scores
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            preds = model(batch_x)
            loss  = criterion(preds, batch_y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * batch_x.size(0)

        epoch_loss /= len(dataset)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch [{epoch+1:>3}/{epochs}]  MSE Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), model_save_path)
    print(f"[BehavioralLayer] Model saved → {model_save_path}")
    return model


# ══════════════════════════════════════════════════════════════════════════════
# INFERENCE WRAPPER  (what the pipeline imports)
# ══════════════════════════════════════════════════════════════════════════════

class BehavioralScoringLayer:
    """
    Pipeline-facing inference wrapper.

    Usage
    -----
    # With a trained model:
    layer = BehavioralScoringLayer.load("behavioral_model.pt")

    # Without a trained model (demo / first-run):
    layer = BehavioralScoringLayer()

    # Score a user session:
    score = layer.score(
        keystroke_seq = np.array([[hold, flight], ...]),  # (T, 2)
        mouse_seq     = np.array([[dist, vel, clicks], ...]),  # (T, 3)
    )
    # Returns float in [0, 100]
    """

    def __init__(self, model: BehaviorLSTM | None = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = (model or BehaviorLSTM()).to(self.device)
        self.model.eval()

    @classmethod
    def load(cls, path: str) -> "BehavioralScoringLayer":
        """Load a previously saved model."""
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Behavioral model not found: {path}\n"
                "Run: python behavioral_layer.py --train --save {path}"
            )
        m = BehaviorLSTM()
        m.load_state_dict(torch.load(path, map_location="cpu"))
        print(f"[BehavioralLayer] Loaded weights from {path}")
        return cls(model=m)

    # ------------------------------------------------------------------
    # Feature assembly
    # ------------------------------------------------------------------

    @staticmethod
    def _assemble(
        keystroke_seq: np.ndarray,   # (T, 2)  [hold_time, flight_time]
        mouse_seq:     np.ndarray,   # (T, 3)  [distance, velocity, clicks]
        seq_length:    int = SEQ_LENGTH,
    ) -> np.ndarray:
        """
        Merge keystroke and mouse arrays into a single (SEQ_LENGTH, 5) array.

        Handles length mismatches by truncating or padding with zeros.
        In a real system both streams would be synchronised by timestamp.
        """
        T = min(len(keystroke_seq), len(mouse_seq), seq_length)

        ks = keystroke_seq[:T]   # (T, 2)
        ms = mouse_seq[:T]       # (T, 3)

        combined = np.concatenate([ks, ms], axis=1).astype(np.float32)  # (T, 5)

        # Pad to SEQ_LENGTH if shorter
        if T < seq_length:
            pad = np.zeros((seq_length - T, FEATURE_DIM), dtype=np.float32)
            combined = np.vstack([combined, pad])

        return combined  # (SEQ_LENGTH, 5)

    # ------------------------------------------------------------------
    # Public scoring API
    # ------------------------------------------------------------------

    def score(
        self,
        keystroke_seq: np.ndarray,
        mouse_seq:     np.ndarray,
    ) -> float:
        """
        Produce a 0-100 behavioral trust score from one user session.

        Args:
            keystroke_seq : np.ndarray (T, 2)  — [[hold, flight], ...]
            mouse_seq     : np.ndarray (T, 3)  — [[dist, vel, clicks], ...]

        Returns:
            float in [0, 100]  — higher = more consistent with normal persona
        """
        features = self._assemble(keystroke_seq, mouse_seq)        # (30, 5)
        tensor   = torch.from_numpy(features).unsqueeze(0)         # (1, 30, 5)
        tensor   = tensor.to(self.device)

        with torch.no_grad():
            raw = self.model(tensor)                                # (1, 1)

        return round(float(raw.item()), 2)

    def score_from_session(self, session: np.ndarray) -> float:
        """
        Alternative entry point when keystroke and mouse are already merged.

        Args:
            session : np.ndarray (T, 5)  — pre-merged feature array
        Returns:
            float in [0, 100]
        """
        T = min(len(session), SEQ_LENGTH)
        arr = session[:T].astype(np.float32)
        if T < SEQ_LENGTH:
            arr = np.vstack([arr, np.zeros((SEQ_LENGTH - T, FEATURE_DIM),
                                           dtype=np.float32)])
        tensor = torch.from_numpy(arr).unsqueeze(0).to(self.device)
        with torch.no_grad():
            raw = self.model(tensor)
        return round(float(raw.item()), 2)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE INTEGRATION HELPER
# ══════════════════════════════════════════════════════════════════════════════

def get_behavioral_score(
    keystroke_seq:    np.ndarray,
    mouse_seq:        np.ndarray,
    model_path:       str | None = None,
) -> float:
    """
    One-line helper used by VisiGuardPipeline:

        from behavioral_layer import get_behavioral_score
        behavioral_score = get_behavioral_score(ks_seq, ms_seq, "model.pt")

    Falls back to random weights if model_path is None or file missing
    (useful for demos where no model has been trained yet).
    """
    try:
        layer = BehavioralScoringLayer.load(model_path) \
                if model_path else BehavioralScoringLayer()
    except FileNotFoundError as e:
        print(f"  [WARN] {e}\n  [WARN] Using untrained model — score is indicative only.")
        layer = BehavioralScoringLayer()

    return layer.score(keystroke_seq, mouse_seq)


# ══════════════════════════════════════════════════════════════════════════════
# CLI  —  python behavioral_layer.py --train [--epochs N] [--save PATH]
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VisiGuard Behavioral Layer")
    parser.add_argument("--train",   action="store_true", help="Train and save model")
    parser.add_argument("--epochs",  type=int,   default=20)
    parser.add_argument("--samples", type=int,   default=500)
    parser.add_argument("--save",    type=str,   default="behavioral_model.pt")
    parser.add_argument("--demo",    action="store_true",
                        help="Run a quick inference demo")
    args = parser.parse_args()

    if args.train:
        train(model_save_path=args.save, epochs=args.epochs,
              num_samples=args.samples)

    if args.demo:
        print("\n[Demo] Running inference on synthetic sessions…")

        # Simulate a normal user (low, consistent keystroke + moderate mouse)
        normal_ks = np.random.normal([0.08, 0.12], [0.01, 0.02],
                                     size=(SEQ_LENGTH, 2)).astype(np.float32)
        normal_ms = np.random.normal([50, 120, 0.5], [10, 25, 0.2],
                                     size=(SEQ_LENGTH, 3)).astype(np.float32)

        # Simulate an anomalous user (erratic, high variance)
        anom_ks = np.random.normal([0.30, 0.50], [0.15, 0.20],
                                   size=(SEQ_LENGTH, 2)).astype(np.float32)
        anom_ms = np.random.normal([300, 600, 5], [100, 200, 3],
                                   size=(SEQ_LENGTH, 3)).astype(np.float32)

        try:
            layer = BehavioralScoringLayer.load(args.save)
        except FileNotFoundError:
            print("  No saved model found — using untrained weights (scores are random).")
            layer = BehavioralScoringLayer()

        s_normal = layer.score(normal_ks, normal_ms)
        s_anom   = layer.score(anom_ks,   anom_ms)

        print(f"  Normal user  behavioral score : {s_normal:.2f} / 100")
        print(f"  Anomalous user behavioral score: {s_anom:.2f} / 100")
