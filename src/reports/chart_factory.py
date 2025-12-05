from matplotlib.figure import Figure


_PALETTE = [
    "#2563EB",  # azul principal
    "#10B981",  # verde
    "#F59E0B",  # ámbar
    "#EF4444",  # rojo
    "#8B5CF6",  # violeta
]


class ChartFactory:

    @staticmethod
    def _style_axes(ax):
        """Estilo base común para todos los gráficos."""
        ax.grid(axis="y", alpha=0.25, linestyle="--")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    @staticmethod
    def bar_chart(labels, values, title, ylabel):
        # Relación de aspecto similar a A4 apaisado para los gráficos de informes
        fig = Figure(figsize=(8.27, 4.8), dpi=110)
        ax = fig.add_subplot(111)

        indices = range(len(labels))
        colors = [_PALETTE[i % len(_PALETTE)] for i in indices]

        bars = ax.bar(indices, values, color=colors)
        ax.set_title(title, fontsize=14, weight="bold")
        ax.set_ylabel(ylabel, fontsize=11)

        ax.set_xticks(list(indices))
        ax.set_xticklabels(labels, rotation=30, ha="right")

        ChartFactory._style_axes(ax)

        # Etiquetas de valor encima de cada barra
        for bar, value in zip(bars, values):
            height = bar.get_height()
            if height is None:
                continue
            txt = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                txt,
                ha="center",
                va="bottom",
                fontsize=9,
            )

        fig.tight_layout()
        return fig

    @staticmethod
    def pie_chart(labels, values, title):
        fig = Figure(figsize=(7.5, 5.5), dpi=110)
        ax = fig.add_subplot(111)

        total = sum(values) if values else 0
        if total <= 0:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", fontsize=14)
            ax.set_title(title, fontsize=14, weight="bold")
            return fig

        colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.45),
            pctdistance=0.8,
        )

        for autotext in autotexts:
            autotext.set_fontsize(9)

        ax.set_title(title, fontsize=14, weight="bold")
        ax.set_aspect("equal")
        return fig

    @staticmethod
    def line_chart(labels, values, title, xlabel, ylabel):
        fig = Figure(figsize=(8.27, 4.8), dpi=110)
        ax = fig.add_subplot(111)

        indices = range(len(labels))
        color = _PALETTE[0]

        ax.plot(indices, values, marker="o", color=color, linewidth=2)
        ax.fill_between(indices, values, [0] * len(values), color=color, alpha=0.1)

        ax.set_title(title, fontsize=14, weight="bold")
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)

        ax.set_xticks(list(indices))
        ax.set_xticklabels(labels, rotation=30, ha="right")

        ChartFactory._style_axes(ax)

        # Etiquetas de valor encima de cada punto
        for x, y in zip(indices, values):
            txt = f"{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ax.text(x, y, txt, ha="center", va="bottom", fontsize=9)

        fig.tight_layout()
        return fig

    @staticmethod
    def empty(title="Sin datos"):
        fig = Figure(figsize=(7.0, 3.0), dpi=110)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=14)
        ax.axis("off")
        return fig
