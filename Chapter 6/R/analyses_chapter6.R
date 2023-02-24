# ---
# title: Analyses chapter 6: The interplay of semasiology and onomasiology (in Lexical variation and change: A distributional-semantic approach)
# description: This file contains all the R-code used for plotting the figures in the chapter.
# author: Karlien Franco
# date: February 2023  
# ---

library(tidyverse); library(ggpubr); library(RColorBrewer)

# 6.1 Onomasiology and token clouds ----
## Model for FURIOUS ('woedend' and 'laaiend')
### Read data
# The data contains the hierarchical clustering solution in 3 clusters (clust_3) for 600 tokens of the lemmas.
# The coordinates from the t-SNE solution are in 'model.x' and 'model.y'.
furious_data <- read_tsv("../data/furious_data.tsv")
furious_data %>% group_by(lemma) %>% count

### Left panel of Figure 6.1
fig6.1_left <- furious_data %>% ggplot(aes(model.x, model.y, color = factor(clust_3), 
                                  shape = lemma)) + geom_point() + 
  scale_shape_manual(values = c(16,2)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") +
  guides(color = guide_legend(title="Cluster"), shape = guide_legend(title="Variant"))

### Right panel of Figure 6.1
furious_data$disambiguation <- factor(furious_data$disambiguation, levels = c("furious", "very", "burning", "other"))
fig6.1_right <- furious_data %>% ggplot(aes(model.x, model.y, color = factor(disambiguation), 
                                  shape = lemma)) + geom_point() + 
  scale_shape_manual(values = c(16,2)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Set1") +
  guides(color = guide_legend(title="Sense"), shape = guide_legend(title="Variant"))

### Figure 6.1
ggarrange(fig6.1_left, fig6.1_right, ncol = 2, nrow=1, common.legend = F)


## Model for GENIUS ('briljant' and 'geniaal')
### Read data
# The data contains the hierarchical clustering solution in 4 clusters (clust_4) for 549 tokens of the lemmas.
# The coordinates from the t-SNE solution are in 'model.x' and 'model.y'.
genius_data <- read_tsv("../data/genius_data.tsv")
genius_data %>% group_by(lemma) %>% count

### Left panel of Figure 6.2
fig6.2_left <- ggplot(genius_data %>% filter(in_concept != "?"), 
                      aes(x = model.x, y = model.y, color = factor(clust_4), shape = factor(country))) +
  geom_point() + scale_shape_manual(values = c(16,2)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") + 
  guides(color = guide_legend(title="Cluster"),shape = guide_legend(title="Country")) +
  theme(plot.title = element_text(size = 16)) 
fig6.2_left

### Right panel of Figure 6.2
right_panel_top <- ggplot(genius_data %>% filter(in_concept != "?"), aes(clust_4, fill = lemma)) + 
  geom_bar(position = position_dodge()) + coord_flip() +
  scale_y_continuous(breaks = c(0,50,100,150,200,250), limits = c(0,250)) +
  theme_classic() + scale_fill_brewer(type = "qual", palette = "Set1") + 
  guides(fill = guide_legend(title="Lemma")) + 
  theme(text = element_text(size = 10), legend.key.size = unit(0.1, "cm")) +
  xlab("") + ylab("frequency")

genius_data$in_concept <- factor(genius_data$in_concept, levels = c("yes", "no"))
right_panel_bottom <- ggplot(genius_data %>% filter(in_concept != "?"), aes(clust_4, fill = in_concept)) + 
  geom_bar(position = position_dodge()) + coord_flip() +
  scale_y_continuous(breaks = c(0,50,100,150,200,250), limits = c(0,250)) +
  theme_classic() + scale_fill_brewer(type = "qual", palette = "Set1") +
  guides(fill = guide_legend(title="Target\nsense")) + 
  theme(text = element_text(size = 10), legend.key.size = unit(0.1, "cm")) +
  xlab("") + ylab("frequency")

ggarrange(right_panel_top, right_panel_bottom, nrow = 2)

# 6.3 Destruction in contemporary Dutch ----
## Read data
destroy_synchrData <- read_tsv("../data/destroy_synchronic_data.tsv")
destroy_synchrData

## Figure 6.3
# The data contains the hierarchical clustering solution in 4 clusters (clust_4) for 486 tokens of the lemmas. 
# The coordinates from the t-SNE solution are in 'model.x' and 'model.y'.
Fig6.3 <- ggplot(destroy_synchrData, 
                 aes(model.x, model.y, colour = factor(clust_4), shape = lemma)) +
  geom_point() + theme_void() + scale_colour_brewer(type = "qual", palette = "Dark2") + 
  scale_shape_manual(values = c(2,16)) + 
  theme(legend.position = "bottom",legend.box = "vertical") +
  labs(color = "cluster")
Fig6.3  

## Figure 6.4
# There is also manually disambiguated data available, coded for agent and patient role (see table 6.1).
# Note that only a sample of tokens was coded (N = 77).
# Columns 'agent_codes' and 'patient_codes' are the original manual codes.
# Columns 'agent' and 'patient' are the reduced version used in Figures 6.4 and 6.5.
table(destroy_synchrData$agent)

# Reorganise factor levels and add NA codes
destroy_synchrData$agent <- factor(destroy_synchrData$agent, levels = c("authority", "criminal", "other_persons", "fire", "other_inanimate"))
destroy_synchrData$agent <- addNA(destroy_synchrData$agent)
table(destroy_synchrData$agent)

# Create custom palette, based on ColorBrewer Set1, with grey color for NAs
palette_agents <- c(brewer.pal(5, "Set1"), "grey")

Fig6.4 <- ggplot(destroy_synchrData, aes(model.x, model.y, shape = lemma, colour = agent, alpha = agent)) +
  geom_point(size = 2) + theme_void() +
  scale_colour_discrete(type = palette_agents) +
  scale_alpha_manual(values = c(rep(1,5), 0.2), guide = "none") +
  theme(legend.position = "bottom",legend.box = "vertical") 
Fig6.4

## Figure 6.5
table(destroy_synchrData$patient)

# Reorganise factor levels and add NA codes
destroy_synchrData$patient <- factor(destroy_synchrData$patient, levels = c("building", "utilitary", "other_concrete", "abstract"))
destroy_synchrData$patient <- addNA(destroy_synchrData$patient) # alternatief: definieer "NA" als factor level (niet zuiver)
table(destroy_synchrData$patient)

# Create custom palette, based on ColorBrewer Set1, with grey color for NAs
palette_patients <- c(brewer.pal(4, "Set1"), "grey")

Fig6.5 <- ggplot(destroy_synchrData, aes(model.x, model.y, shape = lemma, colour = patient, alpha = patient)) +
  geom_point(size = 2) + theme_void() + 
  scale_colour_discrete(type = palette_patients) + 
  scale_alpha_manual(values = c(rep(1, 4), 0.2), guide = FALSE) +
  theme(legend.position = "bottom",legend.box = "vertical") 
Fig6.5

# 6.5 The evolution of onomasiological sets ----
destroy_diachrData <- read_tsv("../data/destroy_diachronic_data.tsv")
destroy_diachrData

plot1617 <- ggplot(destroy_diachrData %>% filter(century == "16_17"), 
                   aes(x = tsne.x, y = tsne.y, color = factor(clust_4), shape = lemma)) +
  geom_point() + scale_shape_manual(values = c(2,16)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") + 
  guides(color = guide_legend(title = "Cluster"), shape = guide_legend(title = "Variant")) +
  theme(plot.title = element_text(size = 16)) + ggtitle("16th/17th century")
plot1617

plot18 <- ggplot(destroy_diachrData %>% filter(century == "18"), 
                   aes(x = tsne.x, y = tsne.y, color = factor(clust_4), shape = lemma)) +
  geom_point() + scale_shape_manual(values = c(2,16)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") + 
  guides(color = guide_legend(title = "Cluster"), shape = guide_legend(title = "Variant")) +
  theme(plot.title = element_text(size = 16)) + ggtitle("18th century")
plot18

plot19 <- ggplot(destroy_diachrData %>% filter(century == "19"), 
                 aes(x = tsne.x, y = tsne.y, color = factor(clust_4), shape = lemma)) +
  geom_point() + scale_shape_manual(values = c(2,16)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") + 
  guides(color = guide_legend(title = "Cluster"), shape = guide_legend(title = "Variant")) +
  theme(plot.title = element_text(size = 16)) + ggtitle("19th century")
plot19

plot20 <- ggplot(destroy_diachrData %>% filter(century == "20"), 
                 aes(x = tsne.x, y = tsne.y, color = factor(clust_4), shape = lemma)) +
  geom_point() + scale_shape_manual(values = c(2,16)) + theme_void() +
  scale_colour_brewer(type = "qual", palette = "Dark2") + 
  guides(color = guide_legend(title = "Cluster"), shape = guide_legend(title = "Variant")) +
  theme(plot.title = element_text(size = 16)) + ggtitle("20th century")
plot20

ggarrange(plot1617, plot18, plot19, plot20, 
          ncol = 2, nrow = 2, common.legend = TRUE, legend="bottom")





