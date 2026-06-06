import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv(".csv")

# углы в радианы для полярного графика
angles_rad = np.radians(df['Angle_deg'])
distances = df['Distance_mm']

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.scatter(angles_rad, distances, s=1, c=df['Intensity'], cmap='hot', alpha=0.6)
ax.set_theta_zero_location('N')    # 0° — вверх 
ax.set_theta_direction(-1)         # по часовой стрелке
ax.set_rmax(12000)                 # 12 м
ax.set_title("LiDAR Scan")
plt.show()

# в декартовых координатах (x, y)
x = distances * np.cos(angles_rad)
y = distances * np.sin(angles_rad)
plt.figure(figsize=(10,10))
plt.scatter(x, y, s=1, c=df['Intensity'], cmap='viridis', alpha=0.8)
plt.axis('equal')
plt.title("Cartesian view")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.show()
