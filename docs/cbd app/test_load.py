import cloudpickle

with open('initial.pkl', 'rb') as f:
    model_initial = cloudpickle.load(f)
print("Loaded successfully!")