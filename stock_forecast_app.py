# pip install streamlit fbprophet yfinance plotly
import streamlit as st
from datetime import date
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Enhanced Stock Forecast App')

# Sidebar for user inputs
st.sidebar.title("Settings")
stocks = ('GOOG', 'AAPL', 'MSFT', 'GME')
selected_stock = st.sidebar.selectbox('Select stock for prediction', stocks)

custom_start_date = st.sidebar.date_input('Select start date:', value=pd.to_datetime(START))
n_years = st.sidebar.slider('Years of prediction:', 1, 4)
period = n_years * 365

# Load data with caching
@st.cache_data
def load_data(ticker, start_date):
    try:
        data = yf.download(ticker, start=start_date, end=TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

# Load and display data
st.subheader(f"Stock Data for {selected_stock}")
data_load_state = st.text('Loading data...')
data = load_data(selected_stock, custom_start_date)
if data is not None and not data.empty:
    data_load_state.text('Loading data... done!')
    st.write(data.tail())

    # Plot raw data
    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="Stock Open"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Stock Close"))
        fig.layout.update(title_text='Stock Price Data with Rangeslider', xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    plot_raw_data()

    # Display basic statistics
    st.subheader("Basic Statistics")
    st.write(data[['Open', 'Close', 'Volume']].describe())

    # Prepare data for forecasting
    df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})

    # Forecast using Prophet
    m = Prophet()
    try:
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        # Display forecast data
        st.subheader('Forecast Data')
        st.write(forecast.tail())

        # Plot forecast
        st.subheader(f'Forecast Plot for {n_years} Years')
        fig1 = plot_plotly(m, forecast)
        st.plotly_chart(fig1)

        # Forecast components
        st.subheader("Forecast Components")
        fig2 = m.plot_components(forecast)
        st.pyplot(fig2)

        # Option to download forecast data
        csv = forecast.to_csv(index=False)
        st.download_button(label="Download Forecast Data as CSV", data=csv, file_name=f"{selected_stock}_forecast.csv", mime='text/csv')
    except Exception as e:
        st.error(f"Error in forecasting: {e}")
else:
    data_load_state.text('No data available. Please adjust your settings.')

