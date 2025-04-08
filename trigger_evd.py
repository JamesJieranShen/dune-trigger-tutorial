### A simple Event Display based on TriggerAnaTree outputs
### @author James Shen <jierans@sas.upenn.edu>

import uproot
import awkward as ak
import matplotlib.pyplot as plt
import argparse
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

def _get_view(ch_num):
    wireid = ch_num % 2560
    if wireid < 800:
        return 0 # U
    elif wireid < 1600:
        return 1 # V
    else:
        return 2 #X
get_view = np.vectorize(_get_view)

def draw_tps(tps, ax):
    norm = mcolors.Normalize(vmin=min(tps.adc_peak), vmax=max(tps.adc_peak))
    cmap = cm.viridis
    for tp in tps:
        color = cmap(norm(tp.adc_peak))
        rect = Rectangle((tp.channel-0.5, tp.time_start), width=1, height=tp.time_over_threshold, color=color)
        ax.add_patch(rect)
    ax.set_xlim(min(tps.channel) - 10, max(tps.channel) + 10)
    ax.set_ylim(min(tps.time_start) - 1000, max(tps.time_start + tps.time_over_threshold) + 1000)


def draw_tas(tas, ax):
    for ta in tas:
        rect = Rectangle((ta.channel_start, ta.time_start), 
                         width=ta.channel_end - ta.channel_start, 
                         height=ta.time_end - ta.time_start,
                         facecolor='none', edgecolor='red', linewidth=2,
                         )
        ax.add_patch(rect)
        ax.vlines(ta.channel_peak, ta.time_start, ta.time_end, color='red', linestyle=':')
        ax.hlines(ta.time_peak, ta.channel_start, ta.channel_end, color='red', linestyle=':')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Event file")
    parser.add_argument("-e", "--event", help="Event to draw")
    parser.add_argument("--combine", help="Overlap everything onto one APA", action='store_true')
    args = parser.parse_args()
    
    with uproot.open(args.input) as f:
        tps = f['triggerAna/TriggerPrimitives/tpmakerTPC__TriggerPrimitiveMaker']
        tps = tps.arrays(cut=f'Event=={args.event}')
        tas = f['triggerAna/TriggerActivities/tamakerTPC__TriggerActivityMaker']
        tas = tas.arrays(cut=f'Event=={args.event}')
        if args.combine:
            tps = ak.with_field(tps, tps["channel"] % 2560, where="channel")
            tas = ak.with_field(tas, tas["channel_start"] % 2560, where="channel_start")
            tas = ak.with_field(tas, tas["channel_peak"] % 2560, where="channel_peak")
            tas = ak.with_field(tas, tas["channel_end"] % 2560, where="channel_end")

        plt.figure()
        for view in range(3):
            plt.subplot(3, 1, view+1)
            view_tps = tps[get_view(tps.channel) == view]
            view_tas = tas[get_view(tas.channel_start) == view]
            ax = plt.gca()
            draw_tps(view_tps, ax)
            draw_tas(view_tas, ax)
            ax.set_xlabel("ChannelID")
            ax.set_ylabel("Time [DTS Ticks]")
            if view == 0:
                ax.set_title("U")
            elif view == 1:
                ax.set_title("V")
            else: 
                ax.set_title("X")

        plt.show()
