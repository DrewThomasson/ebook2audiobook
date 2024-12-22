#!/bin/bash

workers=$1

# Clean up operator directory
rm -rf "./Operator"
rm -rf "./Chapter_wav_files"
mkdir "./Operator"
mkdir "./Chapter_wav_files"


# Make appropriate temp directories
for i in $(seq 1 $workers); do
    mkdir "./Operator/$i"
    mkdir "./Operator/$i/temp"
    mkdir "./Operator/$i/temp_ebook"
done

echo "Created $workers directories"

#Divide the chapters
share=1
for FILE in ./Working_files/temp_ebook/*; do
    cp $FILE "./Operator/$share/temp_ebook/"
    if [ $share -lt $workers ];
    then
        share=$((share+1))
    else
        share=1
    fi
done

echo "Split chapters into operator"

#Run audio generation
#for i in $(seq 1 $workers); do
#    echo "Starting Worker $i"
#    python p2a_worker.py $i &
#done

gpu=1
for i in $(seq 1 $workers); do
    if [ $gpu -lt 2 ];
    then
        echo "Starting Worker $i on GPU 1"
        python p2a_worker_gpu1.py $i & #Run audio generation GPU 1 T4
        gpu=2 # switch to gpu 2 on next loop
    else
        echo "Starting Worker $i on GPU 2"
        python p2a_worker_gpu2.py $i & #Run audio generation GPU 2 T4
        gpu=1 # switch to gpu 1 on next loop
    fi
done



echo "All workers started waiting for completion...."
wait
echo "Done!"
