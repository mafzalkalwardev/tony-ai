# Live Voice

Tony V4 adds optional live voice and wake mode architecture.

## Wake Phrases

```text
Wake Up, Tony!
Wake up Tony, Daddy's Home
```

Tony tries to use `openwakeword` when available. If the model is missing, Tony falls back to conservative phrase matching after transcription. This fallback is useful but not perfect.

## Push-To-Talk

Push-to-talk remains the recommended reliable mode. Click `Push to Talk`, speak, and Tony shows:

```text
You said: [transcript]
```

Tony auto-runs only clearly safe commands when settings allow it.

## Live Mode

Live mode is disabled by default. Use the UI toggle or:

```text
Tony live listening start karo
Wake mode on karo
```

Tony listens after wake, shows audio waves, transcribes, classifies safety, and then runs, asks approval, or blocks.

## Voice Safety

Voice transcription can make mistakes, especially with Urdu, Hindi, Roman Urdu, and Hinglish. Risky commands still require confirmation. Blocked commands stay blocked.

## Troubleshooting

- Check microphone permission in Windows.
- Install `requirements.txt`.
- Use push-to-talk if live wake mode is unreliable.
- Keep `live_voice_enabled` and `wake_mode_enabled` false to disable live voice.

