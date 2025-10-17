import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import mesa


class PointAgent:
    """Agente ligero que representa un punto etiquetado en el plano.
    No heredamos de mesa.Agent para evitar errores de compatibilidad con distintas versiones.
    """

    def __init__(self, unique_id, pos, label):
        self.unique_id = unique_id
        self.pos = np.array(pos, dtype=float)
        self.label = int(label)  # -1 o 1


class PerceptronModel(mesa.Model):
    """Modelo que contiene el perceptrón y los puntos (usa Mesa sólo para la estructura del modelo)."""

    def __init__(self, n_train=100, n_test=200, learning_rate=0.1):
        super().__init__()
        self.n_train = int(n_train)
        self.n_test = int(n_test)
        self.learning_rate = float(learning_rate)

        # NOTA: Mesa 3.0+ reserva `self.agents`. No usar ese nombre para almacenamiento propio.
        self.train_points = []  # lista de PointAgent de entrenamiento
        self.test_points = []   # lista de PointAgent de prueba

        # línea verdadera (ax + by + c = 0) para etiquetar los datos
        a, b = np.random.uniform(-1, 1, 2)
        c = np.random.uniform(-0.5, 0.5)
        if abs(a) < 1e-3 and abs(b) < 1e-3:
            a = 1.0
        self.true_line = (a, b, c)

        # inicializar pesos y bias aleatorios (2 entradas)
        self.weights = np.random.uniform(-1, 1, 2)
        self.bias = np.random.uniform(-0.5, 0.5)

        self.epoch = 0
        self.generate_data()

    def reset_model(self):
        """Regenerar línea, datos y re-inicializar pesos."""
        a, b = np.random.uniform(-1, 1, 2)
        c = np.random.uniform(-0.5, 0.5)
        if abs(a) < 1e-3 and abs(b) < 1e-3:
            a = 1.0
        self.true_line = (a, b, c)
        self.weights = np.random.uniform(-1, 1, 2)
        self.bias = np.random.uniform(-0.5, 0.5)
        self.epoch = 0
        self.generate_data()

    def generate_data(self):
        """Genera puntos de entrenamiento y prueba, etiquetados según la línea verdadera."""
        self.train_points = []
        self.test_points = []

        a, b, c = self.true_line

        def label(pt):
            val = a * pt[0] + b * pt[1] + c
            return 1 if val >= 0 else -1

        for i in range(self.n_train):
            x, y = np.random.uniform(-1, 1, 2)
            lab = label((x, y))
            ag = PointAgent(i, (x, y), lab)
            self.train_points.append(ag)

        for i in range(self.n_train, self.n_train + self.n_test):
            x, y = np.random.uniform(-1, 1, 2)
            lab = label((x, y))
            ag = PointAgent(i, (x, y), lab)
            self.test_points.append(ag)

    def predict(self, x):
        """Computa la predicción del perceptrón (1 o -1)."""
        x = np.array(x, dtype=float)
        val = np.dot(self.weights, x) + self.bias
        return 1 if val >= 0 else -1

    def step(self):
        """Un paso: recorrer todos los puntos de entrenamiento y actualizar pesos si están mal clasificados."""
        errors = 0
        for ag in self.train_points:
            x = ag.pos
            y = ag.label
            pred = self.predict(x)
            if pred != y:
                # regla del perceptrón
                self.weights += self.learning_rate * y * x
                self.bias += self.learning_rate * y
                errors += 1
        self.epoch += 1
        return errors

    def train(self, epochs, callback=None, update_every=1):
        """Entrena el perceptrón por `epochs` iteraciones.
        callback(model, epoch) se llama cada `update_every` iteraciones para actualizar la UI.
        """
        epochs = int(epochs)
        for e in range(epochs):
            errs = self.step()
            if callback and ((e + 1) % update_every == 0 or e == epochs - 1):
                callback(self, self.epoch)
            # si no hay errores, el perceptrón ya separó perfectamente
            if errs == 0:
                if callback:
                    callback(self, self.epoch)
                break

    def evaluate(self):
        """Evalúa en el conjunto de prueba y devuelve porcentaje de aciertos."""
        if len(self.test_points) == 0:
            return 0.0
        correct = 0
        for ag in self.test_points:
            if self.predict(ag.pos) == ag.label:
                correct += 1
        return correct / len(self.test_points) * 100.0


# ---------- Interfaz con matplotlib ----------


