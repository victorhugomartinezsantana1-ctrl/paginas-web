# Laboratorio — ART-018 Control PID

Fecha de ejecución: 2026-10-27. Equipo: simulación numérica en Python 3.14.2 y g++ 16.1.0 (-std=c++20 -Wall -Wextra -O0) sobre Windows 11, integración de Euler con paso de 2 ms, planta ficticia G(s)=1/(s+1)^3. No hay hardware: ningún resultado procede de un motor ni de un microcontrolador. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_pid.py

```python
import math
import random
import statistics
import sys

DT = 0.002


def titulo(t):
    print(f"\n=== {t} ===")


class Planta:
    """G(s) = 1/(s+1)^3: tres etapas de primer orden en serie, ganancia estática 1."""

    def __init__(self):
        self.x = [0.0, 0.0, 0.0]

    def paso(self, u, dt=DT):
        e = u
        for i in range(3):
            self.x[i] += dt * (e - self.x[i])
            e = self.x[i]
        return self.x[2]


class PID:
    def __init__(self, kp, ki, kd, umin=None, umax=None, antiwindup=False, deriv_medida=False, tau_d=None):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.umin, self.umax, self.aw = umin, umax, antiwindup
        self.dm, self.tau = deriv_medida, tau_d
        self.i = 0.0
        self.prev = None
        self.dfilt = 0.0

    def paso(self, ref, y, dt=DT):
        e = ref - y
        if self.prev is None:
            self.prev = y if self.dm else 0.0
        raw = (-(y - self.prev) if self.dm else (e - self.prev)) / dt
        self.prev = y if self.dm else e
        if self.tau:
            a = dt / (self.tau + dt)
            self.dfilt += a * (raw - self.dfilt)
            d = self.dfilt
        else:
            d = raw
        i_nuevo = self.i + self.ki * e * dt
        u = self.kp * e + i_nuevo + self.kd * d
        us = u
        if self.umin is not None:
            us = min(max(u, self.umin), self.umax)
        if self.aw and us != u:
            pass  # integración condicional: no acumular mientras sature
        else:
            self.i = i_nuevo
        return us


def simula(pid, ref=1.0, t_fin=40.0, ruido=0.0, semilla=1, planta=None, ref_fn=None):
    p = planta or Planta()
    rnd = random.Random(semilla)
    y = 0.0
    ts, ys, us = [], [], []
    n = int(t_fin / DT)
    for k in range(n):
        t = k * DT
        r = ref_fn(t) if ref_fn else ref
        u = pid.paso(r, y + (rnd.gauss(0, ruido) if ruido else 0.0))
        y = p.paso(u)
        ts.append(t)
        ys.append(y)
        us.append(u)
    return ts, ys, us


def metricas(ts, ys, ref=1.0):
    pico = max(ys)
    sobre = max(0.0, (pico - ref) / ref * 100)
    t10 = next((t for t, y in zip(ts, ys) if y >= 0.1 * ref), float("nan"))
    t90 = next((t for t, y in zip(ts, ys) if y >= 0.9 * ref), float("nan"))
    asent = 0.0
    for t, y in zip(ts, ys):
        if abs(y - ref) > 0.02 * ref:
            asent = t
    ess = ref - statistics.mean(ys[-int(2 / DT):])
    return {"subida": t90 - t10, "sobre": sobre, "asent": asent, "ess": ess}


def fila(nombre, m):
    print(f"  {nombre:28s} subida10-90={m['subida']:6.2f} s | sobreimpulso={m['sobre']:6.1f} % | asentamiento 2 %={m['asent']:6.2f} s | error final={m['ess']:7.4f}")


print("Python", sys.version.split()[0], "| planta 1/(s+1)^3 | paso de integración", DT, "s")

titulo("1. Solo P: el error estacionario")
for kp in (0.5, 1, 2, 4):
    ts, ys, _ = simula(PID(kp, 0, 0))
    m = metricas(ts, ys)
    print(f"  Kp={kp:<4}: valor final={1 - m['ess']:.4f} (teórico Kp/(1+Kp)={kp / (1 + kp):.4f}) | error final={m['ess']:.4f} | sobreimpulso={m['sobre']:.1f} %")

titulo("2. P, PI y PID sobre la misma planta (Kp=2)")
for nombre, pid in (("P   Kp=2", PID(2, 0, 0)), ("PI  Kp=2 Ki=0.5", PID(2, 0.5, 0)), ("PID Kp=2 Ki=0.5 Kd=1", PID(2, 0.5, 1, tau_d=0.05))):
    ts, ys, _ = simula(pid, t_fin=60)
    fila(nombre, metricas(ts, ys))

titulo("3. Ganancia última Ku y periodo Tu (solo P, por bisección)")


def oscila(kp):
    ts, ys, _ = simula(PID(kp, 0, 0), t_fin=120)
    cola = ys[-int(30 / DT):]
    amp_ini = max(cola[: len(cola) // 2]) - min(cola[: len(cola) // 2])
    amp_fin = max(cola[len(cola) // 2:]) - min(cola[len(cola) // 2:])
    return amp_fin >= amp_ini * 0.999, ts, ys


lo, hi = 4.0, 12.0
for _ in range(14):
    mid = (lo + hi) / 2
    crece, _, _ = oscila(mid)
    if crece:
        hi = mid
    else:
        lo = mid
ku = (lo + hi) / 2
_, ts, ys = oscila(ku)
cruces = [ts[i] for i in range(1, len(ys)) if (ys[i - 1] - 1.0) < 0 <= (ys[i] - 1.0) and ts[i] > 60]
tu = statistics.mean([b - a for a, b in zip(cruces, cruces[1:])]) if len(cruces) > 2 else float("nan")
print(f"  Ku medido = {ku:.3f} (analítico para 1/(s+1)^3: 8)  | Tu medido = {tu:.3f} s (analítico 2π/√3 = {2 * math.pi / math.sqrt(3):.3f} s)")

titulo("4. Reglas de Ziegler-Nichols con Ku=8 y Tu=3.628 s")
KU, TU = 8.0, 2 * math.pi / math.sqrt(3)
reglas = {
    "P  (0.5Ku)": (0.5 * KU, 0, 0),
    "PI (0.45Ku, Ti=0.833Tu)": (0.45 * KU, 0.45 * KU / (0.833 * TU), 0),
    "PID clásico (0.6Ku, Ti=0.5Tu, Td=0.125Tu)": (0.6 * KU, 0.6 * KU / (0.5 * TU), 0.6 * KU * 0.125 * TU),
}
for nombre, (kp, ki, kd) in reglas.items():
    ts, ys, _ = simula(PID(kp, ki, kd, tau_d=0.05), t_fin=60)
    print(f"  {nombre}: Kp={kp:.2f} Ki={ki:.2f} Kd={kd:.2f}")
    fila("    resultado", metricas(ts, ys))

titulo("5. Efecto de aumentar cada ganancia desde Kp=2, Ki=0.5, Kd=1")
base = (2.0, 0.5, 1.0)
variantes = [("base", base), ("Kp x2", (4.0, 0.5, 1.0)), ("Ki x2", (2.0, 1.0, 1.0)), ("Kd x2", (2.0, 0.5, 2.0))]
for nombre, (kp, ki, kd) in variantes:
    ts, ys, _ = simula(PID(kp, ki, kd, tau_d=0.05), t_fin=80)
    fila(nombre, metricas(ts, ys))

titulo("6. Saturación del actuador y acumulación del integrador (windup)")
ref_fn = lambda t: 4.0 if t < 25 else 1.5
for nombre, aw in (("sin protección", False), ("integración condicional", True)):
    ts, ys, us = simula(PID(2, 0.8, 0, umin=0.0, umax=2.0, antiwindup=aw), t_fin=70, ref_fn=ref_fn)
    pico = max(y for t, y in zip(ts, ys) if t > 25)
    vuelta = next((t - 25 for t, y in zip(ts, ys) if t > 25 and y <= 1.5), float("nan"))
    asent = 0.0
    for t, y in zip(ts, ys):
        if t > 25 and abs(y - 1.5) > 0.03:
            asent = t
    print(f"  {nombre:26s}: tras bajar la consigna de 4 a 1,5 en t=25 s -> pico posterior={pico:.2f} | vuelve a 1,5 tras {vuelta:5.1f} s | asentado (±0,03) en t={asent:5.1f} s")

titulo("7. Ruido de medida (σ=0,01) y derivada")
for nombre, pid in (
    ("derivada sin filtro, sobre el error", PID(2, 0.5, 1)),
    ("derivada filtrada (τ=0,05 s)", PID(2, 0.5, 1, tau_d=0.05)),
    ("derivada filtrada sobre la medida", PID(2, 0.5, 1, tau_d=0.05, deriv_medida=True)),
    ("sin derivada (PI)", PID(2, 0.5, 0)),
):
    ts, ys, us = simula(pid, t_fin=40, ruido=0.01)
    cola = us[int(20 / DT):]
    print(f"  {nombre:38s}: desviación típica de u = {statistics.pstdev(cola):.3f} | pico |u| inicial = {max(abs(u) for u in us[:100]):.1f}")
class PlantaK(Planta):
    def __init__(self, k=1.0, retardo=0.0):
        super().__init__()
        self.k = k
        self.cola = [0.0] * int(retardo / DT)

    def paso(self, u, dt=DT):
        if self.cola:
            self.cola.append(u)
            u = self.cola.pop(0)
        return self.k * super().paso(u, dt)


titulo("8. Robustez: la misma sintonía con una planta de otra ganancia")
for nombre, (kp, ki, kd) in (("manual (2; 0,5; 1)", (2, 0.5, 1)), ("Ziegler-Nichols PID (4,8; 2,65; 2,18)", (4.8, 2.65, 2.18))):
    print(f"  {nombre}")
    for k in (0.5, 1.0, 1.5, 2.0):
        ts, ys, _ = simula(PID(kp, ki, kd, tau_d=0.05), t_fin=80, planta=PlantaK(k))
        ref_ = 1.0
        m = metricas(ts, ys, ref_)
        estable = abs(ys[-1] - 1.0) < 0.05 and max(abs(y) for y in ys[-int(10 / DT):]) < 3
        print(f"    ganancia de la planta x{k}: sobreimpulso={min(m['sobre'], 9999):7.1f} % | asentamiento 2 %={m['asent']:6.2f} s | ¿se asienta en 1 ± 0,05 al final?: {estable}")

titulo("9. Un retardo puro (tiempo muerto) en la planta, sintonía manual (2; 0,5; 1)")
for retardo in (0.0, 0.5, 1.0, 2.0):
    ts, ys, _ = simula(PID(2, 0.5, 1, tau_d=0.05), t_fin=120, planta=PlantaK(1.0, retardo))
    m = metricas(ts, ys)
    estable = abs(ys[-1] - 1.0) < 0.05 and max(abs(y) for y in ys[-int(10 / DT):]) < 3
    print(f"  retardo={retardo:3.1f} s: sobreimpulso={min(m['sobre'], 9999):7.1f} % | asentamiento 2 %={m['asent']:6.2f} s | ¿se asienta al final?: {estable}")

titulo("10. Ajuste manual paso a paso (una ganancia cada vez)")
pasos = [
    ("1. solo P, Kp=1", (1, 0, 0)),
    ("2. P más fuerte, Kp=2", (2, 0, 0)),
    ("3. añadir I suave, Ki=0,2", (2, 0.2, 0)),
    ("4. subir I, Ki=0,5", (2, 0.5, 0)),
    ("5. añadir D, Kd=1", (2, 0.5, 1)),
    ("6. subir I con D, Ki=0,8", (2, 0.8, 1)),
]
for nombre, (kp, ki, kd) in pasos:
    ts, ys, _ = simula(PID(kp, ki, kd, tau_d=0.05), t_fin=100)
    fila(nombre, metricas(ts, ys))
print("\nfin")
```

