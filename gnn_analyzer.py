# gnn_analyzer.py
import torch
import torch_geometric
from torch_geometric.nn import GCNConv, GATConv
from torch_geometric.data import Data

class WorkflowGNN(nn.Module):
    """
    Graph Neural Network for analyzing and optimizing workflow graphs
    """
    def __init__(self, node_features=32, hidden_channels=64, num_classes=10):
        super().__init__()
        self.conv1 = GCNConv(node_features, hidden_channels)
        self.conv2 = GATConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        
        self.optimization_head = nn.Linear(hidden_channels, num_classes)
        self.bottleneck_detector = nn.Sequential(
            nn.Linear(hidden_channels, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, workflow_graph):
        # Extract node features (actions, dependencies, durations)
        x, edge_index = workflow_graph.x, workflow_graph.edge_index
        
        # Apply GNN layers
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index).relu()
        
        # Predict optimizations
        optimizations = self.optimization_head(x)
        
        # Detect bottlenecks
        bottlenecks = self.bottleneck_detector(x)
        
        return {
            'optimizations': optimizations,
            'bottlenecks': bottlenecks,
            'graph_embedding': x.mean(dim=0)  # Overall workflow embedding
        }