import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from statsmodels.tsa.arima.model import ARIMA

def greet_user():
    print("\n🤖 Welcome to AI Finance Manager!")
    name = input("Enter your name: ")
    salary = float(input("Enter your monthly salary (₹): "))
    print(f"Hello {name}! Let's analyze your finances and help you save better.\n")
    return name, salary

def load_data(file_name):
    try:
        data = pd.read_csv(file_name)
        data["Date"] = pd.to_datetime(data["Date"])
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def analyze_expenses(data):
    print("\n📊 Analyzing Your Expenses...")
    category_expense = data.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    print("\nTotal Spend Per Category:")
    for category, amount in category_expense.items():
        print(f"{category}: ₹{amount:.2f}")
    
    plt.figure(figsize=(10,5))
    sns.barplot(x=category_expense.index, y=category_expense.values, hue=category_expense.index, dodge=False, legend=False, palette="coolwarm")
    plt.xticks(rotation=45)
    plt.title("Total Spend Per Category")
    plt.show(block=False)

def predict_future_expenses(data):
    print("\n📈 Predicting Future Expenses...")
    data = data.sort_values(by="Date")
    expense_series = data.groupby("Date")["Amount"].sum().asfreq('D')
    
    model = ARIMA(expense_series, order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)
    forecast = np.maximum(forecast, 0)  # Ensure no negative predictions
    
    print("Predicted Expenses for Next 30 Days:")
    for date, value in zip(pd.date_range(start=expense_series.index[-1], periods=30, freq='D'), forecast):
        print(f"{date.strftime('%Y-%m-%d')}: ₹{value:.2f}")
    
    plt.figure(figsize=(10,5))
    plt.plot(expense_series, label="Actual Spending")
    plt.plot(pd.date_range(start=expense_series.index[-1], periods=30, freq='D'), forecast, label="Predicted Spending", linestyle='dashed', color='red')
    plt.legend()
    plt.title("Expense Prediction for Next 30 Days")
    plt.show(block=False)

def detect_wasteful_expenses(data, salary):
    print("\n⚠️ Detecting Wasteful Expenses & Fraudulent Transactions...")
    wasteful_categories = ["Shopping", "Entertainment", "Luxury", "Parties"]
    wasteful_expenses = data[data["Category"].isin(wasteful_categories)]
    
    if wasteful_expenses.empty:
        print("No Wasteful Expenses Detected ✅")
        new_savings = salary - data["Amount"].sum()
    else:
        print("Potential Wasteful Transactions:")
        print(wasteful_expenses)
        recovered_amount = wasteful_expenses["Amount"].sum()
        new_savings = salary - (data["Amount"].sum() - recovered_amount)
    
    print(f"\n💰 Savings Before Eliminating Wasteful Expenses: ₹{salary - data['Amount'].sum():.2f}")
    print(f"💰 Savings After Eliminating Wasteful Expenses: ₹{new_savings:.2f}")
    return new_savings

def suggest_investment(savings):
    print("\n📈 Suggested Investment Options:")
    if savings > 5000:
        print("- ✅ Mutual Funds")
    if savings > 10000:
        print("- ✅ Stocks")
        stock_return = savings * (1.1 ** 5)  # 10% compound interest per year for 5 years
        print(f"📈 If you invest ₹{savings:.2f} in stocks today, it could grow to ₹{stock_return:.2f} in 5 years.")
    if savings > 25000:
        print("- ✅ Real Estate")
    print("Invest wisely to grow your wealth! 💸")

if __name__ == "__main__":
    name, salary = greet_user()
    data = load_data("general_indian_expense_data.csv")
    if data is not None:
        analyze_expenses(data)
        predict_future_expenses(data)
        new_savings = detect_wasteful_expenses(data, salary)
        suggest_investment(new_savings)
        print("\n🚀 AI Finance Manager has successfully analyzed your finances!")
        show_dashboard = input("\nDo you want to see the dashboard? (yes/no): ").strip().lower()
        if show_dashboard == "yes":
            os.system("python -m streamlit run finance_dashboard.py")
