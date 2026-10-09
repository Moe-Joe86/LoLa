"""Startet speech-to-speech unverändert, lädt aber vorher Silero und stellt danach die Thread-Zahl zurück.

Grund: Das Silero-Modul setzt beim ersten Laden `torch.set_num_threads(1)` für das ganze Programm; Parakeet
rechnet danach mit einem Kern. Hier wird Silero zuerst geladen, die Thread-Zahl zurückgestellt und erst dann
speech-to-speech im selben Programm gestartet. Am Code von speech-to-speech ändert das nichts.
Wird von `lola_start` mit der Umgebung von speech-to-speech aufgerufen (dort sind torch und speech_to_speech
installiert, im Repo nicht): python sprachkette_start.py serve <Schalter wie bei speech-to-speech>
"""

import sys

import torch

kerne = torch.get_num_threads()
torch.hub.load("snakers4/silero-vad:master", "silero_vad", trust_repo=True, skip_validation=True)
torch.set_num_threads(kerne)

from speech_to_speech.cli import main  # noqa: E402

sys.exit(main())
