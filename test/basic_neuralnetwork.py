import torch
import torch.nn as nn
import torch.optim as optim

class SimpleNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)  # First layer
        self.fc2 = nn.Linear(hidden_size, output_size)  # Second layer

    def forward(self, x):
        x = torch.relu(self.fc1(x))  # Apply ReLU activation
        x = self.fc2(x)  # Output layer
        return x

# Example usage:
if __name__ == '__main__':
    input_size = 10  # Example input size
    hidden_size = 5  # Example hidden layer size
    output_size = 2  # Example output size

    model = SimpleNeuralNetwork(input_size, hidden_size, output_size)
    print(model)
