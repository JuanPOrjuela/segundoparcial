from mesa import Agent, Model
from mesa.time import RandomActivation
import re
import math
import uuid
import sys

# --------------------
# Agentes
# --------------------
class OperationAgent(Agent):
    """Agente genérico para operaciones. Mantiene una cola de tareas."""
    def __init__(self, unique_id, model, op_symbol, func):
        super().__init__(unique_id, model)
        self.op = op_symbol
        self.func = func
        self.queue = []

    def step(self):
        if not self.queue:
            return
        task = self.queue.pop(0)
        task_id = task['id']
        a = task['a']
        b = task['b']
        try:
            res = self.func(a, b)
            self.model.results[task_id] = {'ok': True, 'value': res}
        except Exception as e:
            self.model.results[task_id] = {'ok': False, 'error': str(e)}


class IOAgent(Agent):
    TOKEN_RE = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|(\^|\+|\-|\*|\/|\(|\)))")

    def __init__(self, unique_id, model, ops_map):
        super().__init__(unique_id, model)
        self.ops_map = ops_map
        self.prec = {'^': 4, '*': 3, '/': 3, '+': 2, '-': 2}
        self.right_assoc = {'^'}

    def tokenize(self, expr):
        tokens = []
        pos = 0
        s = expr
        while pos < len(s):
            m = self.TOKEN_RE.match(s, pos)
            if not m:
                raise ValueError(f"Token inválido cerca de: {s[pos:]}")
            num, op = m.groups()
            if num:
                tokens.append(num)
            else:
                tokens.append(op)
            pos = m.end()
        return tokens

    def to_rpn(self, tokens):
        output = []
        stack = []
        for tok in tokens:
            if re.fullmatch(r"\d+(?:\.\d+)?", tok):
                output.append(tok)
            elif tok in self.prec:
                while stack and stack[-1] in self.prec:
                    top = stack[-1]
                    if ((tok in self.right_assoc and self.prec[tok] < self.prec[top]) or
                        (tok not in self.right_assoc and self.prec[tok] <= self.prec[top])):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack or stack[-1] != '(':
                    raise ValueError("Paréntesis mismatched")
                stack.pop()
            else:
                raise ValueError(f"Token desconocido: {tok}")
        while stack:
            if stack[-1] in ('(', ')'):
                raise ValueError("Paréntesis mismatched")
            output.append(stack.pop())
        return output

    # helper para localizar agente por id (compatible con distintas versiones de mesa)
    def _find_agent_by_id(self, agent_id):
        sched = self.model.schedule
        agents_list = getattr(sched, 'agents', None)
        if isinstance(agents_list, list):
            for ag in agents_list:
                if getattr(ag, 'unique_id', None) == agent_id:
                    return ag
        agents_dict = getattr(sched, '_agents', None)
        if isinstance(agents_dict, dict):
            return agents_dict.get(agent_id, None)
        if hasattr(sched, 'get_agent'):
            try:
                return sched.get_agent(agent_id)
            except Exception:
                pass
        return None

    def request_operation(self, op_symbol, a, b):
        if op_symbol not in self.ops_map:
            raise ValueError(f"Operador '{op_symbol}' no soportado")
        task_id = str(uuid.uuid4())
        agent_id = self.ops_map[op_symbol]
        agent = self._find_agent_by_id(agent_id)
        if agent is None:
            raise RuntimeError("Agente de operación no encontrado")
        agent.queue.append({'id': task_id, 'a': a, 'b': b})
        self.model.results[task_id] = {'ok': None}
        return task_id

    def wait_for_result(self, task_id, max_steps=1000):
        steps = 0
        while steps < max_steps:
            val = self.model.results.get(task_id, None)
            if val is None:
                pass
            elif val.get('ok') is not None:
                return val
            self.model.step()
            steps += 1
        raise TimeoutError("Tiempo de espera agotado para la operación")

    def evaluate_rpn(self, rpn_tokens):
        stack = []
        for tok in rpn_tokens:
            if re.fullmatch(r"\d+(?:\.\d+)?", tok):
                stack.append(float(tok))
            elif tok in self.ops_map:
                if len(stack) < 2:
                    raise ValueError("Expresión inválida")
                b = stack.pop()
                a = stack.pop()
                task_id = self.request_operation(tok, a, b)
                res = self.wait_for_result(task_id)
                if not res['ok']:
                    raise ValueError(f"Error en operación: {res.get('error')}")
                stack.append(res['value'])
            else:
                raise ValueError(f"Operador desconocido en RPN: {tok}")
        if len(stack) != 1:
            raise ValueError("Expresión inválida al finalizar evaluación")
        return stack[0]


