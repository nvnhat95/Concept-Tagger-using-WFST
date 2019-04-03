# Concept-Tagger-using-WFST
Building concept tagging model with Weighted finite state transducer using OpenFST and OpenGRM


**1. Structure**:
  * *main.py*:  main file, run this file to execute the models
  * *utils.py*: 
  * *variations.py*:  config different versions of models, read the report for more details
  * *wrapper.py*: a Python wrapper of some functions of OpenFST and OpenGRM used in this project
  * *datasets*: contains data files
  * *baseline*:
    * *language_models*: contains language model *.lm files
    * *result*:
      * pred_X: prediction when running with method X
      * score_pred_X: score (accuracy, F1, ...) when running with method X
  * *variation\**: similar to *baseline*
  * *explore_dataset*: notebook file used for exploring dataset and get the results
  * *conlleval.pl*: for evaluation
  
**2. How to run**:
  Make sure you have OpenFST, OpenGRM and Python3 installed
  * To know the arguments of program:
  > python3 main.py -h
  * For example: 
      * to run the benchmark between configurations with baseline model, type
      > python3 main.py --version=baseline --mode=benchmark
      * to run single configuration, such as 4-gram absolute smoothing method, with variation1, type
      > python3 main.py --version=variation1 --mode=single --method=absolute-4
  * Note: By default, this program does not run again methods that had been done, to force it to run again, manually delete the target forlder or set
      > --iscontinue=False
      
 	
~~~~
Author: Viet Nhat Nguyen - 204734
~~~~
