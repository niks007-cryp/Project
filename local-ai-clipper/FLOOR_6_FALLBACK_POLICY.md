# FLOOR 6 FALLBACK POLICY — GPU & CPU RENDERING

## Fallback Strategy Hierarchy

```text
Attempt Hardware-Accelerated Rendering (NVENC / QSV / AMF)
                           │
             ┌─────────────┴─────────────┐
             │                           │
          Success                     Failure
             │                           │
   Record Backend: GPU           Log Diagnostic Warning
                                         │
                                         ▼
                            Fallback to CPU Software Rendering
                                    (libx264 / aac)
                                         │
                           ┌─────────────┴─────────────┐
                           │                           │
                        Success                     Failure
                           │                           │
                 Record Backend: CPU          Raise SystemError
             Record Fallback Reason           Mark RenderJob FAILED
```

## Non-Negotiable Rules
- Software CPU rendering (`libx264`) MUST be supported on every host system.
- Provenance metadata MUST accurately record `render_backend = "GPU"` or `render_backend = "CPU"`.
