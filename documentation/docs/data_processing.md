# Instructions to Create Model-Ready Dataset

1. Create an environment by following these directions. It should have all dependencies you need installed. A note that if you have a mac, some of the packages like GDAL might be harder to install.
    - Make sure you have the miniconda shell or another type of terminal installed. Type `conda info --envs` to see the other environments that exist.
    - Then type `conda env create tovaperlman/itu_test_02` . It should take a few moments to minutes for all the packages to download. 
    - Once this is done, you can check that it's an environment present in your computer by typing again `conda info --envs`
    - Then to activate the environment you can type `conda activate itu_test_02`


2. Once you've activated the environment which has all the necessary packages and dependencies installed, navigate in the same terminal to wherever you've saved the repository. Within that navigate to src/scripts/map_offline/. Then open the repository within a code editor (Visual Studio Code, Atom, Pycharm, etc.)

3. To generate a dataframe comprising any target variables and predictors that you wish to use, first set up the use case configurations in feature_engineering/configs.py. Details of the configurable variables and their expected assignments can be found in the 'configurations' section of the documentation.

For this, you must separately get access tokens for open cell ID, Google Earth Engine, and Facebook API. Once you have these, log all of them in the configs file. 

For Open Cell ID, you just need to sign up for an account and it will give you an API Access Token.

For Google Earth Engine, you must first [sign up](https://signup.earthengine.google.com/) for a [Google Earth Engine account] (https://earthengine.google.com/). You cannot use Google Earth Engine unless your application has been approved. Once you receive the application approval email, you can log in to the Earth Engine Code Editor to get familiar with the JavaScript API.

4. Having correctly set the desired configurations, all you need to do is run 'main.py'. Following this, a dataset for model training and/or application will be saved within a training_sets folder, which is situated within the data directory.
