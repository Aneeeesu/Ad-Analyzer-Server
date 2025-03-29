import torch
from torchvision.models import efficientnet_b0
from pytorch_benchmark import benchmark
from efficientnet_pytorch import EfficientNet
import yaml

#model = EfficientNet.from_pretrained('efficientnet-b0').to("cuda")

model = efficientnet_b0().to("cuda") # Model device sets benchmarking device
sample = torch.randn(8, 3, 224, 224)  # (B, C, H, W)
results = benchmark(model, sample, num_runs=100)

print(yaml.dump(results))
