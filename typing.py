import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# Set random seed for reproducibility
torch.manual_seed(42)

# ---------------------------------------------------------
# 1. Define the LSTM Model
# ---------------------------------------------------------
class TypingSpeedLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size=1):
        super(TypingSpeedLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM Layer
        # batch_first=True means input shape is (batch_size, seq_len, input_size)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2 if num_layers > 1 else 0.0)
        
        # Fully Connected Layer to map hidden state to the final WPM prediction
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # Initialize hidden and cell states with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        # out shape: (batch_size, seq_len, hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step (seq_len - 1)
        out = self.fc(out[:, -1, :])
        return out

# ---------------------------------------------------------
# 2. Hyperparameters & Dummy Data Generation
# ---------------------------------------------------------
# Configuration
SEQ_LENGTH = 15      # Look at a sequence of 15 consecutive keystrokes
INPUT_SIZE = 2       # Features per keystroke: [Hold Time, Flight Time]
HIDDEN_SIZE = 64     # Number of features in LSTM hidden state
NUM_LAYERS = 2       # Number of stacked LSTM layers
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 20

# Generating dummy data for demonstration
# Imagine 1000 samples of user typing sequences
num_samples = 1000
X_dummy = np.random.rand(num_samples, SEQ_LENGTH, INPUT_SIZE).astype(np.float32)

# Create mock target (WPM). Faster typists have lower hold/flight times.
# We'll generate a realistic WPM range (e.g., 30 to 120 WPM) based inversely on the input values.
Y_dummy = (120 - (X_dummy.mean(axis=(1, 2)) * 80)).reshape(-1, 1).astype(np.float32)

# Convert to PyTorch Tensors and create DataLoader
dataset = TensorDataset(torch.from_numpy(X_dummy), torch.from_numpy(Y_dummy))
train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# ---------------------------------------------------------
# 3. Model Initialization, Loss, and Optimizer
# ---------------------------------------------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = TypingSpeedLSTM(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS).to(device)

criterion = nn.MSELoss() # Mean Squared Error for regression (predicting continuous WPM)
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

print(f"Training on device: {device}\n" + "-"*30)

# ---------------------------------------------------------
# 4. Training Loop
# ---------------------------------------------------------
model.train()
for epoch in range(EPOCHS):
    epoch_loss = 0.0
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        
        # Forward pass
        predictions = model(batch_x)
        loss = criterion(predictions, batch_y)
        
        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item() * batch_x.size(0)
        
    epoch_loss /= len(train_loader.dataset)
    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f"Epoch [{epoch+1}/{EPOCHS}] -> Loss (MSE): {epoch_loss:.4f}")

# ---------------------------------------------------------
# 5. Inference Example
# ---------------------------------------------------------
model.eval()
with torch.no_grad():
    # Simulate a single user's typing stream (15 keystrokes)
    # Let's simulate a very fast typist (low hold time, low flight time)
    fast_user_sample = torch.tensor([[[0.05, 0.08]] * SEQ_LENGTH], dtype=torch.float32).to(device)
    predicted_wpm_fast = model(fast_user_sample).item()
    
    # Simulate a slower typist (higher delay times)
    slow_user_sample = torch.tensor([[[0.25, 0.45]] * SEQ_LENGTH], dtype=torch.float32).to(device)
    predicted_wpm_slow = model(slow_user_sample).item()
    
    print("-"*30)
    print(f"Predicted Speed for Fast Pattern: {predicted_wpm_fast:.2f} WPM")
    print(f"Predicted Speed for Slow Pattern: {predicted_wpm_slow:.2f} WPM")
