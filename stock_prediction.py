import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# 1. Load and preprocess data
data = pd.read_csv("TSLA.csv")
data = data[['Close']]  # use only closing price

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# 2. Create sequences
def create_sequences(data, seq_len5gth):
    x, y = [], []
    for i in range(len(data) - seq_length):
        x.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(x), np.array(y)

seq_length = 60
x, y = create_sequences(scaled_data, seq_length)

# Convert to tensors
x = torch.tensor(x, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32).view(-1, 1)  # shape (n_samples, 1)

# 3. Train/Test split (sequential)
train_size = int(len(x) * 0.8)
x_train, x_test = x[:train_size], x[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 4. GRU model
class StockPricePredictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(StockPricePredictor, self).__init__()
        self.lstm = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # last hidden state
        return out

input_size = 1
hidden_size = 128
num_layers = 3
model = StockPricePredictor(input_size, hidden_size, num_layers)

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 5. Training loop
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    outputs = model(x_train)
    loss = criterion(outputs, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.6f}")

# 6. Evaluation
model.eval()
with torch.no_grad():
    predictions = model(x_test)
    predictions = scaler.inverse_transform(predictions.numpy())
    actual = scaler.inverse_transform(y_test.numpy())


# Function to predict future stock prices based on user input
def predict_future(data, model, scaler, seq_length, num_predictions):
    last_sequence = data[-seq_length:]
    predictions = []

    model.eval()
    with torch.no_grad():
        for _ in range(num_predictions):
            input_seq = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0)
            next_value = model(input_seq)
            predictions.append(next_value.item())
            next_value_scaled = next_value.numpy()
            last_sequence = np.append(last_sequence[1:], next_value_scaled, axis=0)
    
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return predictions

# Get user input for future predictions
num_predictions = int(input("Enter the number of future days to predict: "))
future_predictions = predict_future(scaled_data, model, scaler, seq_length, num_predictions)

# Extend the x-axis for future predictions
future_days = np.arange(len(actual), len(actual) + num_predictions)

# Plot the actual, predicted, and future predictions
plt.figure(figsize=(12, 6))
plt.plot(actual, label="Actual Price", color="blue")
plt.plot(predictions, label="Predicted Price", color="orange")
plt.scatter(future_days, future_predictions, label="Future Predictions", color="red", s=10)
plt.title("Tesla Stock Price Prediction")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show()
