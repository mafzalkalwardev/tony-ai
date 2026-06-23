from __future__ import annotations

import re


class CommandNormalizer:
    """Normalize Tony's mixed-language commands into stable internal phrases."""

    _ASSISTANT_PREFIXES = (
        "wake up tony daddy home",
        "wake up tony daddy's home",
        "wake up tony",
        "wake up, tony",
        "hey tony",
        "tony",
    )

    def normalize(self, text: str) -> str:
        cleaned = self._clean(text)
        if not cleaned:
            return ""

        for pattern, replacement in self._phrase_rules():
            if re.search(pattern, cleaned):
                return replacement

        cleaned = self._replace_words(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _clean(self, text: str) -> str:
        cleaned = text.strip().lower()
        cleaned = cleaned.replace("’", "'").replace("“", "").replace("”", "")
        cleaned = cleaned.replace(",", " ").replace("!", " ").replace("?", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        for prefix in self._ASSISTANT_PREFIXES:
            if cleaned == prefix:
                return ""
            if cleaned.startswith(prefix + " "):
                cleaned = cleaned[len(prefix) :].strip()
                break
        return cleaned

    def _phrase_rules(self) -> tuple[tuple[str, str], ...]:
        return (
            (r"\b(screen|meri screen)\s+(dekho|observe|dekh)\b|\blook at (my )?screen\b", "observe screen"),
            (r"\bkya\s+issue\s+hai\s+screen\b|\bscreen\b.*\b(issue|problem|masla|analy[sz]e)\b|\banaly[sz]e\s+screen\b", "analyze screen"),
            (r"\bdescribe\s+screen\b|\bscreen\s+summary\b", "describe screen"),
            (r"\bobserve\s+mode\b.*\b(start|on|karo)\b", "start observe mode"),
            (r"\bobserve\b.*\b(band|stop|off)\b|\bobserve\s+mode\b.*\b(stop|off|band)\b", "stop observe mode"),
            (r"\bwatch me\b|\bmujhe\s+dekh\s+ke\s+seekho\b|\blearn this workflow\b|\brecord this process\b", "start teach mode"),
            (r"\bteach\b.*\b(stop|band|off)\b|\bstop\s+teach\b", "stop teach mode"),
            (r"\bye\s+(steps|workflow)\s+yaad\s+rakho\b|\bworkflow\s+save\b|\bsave\s+workflow\b", "save workflow"),
            (r"\bdiscard\s+workflow\b|\bworkflow\s+discard\b", "discard workflow"),
            (r"\bworkflows?\s+(dikhao|show|list)\b|\blist\s+workflows?\b", "list workflows"),
            (r"\bpreview\s+workflow\b|\bworkflow\s+preview\b", "preview workflow"),
            (r"\blast\s+workflow\s+replay\b|\bworkflow\s+replay\b|\breplay\s+workflow\b", "replay workflow"),
            (r"\bdry\s+run\b|\bdry\s+run\s+workflow\b", "dry run workflow"),
            (r"\breplay\b.*\b(stop|band|off)\b|\bstop\s+replay\b", "stop replay"),
            (r"\bsummarize\s+workflow\b|\bworkflow\s+summary\b", "summarize workflow"),
            (r"\b(repo|git)\s+status\b|\bstatus\s+(dikhao|show|batao)\b", "repo status"),
            (r"\bgit\s+diff\b|\brepo\s+diff\b", "git diff"),
            (r"\bgit\s+log\b|\brepo\s+log\b", "git log"),
            (r"\bgit\s+push\b|\bpush\s+karo\b", "git push"),
            (r"\bgit\s+commit\b|\bcommit\s+karo\b", "git commit"),
            (r"\b(vs code|vscode|visual studio code).*(kholo|khol|open)\b|\b(kholo|khol|open).*(vs code|vscode|visual studio code)\b", "open vscode"),
            (r"\bterminal\b.*\b(kholo|khol|open)\b|\b(kholo|khol|open)\b.*\bterminal\b", "open terminal"),
            (r"\b(file explorer|explorer)\b.*\b(kholo|khol|open)\b|\b(kholo|khol|open)\b.*\b(file explorer|explorer)\b", "open file explorer"),
            (r"\bproject\b.*\b(run|chalao|start)\b|\b(run|chalao|start)\b.*\bproject\b", "run project"),
            (r"\b(test|tests)\b.*\b(run|chalao)\b|\b(run|chalao)\b.*\b(test|tests)\b", "run tests"),
            (r"\b(project\s+analy[sz]e|analy[sz]e\s+project|project\s+check|error\s+check|masla|issue)\b", "analyze project"),
            (r"\bscreen\s+record\b|\bscreen\s+recording\s+start\b|\brecord\s+karo\b", "start screen recording"),
            (r"\b(actions?|macro)\s+record\b|\bmeri\s+actions?\s+record\b", "start action recording"),
            (r"\brecording\s+(band|stop)\b|\bstop\s+recording\b", "stop recording"),
            (r"\b(last\s+)?(macro|actions?)\s+replay\b|\breplay\s+(macro|actions?)\b|\breplay\s+karo\b", "replay macro"),
            (r"\bscreenshot\b|\bscreen\s+shot\b", "take screenshot"),
            (r"(?<!\w)\.env(?!\w).*\b(read|parho|parhna)\b|\b(read|parho|parhna)\b.*(?<!\w)\.env(?!\w)", "read .env"),
            (r"\bdot\s+env\b.*\b(read|parho|parhna)\b|\b(read|parho|parhna)\b.*\bdot\s+env\b", "read .env"),
            (r"\b(read|parho|parhna)\b", "read file"),
            (r"\b(file\s+banao|create\s+file|new\s+file|nayi\s+file)\b", "create file"),
            (r"\b(client\s+message|client\s+ko|update\s+message)\b", "client message"),
            (r"\bmessage\s+banao\b", "message"),
            (r"\bdelivery\s+(note|report)\b", "delivery note"),
            (r"\bdaily\s+report\b|\baaj\s+ka\s+kaam\s+summarize\b", "daily report"),
            (r"\bcodex\b.*\bprompt\b|\bprompt\b.*\bcodex\b", "codex prompt"),
            (r"\bwake\s+mode\b.*\b(on|start|enable)\b", "start wake mode"),
            (r"\bwake\s+mode\b.*\b(off|stop|disable|band)\b", "stop wake mode"),
            (r"\bpush\s+to\s+talk\b|\bvoice\s+input\b", "push to talk"),
            (r"\bstop\s+task\b|\bstop\s+tony\b", "stop task"),
            (r"\bgithub\s+status\b", "github status"),
            (r"\b(issues|github\s+issues)\b.*\b(list|dikhao|show)?\b", "list issues"),
            (r"\b(prs|pull requests|github\s+prs)\b.*\b(list|dikhao|show)?\b", "list prs"),
        )

    def _replace_words(self, text: str) -> str:
        replacements = (
            (" dikhao", " show"),
            (" batao", " tell"),
            (" kholo", " open"),
            (" khol", " open"),
            (" chalao", " run"),
            (" start karo", " start"),
            (" band karo", " stop"),
            (" check karo", " analyze"),
            (" parho", " read"),
            (" parhna", " read"),
            (" bhejo", " send"),
            (" banao", " create"),
        )
        cleaned = f" {text} "
        for old, new in replacements:
            cleaned = cleaned.replace(old, new)
        return cleaned.strip()
