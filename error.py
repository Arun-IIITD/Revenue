import numpy as np
import matplotlib.pyplot as plt

def calculate_day_to_day_ape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    return np.abs((actual - predicted) / actual) * 100

def plot_actual_vs_predicted_with_error(actual, predicted):
    daily_ape = calculate_day_to_day_ape(actual, predicted)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Revenue', color=color)
    ax1.plot(actual, label='Actual Revenue', color='blue', marker='o')
    ax1.plot(predicted, label='Predicted Revenue', color='red', linestyle='--', marker='x')
    ax1.tick_params(axis='y', labelcolor=color)

    # Instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()  
    color = 'tab:green'
    ax2.set_ylabel('Error Rate (%)', color=color)
    ax2.plot(daily_ape, label='Day-to-Day APE', color='green', linestyle='-', marker='o')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 100)
    fig.tight_layout()  # To ensure there's no clipping of the ylabel
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.title('Actual vs Predicted Revenue and Error Rate')
    plt.show()

actual_revenue = [100, 150, 200, 250, 300, 350, 400]  
predicted_revenue = [110, 140, 210, 240, 310, 330, 390]  

plot_actual_vs_predicted_with_error(actual_revenue, predicted_revenue)


