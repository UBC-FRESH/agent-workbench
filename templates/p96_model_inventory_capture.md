# P96 Model Inventory Capture

Use this template to capture model availability evidence for P96.3 when using
remote Ollama via the VS Code Copilot Chat provider picker.

## Capture Context

- Phase: P96
- Parent issue: #585
- Child issue: #588
- Capture timestamp (UTC):
- Captured by:
- VS Code workspace:

## Capture Method

1. Open Copilot Chat in VS Code.
2. Open provider/model picker.
3. Select provider `ollama`.
4. Record the visible model list exactly as shown.

## Visible Ollama Models

- 

## Required Lane Check

- Baseline required: `qwen3.6:35b-a3b-bf16`
  - Present: yes/no
- Candidate required: `qwen3.6:35b-a3b-q8_0`
  - Present: yes/no

## Evidence Attachments

- Screenshot path(s):
- Text export path (if available):

## Notes

- If either required model is missing, P96.3 remains blocked and issue #588
  should carry the blocker note plus this capture artifact.
- If both required models are present, proceed to bounded run execution using
  `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`.
