# -*- coding: utf-8 -*-
"""
@title: Modelling procedure chapter 6: The interplay of semasiology and onomasiology (in Lexical variation and change: A distributional-semantic approach)
@description: This file describes the procedure for creating the models in chapter 6. It focuses on the diachronic data (section 6.5) and specifically builds the model for the 16th and 17th century. All other models in the chapter have been built with the same code.
@author: Karlien Franco
@date: February 2023
"""
#%% Import libraries
import pandas as pd
import scipy as sp
import sys, re, random

nephosemdir = "/YOUR/PATH/TO/NEPHOSEM" # see https://github.com/QLVL/nephosem
sys.path.append(nephosemdir)
semasioFlowdir = "/YOUR/PATH/TO/SEMASIOFLOW" # see https://github.com/QLVL/semasioFlow
sys.path.append(semasioFlowdir)

from nephosem.conf import ConfigLoader # to setup the configuration
from nephosem import Vocab, TypeTokenMatrix # to manage frequency lists and matrices
from nephosem import ItemFreqHandler, ColFreqHandler, TokenHandler # to generate frequency lists and matrices
from nephosem import compute_association, compute_distance # to compute PPMI and distances
from nephosem.specutils.mxcalc import compute_token_weights, compute_token_vectors # for token level

from semasioFlow.utils import listCws # for getting cws per token

#%% Define other settings, based on your corpus
# See the tutorial: https://qlvl.github.io/nephosem/tutorials/all-in-one.html#1.-Configuration
conf = ConfigLoader()
settings = conf.settings
settings = conf.update_config('/PATH/TO/YOUR/config.ini')

print(settings)

output_path = settings["output-path"] 
# make sure to add an output folder to the configuration file, e.g. ../data/
# I tend to use subfolders: 
    # /input-files for intermediate matrixes (not included with this script due to data sharing limitations)
    # /token-level for the output with the final datasets (token vectors and token distances)

#%% Create frequency list for the corpus
# We rely on a txt-file containing the filenames that are available in the corpus
# This is repeated for every century (i.e. subcorpus) under analysis
centuries = [16,17,18,19,20]
fnames_per_cent = {}

for c in centuries:
    myfile = f"{output_path}/input-files/filenames/fnames_{c}.txt"
    with open(myfile, "r") as f:
        fnames = [x.strip() for x in f.readlines()]
    fnames_per_cent[c] = fnames

fnames_per_cent[1617] = fnames_per_cent[16] + fnames_per_cent[17] 
# 16th and 17th century data combined because of corpus sizes

# Then create the frequency list
vocabs_dict = {}
centuries = [16,17,1617,18,19,20]

for c in centuries:
    ifhan = ItemFreqHandler(settings = settings)
    vocab = ifhan.build_item_freq(fnames = fnames_per_cent[c])
    vocabs_dict[c] = vocab

# Finally store it
for c in centuries:
    vocab_fname = f"{output_path}/input-files/frequency-lists/freqlist_cent{c}.freq"
    vocabs_dict[c].save(vocab_fname) # note that 1617 = 1617

#%% Create co-occurrence matrix
# Loop over the centuries (subcorpora) and windowsizes needed and create a collocation frequency matrix with ColFreqHandler()
centuries = [1617,18,19,20]
windowsizes = [4,5,10]

for c in centuries:
    vocab = vocabs_dict[c]
    for w in windowsizes:
        settings['left-span'] = w
        settings['right-span'] = w
        cfhan = ColFreqHandler(settings=settings, row_vocab = vocab, col_vocab = vocab)
        freqMTX = cfhan.build_col_freq(fnames = fnames_per_cent[c])
        freqMTX.save(f"{output_path}/input-files/frequency-matrices/freqMTX_cent{c}_CW{w}.wcmx.pac")        

#%% Extract variant wordforms (and spellings in diachronic data) from the corpus
# For non-lemmatized data only
# Here, we extract them by checking which variants occur in the corpus data from the 16th and 17th century
cent = 1617 # choose between 1617, 18, 19, 20
vocab = vocabs_dict[cent] # This is the frequency list created previously
corpusspellings = vocab.keys()

