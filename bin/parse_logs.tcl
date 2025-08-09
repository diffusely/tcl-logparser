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
}

main
