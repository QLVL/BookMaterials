# Read me Chapter 6

Here, you can find all the Python and R scripts used for the analyses in chapter 6. The focus is on a single model (for the 16th and 17th century) but the code can also be used with minor adaptations to construct the other models referenced in the chapter.

## Contents
Data files are available in the [data folder](data/). The relevant scripts in [Python](Python/) and [R](R/) can be found in their respective folders.

The following scripts are available:
* [models_chapter6.py](Python/models_chapter6.py): Python script to create the distributional models, resulting in a [matrix with distances between all tokens](data/token-level/tokdists1617.ttmx.pac)
* [clustering_chapter6.R](R/clustering_chapter6.R): R-script to cluster the token distances with hierarchical clustering and to obtain t-SNE coordinates (data/destroy_diachronic_data.tsv and other files)
* [analyses_chapter6.R](R/analyses_chapter6.R): Script to obtain the visualizations on which the analyses in chapter 6 build

The scripts should be executed in this order.
