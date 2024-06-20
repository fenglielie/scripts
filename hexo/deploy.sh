#!/bin/bash

~/miniconda3/bin/python ./blogcheck.py

if [ $? -ne 0 ]; then
    echo "blog check: fail."
    exit 1
fi

~/miniconda3/bin/python ./headcheck.py

if [ $? -ne 0 ]; then
    echo "head check: fail."
    exit 1
fi

./hexo clean

if [ $? -ne 0 ]; then
    echo "hexo clean: fail."
    exit 1
fi


./hexo g

if [ $? -ne 0 ]; then
    echo "hexo g: fail."
    exit 1
fi

./hexo d

if [ $? -ne 0 ]; then
    echo "hexo d: fail."
    exit 1
fi
