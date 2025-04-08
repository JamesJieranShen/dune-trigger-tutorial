import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import sys

if len(sys.argv) < 2:
    print("Error: Please provide the filename as a command line argument.")
    sys.exit(1)


filename = sys.argv[1]
try:
    waveforms = np.loadtxt(filename, delimiter=None, max_rows=30000)
except Exception as e:
    print(f"Error loading file {filename}: {e}")
    sys.exit(1)

# Extract the ADC values (first 3 columns are event, channel, and col signal flag)
adc_values = waveforms[:, 3:]

# fudge the pedestal subtraction 
adc_values = adc_values - adc_values.mean(axis=1, keepdims=True)


fig, ax = plt.subplots(figsize=(10, 6))
cax = ax.imshow(adc_values, aspect='auto', origin='lower', cmap='seismic', vmin=-50, vmax=50)


ax.set_xlabel('Time [ticks]')
ax.set_ylabel('Channel Index')
fig.colorbar(cax, ax=ax, label='ADC Value from baseline')

# -- zooming functionality with window selection --
def onselect(eclick, erelease):
    # Get the coordinates of the selected region (in terms of x and y axis)
    x_min, x_max = int(eclick.xdata), int(erelease.xdata)
    y_min, y_max = int(eclick.ydata), int(erelease.ydata)
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    fig.canvas.draw()
rect_selector = RectangleSelector(ax, onselect, useblit=True,
                                  props={'facecolor': 'yellow', 'edgecolor': 'red', 'alpha': 0.5, 'fill': True})

# Fingers crossed the interactive zoom feature works
plt.show()
