import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest

def load_data():
    try:
        data = pd.read_csv("general_indian_expense_data.csv")
        data["Date"] = pd.to_datetime(data["Date"])
        return data
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

data = load_data()

st.sidebar.title("💰 AI Finance Manager")
name = st.sidebar.text_input("Enter your Name:")
salary = st.sidebar.number_input("Enter your Monthly Salary (₹):", min_value=1000, step=1000)
if name and salary > 0:
    st.sidebar.write(f"👋 Hello {name}! Let's analyze your finances.")

if data is not None:
    st.title("📊 Expense Analysis")
    category_expense = data.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    st.bar_chart(category_expense)
    st.write("### Total Spend Per Category:")
    st.write(category_expense)
    
    st.write("💡 **Insights:** You are spending the most on", category_expense.idxmax(), ". Consider optimizing this category.")
    
    st.title("📈 Future Expense Prediction")
    expense_series = data.groupby("Date")["Amount"].sum()
    model = ARIMA(expense_series, order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)
    forecast_dates = pd.date_range(start=expense_series.index[-1], periods=30, freq='D')
    
    forecast_df = pd.DataFrame({"Predicted Expense": np.maximum(forecast, 0)}, index=forecast_dates)
    forecast_df.index.name = "Date"
    st.dataframe(forecast_df.reset_index())  
    st.line_chart(forecast_df) 
    st.write("### Predicted Expenses for Next 30 Days:")
    st.dataframe(forecast_df)
    
    st.title("⚠️ Fraud & Wasteful Expense Detection")
    wasteful_categories = ["Shopping", "Entertainment", "Luxury", "Parties"]
    wasteful_expenses = data[data["Category"].isin(wasteful_categories)]
    fraud_detector = IsolationForest(contamination=0.05, random_state=42)
    data["Fraud_Score"] = fraud_detector.fit_predict(data[["Amount"]])
    fraud_cases = data[data["Fraud_Score"] == -1]
    
    if not wasteful_expenses.empty:
        st.warning("⚠️ Wasteful Expenses Detected:")
        st.dataframe(wasteful_expenses)
        recovered_amount = wasteful_expenses["Amount"].sum()
        new_savings = salary - (data["Amount"].sum() - recovered_amount)
    else:
        new_savings = salary - data["Amount"].sum()
    
    st.write(f"💰 **Savings Before Eliminating Wasteful Expenses:** ₹{salary - data['Amount'].sum():.2f}")
    st.write(f"💰 **Savings After Eliminating Wasteful Expenses:** ₹{new_savinags:.2f}")
    
    st.title("📈 Suggested Investment Options")
    if new_savings > 5000:
        st.write("- ✅ Mutual Funds")
    if new_savings > 10000:
        st.write("- ✅ Stocks")
        stock_return = new_savings * (1.1 ** 5)
        st.write(f"📈 If you invest ₹{new_savings:.2f} today, it could grow to ₹{stock_return:.2f} in 5 years.")
    if new_savings > 25000:
        st.write("- ✅ Real Estate")
    if new_savings <= 0:
        st.error("🚨 You are overspending! Try reducing unnecessary expenses.")
    
    st.write("🔍 AI-powered insights to make your financial planning smarter!")
