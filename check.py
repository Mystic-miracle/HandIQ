import torch


print(torch.cuda.device_count())
print(torch.version.cuda) 
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)