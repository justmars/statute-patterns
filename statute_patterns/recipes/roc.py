roc_texts = ["Rules", "of", "Court"]

roc_texts_title = r"\s+".join(roc_texts)
roc_title = rf"(?:{roc_texts_title})"

roc_texts_upper = r"\s+".join([i.upper() for i in roc_texts])
roc_title_capped = rf"(?:{roc_texts_upper})"

roc_short = r"""(?:ROC)"""

ROC = "|".join([roc_title_capped, roc_title, roc_short])