# For 'vernielen', a word needs to start with 'verniel' or 'vernyel'
vernielen = list(filter(lambda x: x.startswith(("verniel", "verneyl")), corpusspellings))
# For 'vernietigen', a word needs to start with 'vernietig' or 'vernietich'
vernielen = list(filter(lambda x: x.startswith(("vernietig", "vernietich")), corpusspellings))
 
destroyspellings = vernielen + vernietigen
with open('destroyspellings.txt', 'w') as f:
    for item in destroyspellings:
        f.write("%s\n" % item)
# These forms need to be manually checked

# The correct forms (after the manual check) are finally stored in a dict
VariantsSpelling = {
    "vernielen": ["vernielen","vernielt","vernield","vernielde","verniele",
                  "verniel","vernielden","vernieldt","vernyelt", "vernyelen"],
    "vernietigen": ["vernietigen","vernietight","vernietigt","vernietigd",
                    "vernietig","vernietige","vernietigden","vernietigde",
                    "vernietighen","vernietighd","vernietighde", "vernieticht",
                    "vernietichde"]
} 

VariantsSpelling 

#%% Get tokens
# The following steps need to be repeated for every century/subcorpus
# First, we subset the frequency list by the variants under investigation
queries_flat = [s for k,v in VariantsSpelling.items() for s in v]
query = vocab.subvocab(queries_flat)

# Then we retrieve the tokens for the variants from the corpus for each century
settings['left-span'] = 10 # windowsize settings
settings['right-span'] = 10

tokhan = TokenHandler(query, settings=settings)
tokens_tmp = tokhan.retrieve_tokens(fnames = fnames_per_cent[cent]) 

# Finally, we sample 400 tokens
random.seed(97)
tokens_sample_ids = random.sample(tokens_tmp.row_items, 400)
tokens = tokens_tmp.submatrix(row = tokens_sample_ids).drop(axis = 1)

#%% Create final frequency matrix
# First load the appropriate frequency matrix created above.
# Rows will be used for the wordforms under investigation; columns are (first-order) context features.
freqMTX_fname = f"{output_path}/input-files/frequency-matrices/freqMTX_cent{c}_CW{w}.wcmx.pac" 
freqMTX = TypeTokenMatrix.load(freqMTX_fname)

# Subset rows to only include wordforms under investigation
freqMTX_FOC = freqMTX.submatrix(row=queries_flat)
freqMTX_FOC

# Subset columns to only include considered context words (here: wordforms with frequency > 10)
# For other data (e.g. with PoS-tagging), other settings can be applied in this step
freqs_words = dict([(key, value) for key, value in vocab.items() if re.match("^\w+$", key)])
freqs_words_vocab = Vocab(freqs_words)
focs = freqs_words_vocab[freqs_words_vocab.freq > 10] # these are the considered first-order context words only
freqMTX_FOC_sub = freqMTX_FOC.submatrix(col = focs.keys()) # subset columns
freqMTX_FOC_sub 

# For non-PoS-tagged data only:
# As we're working with word forms, we need to create a matrix 
# with one value that is identical for all wordforms per lemma 
# (i.e. a single value for all the rows belonging to the same lemma vernielen or vernietigen).
# We do this by calculating the summed frequency of all the variants per lemma.
## Vernielen
vernielen_variants = ['vernielen','vernielt','vernield','vernielde','verniele','verniel',
                      'vernielden','vernieldt','vernyelt','vernyelen']

freqMTX_FOC_sub_vernielen = freqMTX_FOC_sub.submatrix(row = vernielen_variants)

# Sum all the frequencies
mtx = freqMTX_FOC_sub_vernielen.get_matrix()
sums = mtx.sum(axis = 0)
sums_sparse = sp.sparse.csr_matrix(sums)
freqMTX_FOC_sub_red_vernielen = TypeTokenMatrix(sums_sparse, ["vernielen"], freqMTX_FOC_sub_vernielen.col_items)

