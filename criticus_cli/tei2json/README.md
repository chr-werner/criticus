# tei2json cli tool

## Usage

The example dir tree looks like
```txt
.
|- nt-transcripts
|     |- ntvmr        # transcripts by the intf muenster
|     -- igntp        # transcripts by the igntp birmingham
|- json               # json files
-- criticus_cli       # containing scripts 
```

## How to run

`python ./critcus_cli/tei2json.py ./nt-transcripts ./json ntvmr igntp`

## Get all directory names for copying into your config

Run: `find ./ -mindepth 1 -type d -exec basename {} \; | sort | sed 's/^/"/;s/$/"/' | paste -sd, -`
Example output: `"0101-igntp","0103-ntvmr","0104-ntvmr","0105-igntp","0109-igntp","010-igntp"`