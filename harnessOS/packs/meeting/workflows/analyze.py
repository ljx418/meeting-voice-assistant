"""Meeting analysis workflow step contract."""

CONNECTOR_ID = "meeting_voice_mcp"
CAPABILITY = "meeting.analyze"
INPUT_KIND = "transcript"
OUTPUT_KINDS = ("analysis", "result")
