import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

# ---------------------------------------------------------
# 1. Dataset Configuration & Preprocessing Pipeline
# ---------------------------------------------------------
class BehaviorSequenceDataset(Dataset):
    """
    Custom Dataset for user behavior sequences.
    Expected feature vector per time-step:
    [typing_speed (cps), mouse_distance, mouse_velocity, click_count]
    """
    def __init__(self, num_samples=100, seq_length=30, feature_dim=4):
        # Generating synthetic data for demonstration purposes
        # In production, replace this with your preprocessed numpy arrays
        self.X = np.random.randn(num_samples, seq_length, feature_dim).astype(np.float32)
        
        # Target scores between 0 (highly irregular/abnormal) and 1 (normal user baseline)
        self.y = np.random.uniform(0.0, 100.0, (num_samples, 1)).astype(np.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx]), torch.tensor(self.y[idx])


# ---------------------------------------------------------
# 2. LSTM Architecture for Behavioral Scoring
# ---------------------------------------------------------
class BehaviorLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim=1, dropout=0.2):
        super(BehaviorLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM Layer to capture temporal dependencies in user dynamics
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        
        # Fully connected head to map hidden states to the behavior score
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, output_dim),
            nn.Sigmoid()  # Restricts output score between 0.0 and 1.0
        )

    def forward(self, x):
        # Initialize hidden state and cell state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        
        # Forward propagate through LSTM
        # out shape: (batch_size, seq_length, hidden_dim)
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step (many-to-one architecture)
        last_time_step = out[:, -1, :]
        
        # Compute behavioral score
        score = self.fc(last_time_step) * 100.0
        return score


# ---------------------------------------------------------
# 3. Training and Inference Setup
# ---------------------------------------------------------
if __name__ == "__main__":
    # Hyperparameters
    SEQ_LENGTH = 30     # Number of seconds/time-steps monitored per evaluation window
    FEATURE_DIM = 4    # [typing_speed, mouse_distance, mouse_velocity, click_count]
    HIDDEN_DIM = 64
    NUM_LAYERS = 2
    BATCH_SIZE = 16
    EPOCHS = 10
    LEARNING_RATE = 0.001

    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #print(f"Using device: {device}")

    # Data Initialization
    dataset = BehaviorSequenceDataset(num_samples=200, seq_length=SEQ_LENGTH, feature_dim=FEATURE_DIM)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Model, Loss, and Optimizer
    model = BehaviorLSTM(input_dim=FEATURE_DIM, hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS).to(device)
    criterion = nn.MSELoss()  # Binary Cross Entropy since outputs are restricted to [0,1]
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Simple Training Loop
    model.train()
    #print("--- Starting Training ---")
    for epoch in range(EPOCHS):
        epoch_loss = 0.0
        for batch_x, batch_y in dataloader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            # Forward pass
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            
            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * batch_x.size(0)
            
        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {epoch_loss / len(dataloader.dataset):.4f}")

    # --- Inference Module / Multimodal Integration ---
    model.eval()
    #print("\n--- Running Inference for Multimodal Pipeline ---")
    
    # Simulating a single active user session window
    # Shape: (1 sample, 30 time-steps, 4 features)
    mock_user_session = np.random.randn(1, SEQ_LENGTH, FEATURE_DIM).astype(np.float32)
    session_tensor = torch.tensor(mock_user_session).to(device)
    
    with torch.no_grad():
        behavior_score = model(session_tensor).item()
        
    print(f"Generated User Behavior Score: {behavior_score:.4f}")
    # This `behavior_score` can now be passed alongside video, audio, or text representations 
    # into your late-fusion multimodal network.
