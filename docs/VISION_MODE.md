# Vision Mode

Tony V6 can capture and summarize basic screen context only after approval.

## What Tony Can See

- Active window title when Windows exposes it
- Foreground process name when detectable
- Screenshot dimensions
- Local screenshot path
- Optional OCR text if `ocr_enabled` is true and local OCR tools are installed

Tony does not pretend to understand more than the local tools provide. If no local vision model is configured, Tony says advanced visual understanding is not ready yet.

## Storage

Screenshots are saved locally under:

```text
tony/logs/screenshots/
```

Tony does not upload screenshots or send them to paid/cloud APIs.

## Safety

Tony requires approval before screen observe or screenshot analysis. Tony refuses or stops when the screen appears to contain passwords, banking/payment content, OTP/2FA, `.env`, secrets, tokens, or private messaging/send screens.
