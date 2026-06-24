import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

np.random.seed(42)
n_samples = 100
time = np.random.randint(10, 120, n_samples)
steps = np.random.randint(1000, 15000, n_samples)
calories = (5 * time) + (0.04 * steps) + np.random.normal(0, 10, n_samples)

df = pd.DataFrame({'time': time, 'steps': steps, 'calories': calories})

X = df[['time', 'steps']]
y = df['calories']

model = LinearRegression()
model.fit(X, y)

print(f"Coefficient (Beta 1, 2): {model.coef_}")
print(f"Intercept (Beta 0): {model.intercept_}")
print(f"R-Squared: {model.score(X, y)}")

with open('model_calo.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Đã lưu model thành công file 'model_calo.pkl'")