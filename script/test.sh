#!/bin/bash
# --input /mnt/lustre-client/hipo/datasets/tools/trace/的下一级目录
#         /mnt/lustre-client/hipo/datasets/tools/trace/cg.F.x-65536-sc.jsirun.bt20.pmu-0320_08-1
#         /mnt/lustre-client/hipo/datasets/tools/trace/sp.F.x-119716-sc.jsirun.bt20.pmu.ss-0320_08-1

# --output NO /mnt/lustre-client/hipo/datasets/tools/download_trace
#         /mnt/lustre/buaa_hipo  + /downloadpartID/

# --line_info_dump /mnt/lustre/buaa_hipo  + /downloadpartID/dwarf

# --event_file 某三个预选文件
# --time_offset  default:0
# --interval_length default:-1
# --number_of_events default:-1

# /ssd/dsk/JSI-Toolkit/build/tool/jsiconvert/jsiextract
# /ssd/dsk/JSI-Toolkit/build_env.sh
# /ssd/dsk/JSI-Toolkit/env.sh

# 输入基础目录
input_base="/mnt/lustre-client/hipo/datasets/tools/trace" #3
# 输入数据集
dataset="cg.F.x-65536-sc.jsirun.bt20.pmu-0320_08-1" #
# 输出基础目录
output_base="/mnt/lustre-client/buaa_hipo" #4 2
# 信息存放目录后缀
dir_suffix="123" #
#line_info_dump
dump="123"
# 工具的完整路径
tool_path="/home/buaa_hipo/JSI-toolkit/jsiextract" #

event_file="/home/buaa_hipo/web/event_file/group1" #1

time_offset=0 #5

interval_length=10 #6

number_of_events=10  #7

# echo $input_base
# echo $dataset
# echo $output_base
# echo $dir_suffix
# echo $tool_path
# echo $event_file
# echo $time_offset
# echo $interval_length
# echo $number_of_events

# 检查工具是否存在
if [ ! -f "$tool_path" ]; then
    echo "Error: Tool not found at $tool_path"
    exit 1
fi

input="$input_base/$dataset"
output="$output_base/$dir_suffix"
line_info_dump="$output_base/$dump"
# echo $input
# echo $output

mkdir -p "$output"

echo "$tool_path \
--input $input \
--output $output \
--line_info_dump $line_info_dump \
--event_file $event_file \
--time_offset $time_offset \
--interval_length $interval_length \
--number_of_events $number_of_events"

"$tool_path" \
    --input "$input" \
    --output "$output" \
    --line_info_dump "$output" \
    --event_file "$event_file" \
    --time_offset $time_offset \
    --interval_length $interval_length \
    --number_of_events $number_of_events

# echo "Processed $input"

# echo "All directories processed."
