#! /bin/sh

cd generated
latex -interaction nonstopmode pp.tex && dvipng -T tight pp.dvi