# Duplicate the rows for the total number of variants and change the row names to the seperate variants
freqMTX_FOC_sub2_vernielen = freqMTX_FOC_sub_red_vernielen.copy()
for s in range(len(vernielen_variants)-1):  
    freqMTX_FOC_sub2_vernielen = freqMTX_FOC_sub2_vernielen.concatenate(freqMTX_FOC_sub_red_vernielen)
freqMTX_FOC_sub2_vernielen.row_items = vernielen_variants

## Vernietigen (same procedure)
vernietigen_variants = ["vernietigen","vernietight","vernietigt","vernietigd","vernietig","vernietige","vernietigden",
                        "vernietigde","vernietighen","vernietighd","vernietighde", "vernieticht", "vernietichde"]

freqMTX_FOC_sub_vernietigen = freqMTX_FOC_sub.submatrix(row = vernietigen_variants)

# Sum all the frequencies
mtx = freqMTX_FOC_sub_vernietigen.get_matrix()
sums = mtx.sum(axis = 0)
sums_sparse = sp.sparse.csr_matrix(sums)
freqMTX_FOC_sub_red_vernietigen = TypeTokenMatrix(sums_sparse, ["vernietigen"], freqMTX_FOC_sub_vernietigen.col_items)

# Duplicate the rows for the total number of variants and change the row names to the seperate variants
freqMTX_FOC_sub2_vernietigen = freqMTX_FOC_sub_red_vernietigen.copy()
for s in range(len(vernietigen_variants)-1):  
    freqMTX_FOC_sub2_vernietigen = freqMTX_FOC_sub2_vernietigen.concatenate(freqMTX_FOC_sub_red_vernietigen)
freqMTX_FOC_sub2_vernietigen.row_items = vernietigen_variants

# Finally merge the two matrixes
freqMTX_FOC_merge = freqMTX_FOC_sub2_vernielen.merge(freqMTX_FOC_sub2_vernietigen)
freqMTX_FOC_merge

# We now have a frequency matrix, with:
    # rows: all the variants occuring for the lemmas (vernielen/vernietigen) in the corpus
    # columns: considered first-order context words only
    # values: total frequency of each lemma with each of the considered context words

#%% Create association matrix
# We now calculate ppmi values (or use another association strength measure) to obtain an association matrix
# Rows and columns remain the same, but values are now association strength values (here: ppmi)
# This matrix will later be used for weighting the impact of the second-order vectors

# First, we need to calculate the marginal frequencies based on co-occurrence frequencies for the full corpus
nfreq = Vocab(freqMTX.sum(axis=1))
cfreq = Vocab(freqMTX.sum(axis=0))

# Next, we calculate the association between the variants and the context words (token.col_items)
# We use the frequency matrix that has the total sum of all the variants per lemma (freqMTX_FOC_sub_red_vernielen or freqMTX_FOC_sub_red_vernietigen)
# vernielen
freqMTX_FOC_sub_red_vernielen_SUB = freqMTX_FOC_sub_red_vernielen.submatrix(row = queries_flat, col = tokens.col_items).drop(axis = 1)
weighter_vernielen = compute_association(freqMTX_FOC_sub_red_vernielen, nfreq=nfreq, cfreq=cfreq, meas = 'ppmi')
# Again, duplicate the rows to have as many as there are variants
weighter_vernielen2 = weighter_vernielen.copy()
for s in range(len(vernielen_variants)-1):  
    weighter_vernielen2 = weighter_vernielen2.concatenate(weighter_vernielen)
weighter_vernielen2.row_items = vernielen_variants
weighter_vernielen2

