#!/bin/bash
FILES=./instances_scenarios_s2/*

rm -r parsed_instances
mkdir parsed_instances

for f in /home/thinklex/newground/generators/tmp/instances/instances_scenario_s2/*
do
	filename=$(basename "$f")
	count=$(grep -E -i -w '^edge' $f --count)

	if (($count < 10))
	then
		grep -E -i -w '^edge' $f > parsed_instances/0000${count}_${filename}
	elif (($count < 100))
	then
		grep -E -i -w '^edge' $f > parsed_instances/000${count}_${filename}
	elif (($count < 1000))
	then
		grep -E -i -w '^edge' $f > parsed_instances/00${count}_${filename}
	elif (($count < 10000))
	then
		grep -E -i -w '^edge' $f > parsed_instances/0${count}_${filename}
	elif (($count < 100000))
	then
		grep -E -i -w '^edge' $f > parsed_instances/${count}_${filename}
	else
		echo 'WHAT THE HELL'
	fi


done
