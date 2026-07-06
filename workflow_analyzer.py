# workflow_analyzer.py
import tensorflow as tf
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.cluster import DBSCAN

class IntelligentAnalyzer:
    """
    Uses NLP and ML to analyze user workflows and predict optimizations
    """
    def __init__(self):
        self.model_name = "distilbert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.similarity_threshold = 0.85
        
    def extract_patterns(self, workflow_data):
        """Use BERT embeddings to find recurring patterns"""
        embeddings = self.get_embeddings(workflow_data['description'])
        
        # Cluster similar workflows
        clusters = self.cluster_workflows(embeddings)
        
        # Predict optimization opportunities
        optimizations = self.predict_optimizations(clusters)
        
        return {
            'patterns': clusters,
            'optimizations': optimizations,
            'similar_workflows': self.find_similar(workflow_data)
        }
    
    def get_embeddings(self, text):
        """Get BERT embeddings for text"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()