## Salida de lab_pid.py

```text
Python 3.14.2 | planta 1/(s+1)^3 | paso de integración 0.002 s

=== 1. Solo P: el error estacionario ===
  Kp=0.5 : valor final=0.3333 (teórico Kp/(1+Kp)=0.3333) | error final=0.6667 | sobreimpulso=0.0 %
  Kp=1   : valor final=0.5000 (teórico Kp/(1+Kp)=0.5000) | error final=0.5000 | sobreimpulso=0.0 %
  Kp=2   : valor final=0.6667 (teórico Kp/(1+Kp)=0.6667) | error final=0.3333 | sobreimpulso=0.0 %
  Kp=4   : valor final=0.8001 (teórico Kp/(1+Kp)=0.8000) | error final=0.1999 | sobreimpulso=23.3 %

=== 2. P, PI y PID sobre la misma planta (Kp=2) ===
  P   Kp=2                     subida10-90=   nan s | sobreimpulso=   0.0 % | asentamiento 2 %= 60.00 s | error final= 0.3333
  PI  Kp=2 Ki=0.5              subida10-90=  1.65 s | sobreimpulso=  16.1 % | asentamiento 2 %= 14.14 s | error final= 0.0000
  PID Kp=2 Ki=0.5 Kd=1         subida10-90=  1.98 s | sobreimpulso=   0.0 % | asentamiento 2 %= 12.11 s | error final= 0.0000

=== 3. Ganancia última Ku y periodo Tu (solo P, por bisección) ===
  Ku medido = 8.022 (analítico para 1/(s+1)^3: 8)  | Tu medido = 3.619 s (analítico 2π/√3 = 3.628 s)

=== 4. Reglas de Ziegler-Nichols con Ku=8 y Tu=3.628 s ===
  P  (0.5Ku): Kp=4.00 Ki=0.00 Kd=0.00
      resultado                subida10-90=  1.15 s | sobreimpulso=  23.3 % | asentamiento 2 %= 60.00 s | error final= 0.2000
  PI (0.45Ku, Ti=0.833Tu): Kp=3.60 Ki=1.19 Kd=0.00
      resultado                subida10-90=  1.05 s | sobreimpulso=  56.0 % | asentamiento 2 %= 30.69 s | error final=-0.0000
  PID clásico (0.6Ku, Ti=0.5Tu, Td=0.125Tu): Kp=4.80 Ki=2.65 Kd=2.18
      resultado                subida10-90=  0.83 s | sobreimpulso=  42.9 % | asentamiento 2 %=  9.15 s | error final= 0.0000

=== 5. Efecto de aumentar cada ganancia desde Kp=2, Ki=0.5, Kd=1 ===
  base                         subida10-90=  1.98 s | sobreimpulso=   0.0 % | asentamiento 2 %= 12.11 s | error final= 0.0000
  Kp x2                        subida10-90=  1.10 s | sobreimpulso=  20.3 % | asentamiento 2 %= 19.39 s | error final= 0.0000
  Ki x2                        subida10-90=  1.58 s | sobreimpulso=  16.2 % | asentamiento 2 %=  7.78 s | error final= 0.0000
  Kd x2                        subida10-90=  5.14 s | sobreimpulso=   0.0 % | asentamiento 2 %= 11.46 s | error final= 0.0000

=== 6. Saturación del actuador y acumulación del integrador (windup) ===
  sin protección            : tras bajar la consigna de 4 a 1,5 en t=25 s -> pico posterior=2.00 | vuelve a 1,5 tras   nan s | asentado (±0,03) en t= 70.0 s
  integración condicional   : tras bajar la consigna de 4 a 1,5 en t=25 s -> pico posterior=2.00 | vuelve a 1,5 tras   1.7 s | asentado (±0,03) en t= 36.8 s

=== 7. Ruido de medida (σ=0,01) y derivada ===
  derivada sin filtro, sobre el error   : desviación típica de u = 7.079 | pico |u| inicial = 495.5
  derivada filtrada (τ=0,05 s)          : desviación típica de u = 0.215 | pico |u| inicial = 21.0
  derivada filtrada sobre la medida     : desviación típica de u = 0.215 | pico |u| inicial = 2.7
  sin derivada (PI)                     : desviación típica de u = 0.020 | pico |u| inicial = 2.1

=== 8. Robustez: la misma sintonía con una planta de otra ganancia ===
  manual (2; 0,5; 1)
    ganancia de la planta x0.5: sobreimpulso=    0.0 % | asentamiento 2 %= 19.74 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x1.0: sobreimpulso=    0.0 % | asentamiento 2 %= 12.11 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x1.5: sobreimpulso=    8.3 % | asentamiento 2 %=  9.72 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x2.0: sobreimpulso=   17.3 % | asentamiento 2 %=  8.84 s | ¿se asienta en 1 ± 0,05 al final?: True
  Ziegler-Nichols PID (4,8; 2,65; 2,18)
    ganancia de la planta x0.5: sobreimpulso=   26.4 % | asentamiento 2 %=  7.82 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x1.0: sobreimpulso=   42.9 % | asentamiento 2 %=  9.14 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x1.5: sobreimpulso=   52.9 % | asentamiento 2 %= 10.37 s | ¿se asienta en 1 ± 0,05 al final?: True
    ganancia de la planta x2.0: sobreimpulso=   60.1 % | asentamiento 2 %= 10.62 s | ¿se asienta en 1 ± 0,05 al final?: True

=== 9. Un retardo puro (tiempo muerto) en la planta, sintonía manual (2; 0,5; 1) ===
  retardo=0.0 s: sobreimpulso=    0.0 % | asentamiento 2 %= 12.11 s | ¿se asienta al final?: True
  retardo=0.5 s: sobreimpulso=   18.2 % | asentamiento 2 %= 13.49 s | ¿se asienta al final?: True
  retardo=1.0 s: sobreimpulso=   48.1 % | asentamiento 2 %= 34.73 s | ¿se asienta al final?: True
  retardo=2.0 s: sobreimpulso= 9999.0 % | asentamiento 2 %=120.00 s | ¿se asienta al final?: False

=== 10. Ajuste manual paso a paso (una ganancia cada vez) ===
  1. solo P, Kp=1              subida10-90=   nan s | sobreimpulso=   0.0 % | asentamiento 2 %=100.00 s | error final= 0.5000
  2. P más fuerte, Kp=2        subida10-90=   nan s | sobreimpulso=   0.0 % | asentamiento 2 %=100.00 s | error final= 0.3333
  3. añadir I suave, Ki=0,2    subida10-90=  1.97 s | sobreimpulso=   0.0 % | asentamiento 2 %= 38.21 s | error final= 0.0003
  4. subir I, Ki=0,5           subida10-90=  1.65 s | sobreimpulso=  16.1 % | asentamiento 2 %= 14.14 s | error final= 0.0000
  5. añadir D, Kd=1            subida10-90=  1.98 s | sobreimpulso=   0.0 % | asentamiento 2 %= 12.11 s | error final= 0.0000
  6. subir I con D, Ki=0,8     subida10-90=  1.69 s | sobreimpulso=   8.4 % | asentamiento 2 %=  7.15 s | error final= 0.0000

fin
```

