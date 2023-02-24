# ---
# title: Preprocessing chapter 6: The interplay of semasiology and onomasiology (in Lexical variation and change: A distributional-semantic approach)
# description: This file contains the R-code used for clustering the token vectors. The focus is on the diachronic data from the 16th and 17th century, but analyses are the same for the other datasets.
# author: Karlien Franco
# date: February 2023  
# ---

library(tidyverse); library(semcloud)

# Read data ----
# The token distances are saved in a json format. We use functions from semcloud to read and transform them.
mat <- tokensFromPac("../data/token-level/tokdists1617.ttmx.pac") # reads the data

# Some tokens do not have any context words according to the model, which distorts the results: they are all clustered in a single cloud, away from all the other tokens. 
# These tokens are removed in the clustering procedure.
cwsDF <- read_tsv("../data/token-level/cws_model1617.tsv")
na_tokids <- cwsDF %>% filter(is.na(cws)) %>% select(tokid) %>% pull

mat_RED <- mat[!rownames(mat) %in% na_tokids, !colnames(mat) %in% na_tokids] # remove tokens without context words (cws)
dists <- transformMats(mat_RED) # log-log-rank transforms the matrix 
dstmtx <- as.dist(dists)

# Clustering ----
## Hierarchical clustering
clust <- hclust(dstmtx, method = 'ward.D2')
clusters <- cutree(clust, 4) # 4 clusters

## nMDS (optional; not used in chapter)
# nmds_res <- getFit(dstmtx, technique = "mds") # wrapper around vegan::metaMDS from semcloud

## t-SNE
# Set a seed for reproducible results with set.seed()
tsne_res <- getFit(dstmtx, technique = "tsne", perp = 20) # wrapper around Rtsne::Rtsne from semcloud

## Make dataframe ----
clusterDF <- tibble(
  tokid = names(clusters), 
  clust_4 = clusters, 
  #NMDS.model.x = nmds_res$points[,"MDS1"], 
  #NMDS.model.y = nmds_res$points[,"MDS2"],
  tsne.x = tsne_res$Y[,1],
  tsne.y = tsne_res$Y[,2]
)
clusterDF

# Add lemmas
clusterDF$lemma <- str_extract(clusterDF$tokid, "^[^/]+")
clusterDF$lemma <- ifelse(str_detect(clusterDF$lemma, "verniet") == T, "vernietigen", "vernielen")
summary(factor(clusterDF$lemma))
clusterDF$century <- "16_17"

# Repeat for other centuries/subcorpora, rbind() the rows and save the data (write.table()).

