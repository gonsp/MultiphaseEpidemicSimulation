import networkx as nx
import subprocess
import platform
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D


state_to_color = [('S', 'forestgreen'), ('I_a', 'red'), ('I_s', 'darkred'), ('I_q', 'yellow'), ('D', 'black')]


def draw_network(graph, pos=None, pagerank=False, without_states=False, axes=None):
    show = axes is None
    if axes is None:
        axes = plt.axes()

    if pos is None:
        if all('pos' in graph.nodes[node] for node in graph.nodes()):
            pos = {node : graph.nodes[node]['pos'] for node in graph.nodes()}
        else:
            pos = nx.random_layout(graph)

    default_node_size = 10000 / (100 + len(graph)) + 1
    
    if pagerank:
        weights = nx.pagerank(graph, alpha=0.85)

    if without_states:
        nx.draw_networkx_nodes(graph, pos, nodelist=graph.nodes, node_size=default_node_size, ax=axes)
    else:
        legend_items = []
        for state, color in state_to_color:
            nodes = [node for node, attributes in graph.nodes(data=True) if attributes['state'] == state]
            if pagerank:
                node_size = [weights[node] * (default_node_size *  len(graph)) for node in nodes]
            else:
                node_size = default_node_size

            legend_items.append(Line2D([0], [0], label=state, markerfacecolor=color, markersize=8, marker='o', color=(1, 1, 1, 0)))
            nx.draw_networkx_nodes(graph, pos, nodelist=nodes, node_size=node_size, node_color=color, label=state, ax=axes)
        plt.legend(handles=legend_items)

    nx.draw_networkx_edges(graph, pos, width=0.3, ax=axes)

    if show:
        plt.show()

    return pos


def plot_states_hist(states_hist, T=None, axes=None, simulation_name=''):
    show = axes is None
    if axes is None:
        fig = plt.figure(dpi=120)
        axes = plt.axes()
    axes.set_title('State count')

    n = sum([hist[-1] for hist in states_hist.values()])

    for state, color in state_to_color:
        axes.plot(states_hist[state], label=state, color=color, linewidth=1)
        axes.set_ylim(bottom=0, top=n + 5)
        axes.set_xlim(left=0)
        if T is not None:
            axes.set_xlim(right=T)

    plt.xlabel('Time')
    plt.ylabel('Count')
    plt.legend()

    if show:
        if simulation_name != '':
            fig.savefig(f'plots/{simulation_name}/states_hist.png', dpi=fig.dpi)
        plt.show()


def plot_new_cases(states_hist, T=None, states=['I_a', 'D'], axes=None, simulation_name=''):
    show = axes is None
    if axes is None:
        fig = plt.figure(dpi=120)
        axes = plt.axes()
    axes.set_title('New cases')

    n = sum([hist[-1] for hist in states_hist.values()])

    for state, color in state_to_color:
        if state in states:
            hist = states_hist[state]
            new_cases = [max(0, hist[i] - hist[i-1]) for i in range(len(hist))]
            axes.plot(new_cases, label=state, color=color, linewidth=1)
            # axes.set_ylim(bottom=0, top=n + 5)
            axes.set_xlim(left=0)
            if T is not None:
                axes.set_xlim(right=T)

    plt.xlabel('Time')
    plt.ylabel('New cases')
    plt.legend()

    if show:
        if simulation_name != '':
            fig.savefig(f'plots/{simulation_name}/new_cases.png', dpi=fig.dpi)
        plt.show()


class AnimatedPlot():

    def __init__(self, T, pagerank=False):
        self.fig = plt.figure(figsize=(8, 6), dpi=200)
        self.gs = gridspec.GridSpec(2, 2)
        plt.subplots_adjust(wspace=0.4, hspace=0.4)

        self.frames = []
        self.pagerank = pagerank
        self.T = T
        self.network_layout = None


    def add_frame(self, graph, states_hist):
        states_hist_axes = self.fig.add_subplot(self.gs[0, 0], label=len(self.frames))
        plot_states_hist(states_hist, self.T, axes=states_hist_axes)

        new_cases_axes = self.fig.add_subplot(self.gs[0, 1], label=len(self.frames))
        plot_new_cases(states_hist, self.T, axes=new_cases_axes)

        network_axes = self.fig.add_subplot(self.gs[1, :], label=len(self.frames))
        self.network_layout = draw_network(graph, pos=self.network_layout, axes=network_axes)

        self.frames.append([states_hist_axes, new_cases_axes, network_axes])


    def show(self, simulation_name='', duration=5):
        print('Generating animated plot')
        anim = animation.ArtistAnimation(self.fig, self.frames, interval=100, blit=False, repeat_delay=10000)

        if simulation_name != '':
            file_path = f'plots/{simulation_name}/animation.mp4'
            print('Saving animation in:', file_path)

            anim.save(file_path, fps=self.T/duration)

            # if platform.system() == 'Darwin':       # macOS
            #     subprocess.call(('open', file_path))
            # elif platform.system() == 'Windows':    # Windows
            #     os.startfile(file_path)
            # else:                                   # linux variants
            #     subprocess.call(('xdg-open', file_path))
        else:
            plt.show()


    