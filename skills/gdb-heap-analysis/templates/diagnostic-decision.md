# Diagnostic Decision Template

## Pattern Match Result

| Pattern | Match? | Evidence |
|---------|--------|----------|
| Large arena + short subheap | {Y/N} | {evidence} |
| Many small arenas | {Y/N} | {evidence} |
| Huge top chunk | {Y/N} | {evidence} |
| Corrupted arena | {Y/N} | {evidence} |
| No symbols | {Y/N} | {evidence} |
| Same-size mass leak（Pattern 6） | {Y/N} | {evidence} |
| gcore live snapshot（Pattern 7） | {Y/N} | {evidence} |
| Zero/reserved mappings（Pattern 8） | {Y/N} | {evidence} |

## Diagnosis

- **Root cause**: {cause}
- **Memory source**: {subheap|direct mmap|mixed}
- **Severity**: {normal|suspicious|abnormal|corrupted}

## Recommended Next Step

{action}
