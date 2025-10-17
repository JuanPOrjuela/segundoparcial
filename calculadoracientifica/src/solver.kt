import java.util.Stack
import kotlin.math.*

object ExpressionEvaluator {
    private val tokenRegex = Regex("""\s*(\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|\^|\+|\-|\*|\/|\(|\)|,)""")
    private val numberRegex = Regex("""^\d+(?:\.\d+)?$""")
    private val prec = mapOf("^" to 4, "*" to 3, "/" to 3, "+" to 2, "-" to 2)
    private val rightAssoc = setOf("^")

    private fun isNumber(tok: String) = numberRegex.matches(tok)
    private fun isFunction(tok: String) = tok.matches(Regex("[A-Za-z_][A-Za-z0-9_]*")) && tok.lowercase() !in setOf("pi", "e")

    fun toRPN(expression: String): List<String> {
        val tokens = mutableListOf<String>()
        var pos = 0
        val s = expression
        while (pos < s.length) {
            val m = tokenRegex.find(s, pos) ?: throw IllegalArgumentException("Token inválido cerca de: '${s.substring(pos)}'")
            val tok = m.groupValues[1]
            tokens.add(tok)
            pos = m.range.last + 1
        }

        val output = mutableListOf<String>()
        val stack = Stack<String>()

        var i = 0
        while (i < tokens.size) {
            val tok = tokens[i]
            when {
                isNumber(tok) || tok.lowercase() == "pi" || tok.lowercase() == "e" -> output.add(tok)
                isFunction(tok) -> stack.push(tok)
                tok == "," -> {
                    while (stack.isNotEmpty() && stack.peek() != "(") output.add(stack.pop())
                    if (stack.isEmpty() || stack.peek() != "(") throw IllegalArgumentException("Separador de función mal colocado")
                }
                tok == "(" -> stack.push(tok)
                tok == ")" -> {
                    while (stack.isNotEmpty() && stack.peek() != "(") output.add(stack.pop())
                    if (stack.isEmpty()) throw IllegalArgumentException("Paréntesis mismatched")
                    stack.pop()
                    if (stack.isNotEmpty() && isFunction(stack.peek())) output.add(stack.pop())
                }
                prec.containsKey(tok) -> {
                    val o1 = tok
                    while (stack.isNotEmpty() && prec.containsKey(stack.peek())) {
                        val o2 = stack.peek()
                        if ((o1 in rightAssoc && prec[o1]!! < prec[o2]!!) || (o1 !in rightAssoc && prec[o1]!! <= prec[o2]!!)) {
                            output.add(stack.pop())
                        } else break
                    }
                    stack.push(o1)
                }
                else -> throw IllegalArgumentException("Token desconocido: $tok")
            }
            i++
        }
        while (stack.isNotEmpty()) {
            val t = stack.pop()
            if (t == "(" || t == ")") throw IllegalArgumentException("Paréntesis mismatched")
            output.add(t)
        }
        return output
    }

    fun evalRPN(tokens: List<String>, calc: CalculadoraCientifica, degrees: Boolean): Double {
        val st = Stack<Double>()
        for (tok in tokens) {
            when {
                isNumber(tok) -> st.push(tok.toDouble())
                tok.lowercase() == "pi" -> st.push(Math.PI)
                tok.lowercase() == "e" -> st.push(Math.E)
                setOf("+", "-", "*", "/", "^").contains(tok) -> {
                    if (st.size < 2) throw IllegalArgumentException("Expresión inválida")
                    val b = st.pop()
                    val a = st.pop()
                    val res = when (tok) {
                        "+" -> calc.suma(a, b)
                        "-" -> calc.resta(a, b)
                        "*" -> calc.multiplicacion(a, b)
                        "/" -> calc.division(a, b)
                        "^" -> calc.pow(a, b)
                        else -> 0.0
                    }
                    st.push(res)
                }
                else -> {
                    // función unaria
                    if (st.isEmpty()) throw IllegalArgumentException("Función sin operandos")
                    val a = st.pop()
                    val res = when (tok.lowercase()) {
                        "sin" -> if (degrees) calc.sinDeg(a) else calc.sinRad(a)
                        "cos" -> if (degrees) calc.cosDeg(a) else calc.cosRad(a)
                        "tan" -> if (degrees) calc.tanDeg(a) else calc.tanRad(a)
                        "log" -> calc.log10Val(a)
                        "ln" -> calc.lnVal(a)
                        "exp" -> calc.expVal(a)
                        "sqrt" -> calc.sqrtVal(a)
                        else -> throw IllegalArgumentException("Función desconocida: $tok")
                    }
                    st.push(res)
                }
            }
        }
        if (st.size != 1) throw IllegalArgumentException("Expresión inválida al finalizar evaluación")
        return st.pop()
    }

    fun evaluate(expression: String, calc: CalculadoraCientifica, degrees: Boolean): Double {
        val rpn = toRPN(expression)
        return evalRPN(rpn, calc, degrees)
    }
}