def make_plot(model):
    fig, ax = plt.subplots(figsize=(7, 7))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # scatter inicial
    pts = np.array([ag.pos for ag in model.train_points])
    labs = np.array([ag.label for ag in model.train_points])

    colors = ['green' if model.predict(p) == l else 'red' for p, l in zip(pts, labs)]
    scatter = ax.scatter(pts[:, 0], pts[:, 1], c=colors, s=40, edgecolors='k')

    # línea verdadera (fina, punteada)
    x_vals = np.array([-1.2, 1.2])
    a, b, c = model.true_line
    if abs(b) > 1e-6:
        y_true = -(a * x_vals + c) / b
        true_line_plot, = ax.plot(x_vals, y_true, linestyle='--', linewidth=1, label='separador verdadero')
    else:
        # línea vertical
        x0 = -c / a
        true_line_plot, = ax.plot([x0, x0], [-1.2, 1.2], linestyle='--', linewidth=1, label='separador verdadero')

    # línea de decisión (inicial)
    decision_line_plot, = ax.plot([], [], linewidth=2, label='frontera de decisión')

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_title('Perceptrón - clasificación lineal')
    ax.legend(loc='upper right')

    # texto de estado
    status_text = ax.text(-1.05, 1.03, f'epoch: {model.epoch}', fontsize=9, bbox=dict(facecolor='white', alpha=0.6))
    acc_text = ax.text(-0.2, 1.03, '', fontsize=9, bbox=dict(facecolor='white', alpha=0.6))

    # sliders: learning rate y num iter
    axlr = plt.axes([0.1, 0.15, 0.8, 0.03])
    axiter = plt.axes([0.1, 0.1, 0.8, 0.03])

    s_lr = Slider(axlr, 'tasa_aprendizaje', 0.001, 1.0, valinit=model.learning_rate, valstep=0.001)
    s_iter = Slider(axiter, 'iteraciones', 1, 1000, valinit=100, valstep=1)

    # botones
    axstart = plt.axes([0.1, 0.02, 0.15, 0.05])
    axreset = plt.axes([0.28, 0.02, 0.15, 0.05])

    b_start = Button(axstart, 'iniciar')
    b_reset = Button(axreset, 'restablecer')

    def update_visual(model_obj, epoch=None):
        # actualizar colores según predicción actual
        pts = np.array([ag.pos for ag in model_obj.train_points])
        labs = np.array([ag.label for ag in model_obj.train_points])
        colors = ['green' if model_obj.predict(p) == l else 'red' for p, l in zip(pts, labs)]

        scatter.set_offsets(pts)
        scatter.set_color(colors)

        # actualizar línea de decisión
        w = model_obj.weights
        b = model_obj.bias
        if abs(w[1]) > 1e-6:
            y_dec = -(w[0] * x_vals + b) / w[1]
            decision_line_plot.set_data(x_vals, y_dec)
        else:
            # línea vertical x = -b/w0
            if abs(w[0]) > 1e-6:
                x0 = -b / w[0]
                decision_line_plot.set_data([x0, x0], [-1.2, 1.2])
            else:
                decision_line_plot.set_data([], [])

        status_text.set_text(f'epoch: {model_obj.epoch}\n' \
                               f'pesos: [{model_obj.weights[0]:.3f}, {model_obj.weights[1]:.3f}] sesgo: {model_obj.bias:.3f}')

        fig.canvas.draw_idle()
        plt.pause(0.001)

    def on_start(event):
        # leer valores de sliders
        lr = s_lr.val
        iters = int(s_iter.val)
        model.learning_rate = lr

        # entrenar y actualizar la visual en cada epoch
        b_start.label.set_text('corriendo...')
        b_start.ax.figure.canvas.draw()
        model.train(iters, callback=update_visual, update_every=1)
        accuracy = model.evaluate()
        acc_text.set_text(f'precisión prueba: {accuracy:.2f}%')
        b_start.label.set_text('iniciar')
        b_start.ax.figure.canvas.draw()

    def on_reset(event):
        model.reset_model()
        # actualizar texto y gráficos
        update_visual(model)
        acc_text.set_text('')

    b_start.on_clicked(on_start)
    b_reset.on_clicked(on_reset)

    # dibujar por primera vez
    update_visual(model)
    plt.show()


# ---------- pruebas rápidas (headless) ----------

def _test_headless():
    """Prueba simple para verificar que la lógica funciona sin GUI.
    Entrenamos por unas pocas iteraciones y mostramos precisión.
    """
    m = PerceptronModel(n_train=50, n_test=200, learning_rate=0.1)
    print('pesos iniciales:', m.weights, 'bias inicial:', m.bias)
    m.train(epochs=50)
    acc = m.evaluate()
    print(f'precisión tras entrenamiento (headless): {acc:.2f}%')


if __name__ == '__main__':
    # ejecutar pruebas headless antes de abrir la GUI
    _test_headless()

    # crear modelo y abrir interfaz
    model = PerceptronModel(n_train=200, n_test=400, learning_rate=0.1)
    make_plot(model)


