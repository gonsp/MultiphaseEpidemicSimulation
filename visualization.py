import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D


state_to_color = [('S', 'forestgreen'), ('I_a', 'red'), ('I_s', 'darkred'), ('I_q', 'yellow'), ('D', 'black')]


def save_plot(fig, name):
    if not os.path.exists('plots/'):
        os.makedirs('plots/')
    fig.savefig(f'plots/{name}.png', dpi=fig.dpi)


def draw_network(graph, pos=None, pagerank=False, axes=None):
    show = axes is None
    if axes is None:
        axes = plt.axes()

    if pos is None:
        pos = nx.kamada_kawai_layout(graph)

    default_node_size = 20

    if pagerank:
        weights = nx.pagerank(graph, alpha=0.85)

    legend_items = []
    for state, color in state_to_color:
        nodes = [node for node, attributes in graph.nodes(data=True) if attributes['state'] == state]
        if pagerank:
            node_size = [weights[node] * (default_node_size *  len(graph)) for node in nodes]
        else:
            node_size = default_node_size

        legend_items.append(Line2D([0], [0], marker='o', color='w', label=state, markerfacecolor=color, markersize=8))
        nx.draw_networkx_nodes(graph, pos, nodelist=nodes, node_size=node_size, node_color=color, label=state, ax=axes)

    nx.draw_networkx_edges(graph, pos, width=0.3, ax=axes)
    plt.legend(handles=legend_items)

    if show:
        plt.show()


def plot_states_hist(states_hist, T=None, axes=None, name='plot'):
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
        save_plot(fig, 'states_hist_' + name)
        plt.show()


def plot_new_cases(states_hist, T=None, states=['I_a', 'D'], axes=None, name='plot'):
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
        save_plot(fig, 'new_cases_' + name)
        plt.show()


class AnimatedPlot():

    def __init__(self, T, pagerank=False):
        self.fig = plt.figure(figsize=(8, 6), dpi=120)
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
        if self.network_layout is None:
            self.network_layout = nx.kamada_kawai_layout(graph)
        draw_network(graph, pos=self.network_layout, axes=network_axes)

        self.frames.append([states_hist_axes, new_cases_axes, network_axes])


    def show(self):
        anim = animation.ArtistAnimation(self.fig, self.frames, interval=100, blit=False, repeat_delay=10000)
        plt.show()



    