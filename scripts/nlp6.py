import threading
import sys

try:
    import pyaudio
    import numpy as np
    import matplotlib.pyplot as plt
    import speech_recognition as sr
    from speech_recognition import AudioData
except ImportError as e:
    print(f"Missing library: {e.name}")
    print("\nInstall:")
    print("Windows: pip install SpeechRecognition pyaudio numpy matplotlib")
    print("macOS:   brew install portaudio && pip install SpeechRecognition pyaudio numpy matplotlib")
    sys.exit(1)

stop_event = threading.Event()


def wait_for_enter():
    input()
    stop_event.set()


def record_audio(label):
    stop_event.clear()

    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    frames = []

    print(f"\n🎙️ {label}")
    print("   Press Enter to stop...")

    threading.Thread(
        target=wait_for_enter,
        daemon=True
    ).start()

    print("🔴 Recording", end="", flush=True)

    while not stop_event.is_set():
        frames.append(
            stream.read(
                1024,
                exception_on_overflow=False
            )
        )
        print(".", end="", flush=True)

    print(" ✅")

    stream.stop_stream()
    stream.close()

    width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()

    return b"".join(frames), 16000, width


def analyze_audio(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)

    if len(samples) == 0:
        return {
            "duration": 0,
            "avg_volume": 0,
            "max_volume": 0,
            "samples": samples
        }

    return {
        "duration": len(samples) / rate,
        "avg_volume": float(np.mean(np.abs(samples))),
        "max_volume": int(np.max(np.abs(samples))),
        "samples": samples
    }


def transcribe(data, rate, width):
    recognizer = sr.Recognizer()

    try:
        audio = AudioData(data, rate, width)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Could not understand speech]"
    except sr.RequestError as e:
        return f"[Speech service error: {e}]"
    except Exception as e:
        return f"[Transcription error: {e}]"


def display_stats(stats, text, label):
    print("\n" + "-" * 40)
    print(f"🎤 {label}")
    print("-" * 40)

    print(f"⏱️  Duration:       {stats['duration']:.2f} seconds")
    print(f"🔊 Avg Amplitude:  {stats['avg_volume']:.0f}")
    print(f"📈 Max Amplitude:  {stats['max_volume']:.0f}")
    print(f"📝 Transcription:  {text}")


def compare(stats1, stats2):
    print("\n" + "=" * 40)
    print("📊 COMPARISON RESULTS")
    print("=" * 40)

    # Duration
    if stats1["duration"] > stats2["duration"]:
        longer = "Recording 1"
        if stats2["duration"] > 0:
            diff = (
                (stats1["duration"] - stats2["duration"])
                / stats2["duration"]
            ) * 100
        else:
            diff = 0
    else:
        longer = "Recording 2"
        if stats1["duration"] > 0:
            diff = (
                (stats2["duration"] - stats1["duration"])
                / stats1["duration"]
            ) * 100
        else:
            diff = 0

    print(f"⏱️  {longer} is longer by {diff:.1f}%")

    # Volume
    if stats1["avg_volume"] > stats2["avg_volume"]:
        louder = "Recording 1"
        if stats2["avg_volume"] > 0:
            diff = (
                (stats1["avg_volume"] - stats2["avg_volume"])
                / stats2["avg_volume"]
            ) * 100
        else:
            diff = 0
    else:
        louder = "Recording 2"
        if stats1["avg_volume"] > 0:
            diff = (
                (stats2["avg_volume"] - stats1["avg_volume"])
                / stats1["avg_volume"]
            ) * 100
        else:
            diff = 0

    print(f"🔊 {louder} has higher average amplitude by {diff:.1f}%")


def plot_both(stats1, stats2, rate):
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(12, 6)
    )

    # Recording 1
    samples1 = stats1["samples"]
    t1 = np.arange(len(samples1)) / rate

    ax1.plot(
        t1,
        samples1,
        linewidth=0.5
    )

    ax1.set_title(
        f"Recording 1 - {stats1['duration']:.2f}s | "
        f"Avg amplitude: {stats1['avg_volume']:.0f}"
    )

    ax1.set_ylabel("Amplitude")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-35000, 35000)

    # Recording 2
    samples2 = stats2["samples"]
    t2 = np.arange(len(samples2)) / rate

    ax2.plot(
        t2,
        samples2,
        linewidth=0.5
    )

    ax2.set_title(
        f"Recording 2 - {stats2['duration']:.2f}s | "
        f"Avg amplitude: {stats2['avg_volume']:.0f}"
    )

    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-35000, 35000)

    plt.tight_layout()
    plt.show()


def main():
    print("=" * 40)
    print("🎙️ VOICE ANALYSIS LAB")
    print("=" * 40)
    print("Record twice and compare your voice!")

    # Recording 1
    audio1, rate, width = record_audio(
        "Recording 1: Speak NORMALLY"
    )

    stats1 = analyze_audio(audio1, rate)
    text1 = transcribe(audio1, rate, width)

    display_stats(
        stats1,
        text1,
        "Recording 1 Results"
    )

    # Recording 2
    input(
        "\n🎙️ Press Enter, then speak LOUDER or FASTER..."
    )

    audio2, rate, width = record_audio(
        "Recording 2: CHANGE your voice!"
    )

    stats2 = analyze_audio(audio2, rate)
    text2 = transcribe(audio2, rate, width)

    display_stats(
        stats2,
        text2,
        "Recording 2 Results"
    )

    # Compare
    compare(stats1, stats2)

    # Plot
    plot_both(
        stats1,
        stats2,
        rate
    )


if __name__ == "__main__":
    main()