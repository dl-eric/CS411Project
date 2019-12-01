## Overview

Sentiment dict is sourced from: NRC Word-Emotion Association Lexicon (Mohammad & Turney, 2013). 

I converted NRC-Emotion-Lexicon-Wordlevel-v0.92.txt file into files of negative, positive arrays of json using python.

To install wordcloud, run:
```
git clone https://github.com/amueller/word_cloud.git
cd word_cloud
pip install .
```
Run 'python3 mongoDBAnalysis.py' after putting file named 'message_1.json' in the same folder 

Mohammad, S. M., & Turney, P. D. (2013). Crowdsourcing A Word-Emotion Association
Lexicon. Computational Intelligence,29(3), 436-465. doi:10.1111/j.1467-
8640.2012.00460.x