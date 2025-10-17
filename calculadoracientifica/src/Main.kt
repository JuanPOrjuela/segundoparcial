// Main.kt
import javax.swing.SwingUtilities

fun runTestsConsole() {
    val calc = CalculadoraCientifica()
    val tests = listOf(
        "2 + 3 * 4 - 5" to 9.0,
        "(2 + 3) * (4 - 1) / 5 + 2^3" to 11.0,
        "3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3" to 3.0001220703125,
        "sin(30)" to 0.5,
        "log(100)" to 2.0,
        "ln(e)" to 1.0,
        "sqrt(9)" to 3.0
    )
    var ok = true
    for ((expr, expected) in tests) {
        try {
            val res = ExpressionEvaluator.evaluate(expr, calc, true)
            println("$expr = $res (expected $expected)")
            if (!res.isFinite() || kotlin.math.abs(res - expected) > 1e-9) {
                println("  -> FAIL"); ok = false
            } else println("  -> OK")
        } catch (e: Exception) {
            println("Error en test $expr : ${e.message}")
            ok = false
        }
    }
    try {
        ExpressionEvaluator.evaluate("1 / 0", calc, true)
        println("1 / 0 did not raise (FAIL)"); ok = false
    } catch (e: Exception) {
        println("1 / 0 raised as expected -> OK")
    }
    if (ok) println("Todos los tests pasaron") else println("Algunos tests fallaron")
}

fun main(args: Array<String>) {
    if (args.contains("--test")) {
        runTestsConsole()
        return
    }
    SwingUtilities.invokeLater {
        CalculatorUI() // opens the GUI
    }
}

