proc json_escape {str} {
	set str [string map { "\\" "\\\\" "\"" "\\\"" } $str]
	return $str
}

proc dict_to_json {dictData} {
    set json "{"
    set firstType 1
    foreach {type messages} $dictData {
        if {!$firstType} { append json "," }
        set firstType 0
        append json "\n\t\"$type\": {"
        set firstLine 1
        foreach {lineNum msg} $messages {
            if {!$firstLine} { append json "," }
            set firstLine 0
            append json "\n\t\t\"$lineNum\": \""
            append json [json_escape $msg]
            append json "\""
        }
        append json "\n\t}"
    }
    append json "\n }"
    return $json
}


proc parse_log_file {filepath} {
	set messages [dict create Error {} Warning {} Info {}]
	set fh [open $filepath "r"]
	set line_num 0
	while {[gets $fh line] >= 0} {
		incr line_num
		if {[regexp {^\s*(error|warning|info)\s*:\s*(.*)} $line -> type msg]} {
			set type [string tolower $type]
			set type [string toupper [string index $type 0]][string range $type 1 end]
			dict set messages $type $line_num $line
		}
	}
	close $fh
	return $messages
}

proc get_log_files {dir} {
	set files {}
	foreach item [glob -nocomplain -directory $dir *] {
		if {[file isdirectory $item]} {
			set files [concat $files [get_log_files $item]]
		} elseif {[string match "*.log" [file tail $item]]} {
			lappend files $item
		}
	}
	return $files
}

proc main {} {

	if {$::argc != 2} {
		puts "Error: Please provide exactly 2 arguments."
		exit 1
	}

	array set args {}

	for {set i 0} {$i < $::argc} {incr i} {
		set arg [lindex $::argv $i]
		if {$arg eq "-path"} {
			incr i
			set args(path) [lindex $::argv $i]
		}
	}

	if {![info exists args(path)]} {
		puts "<Usage: log_finding_script_name>.tcl -path <logs_root_path>"
		exit 1
	}

	set dir $args(path)
	if {![file isdirectory $dir]} {
		puts "Error: $dir is not a directory"
		exit 1
	}

	set all_logs [get_log_files $dir]

	if {[llength $all_logs] == 0} {
		puts "No log files found in directory: $dir"
		exit 1
	}

	set result {}

	foreach f $all_logs {
		set fname [file tail $f]
		set parsed [parse_log_file $f]
		dict set result $fname $parsed
	}

	set json_str "{"
	set firstFile 1
	foreach {fileName data} $result {
		if {!$firstFile} { append json_str "," }
		set firstFile 0
		append json_str "\n \"$fileName\": " [dict_to_json $data]
	}
	append json_str "\n}"

	set outFile "parsed_logs.json"
	set fh [open $outFile "w"]
	puts $fh $json_str
	close $fh

	puts "Result written to $outFile"
}

main
