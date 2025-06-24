# Education in Danger: Interactive Dashboard

An interactive dashboard built with Python, Streamlit, and Plotly to visualize and analyze global attacks on education from 2020 to 2025. This project uses the ["Education in Danger Incident Data 2020 to 2025"](https://www.kaggle.com/datasets/mohamedramadan2040/education-in-danger-incident-data-2020-to2025) dataset from Kaggle.

![Dashboard Screenshot](https://i.imgur.com/your-screenshot-url.png)
*(Recommendation: Run the dashboard and take a screenshot, then upload it to a site like Imgur and paste the link here.)*

---

## ✨ Features

* **Global KPIs:** High-level metrics for total incidents, victims, and affected countries.
* **Interactive World Map:** A geo-location plot of all incidents, color-coded and sized by the number of victims.
* **Dynamic Filtering:** Filter the entire dashboard by country, year range, and perpetrator type.
* **Detailed Visualizations:** Interactive charts showing:
    * Incidents by Country
    * Incidents by Perpetrator
    * Incident Trends Over Time
    * Incident Severity (Average Victims per Attack Type)

## 🛠️ Tech Stack

* **Language:** Python
* **Dashboard Framework:** Streamlit
* **Data Manipulation:** Pandas
* **Data Visualization:** Plotly Express
* **Data Source:** KaggleHub

---

## 🚀 Setup and Installation

Follow these steps to run the dashboard on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/education-danger-dashboard.git](https://github.com/your-username/education-danger-dashboard.git)
cd education-danger-dashboard
```

### 2. Set Up Kaggle API Credentials

This project uses `kagglehub` to download the dataset directly. You need to have your Kaggle API key configured.
- Go to your Kaggle account page and click "Create New Token" in the API section. A `kaggle.json` file will be downloaded.
- Place the `kaggle.json` file in the correct directory: 
    - Linux/macOS: `~/.kaggle/`
    - Windows: `C:\Users\<Your-Username>\.kaggle\`

### 3. Create a Virtual Environment (Recommended)

```bash
# Create the environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install all the required libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

--- 

## ▶️ Running the Application

Launch the dashboard by running the following command in your terminal:

```bash
streamlit run dashboard.py
```

Your web browser will automatically open with the application running. That's it!

---

## ☁️ Deployment

This app can be easily deployed for free using [Streamlit Community Cloud](https://share.streamlit.io/).

1. Push your project (including `dashboard.py` and `requirements.txt`) to your GitHub repository.
2. Log in to Streamlit Community Cloud with your GitHub account.
3. Click "New app", select your repository, and deploy.
4. **Important**: Use the "Secrets" management in the advanced settings to store your Kaggle credentials securely instead of exposing them.