## Fuente: lab_pid.cpp

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// Misma planta y mismo paso que lab_pid.py: G(s) = 1/(s+1)^3, Euler, dt = 2 ms.
struct Planta {
    double x[3] = {0, 0, 0};
    double paso(double u, double dt) {
        double e = u;
        for (int i = 0; i < 3; ++i) {
            x[i] += dt * (e - x[i]);
            e = x[i];
        }
        return x[2];
    }
};

class PID {
public:
    PID(double kp, double ki, double kd, double tau) : kp_(kp), ki_(ki), kd_(kd), tau_(tau) {}
    double paso(double ref, double y, double dt) {
        double e = ref - y;
        double raw = (e - prev_) / dt;
        prev_ = e;
        double a = dt / (tau_ + dt);
        dfilt_ += a * (raw - dfilt_);
        i_ += ki_ * e * dt;
        return kp_ * e + i_ + kd_ * dfilt_;
    }
private:
    double kp_, ki_, kd_, tau_;
    double i_ = 0, prev_ = 0, dfilt_ = 0;
};

int main() {
    const double dt = 0.002;
    const int n = static_cast<int>(100.0 / dt);
    Planta p;
    PID pid(2.0, 0.5, 1.0, 0.05);
    std::vector<double> t(n), ys(n);
    double y = 0;
    for (int k = 0; k < n; ++k) {
        double u = pid.paso(1.0, y, dt);
        y = p.paso(u, dt);
        t[k] = k * dt;
        ys[k] = y;
    }
    double pico = *std::max_element(ys.begin(), ys.end());
    double t10 = 0, t90 = 0, asent = 0;
    for (int k = 0; k < n; ++k) {
        if (t10 == 0 && ys[k] >= 0.1) t10 = t[k];
        if (t90 == 0 && ys[k] >= 0.9) t90 = t[k];
        if (std::fabs(ys[k] - 1.0) > 0.02) asent = t[k];
    }
    std::printf("C++ PID(2; 0,5; 1; tau=0,05) sobre 1/(s+1)^3:\n");
    std::printf("  subida10-90=%.2f s | sobreimpulso=%.1f %% | asentamiento 2 %%=%.2f s | valor final=%.4f\n",
                t90 - t10, std::max(0.0, (pico - 1.0) * 100), asent, ys[n - 1]);
    return 0;
}
```

## Salida de lab_pid.cpp

```text
C++ PID(2; 0,5; 1; tau=0,05) sobre 1/(s+1)^3:
  subida10-90=1.98 s | sobreimpulso=0.0 % | asentamiento 2 %=12.11 s | valor final=1.0000
```
