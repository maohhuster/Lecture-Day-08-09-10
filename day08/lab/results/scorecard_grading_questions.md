# Scorecard — Grading Questions
Generated: 2026-04-13 17:54

## Config
```
retrieval_mode = "hybrid"
top_k_search = 10
top_k_select = 3
use_rerank = True
embedding_provider = "hash"
```

## Summary

- Average Context Recall (expected_sources): **0.83**
- Answered (non-abstain): **6/10**
- Abstain: **4/10**

## Per-question

| ID | Pts | Category | Answered? | Abstain? | Context recall | Missing expected sources | Retrieved sources |
|----|-----|----------|----------|----------|---------------|--------------------------|------------------|
| gq01 | 10 | SLA | Yes | No | 1.00 |  | support/helpdesk-faq.md, support/sla-p1-2026.pdf |
| gq02 | 10 | Cross-Document | Yes | No | 0.50 | hr/leave-policy-2026.pdf | support/helpdesk-faq.md, support/sla-p1-2026.pdf |
| gq03 | 10 | Refund | Yes | No | 1.00 |  | policy/refund-v4.pdf |
| gq04 | 8 | Refund | No | Yes | 1.00 |  | policy/refund-v4.pdf |
| gq05 | 10 | Access Control | Yes | No | 1.00 |  | it/access-control-sop.md, support/helpdesk-faq.md |
| gq06 | 12 | Cross-Document | Yes | No | 1.00 |  | it/access-control-sop.md, support/sla-p1-2026.pdf |
| gq07 | 10 | Insufficient Context | No | Yes | N/A |  | support/helpdesk-faq.md, support/sla-p1-2026.pdf |
| gq08 | 10 | HR Policy | No | Yes | 0.00 | hr/leave-policy-2026.pdf | policy/refund-v4.pdf, support/helpdesk-faq.md, support/sla-p1-2026.pdf |
| gq09 | 8 | IT Helpdesk | No | Yes | 1.00 |  | it/access-control-sop.md, policy/refund-v4.pdf, support/helpdesk-faq.md |
| gq10 | 10 | Refund | Yes | No | 1.00 |  | policy/refund-v4.pdf |

## Notes

- Đây là scorecard **tự động** dựa trên `expected_sources` và `logs/grading_run.json` (không chấm Full/Partial theo rubric vì cần judge/human).
- Các câu abstain nhưng có expected_sources thường là dấu hiệu **retrieval/select chưa kéo đúng chunk** hoặc **prompt chưa ép trả lời số liệu**.
