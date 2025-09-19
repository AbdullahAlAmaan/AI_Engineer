import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Load dataset
df=pd.read_csv('housing_prices.csv')
X = df[['size']]
y = df['price']

# Split dataset and train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)
print("Predicted Prices:", y_pred)
print("Actual Prices:", y_test.values)


#Evaluation
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print("RMSE:", rmse)

# Test a new house size
new_size = pd.DataFrame([[1500]], columns=['size'])  
predicted_price = model.predict(new_size)
print(f"Predicted price for house size {new_size.iloc[0, 0]} sqft: {predicted_price[0]}")

# Visualization
plt.scatter(X_test, y_test, color="blue", label="Actual Prices")
plt.scatter(X_test, y_pred, color="red", label="Predicted Prices")
plt.xlabel("House Size (sqft)")
plt.ylabel("Price")
plt.legend()    
plt.show()