# --------------------
# Model
# --------------------
class CalcModel(Model):
    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.results = {}
        self.agents_map = {}
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: (a / b) if b != 0 else (_ for _ in ()).throw(ZeroDivisionError("División por cero")),
            '^': lambda a, b: math.pow(a, b),
        }
        for i, (sym, func) in enumerate(ops.items()):
            aid = f"op_{i}_{sym}"
            agent = OperationAgent(aid, self, sym, func)
            self.schedule.add(agent)
            self.agents_map[sym] = aid
        self.io_agent = IOAgent('io_1', self, self.agents_map)
        self.schedule.add(self.io_agent)

    def step(self):
        self.schedule.step()


# --------------------
# Interfaz de usuario (CLI) - SOLO EXPRESIÓN COMPLETA
# --------------------
def main():
    # mantener compatibilidad con '--test' si se desea
    if '--test' in sys.argv:
        print("Modo test activado (--test). Ejecutando tests básicos y saliendo.")
        run_tests()
        return

    print("Escribe una expresión completa para evaluar (ej: 2 + 3 * 4 - 5)")
    print("Para salir escribe 'salir', 'exit' o 'q'\n")

    model = CalcModel()

    while True:
        expr = input("Ingresa la expresión completa (o 'salir' para terminar): ").strip()
        if not expr:
            continue
        if expr.lower() in ('salir', 'exit', 'q'):
            print("Saliendo. ¡Hasta luego!")
            break
        try:
            tokens = model.io_agent.tokenize(expr)
            rpn = model.io_agent.to_rpn(tokens)
            res = model.io_agent.evaluate_rpn(rpn)
            print(f"Resultado: {res}\n")
        except Exception as e:
            print(f"Error al evaluar la expresión: {e}\n")


# Mantengo run_tests y modo paso a paso por compatibilidad (no se usan en el flujo principal)
def modo_paso_a_paso(model):
    while True:
        try:
            a = float(input("Ingresa el primer número: ").strip())
            break
        except ValueError:
            print("Entrada inválida. Ingresa un número.")
    ops = list(model.agents_map.keys())
    while True:
        op = input(f"Ingresa el operador ({' '.join(ops)}): ").strip()
        if op in ops:
            break
        print("Operador inválido.")
    while True:
        try:
            b = float(input("Ingresa el segundo número: ").strip())
            break
        except ValueError:
            print("Entrada inválida. Ingresa un número.")
    expr = f"{a} {op} {b}"
    try:
        tokens = model.io_agent.tokenize(expr)
        rpn = model.io_agent.to_rpn(tokens)
        res = model.io_agent.evaluate_rpn(rpn)
        print(f"Expresión: {expr}\nResultado: {res}\n")
    except Exception as e:
        print(f"Error al evaluar: {e}\n")


def run_tests():
    print("Ejecutando tests básicos...")
    m = CalcModel()
    tests = [
        ("2 + 3 * 4 - 5", 9.0),
        ("(2 + 3) * (4 - 1) / 5 + 2^3", 11.0),
        ("3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3", 3.0001220703125),
    ]
    extra = [
        ("4 / 2 + 1", 3.0),
    ]
    ok = True
    for expr, expected in tests + extra:
        try:
            tokens = m.io_agent.tokenize(expr)
            rpn = m.io_agent.to_rpn(tokens)
            res = m.io_agent.evaluate_rpn(rpn)
            print(f"{expr} = {res} (expected {expected})")
            if abs(res - expected) > 1e-9:
                print("  -> FAIL")
                ok = False
            else:
                print("  -> OK")
        except Exception as e:
            print(f"Error evaluando {expr}: {e}")
            ok = False

    try:
        expr = "1 / 0"
        tokens = m.io_agent.tokenize(expr)
        rpn = m.io_agent.to_rpn(tokens)
        _ = m.io_agent.evaluate_rpn(rpn)
        print("1 / 0 did not raise (FAIL)")
        ok = False
    except Exception:
        print("1 / 0 raised as expected -> OK")

    if ok:
        print("Todos los tests pasaron.\n")
    else:
        print("Algunos tests fallaron.\n")


if __name__ == "__main__":
    main()
