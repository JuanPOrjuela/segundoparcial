// Calculadora.kt
open class Calculadora {
    // Double versions
    open fun suma(a: Double, b: Double): Double = a + b
    open fun resta(a: Double, b: Double): Double = a - b
    open fun multiplicacion(a: Double, b: Double): Double = a * b

    open fun division(a: Double, b: Double): Double {
        if (b == 0.0) throw ArithmeticException("División por cero")
        return a / b
    }

    // Int overloads (polimorfismo por sobrecarga)
    fun suma(a: Int, b: Int): Int = a + b
    fun resta(a: Int, b: Int): Int = a - b
    fun multiplicacion(a: Int, b: Int): Int = a * b
    fun division(a: Int, b: Int): Double {
        if (b == 0) throw ArithmeticException("División por cero")
        return a.toDouble() / b.toDouble()
    }
}
