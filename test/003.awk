
function mysub(x, y) {
	return x - y
}

mysub($1, 0) {
	print mysub(sqrt($1), $2)
}
