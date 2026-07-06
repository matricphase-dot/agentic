# federated_learning.py
import torch
import syft as sy
from torch import nn, optim

class FederatedAutomation:
    """
    Federated learning system that trains across multiple users without sharing data
    """
    def __init__(self):
        self.hook = sy.TorchHook(torch)
        
        # Virtual workers (simulated users)
        self.workers = {
            'user1': sy.VirtualWorker(self.hook, id="user1"),
            'user2': sy.VirtualWorker(self.hook, id="user2"),
            'user3': sy.VirtualWorker(self.hook, id="user3")
        }
        
        self.global_model = self.create_model()
        
    def train_federated(self, local_data_dict):
        """Train model using federated learning"""
        
        # Send model to workers
        local_models = {}
        for worker_id, data in local_data_dict.items():
            model = self.global_model.copy().send(self.workers[worker_id])
            local_models[worker_id] = model
            
        # Train locally on each worker
        for worker_id, model in local_models.items():
            # Train on local data (never leaves the worker)
            self.train_local(model, local_data_dict[worker_id])
            
        # Aggregate models (Federated Averaging)
        with torch.no_grad():
            global_dict = self.global_model.state_dict()
            
            for k in global_dict.keys():
                global_dict[k] = torch.stack([
                    local_models[worker].state_dict()[k].copy().get()
                    for worker in local_models.keys()
                ], 0).mean(0)
                
            self.global_model.load_state_dict(global_dict)
        
        return self.global_model