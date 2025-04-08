import matplotlib
matplotlib.use('Agg')
import numpy as np
from flask import Flask, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from flask_cors import CORS
import io
import base64

app = Flask(__name__)
CORS(app)

# Format Y-axis to show numbers in lakhs
def lakhs_formatter(x, pos):
    return f'{int(x / 100000)}L'

@app.route('/covid-data', methods=['POST'])
def covid_data():
    try:
        data = request.get_json()
        countries = data.get('countries', [])

        df = pd.read_csv("C:/Users/ADMIN/Downloads/country_wise_latest.csv")

        df["Total Recovered"] = df["Recovered"] + df["New recovered"]
        df["Total Deaths"] = df["Deaths"] + df["New deaths"]
        df["Recovery Rate"] = df["Total Recovered"] / df["Confirmed"] * 100
        df["Death Rate"] = df["Total Deaths"] / df["Confirmed"] * 100

        filtered_df = df[df["Country/Region"].isin(countries)]

        x = np.arange(len(filtered_df))
        width = 0.10

        # Chart 1: Confirmed, Recovered, Deaths
        fig1, ax1 = plt.subplots(figsize=(12, 7))
        bars1 = ax1.bar(x - width, filtered_df["Confirmed"], width=width, label="Confirmed", color='#007acc', edgecolor='black')
        bars2 = ax1.bar(x, filtered_df["Total Recovered"], width=width, label="Recovered", color='green', edgecolor='black')
        bars3 = ax1.bar(x + width, filtered_df["Total Deaths"], width=width, label="Deaths", color='red', edgecolor='black')

        ax1.set_ylabel("Cases (in Lakhs)", fontsize=20)
        ax1.set_title("COVID-19 Statistics", fontsize=20, weight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(filtered_df["Country/Region"], fontsize=22, ha='right')
        ax1.yaxis.set_major_formatter(FuncFormatter(lakhs_formatter))
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        ax1.legend(fontsize=20)
        plt.tight_layout()

        img1 = io.BytesIO()
        fig1.savefig(img1, format='png')
        img1.seek(0)
        chart1_base64 = base64.b64encode(img1.read()).decode('utf-8')
        img1.close()
        plt.close(fig1)

        # Chart 2: Recovery Rate vs Death Rate
        fig2, ax2 = plt.subplots(figsize=(12, 7))
        ax2.bar(x - width/2, filtered_df["Recovery Rate"], width=width, label="Recovery Rate (%)", color='limegreen', edgecolor='black')
        ax2.bar(x + width/2, filtered_df["Death Rate"], width=width, label="Death Rate (%)", color='crimson', edgecolor='black')

        ax2.set_ylabel("Rate (%)", fontsize=22)
        ax2.set_title("COVID-19 Recovery and Death Rates", fontsize=22, weight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(filtered_df["Country/Region"],fontsize=20, ha='right')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        ax2.legend(fontsize=20)
        plt.tight_layout()

        img2 = io.BytesIO()
        fig2.savefig(img2, format='png')
        img2.seek(0)
        chart2_base64 = base64.b64encode(img2.read()).decode('utf-8')
        img2.close()
        plt.close(fig2)

        response_data = filtered_df[[
            "Country/Region", "Confirmed", "Total Recovered", "Total Deaths",
            "Recovery Rate", "Death Rate"
        ]].to_dict(orient='records')

        return jsonify({
            "data": response_data,
            "chart1": chart1_base64,
            "chart2": chart2_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
