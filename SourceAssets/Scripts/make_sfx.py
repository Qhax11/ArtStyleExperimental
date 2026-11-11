"""Synthesises the game's cute sound effects (numpy only) and a page to listen to them.

  python make_sfx.py <out_dir>
Writes <out_dir>/SFX_<Name>.wav (44.1 kHz, 16-bit mono) and <out_dir>/preview.html.
Every wardrobe tab gets its own put-on and take-off sound: putting on rises and sparkles,
taking off falls and is softer. Notes stay in C major pentatonic so everything sounds together.
"""
import base64
import io
import os
import sys
import wave

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)


def note(name):
    """'C5' -> Hz."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    semis = names[name[0]] + (1 if "#" in name else 0)
    octave = int(name[-1])
    return 440.0 * 2 ** ((semis + 12 * (octave + 1) - 69) / 12)


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def env(n, attack, decay_rate):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t * decay_rate)


def bell(f, dur=0.8, amp=1.0, bright=1.0):
    """Soft glockenspiel / music box: inharmonic partials, higher ones die faster."""
    t = t_axis(dur)
    out = np.zeros_like(t)
    for ratio, a, d in ((1.0, 1.0, 5.0), (2.76, 0.45 * bright, 9.0), (5.4, 0.2 * bright, 16.0), (8.9, 0.08 * bright, 26.0)):
        if f * ratio > 15000:  # above this it only adds a harsh, aliased edge
            continue
        out += a * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * d)
    out *= np.clip(t / 0.003, 0, 1)
    tail = min(len(t), int(SR * 0.05))
    out[-tail:] *= np.linspace(1, 0, tail)
    return amp * out


def pluck(f, dur=0.7, amp=1.0, soft=0.5):
    """Karplus-Strong harp string."""
    n = int(SR * dur)
    period = int(SR / f)
    buf = RNG.uniform(-1, 1, period)
    # Lowpass the excitation for a rounder, cuter pluck.
    for _ in range(int(1 + soft * 4)):
        buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        j = i % period
        buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % period])
    out *= env(n, 0.002, 3.0)
    tail = int(SR * 0.05)
    out[-tail:] *= np.linspace(1, 0, tail)
    return amp * out


def bubble(f0, f1, dur=0.09, amp=1.0):
    """Water-drop pop: a sine gliding from f0 to f1 with a quick fade."""
    t = t_axis(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(phase) * np.sin(np.pi * t / dur) ** 1.5


def band_noise(dur, f_from, f_to, width=0.6, amp=1.0, attack=0.02, shape=2.0):
    """Fabric swish: noise through a band that sweeps from f_from to f_to (frame-wise FFT)."""
    n = int(SR * dur)
    noise = RNG.normal(0, 1, n + 2048)
    frame, hop = 1024, 256
    win = np.hanning(frame)
    out = np.zeros(n + 2048)
    freqs = np.fft.rfftfreq(frame, 1 / SR)
    for start in range(0, n, hop):
        p = start / max(n - 1, 1)
        centre = f_from * (f_to / f_from) ** p
        spec = np.fft.rfft(noise[start:start + frame] * win)
        gain = np.exp(-0.5 * (np.log(np.maximum(freqs, 1) / centre) / width) ** 2)
        out[start:start + frame] += np.fft.irfft(spec * gain) * win
    out = out[:n]
    t = np.arange(n) / SR
    shape_env = np.clip(t / attack, 0, 1) * (1 - t / dur) ** shape
    out *= shape_env
    return amp * out / (np.abs(out).max() + 1e-9)


def tap(f, amp=1.0):
    """Little wooden heel tap."""
    t = t_axis(0.12)
    body = np.sin(2 * np.pi * f * t) * np.exp(-t * 45)
    click = RNG.normal(0, 1, len(t)) * np.exp(-t * 400) * 0.35
    return amp * (body + click)


def mix(length, *parts):
    """parts: (start_seconds, signal). Grows past `length` so no part is cut off (a cut clicks)."""
    end = max([int(SR * length)] + [int(SR * start) + len(sig) for start, sig in parts])
    out = np.zeros(end)
    for start, sig in parts:
        i = int(SR * start)
        out[i:i + len(sig)] += sig
    return out


def reverb(sig, amount=0.18, length=0.6):
    """Small room: convolve with decaying, lowpassed noise."""
    n = int(SR * length)
    ir = RNG.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 7.0)
    ir = np.convolve(ir, np.ones(8) / 8, mode="same")
    ir[0] = 0
    wet = np.fft.irfft(np.fft.rfft(sig, len(sig) + n) * np.fft.rfft(ir, len(sig) + n))[:len(sig) + n]
    dry = np.concatenate([sig, np.zeros(n)])
    out = dry + amount * wet / (np.abs(wet).max() + 1e-9) * np.abs(sig).max()
    # Trim the silent tail.
    idx = np.nonzero(np.abs(out) > 1e-3 * np.abs(out).max())[0]
    return out[:idx[-1] + 1] if len(idx) else out


def finish(sig, loudness=0.1, ceiling=0.9):
    """Same perceived level for every sound (RMS of the loud part), soft-limited peaks."""
    sig = sig - sig.mean()
    fade = int(SR * 0.01)
    sig[-fade:] *= np.linspace(1, 0, fade)
    loud = np.abs(sig) > 0.05 * np.abs(sig).max()
    rms = np.sqrt(np.mean(sig[loud] ** 2)) if loud.any() else 1.0
    sig = sig * (loudness / rms)
    return ceiling * np.tanh(sig / ceiling)


def sparkle(start, count, notes, gap, amp):
    return [(start + i * gap, bell(note(notes[i % len(notes)]), 0.5, amp * (0.8 ** i), 0.6)) for i in range(count)]


SOUNDS = {
    # Top: light swish up, a bubble pop and a bright little bell.
    "Top_On": lambda: mix(0.9, (0, band_noise(0.2, 1500, 5000, amp=0.35)),
                          (0.1, bubble(500, 1300, 0.08, 0.6)), (0.14, bell(note("E6"), 0.7, 0.55))),
    "Top_Off": lambda: mix(0.8, (0, band_noise(0.2, 4500, 1500, amp=0.3)),
                           (0.08, bubble(1100, 450, 0.09, 0.45)), (0.12, bell(note("C6"), 0.6, 0.3, 0.5))),
    # Bottom: lower, longer swish and a two-note harp step up.
    "Bottom_On": lambda: mix(1.0, (0, band_noise(0.26, 800, 2800, amp=0.35)),
                             (0.12, pluck(note("G4"), 0.6, 0.55)), (0.22, pluck(note("C5"), 0.7, 0.6))),
    "Bottom_Off": lambda: mix(0.9, (0, band_noise(0.26, 2600, 800, amp=0.3)),
                              (0.1, pluck(note("C5"), 0.5, 0.4)), (0.2, pluck(note("G4"), 0.6, 0.4))),
    # Dress: a twirl and a harp arpeggio with a sparkle tail, the biggest one.
    "Dress_On": lambda: mix(1.6, (0, band_noise(0.45, 900, 4500, width=0.8, amp=0.32, attack=0.06)),
                            *[(0.08 + i * 0.07, pluck(note(n), 0.8, 0.5)) for i, n in enumerate(("C5", "E5", "G5", "C6"))],
                            *sparkle(0.42, 4, ("E7", "C7", "G6", "A6"), 0.06, 0.25)),
    "Dress_Off": lambda: mix(1.2, (0, band_noise(0.4, 4000, 900, width=0.8, amp=0.28, attack=0.04)),
                             *[(0.06 + i * 0.07, pluck(note(n), 0.6, 0.38)) for i, n in enumerate(("C6", "G5", "E5", "C5"))]),
    # Shoes: tap-tap of heels, then a tiny ding.
    "Shoes_On": lambda: mix(0.8, (0, tap(900, 0.7)), (0.11, tap(1200, 0.7)), (0.2, bell(note("G6"), 0.5, 0.35))),
    "Shoes_Off": lambda: mix(0.5, (0, tap(1150, 0.55)), (0.11, tap(850, 0.5))),
    # Hair: a soft airy fluff and a music-box run up.
    "Hair_On": lambda: mix(1.0, (0, band_noise(0.35, 2500, 6000, width=1.0, amp=0.22, attack=0.08, shape=1.2)),
                           *[(0.06 + i * 0.05, bell(note(n), 0.5, 0.4, 0.4)) for i, n in enumerate(("C6", "D6", "E6", "G6"))]),
    "Hair_Off": lambda: mix(0.9, (0, band_noise(0.3, 5500, 2500, width=1.0, amp=0.2, attack=0.06, shape=1.2)),
                            *[(0.05 + i * 0.05, bell(note(n), 0.45, 0.3, 0.4)) for i, n in enumerate(("G6", "E6", "D6", "C6"))]),
    # Accessory: a glassy twinkle.
    "Accessory_On": lambda: mix(1.0, (0, bell(note("A6"), 0.8, 0.6, 1.2)),
                                *sparkle(0.07, 3, ("E7", "G7", "C8"), 0.05, 0.3)),
    "Accessory_Off": lambda: mix(0.8, (0, bell(note("E6"), 0.6, 0.45, 0.8)), (0.09, bell(note("C6"), 0.6, 0.35, 0.6))),
    # Interface.
    # Wardrobe tab: a soft wooden "tok" with a hint of paper.
    "UI_Tab": lambda: mix(0.3, (0, bubble(420, 620, 0.06, 0.8)), (0, band_noise(0.05, 3000, 2000, amp=0.15, attack=0.003))),
    # Colour swatch: a little bloop with a high sparkle.
    "UI_Color": lambda: mix(0.6, (0, bubble(650, 1250, 0.07, 0.8)), (0.05, bell(note("E7"), 0.4, 0.18, 0.4))),
    # Any other button: the softest pop.
    "UI_Click": lambda: mix(0.2, (0, bubble(380, 560, 0.045, 0.7))),
    # Finish: harp run up and a shower of sparkles.
    "Finish": lambda: mix(2.2, *[(i * 0.08, pluck(note(n), 1.0, 0.5)) for i, n in enumerate(("C5", "E5", "G5", "C6", "E6"))],
                          (0.4, bell(note("G6"), 1.2, 0.45)),
                          *sparkle(0.48, 7, ("E7", "C7", "G7", "A6", "D7", "C8", "G6"), 0.07, 0.3)),
    # Photo: a camera shutter, "ch-chk", then a tiny ding.
    "Photo": lambda: mix(0.8, (0, band_noise(0.03, 3500, 2500, width=0.5, amp=0.9, attack=0.001, shape=3)),
                         (0.008, tap(2200, 0.35)),
                         (0.075, band_noise(0.04, 2200, 1500, width=0.5, amp=0.7, attack=0.001, shape=3)),
                         (0.08, tap(1500, 0.3)), (0.18, bell(note("C7"), 0.5, 0.2, 0.4))),
}

# Perceived level of each sound (RMS of its loud part). Taking off sits below putting on,
# interface clicks below both, the finish fanfare on top.
LOUDNESS = {"UI_Tab": 0.06, "UI_Color": 0.06, "UI_Click": 0.05, "Finish": 0.12, "Photo": 0.09}


def to_wav_bytes(sig):
    pcm = (np.clip(sig, -1, 1) * 32767).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)
    return buf.getvalue()


LABELS = {"Top": "Üst", "Bottom": "Alt", "Dress": "Elbise", "Shoes": "Ayakkabı", "Hair": "Saç", "Accessory": "Aksesuar"}


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for name, make in SOUNDS.items():
        loudness = LOUDNESS.get(name, 0.08 if name.endswith("_Off") else 0.11)
        data = to_wav_bytes(finish(reverb(make()), loudness=loudness))
        open(os.path.join(out_dir, f"SFX_{name}.wav"), "wb").write(data)
        rows.append((name, base64.b64encode(data).decode()))
        print("SFX", name, f"{len(data) / 2 / SR:.2f}s")
    cells = []
    for cat, label in LABELS.items():
        on = next(b for n, b in rows if n == f"{cat}_On")
        off = next(b for n, b in rows if n == f"{cat}_Off")
        cells.append(f'<div class="row"><span>{label}</span>'
                     f'<button onclick="play(\'{cat}_On\')">Giy</button>'
                     f'<button class="off" onclick="play(\'{cat}_Off\')">Çıkar</button></div>')
    for key, label in (("UI_Tab", "Sekme"), ("UI_Color", "Renk"), ("UI_Click", "Düğme"), ("Finish", "Bitir"), ("Photo", "Fotoğraf")):
        cells.append(f'<div class="row"><span>{label}</span><button onclick="play(&quot;{key}&quot;)">Çal</button></div>')
    audio = "".join(f'<audio id="{n}" src="data:audio/wav;base64,{b}"></audio>' for n, b in rows)
    html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Dolap sesleri</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{background:#f2c5d4;font-family:Segoe UI,sans-serif;color:#6e1e3e;display:flex;justify-content:center;padding:24px}}
.card{{background:#fbe6ee;border:3px solid #a93f6c;border-radius:24px;padding:20px 28px;min-width:300px}}
h1{{margin:0 0 12px;font-size:26px}} .row{{display:flex;align-items:center;gap:10px;margin:10px 0}}
.row span{{width:90px;font-weight:600}} button{{background:#a93f6c;color:#fff;border:0;border-radius:14px;padding:8px 16px;font-size:15px;cursor:pointer}}
button.off{{background:#d98aa8}} button:active{{transform:scale(.95)}}
</style></head><body><div class="card"><h1>Dolap sesleri</h1>{''.join(cells)}</div>{audio}
<script>function play(n){{const a=document.getElementById(n);a.currentTime=0;a.play();}}</script></body></html>"""
    open(os.path.join(out_dir, "preview.html"), "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    main()
