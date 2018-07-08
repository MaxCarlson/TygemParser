# TygemParser
A simple utility to parse the TYGEM Go dataset into a useable format for GoNet. 

## Process Data
In order to use this utility you must download the [TYGEM dataset](https://github.com/yenw/computer-go-dataset#5-professional) and extract both the Kifu and index files. You can then tell the utlity where those folders of extracted files are, as well as where you'd like the output to be saved. Other options are max moves to write from each game and total moves to process. I recommed the low moves per game for better quality data (there's a distinct issue of overfitting with the value-head of GoNet if the moves per game is high).
