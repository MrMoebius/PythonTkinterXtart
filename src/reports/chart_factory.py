from matplotlib.figure import Figure

class ChartFactory:

    @staticmethod
    def bar_chart(labels, values, title, ylabel):
        fig = Figure(figsize=(9,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(labels, values)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=40)
        fig.tight_layout()
        return fig

    @staticmethod
    def pie_chart(labels, values, title):
        fig = Figure(figsize=(8,6), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title(title)
        return fig

    @staticmethod
    def line_chart(labels, values, title, xlabel, ylabel):
        fig = Figure(figsize=(10,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(labels, values, marker="o")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=40)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return fig

    @staticmethod
    def empty(title="Sin datos"):
        fig = Figure(figsize=(7,3), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=14)
        return fig
