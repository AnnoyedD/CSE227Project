#!/bin/bash
DATA_PATH=$(pwd)
FILE_OUTPUT="$DATA_PATH/$2.data"
let frame_count=0

#Open original binary file ($ELF)
#Output its section information - $readelf -t $ELF
#readelf -t $1 > $FILE_OUTPUT 

#Open core file ($CORE)
#First count number of frames - frame > frame.tmp
if [ -e gdb_count_frame ]; then
	rm gdb_count_frame
fi
if [ -e $2_frame.tmp ]; then
	rm $2_frame.tmp
fi

touch gdb_count_frame
echo "file $1" >> gdb_count_frame
echo "core $2" >> gdb_count_frame
echo "set logging file $2_frame.tmp" >> gdb_count_frame
echo "set logging overwrite on" >> gdb_count_frame
echo "set logging on" >> gdb_count_frame
echo "bt" >> gdb_count_frame
echo "set logging off" >> gdb_count_frame
echo "quit" >> gdb_count_frame

gdb < gdb_count_frame
frame_count=$(cat $2_frame.tmp | wc -l)
let "frame_count-=1"
echo -----Frame_Count is $frame_count

#Record the size of each frame
declare -a FRAME_SIZE
if [ -e gdb_count_size ]; then
	rm gdb_count_size
fi
if [ -e $2_frame_size.tmp ]; then
	rm $2_frame_size.tmp
fi

touch gdb_count_size
echo "file $1" >> gdb_count_size
echo "core $2" >> gdb_count_size
echo "set logging file $2_frame_size.tmp" >> gdb_count_size

let i=0
while [ $i -le $frame_count ]; do
	echo "set logging on" >> gdb_count_size
	echo "p (\$rbp-\$rsp)/4" >> gdb_count_size
	echo "set logging off" >> gdb_count_size
	if [ $i -ne $frame_count ]; then
		echo "up" >> gdb_count_size
	fi

	((i++))
done

echo "set logging off" >> gdb_count_size
echo "quit" >> gdb_count_size
gdb < gdb_count_size

#Store the size of each frame into script
declare -a FRAME_SIZE
declare -a tmp_arr
exec 10<$0
exec < $2_frame_size.tmp
let count=0
while read LINE; do
	tmp_arr=($LINE)
	FRAME_SIZE[$count]=${tmp_arr[-1]}
	((count++))
done
echo The size of each frame is: ${FRAME_SIZE[@]}

#Open core file again ($CORE)
#Output content of each frame
if [ -e gdb_output_stack ]; then
	rm gdb_output_stack
fi
if [ -e $FILE_OUTPUT ]; then
	rm $FILE_OUTPUT
fi
touch gdb_output_stack
echo "file $1" > gdb_output_stack
echo "core $2" >> gdb_output_stack
echo "set logging file $FILE_OUTPUT" >> gdb_output_stack

let i=0
for frame in ${FRAME_SIZE[@]}; do
	echo "set logging on" >> gdb_output_stack
	if (( ${frame} > 0 )); then
		echo "echo \n@$i\n" >> gdb_output_stack
		echo "x/$frame""xw \$rsp" >> gdb_output_stack
		echo "echo \n%$i\n" >> gdb_output_stack
	fi
	echo "set logging off" >> gdb_output_stack
	echo "up" >> gdb_output_stack
	((i++))
done

echo "quit" >> gdb_output_stack

#Execute analysis script



