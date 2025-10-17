// CalculadoraCientifica.kt
import kotlin.math.*

class CalculadoraCientifica : Calculadora() {
    // Trig (grados)
    fun sinDeg(deg: Double): Double = sin(Math.toRadians(deg))
    fun cosDeg(deg: Double): Double = cos(Math.toRadians(deg))
    fun tanDeg(deg: Double): Double = tan(Math.toRadians(deg))

    // Trig (radianes)
    fun sinRad(rad: Double): Double = sin(rad)
    fun cosRad(rad: Double): Double = cos(rad)
    fun tanRad(rad: Double): Double = tan(rad)

    fun pow(a: Double, b: Double): Double = a.pow(b)

    fun sqrtVal(a: Double): Double {
        if (a < 0.0) throw ArithmeticException("Raíz de número negativo")
        return sqrt(a)
    }

    fun log10Val(a: Double): Double {
        if (a <= 0.0) throw ArithmeticException("Logaritmo base 10 de valor no positivo")
        return log10(a)
    }

    fun lnVal(a: Double): Double {
        if (a <= 0.0) throw ArithmeticException("Logaritmo natural de valor no positivo")
        return ln(a)
    }

    fun expVal(a: Double): Double = exp(a)

    fun degToRad(deg: Double): Double = Math.toRadians(deg)
    fun radToDeg(rad: Double): Double = Math.toDegrees(rad)
}
