#!/bin/bash
declare -a PROCESS_ARR
declare -a tmp_arr

exec 10<&0

exec < $1
let count=0

while read LINE; do
	PROCESS_ARR[$count]=$LINE
	((count++))
done

echo Number of elements: ${#PROCESS_ARR[@]}

echo ${PROCESS_ARR[@]}

exec 0<&10 10<&-


let i=0

while [ $i -le 10 ]; do

	if [ -e gdb_cmds ]; then
		rm gdb_cmds
		touch gdb_cmds
	else
		touch gdb_cmds
	fi

	for process in ${PROCESS_ARR[@]}; do
		echo $process
		tmp_arr=($(echo $process | tr ":" "\n"))
		echo attach ${tmp_arr[1]} >> gdb_cmds
		echo generate-core-file ${tmp_arr[0]}_${tmp_arr[1]}_$i>> gdb_cmds
		echo detach >> gdb_cmds
	done
	echo quit >> gdb_cmds
	((i++))
	sudo gdb < gdb_cmds
	sleep 10
done
