// Memoria.kt
class Memoria {
    private var mem: Double = 0.0
    fun mPlus(v: Double) { mem += v }
    fun mMinus(v: Double) { mem -= v }
    fun recall(): Double = mem
    fun clear() { mem = 0.0 }
}
