
$1 == "<P" {
	p = 0
}

p

$1 == "P>" {
	p = 1
}

END {
	print "exit"
}
