# Rule Schema
The following describes how to write a `rule.yaml` file.

The file should have 2 top-level objects: 'rule', and 'filter'.

## Filter
The filter spec creates a filter object, which is run against all files scanned by the rule. If the file passes the filter, then actions are applied to it. The following fields are permitted in a filer declaration:

### name
*string* \
A regex pattern. Any files names that don't fully match the pattern are filtered out, even partial matches.

### size
*object* \
A size object defines parameters used to filter by the number of bytes a file has. \
All fields in this object accept string of the form `number unit`, where `unit` is either b, kb, mb, gb, or tb.

#### min
*file size* \
The minimum file size allowed.

#### max
*file size* \
The maximum file size allowed.

#### equals
*file size* \
Only allows files which are exactly this size. Cannot be used in conjuntion with `min` or `max`.

### age
*object* \
You can filter files by how old they are, to exclude anythign older than 6 months, or ignore anything from the last few days. \
All fields in this object should be formatted as `00 yr 00 mo 00 dy 00 h 00 m 00 s`. You can excludes units you aren't using (ex. just `12 h`), but you cannot rearrange the unit order (ex. `30 m 12 h`). The units are, in order, years, months, days, hours, minutes, seconds.

**Note**: The time spans specified in this section are natural: specifying `1 mo` will mean "this same date last month", regardless of how long the month is. If you want to specify "anythin within 90 days", you're better off using `90 dy` instead of `3 mo`.

#### min
*time span* \
Ignores files that are newer than this.

#### max
*time span* \
Ignores files that are older than this.

#### equals
*time span* \
Only include files that are exactly this old.