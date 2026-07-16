# Diagnostic Decision Template

## Pattern Match Result

| Pattern | Match? | Evidence |
|---------|--------|----------|
| Large arena + short subheap | {Y/N} | {evidence} |
| Many small arenas | {Y/N} | {evidence} |
| Huge top chunk | {Y/N} | {evidence} |
| Corrupted arena | {Y/N} | {evidence} |
| No symbols | {Y/N} | {evidence} |

## Diagnosis

- **Root cause**: {cause}
- **Memory source**: {subheap|direct mmap|mixed}
- **Severity**: {normal|suspicious|abnormal|corrupted}

## Recommended Next Step

{action}
