import importlib
modules = ['sentence_transformers', 'sklearn.metrics.pairwise', 'fitz', 'langdetect', 'reportlab']
for m in modules:
    try:
        importlib.import_module(m)
        print(m, 'OK')
    except Exception as e:
        print(m, 'ERROR', e)