# vernietigen
freqMTX_FOC_sub_red_vernietigen_SUB = freqMTX_FOC_sub_red_vernietigen.submatrix(row = queries_flat, col = tokens.col_items).drop(axis = 1)
weighter_vernietigen = compute_association(freqMTX_FOC_sub_red_vernietigen, nfreq=nfreq, cfreq=cfreq, meas = 'ppmi')
# Again, duplicate the rows to have as many as there are variants
weighter_vernietigen2 = weighter_vernietigen.copy()
for s in range(len(vernietigen_variants)-1):  
    weighter_vernietigen2 = weighter_vernietigen2.concatenate(weighter_vernietigen)
weighter_vernietigen2.row_items = vernietigen_variants
weighter_vernietigen2

# Merge the matrixes
weighter_merge = weighter_vernielen2.merge(weighter_vernietigen2)
weighter_merge

# We add some further limits on allowed contextwords (here: only ppmi > 2)
weighter_final = weighter_merge.submatrix(col = tokens.col_items).drop(axis = 1)
weighter_final = weighter_final.multiply(weighter_final > 2).drop(axis=1) # Additional ppmi cut-off

#%% Compute token weights
# We compute tokens weights, weighing the context words by their association with the target variants
tokens_SUB = tokens.submatrix(col = weighter_final.col_items)
weighted = compute_token_weights(tokens_SUB, weighter_final)
weighted

#%% Second-order dimensions
# Finally, we replace the weighted context words by their type-level vectors with compute_token_vectors().
# This function needs a token level weight matrix (weighted_FIN below) and a second-order type-level matrix (socMTX below) 

# Create socMTX
# First, we load the frequency matrix with context windows = 4 (used for calculating associations with type-level vectors)
freqMTX4_fname = f"{output_path}/input-files/frequency-matrices/freqMTX_cent{c}_CW{w}.wcmx.pac" # cent
freqMTX4 = TypeTokenMatrix.load(freqMTX4_fname)

# Then we define which second-order context words will be allowed and subset the frequency matrix
# (here: 5000 most frequent items that are wordforms, excluding the first (uninformative) 100)
vocab_socs = Vocab(dict([(key, value) for key, value in vocabs_dict[cent].items() if re.match("^\w+$", key)])) #cent
vocab_sub = vocab_socs[100:] 
vocab_sub5000 = vocab_sub[:5000]
vocab_sub5000
freqMTX4_5000 = freqMTX4.submatrix(row = vocab_sub5000.get_item_list(), col = vocab_sub5000.get_item_list())

# We calculate the values (pmi) in the same way as before
nfreq = Vocab(freqMTX4_5000.sum(axis=1))
cfreq = Vocab(freqMTX4_5000.sum(axis=0))
ppmiMTX_soc = compute_association(freqMTX4_5000, nfreq=nfreq, cfreq=cfreq, meas = 'ppmi')

# Then we subset the matrix to have the first-order context words (weighted.col_items) as rows 
socMTX = ppmiMTX_soc.submatrix(row = weighted.col_items).drop(axis = 1)

# Finalize the token-level weighted matrix
# Subset so that the columns are identical to the rows of socMTX
weighted_FIN = weighted.submatrix(col = socMTX.row_items)

# We use these matrixes to obtain the final token vectors
tokvecs = compute_token_vectors(weighted_FIN, socMTX)
tokvecs

# Optionally save the vectors with save method for TypeTokenMatrix class:
# tokvecs.save(f"{output_path}/token-level/tokvecs{cent}.ttmx.ppmi.pac") 

#%% Distances between tokens
# Distances are calculated with compute_distance(). The default is to calculate cosine distances.
tokdists = compute_distance(tokvecs)
tokdists

tokdists.save(f"{output_path}/token-level/tokdists{cent}.ttmx", pack = True)

#%% Other data
# For the calculations in Tables 6.6-6.9, we also need the context words on which the model relies per token.
# We extract these with listCWS() from the token-level weighted matrix and save them as a tsv-file.
cws = listCws(weighted_FIN)
cws_df = pd.DataFrame.from_dict(cws, orient = "index").reset_index()
cws_df.columns = ['tokid', 'cws']
cws_df.to_csv(f"{output_path}/token-level/cws_model{cent}.tsv", index = False, sep = "\t") # cent
