set windows-shell := ["powershell"]

root := "src.app"

run:
	uv run -m {{root}}

debug:
	uv run -m {{root}} --debug
