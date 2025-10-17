import java.awt.BorderLayout
import java.awt.Dimension
import java.awt.GridLayout
import javax.swing.*

class CalculatorUI {
    private val calc = CalculadoraCientifica()
    private val mem = Memoria()

    private val frame = JFrame("Calculadora Científica - Kotlin")
    private val display = JTextField()
    private val statusLabel = JLabel("Modo: Grados") // muestra resultado o modo
    private val degreesCheck = JCheckBox("Degrees", true) // controla grados/radianes

    init {
        createAndShowGUI()
    }

    private fun createAndShowGUI() {
        frame.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        frame.layout = BorderLayout(6,6)

        // DISPLAY arriba
        display.isEditable = true
        display.preferredSize = Dimension(420, 40)
        frame.add(display, BorderLayout.NORTH)

        // PANEL CENTRAL con GRID organizado
        // Usamos 7 filas x 5 columnas (puedes ajustar filas/cols si añades/quitas botones)
        val gridRows = 7
        val gridCols = 5
        val btnPanel = JPanel(GridLayout(gridRows, gridCols, 6, 6))
        btnPanel.border = BorderFactory.createEmptyBorder(6,6,6,6)

        // Lista organizada por filas (fila 1 arriba)
        val buttons = listOf(
            "7","8","9","/","sqrt",
            "4","5","6","*","^",
            "1","2","3","-","(",
            "0",".","ANS","+",")",
            "sin","cos","tan","log","ln",
            "exp","pi","e","M+","M-",
            "MR","MC","CLR","BACK","DEG" // DEG será tratado: al pulsarlo alterna degreesCheck
        )

        // Crea y anexa botones al panel. Para el último cell (DEG) también incluimos el JCheckBox debajo
        for (label in buttons) {
            if (label == "DEG") {
                // Ponemos un panel que contiene el botón DEG y el JCheckBox (apilados verticalmente)
                val degPanel = JPanel(GridLayout(2,1,2,2))
                val degBtn = JButton("DEG")
                degBtn.addActionListener { toggleDegrees() }
                degPanel.add(degBtn)
                degPanel.add(degreesCheck)
                btnPanel.add(degPanel)
            } else {
                val btn = JButton(label)
                btn.addActionListener { onButtonPressed(label) }
                btnPanel.add(btn)
            }
        }

        frame.add(btnPanel, BorderLayout.CENTER)

        // PANEL INFERIOR con acciones principales y estado
        val bottom = JPanel()
        val evalBtn = JButton("Evaluar")
        evalBtn.addActionListener { evaluateExpression() }
        val clearBtn = JButton("Limpiar")
        clearBtn.addActionListener { display.text = ""; statusLabel.text = if (degreesCheck.isSelected) "Modo: Grados" else "Modo: Radianes" }

        bottom.add(evalBtn)
        bottom.add(clearBtn)
        bottom.add(statusLabel)
        frame.add(bottom, BorderLayout.SOUTH)

        frame.pack()
        frame.setLocationRelativeTo(null)
        frame.isVisible = true
    }

    private var lastAnswer: Double? = null

    private fun onButtonPressed(label: String) {
        when (label) {
            "CLR" -> { display.text = ""; statusLabel.text = if (degreesCheck.isSelected) "Modo: Grados" else "Modo: Radianes" }
            "BACK" -> { if (display.text.isNotEmpty()) display.text = display.text.dropLast(1) }
            "M+" -> memoryAdd()
            "M-" -> memorySubtract()
            "MR" -> display.text += mem.recall().toString()
            "MC" -> { mem.clear(); JOptionPane.showMessageDialog(frame, "Memoria borrada") }
            "ANS" -> display.text += (lastAnswer?.toString() ?: "")
            "pi" -> display.text += "pi"
            "e" -> display.text += "e"
            "sqrt","sin","cos","tan","log","ln","exp" -> display.text += "$label("
            else -> display.text += label
        }
    }

    private fun toggleDegrees() {
        degreesCheck.isSelected = !degreesCheck.isSelected
        statusLabel.text = if (degreesCheck.isSelected) "Modo: Grados" else "Modo: Radianes"
    }

    private fun evaluateExpression() {
        val expr = display.text.trim()
        if (expr.isEmpty()) return
        try {
            val degrees = degreesCheck.isSelected
            val res = ExpressionEvaluator.evaluate(expr, calc, degrees)
            lastAnswer = res
            statusLabel.text = "= $res"
        } catch (ex: Exception) {
            JOptionPane.showMessageDialog(frame, "Error: ${ex.message}", "Error", JOptionPane.ERROR_MESSAGE)
        }
    }

    private fun memoryAdd() {
        val expr = display.text.trim()
        if (expr.isEmpty()) { JOptionPane.showMessageDialog(frame, "Ingresa expresión para M+") ; return }
        try {
            val degrees = degreesCheck.isSelected
            val v = ExpressionEvaluator.evaluate(expr, calc, degrees)
            mem.mPlus(v)
            JOptionPane.showMessageDialog(frame, "Memoria = ${mem.recall()}")
        } catch (ex: Exception) {
            JOptionPane.showMessageDialog(frame, "Error: ${ex.message}", "Error", JOptionPane.ERROR_MESSAGE)
        }
    }

    private fun memorySubtract() {
        val expr = display.text.trim()
        if (expr.isEmpty()) { JOptionPane.showMessageDialog(frame, "Ingresa expresión para M-") ; return }
        try {
            val degrees = degreesCheck.isSelected
            val v = ExpressionEvaluator.evaluate(expr, calc, degrees)
            mem.mMinus(v)
            JOptionPane.showMessageDialog(frame, "Memoria = ${mem.recall()}")
        } catch (ex: Exception) {
            JOptionPane.showMessageDialog(frame, "Error: ${ex.message}", "Error", JOptionPane.ERROR_MESSAGE)
        }
    }
}