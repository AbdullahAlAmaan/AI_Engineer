import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

# 1. Load dataset
df = pd.read_csv("student-mat.csv", sep=";")

# 2. Create Pass/Fail target (1 = Pass if G3 >= 10, else 0)
df["Pass"] = (df["G3"] >= 10).astype(int)
print("Target distribution:\n", df["Pass"].value_counts())

# 3. Select features (you can add/remove more)
features = ["studytime", "failures", "absences", "G1", "G2"]
X = df[features]
y = df["Pass"]

# 4. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Linear Regression as Classifier

lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)

# Predict continuous values
y_pred_lin = lin_reg.predict(X_test)

# Convert to class with threshold
y_class_lin = (y_pred_lin >= 0.5).astype(int)

# Evaluate
print("Linear Regression Accuracy:", accuracy_score(y_test, y_class_lin))

# Confusion matrix
cm_lin = confusion_matrix(y_test, y_class_lin)
disp_lin = ConfusionMatrixDisplay(confusion_matrix=cm_lin, display_labels=["Fail", "Pass"])
disp_lin.plot(cmap="Blues")
plt.title("Linear Regression (as Classifier)")
plt.show(block=False)

# Logistic Regression

log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train, y_train)

y_class_log = log_reg.predict(X_test)

# Evaluate
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_class_log))

# Confusion matrix
cm_log = confusion_matrix(y_test, y_class_log)
disp_log = ConfusionMatrixDisplay(confusion_matrix=cm_log, display_labels=["Fail", "Pass"])
disp_log.plot(cmap="Greens")
plt.title("Logistic Regression")
plt.show()
