import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

# Custom CSS for improved interface styling
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6 }
    .sidebar .sidebar-content { background: #ffffff }
    .Widget>label { color: #31333F; font-weight: bold; }
    .stButton>button { color: #ffffff; background-color: #4CAF50; border-radius: 5px; }
    .stTextInput>input { border-radius: 5px; }
    .stDateInput>input { border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Initialize database within main function
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses
        (date TEXT, amount REAL, category TEXT, description TEXT)
    ''')
    conn.commit()
    return conn, c

# Database functions
def add_expense(conn, c, date, amount, category, description):
    """Add a new expense to the database"""
    c.execute('INSERT INTO expenses VALUES (?, ?, ?, ?)',
              (date, amount, category, description))
    conn.commit()

def get_expenses(conn):
    """Retrieve all expenses from the database"""
    df = pd.read_sql('SELECT * FROM expenses', conn)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Authentication System
def authenticate(username, password):
    if username == "admin" and password == "password":
        return True
    else:
        return False

# Main app functionality
def main():
    # Authentication
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')

    if not authenticate(username, password):
        st.sidebar.warning("Incorrect Username/Password")
        return

    conn, c = init_db()

    st.title('💰 Expense Tracker')

    # Sidebar for navigation
    st.sidebar.title('Navigation')
    menu = ['Dashboard', 'Add Expense', 'View Expenses', 'Data Visualization', 'Code Examples']
    choice = st.sidebar.radio("Go to", menu)

    # Currency Selector
    currency = st.sidebar.selectbox("Select Currency", ["USD", "EUR", "GBP", "INR"])

    if choice == 'Dashboard':
        st.header('Expense Tracker Dashboard')
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Quick Add Expense')
            date = st.date_input('Date')
            amount = st.number_input(f'Amount ({currency})', min_value=0.01, step=0.01)
            category = st.selectbox('Category', ['Food', 'Transportation', 'Housing', 'Utilities', 'Entertainment', 'Other'])
            description = st.text_input('Description')
            
            if st.button('Add Expense'):
                add_expense(conn, c, date.strftime('%Y-%m-%d'), amount, category, description)
                st.success('Expense Added Successfully')
        
        with col2:
            st.subheader('Recent Expenses')
            df = get_expenses(conn)
            st.dataframe(df.tail())

    elif choice == 'Add Expense':
        st.header('Add New Expense')
        date = st.date_input('Date')
        amount = st.number_input(f'Amount ({currency})', min_value=0.01, step=0.01)
        category = st.selectbox('Category', ['Food', 'Transportation', 'Housing', 'Utilities', 'Entertainment', 'Other'])
        description = st.text_input('Description')

        if st.button('Add Expense'):
            add_expense(conn, c, date.strftime('%Y-%m-%d'), amount, category, description)
            st.success('Expense Added Successfully')

    elif choice == 'View Expenses':
        st.header('Expense List')
        df = get_expenses(conn)
        st.dataframe(df)

        # Add export functionality
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Expenses as CSV",
                data=csv,
                file_name="expenses.csv",
                mime="text/csv",
            )

    elif choice == 'Data Visualization':
        st.header('Expense Analysis')
        df = get_expenses(conn)

        if df.empty:
            st.warning("No expenses recorded yet. Add some expenses to see visualizations.")
        else:
            # Total Spending
            total_spending = df['amount'].sum()
            st.metric('Total Spending', f'{currency} {total_spending:.2f}')

            col1, col2 = st.columns(2)

            with col1:
                # Spending by Category
                st.subheader('Spending by Category')
                category_spending = df.groupby('category')['amount'].sum().reset_index()
                fig_pie = px.pie(category_spending, values='amount', names='category', title='')
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Top 5 Expenses
                st.subheader('Top 5 Expenses')
                top_expenses = df.nlargest(5, 'amount')
                fig_bar = px.bar(top_expenses, x='description', y='amount', title='')
                st.plotly_chart(fig_bar, use_container_width=True)

            # Daily Spending Trend
            st.subheader('Daily Spending Trend')
            daily_spending = df.groupby('date')['amount'].sum().reset_index()
            fig_line = px.line(daily_spending, x='date', y='amount', title='')
            st.plotly_chart(fig_line, use_container_width=True)

            # Monthly summary
            st.subheader('Monthly Summary')
            df['month'] = df['date'].dt.to_period('M')
            monthly_summary = df.groupby('month')['amount'].agg(['sum', 'mean', 'count']).reset_index()
            monthly_summary.columns = ['Month', 'Total Spent', 'Average Expense', 'Number of Expenses']
            monthly_summary['Month'] = monthly_summary['Month'].astype(str)
            st.dataframe(monthly_summary, use_container_width=True)

    elif choice == 'Code Examples':
        st.header('Code Examples in Different Languages')

        languages = ['Python', 'JavaScript', 'SQL']
        selected_language = st.selectbox('Select Language', languages)

        if selected_language == 'Python':
            st.code('''
def add_expense(date, amount, category, description):
    # Logic to add expense to database
    pass
            ''', language='python')

        elif selected_language == 'JavaScript':
            st.code('''
function addExpense(date, amount, category, description) {
    // Logic to add expense to database
}
            ''', language='javascript')

        elif selected_language == 'SQL':
            st.code('''
INSERT INTO expenses (date, amount, category, description)
VALUES ('2024-10-25', 50.00, 'Food', 'Lunch');
            ''', language='sql')

    # Close connection after use
    conn.close()

if __name__ == '__main__':
    main()
